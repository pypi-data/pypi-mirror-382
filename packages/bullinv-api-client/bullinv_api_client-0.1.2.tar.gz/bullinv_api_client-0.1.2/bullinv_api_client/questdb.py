import os
import json
from datetime import date, datetime
from typing import Optional, Union, Dict, Any, List

import requests
import pandas as pd


DateLike = Union[str, date, datetime]


class QuestDBClient:
    """
    Thin REST client for executing SQL queries against a QuestDB-compatible endpoint.

    By default, this targets `https://questdb-api.bullinv.tech/exec` and
    authenticates via Cloudflare Access headers. Credentials are read from the
    environment variables `CF_ACCESS_CLIENT_ID` and `CF_ACCESS_CLIENT_SECRET` unless
    explicitly provided to the constructor.

    The main convenience provided is `get_daily_candles`, which returns a pandas
    DataFrame for a daily candlestick table.
    """

    def __init__(
        self,
        base_url: str = "https://questdb-api.bullinv.tech",
        exec_path: str = "/exec",
        cf_access_client_id: Optional[str] = None,
        cf_access_client_secret: Optional[str] = None,
        timeout_seconds: int = 30,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.exec_path = exec_path
        self.timeout_seconds = timeout_seconds

        self.cf_access_client_id = (
            cf_access_client_id
            if cf_access_client_id is not None
            else os.getenv("CF_ACCESS_CLIENT_ID")
        )
        self.cf_access_client_secret = (
            cf_access_client_secret
            if cf_access_client_secret is not None
            else os.getenv("CF_ACCESS_CLIENT_SECRET")
        )

        if not self.cf_access_client_id or not self.cf_access_client_secret:
            raise ValueError(
                "Missing Cloudflare Access credentials. Set CF_ACCESS_CLIENT_ID and CF_ACCESS_CLIENT_SECRET."
            )

        self._session = session or requests.Session()

    # -----------------------------
    # Public API
    # -----------------------------
    def execute_sql(self, sql: str) -> pd.DataFrame:
        """
        Execute raw SQL using the QuestDB `/exec`-compatible endpoint and return a DataFrame.
        """
        url = f"{self.base_url}{self.exec_path}"
        headers = self._build_headers()
        params = {"query": sql}

        response = self._session.get(
            url,
            headers=headers,
            params=params,
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()

        # Expect QuestDB JSON shape with `columns` and `dataset`.
        # If the response is not JSON (e.g., HTML error page), raise a helpful error.
        try:
            payload = response.json()
        except Exception as exc:  # JSON decode error or similar
            content_type = response.headers.get("Content-Type", "")
            snippet = (response.text or "")[:500]
            raise ValueError(
                f"Non-JSON response from QuestDB endpoint: status={response.status_code}, "
                f"content_type='{content_type}', url='{url}'. Body snippet: {snippet}"
            ) from exc

        return self._to_dataframe(payload)

    def get_daily_candles(
        self,
        symbol: str,
        start_date: DateLike,
        end_date: Optional[DateLike] = None,
        *,
        table: str = "candlesticks_1d",
        symbol_column: str = "symbol",
        time_column: str = "ts",
        columns: Optional[List[str]] = None,
        source: Optional[str] = None,
        asset_type: Optional[str] = None,
        exchange: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Fetch daily candlestick rows for a given symbol and date range.

        Parameters
        - symbol: ticker symbol (e.g., "AAPL")
        - start_date: inclusive start date (str "YYYY-MM-DD" or datetime/date)
        - end_date: exclusive end date (defaults to None for open-ended)
        - table: QuestDB table name for daily candles (default: "candlesticks_1d")
        - symbol_column: column name for the symbol (default: "symbol")
        - time_column: timestamp/date column name (default: "ts")
        - columns: optional list of columns to select; defaults to OHLCV + transactions
        - source/asset_type/exchange: optional filters matching schema columns
        """
        if columns is None:
            columns = [
                time_column,
                "open",
                "high",
                "low",
                "close",
                "volume",
                "transactions",
            ]

        start_str = self._to_iso_date_string(start_date)
        end_str = self._to_iso_date_string(end_date) if end_date is not None else None

        safe_symbol = symbol.replace("'", "''")
        safe_source = source.replace("'", "''") if source is not None else None
        safe_asset_type = asset_type.replace("'", "''") if asset_type is not None else None
        safe_exchange = exchange.replace("'", "''") if exchange is not None else None
        select_cols = ", ".join(columns)

        conditions = [f"{symbol_column} = '{safe_symbol}'", f"{time_column} >= cast('{start_str}' as date)"]
        if end_str is not None:
            conditions.append(f"{time_column} < cast('{end_str}' as date)")
        if safe_source is not None:
            conditions.append(f"source = '{safe_source}'")
        if safe_asset_type is not None:
            conditions.append(f"asset_type = '{safe_asset_type}'")
        if safe_exchange is not None:
            conditions.append(f"exchange = '{safe_exchange}'")

        where_clause = " AND ".join(conditions)
        sql = f"SELECT {select_cols} FROM {table} WHERE {where_clause} ORDER BY {time_column}"

        df = self.execute_sql(sql)

        # Attempt to parse time column as datetime if present
        if time_column in df.columns:
            try:
                df[time_column] = pd.to_datetime(df[time_column], utc=True)
            except Exception:
                pass
        return df

    # -----------------------------
    # Internals
    # -----------------------------
    def _build_headers(self) -> Dict[str, str]:
        # Prefer two-header mode per Cloudflare docs, optionally support single-header Authorization-like form.
        single_header = os.getenv("CF_ACCESS_SINGLE_HEADER")  # e.g., "Authorization"
        if single_header:
            value = {
                "cf-access-client-id": self.cf_access_client_id,
                "cf-access-client-secret": self.cf_access_client_secret,
            }
            return {
                single_header: json.dumps(value),
                "Accept": "application/json, text/plain;q=0.9, */*;q=0.8",
            }

        return {
            "CF-Access-Client-Id": self.cf_access_client_id,  # Cloudflare Access
            "CF-Access-Client-Secret": self.cf_access_client_secret,  # Cloudflare Access
            "Accept": "application/json, text/plain;q=0.9, */*;q=0.8",
        }

    @staticmethod
    def _to_iso_date_string(value: DateLike) -> str:
        if isinstance(value, str):
            return value
        if isinstance(value, datetime):
            return value.date().isoformat()
        if isinstance(value, date):
            return value.isoformat()
        raise TypeError("start_date/end_date must be str, date, or datetime")

    @staticmethod
    def _to_dataframe(payload: Dict[str, Any]) -> pd.DataFrame:
        columns_meta = payload.get("columns") or []
        rows = payload.get("dataset") or []

        column_names = [col.get("name") for col in columns_meta]
        if not column_names and isinstance(rows, list) and rows and isinstance(rows[0], dict):
            # Fallback if server returns list of dicts
            return pd.DataFrame(rows)
        return pd.DataFrame(rows, columns=column_names)


