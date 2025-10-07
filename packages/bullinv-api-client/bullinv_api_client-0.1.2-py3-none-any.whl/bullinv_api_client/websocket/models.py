from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional, NewType, List, Union


def parse_rfc3339(ts: str) -> datetime:
    # Python 3.11+ supports fromisoformat for RFC3339 without Z.
    try:
        if ts.endswith("Z"):
            # Replace Z with +00:00 for fromisoformat
            return datetime.fromisoformat(ts[:-1] + "+00:00")
        return datetime.fromisoformat(ts)
    except Exception:
        # Fallback to naive parsing
        return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S%z").astimezone(timezone.utc)


@dataclass
class Aggregate:
    symbol: str
    market: str
    ts: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    transactions: int
    event_time: Optional[datetime]

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Aggregate":
        return Aggregate(
            symbol=str(data.get("symbol", "")),
            market=str(data.get("market", "")),
            ts=parse_rfc3339(str(data.get("ts"))),
            open=float(data.get("open", 0.0)),
            high=float(data.get("high", 0.0)),
            low=float(data.get("low", 0.0)),
            close=float(data.get("close", 0.0)),
            volume=float(data.get("volume", 0.0)),
            transactions=int(data.get("transactions", 0)),
            event_time=parse_rfc3339(data["event_time"]) if data.get("event_time") else None,
        )


@dataclass
class Indicators:
    symbol: str
    market: str
    ts: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    transactions: int
    indicators: Dict[str, Any]
    event_time: Optional[datetime]

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Indicators":
        return Indicators(
            symbol=str(data.get("symbol", "")),
            market=str(data.get("market", "")),
            ts=parse_rfc3339(str(data.get("ts"))),
            open=float(data.get("open", 0.0)),
            high=float(data.get("high", 0.0)),
            low=float(data.get("low", 0.0)),
            close=float(data.get("close", 0.0)),
            volume=float(data.get("volume", 0.0)),
            transactions=int(data.get("transactions", 0)),
            indicators=dict(data.get("indicators", {})),
            event_time=parse_rfc3339(data["event_time"]) if data.get("event_time") else None,
        )


WebSocketMessage = NewType("WebSocketMessage", List[Union[Aggregate, Indicators]])