import os
import json
from typing import Optional, List, Set, Union, Callable, Awaitable
import asyncio
import ssl
import certifi
from ..exceptions import AuthError
from .common import DataType
from .models import WebSocketMessage
from ..logger import get_logger
import logging
from websockets.client import connect, WebSocketClientProtocol
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError
env_key = "BULLINV_API_KEY"
logger = get_logger(__name__)

class WebSocketClient:
    def __init__(
        self,
        api_key: Optional[str] = os.getenv(env_key),
        datatype: DataType = DataType.Aggregates,
        subscriptions: Optional[List[str]] = None,
        max_reconnects: Optional[int] = 5,
        secure: bool = True,
        verbose: bool = False
    ):
        if verbose:
            logger.setLevel(logging.DEBUG)
        
        if api_key is None:
            raise AuthError(f"Must specify env var {env_key} or pass api_key in constructor")

        self.api_key = api_key
        # self.url = "wss://quote-ws.bullinv.tech" if secure else "ws://quote-ws.bullinv.tech"
        self.url = f"ws{'s' if secure else ''}://quote-ws.bullinv.tech/{datatype.value}"
        self.subscribed = False
        self.subs: Set[str] = set()
        self.max_reconnects = max_reconnects
        self.websocket: Optional[WebSocketClientProtocol] = None
        if subscriptions is None:
            subscriptions = []
        self.scheduled_subs: Set[str] = set(subscriptions)
        self.schedule_resub = True
        self.json = json

    async def connect(
            self,
            processor: Union[
                Callable[[List[WebSocketMessage]], Awaitable],
                Callable[[Union[str, bytes]], Awaitable],
            ],
            close_timeout: int = 1,
            **kwargs,
        ):
            """
            Connect to websocket server and run `processor(msg)` on every new `msg`.

            :param processor: The callback to process messages.
            :param close_timeout: How long to wait for handshake when calling .close.
            :raises AuthError: If invalid API key is supplied.
            """
            reconnects = 0
            logger.debug("connect: %s", self.url)

            ssl_context = None
            if self.url.startswith("wss://"):
                ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                ssl_context.load_verify_locations(certifi.where())

            async for s in connect(
                self.url, close_timeout=close_timeout, ssl=ssl_context, **kwargs
            ):
                self.websocket = s
                try:
                    msg = await s.recv()
                    logger.debug("connected: %s", msg)
                    logger.debug("authing...")
                    await s.send(
                        self.json.dumps({"action": "auth", "params": self.api_key})
                    )
                    auth_msg = await s.recv()
                    auth_msg_parsed = self.json.loads(auth_msg)
                    logger.debug("authed: %s", auth_msg)
                    if auth_msg_parsed[0]["status"] == "auth_failed":
                        raise AuthError(auth_msg_parsed[0]["message"])
                    while True:
                        if self.schedule_resub:
                            logger.debug(
                                "reconciling: %s %s", self.subs, self.scheduled_subs
                            )
                            new_subs = self.scheduled_subs.difference(self.subs)
                            await self._subscribe(new_subs)
                            old_subs = self.subs.difference(self.scheduled_subs)
                            await self._unsubscribe(old_subs)
                            self.subs = self.scheduled_subs
                            self.subs = set(self.scheduled_subs)
                            self.schedule_resub = False

                        try:
                            cmsg: Union[List[WebSocketMessage], Union[str, bytes]] = (
                                await asyncio.wait_for(s.recv(), timeout=1)
                            )
                        except asyncio.TimeoutError:
                            continue

                        msg_json = self.json.loads(cmsg)  # type: ignore
                        filtered = [m for m in msg_json if m.get("ev", "") != "status"]
                        for m in msg_json:
                            if m.get("ev", "") == "status":
                                logger.debug("status: %s", m.get("message", ""))

                        if len(filtered) > 0:
                            await processor(filtered)  # type: ignore
                except ConnectionClosedOK as e:
                    logger.debug("connection closed (OK): %s", e)
                    return
                except ConnectionClosedError as e:
                    logger.debug("connection closed (ERR): %s", e)
                    reconnects += 1
                    self.scheduled_subs = set(self.subs)
                    self.subs = set()
                    self.schedule_resub = True
                    if self.max_reconnects is not None and reconnects > self.max_reconnects:
                        return
                    continue

    def run(
        self,
        handle_msg: Union[
            Callable[[List[WebSocketMessage]], None],
            Callable[[Union[str, bytes]], None],
        ],
        close_timeout: int = 1,
        **kwargs,
    ):
        """
        Connect to websocket server and run `processor(msg)` on every new `msg`. Synchronous version of `.connect`.

        :param processor: The callback to process messages.
        :param close_timeout: How long to wait for handshake when calling .close.
        :raises AuthError: If invalid API key is supplied.
        """

        async def handle_msg_wrapper(msgs):
            handle_msg(msgs)

        asyncio.run(self.connect(handle_msg_wrapper, close_timeout, **kwargs))

    async def _subscribe(self, topics: Union[List[str], Set[str]]):
        print("subbing", topics)
        if self.websocket is None or len(topics) == 0:
            return
        subs = ",".join(topics)
        logger.debug("subbing: %s", subs)
        await self.websocket.send(
            self.json.dumps({"action": "subscribe", "params": subs})
        )

    async def _unsubscribe(self, topics: Union[List[str], Set[str]]):
        if self.websocket is None or len(topics) == 0:
            return
        subs = ",".join(topics)
        logger.debug("unsubbing: %s", subs)
        await self.websocket.send(
            self.json.dumps({"action": "unsubscribe", "params": subs})
        )

    @staticmethod
    def _parse_subscription(s: str):
        s = s.strip()
        split = s.split(".", 1)  # Split at the first period
        if len(split) != 2:
            logger.warning("invalid subscription:", s)
            return [None, None]

        return split

    def subscribe(self, *subscriptions: str):
        """
        Subscribe to given subscriptions.

        :param subscriptions: Subscriptions (args)
        """
        for s in subscriptions:
            topic, sym = self._parse_subscription(s)
            if topic == None:
                continue
            logger.debug("sub desired: %s", s)
            self.scheduled_subs.add(s)
            # If user subs to X.*, remove other X.\w+
            if sym == "*":
                for t in list(self.subs):
                    if t.startswith(topic):
                        self.scheduled_subs.discard(t)

        self.schedule_resub = True

    def unsubscribe(self, *subscriptions: str):
        """
        Unsubscribe from given subscriptions.

        :param subscriptions: Subscriptions (args)
        """
        for s in subscriptions:
            topic, sym = self._parse_subscription(s)
            if topic == None:
                continue
            logger.debug("sub undesired: %s", s)
            self.scheduled_subs.discard(s)

            # If user unsubs to X.*, remove other X.\w+
            if sym == "*":
                for t in list(self.subs):
                    if t.startswith(topic):
                        self.scheduled_subs.discard(t)

        self.schedule_resub = True

    def unsubscribe_all(self):
        """
        Unsubscribe from all subscriptions.
        """
        self.scheduled_subs = set()
        self.schedule_resub = True

    async def close(self):
        """
        Close the websocket connection.
        """
        logger.debug("closing")

        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        else:
            logger.warning("no websocket open to close")

