from __future__ import annotations

from json import JSONDecodeError
from typing import Any, Callable, TypeVar

import httpx
from pydantic import ValidationError

from woofi.api.source_stats_api import fetch_source_stat
from woofi.api.staking_api import fetch_staking
from woofi.api.stats_api import fetch_stat
from woofi.api.yield_api import fetch_yield
from woofi.constants import API_BASE_URL, DEFAULT_TIMEOUT
from woofi.exceptions import (
    WOOFiHTTPError,
    WOOFiPayloadError,
    WOOFiTimeoutError,
    WOOFiValidationError,
)
from woofi.schemas.source_stats import SourceStatResponseRaw
from woofi.schemas.staking import StakingResponseRaw
from woofi.schemas.stats import StatResponseRaw
from woofi.schemas.yield_schema import YieldResponseRaw
from woofi.services.staking_service import normalize_staking
from woofi.services.stats_service import (
    compute_stat_summary,
    compute_top_source,
    normalize_source_stats,
    normalize_stat_buckets,
)
from woofi.services.yield_service import compute_yield_summary, lookup_vault, normalize_vaults

T = TypeVar("T")


### WOOFi Python SDK
class WOOFiClient:
    """Synchronous client for the WOOFi API.

    Usage::

        with WOOFiClient() as client:
            stats = client.get_stats(period="1d", network="arbitrum")
    """

    def __init__(
        self,
        timeout: int = DEFAULT_TIMEOUT,
        base_url: str = API_BASE_URL,
    ) -> None:
        self._timeout = timeout
        self._base_url = base_url
        self._http: httpx.Client | None = None

    def _get_http(self) -> httpx.Client:
        if self._http is None:
            self._http = httpx.Client(
                base_url=self._base_url,
                timeout=self._timeout,
                headers={"Accept": "application/json"},
            )
        return self._http

    def close(self) -> None:
        if self._http is not None:
            self._http.close()
            self._http = None

    def __enter__(self) -> WOOFiClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Raw methods (bottom-layer)
    # ------------------------------------------------------------------

    def get_stats(self, period: str, network: str) -> StatResponseRaw:
        return self._call(fetch_stat, self._get_http(), period, network)

    def get_source_stats(self, period: str, network: str) -> SourceStatResponseRaw:
        return self._call(fetch_source_stat, self._get_http(), period, network)

    def get_yield(self, network: str) -> YieldResponseRaw:
        return self._call(fetch_yield, self._get_http(), network)

    def get_staking(self) -> StakingResponseRaw:
        return self._call(fetch_staking, self._get_http())

    # ------------------------------------------------------------------
    # High-level helpers
    # ------------------------------------------------------------------

    def get_stat_series(
        self,
        period: str,
        network: str,
        from_ts: int | None = None,
        to_ts: int | None = None,
    ) -> list[dict[str, str]]:
        raw = self.get_stats(period, network)
        return normalize_stat_buckets(raw, from_ts, to_ts)

    def get_stat_summary(
        self,
        period: str,
        network: str,
        from_ts: int | None = None,
        to_ts: int | None = None,
    ) -> dict[str, object]:
        raw = self.get_stats(period, network)
        return compute_stat_summary(raw, from_ts, to_ts)

    def list_sources(
        self,
        period: str,
        network: str,
        sort_by: str = "volume_usd",
        order: str = "desc",
        limit: int | None = None,
        include_other: bool = True,
    ) -> list[dict[str, object]]:
        raw = self.get_source_stats(period, network)
        return normalize_source_stats(raw, sort_by, order, limit, include_other)

    def get_top_source(
        self,
        period: str,
        network: str,
        exclude_other: bool = True,
    ) -> dict[str, object]:
        raw = self.get_source_stats(period, network)
        return compute_top_source(raw, exclude_other)

    def list_vaults(
        self,
        network: str,
        symbol: str | None = None,
        source: str | None = None,
        sort_by: str = "apy",
        order: str = "desc",
        limit: int | None = None,
    ) -> list[dict[str, object]]:
        raw = self.get_yield(network)
        return normalize_vaults(raw, symbol, source, sort_by, order, limit)

    def get_vault(
        self,
        network: str,
        address: str,
    ) -> dict[str, object] | None:
        raw = self.get_yield(network)
        return lookup_vault(raw, address)

    def get_yield_summary(self, network: str) -> dict[str, object]:
        raw = self.get_yield(network)
        return compute_yield_summary(raw)

    def get_staking_info(self) -> dict[str, object]:
        raw = self.get_staking()
        return normalize_staking(raw)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _call(fn: Callable[..., T], *args: Any) -> T:
        try:
            return fn(*args)
        except httpx.HTTPStatusError as e:
            raise WOOFiHTTPError(
                status_code=e.response.status_code,
                response_body=e.response.text,
            ) from e
        except httpx.TimeoutException as e:
            raise WOOFiTimeoutError(str(e)) from e
        except JSONDecodeError as e:
            raise WOOFiPayloadError(str(e)) from e
        except ValidationError as e:
            raise WOOFiValidationError(str(e)) from e
