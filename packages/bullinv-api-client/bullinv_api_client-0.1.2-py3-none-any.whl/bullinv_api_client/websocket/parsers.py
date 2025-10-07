from __future__ import annotations

import json
from typing import Any, Mapping, List
from dataclasses import dataclass

from .models import Aggregate, Indicators


@dataclass
class Subscription:
    timespan: str
    ticker: str


def _to_mapping(data: Any) -> Mapping[str, Any]:
    if isinstance(data, (bytes, bytearray)):
        return json.loads(data.decode())
    if isinstance(data, str):
        return json.loads(data)
    if isinstance(data, Mapping):
        return data
    raise TypeError("Unsupported input type for parse function")


def parse_aggregate(data: Any) -> Aggregate:
    obj = _to_mapping(data)
    return Aggregate.from_dict(obj)


def parse_indicators(data: Any) -> Indicators:
    obj = _to_mapping(data)
    return Indicators.from_dict(obj)


def parse_subscriptions(params: str) -> List[Subscription]:
    items: List[Subscription] = []
    for token in (params or "").split(","):
        token = token.strip()
        if not token:
            continue
        if "." not in token:
            raise ValueError(f"Invalid subscription item: {token}")
        timespan, ticker = token.split(".", 1)
        items.append(Subscription(timespan, ticker))
    return items


# Convenience alias
parse_subs = parse_subscriptions


