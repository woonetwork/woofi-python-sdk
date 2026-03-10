"""Tests for WOOFiClient — the SDK's public facade."""
from __future__ import annotations

import httpx
import pytest
import respx

from woofi import WOOFiClient
from woofi.constants import API_BASE_URL
from woofi.exceptions import (
    WOOFiError,
    WOOFiHTTPError,
    WOOFiPayloadError,
    WOOFiTimeoutError,
    WOOFiValidationError,
)

# ---------------------------------------------------------------------------
# Fixtures / sample payloads
# ---------------------------------------------------------------------------

STAT_PAYLOAD = {
    "status": "1",
    "data": [
        {
            "id": "1",
            "timestamp": "1700000000",
            "volume_usd": "2000000000000000000",
            "traders": "10",
            "txs": "5",
            "txns": "5",
        },
        {
            "id": "2",
            "timestamp": "1700003600",
            "volume_usd": "3000000000000000000",
            "traders": "15",
            "txs": "8",
            "txns": "8",
        },
    ],
}

SOURCE_STAT_PAYLOAD = {
    "status": "1",
    "data": [
        {"id": "1", "name": "OpenOcean", "volume_usd": "5000000000000000000", "txns": 100, "percentage": 50.0},
        {"id": "2", "name": "KyberSwap", "volume_usd": "3000000000000000000", "txns": 60, "percentage": 30.0},
        {"id": "3", "name": "Other", "volume_usd": "2000000000000000000", "txns": 40, "percentage": 20.0},
    ],
}

YIELD_PAYLOAD = {
    "status": "1",
    "data": {
        "auto_compounding": {
            "0xabc": {
                "symbol": "USDC",
                "source": "lending",
                "apy": 5.5,
                "tvl": "1000000000000",
                "price": 1.0,
                "share_price": "1.0",
                "decimals": 6,
            },
            "0xdef": {
                "symbol": "ETH",
                "source": "vault",
                "apy": 8.2,
                "tvl": "500000000000000000000",
                "price": 3000.0,
                "share_price": "1.0",
                "decimals": 18,
            },
        },
        "total_deposit": "2000000000000000000000",
    },
}

STAKING_PAYLOAD = {
    "status": "1",
    "data": {
        "avg_apr": 12.5,
        "base_apr": 8.0,
        "mp_boosted_apr": 4.5,
        "total_woo_staked": "1000000000000000000000000",
        "woo_decimals": 18,
    },
}


# ---------------------------------------------------------------------------
# Context manager
# ---------------------------------------------------------------------------


class TestClientContextManager:
    def test_with_statement(self):
        with WOOFiClient() as client:
            assert client is not None

    def test_manual_close(self):
        client = WOOFiClient()
        client.close()

    def test_custom_timeout(self):
        with WOOFiClient(timeout=10) as client:
            assert client._timeout == 10

    def test_custom_base_url(self):
        with WOOFiClient(base_url="https://custom.api") as client:
            assert client._base_url == "https://custom.api"


# ---------------------------------------------------------------------------
# Raw methods (bottom-layer)
# ---------------------------------------------------------------------------


class TestGetStats:
    @respx.mock
    def test_returns_raw_model(self):
        respx.get(f"{API_BASE_URL}/stat").mock(
            return_value=httpx.Response(200, json=STAT_PAYLOAD)
        )
        with WOOFiClient() as client:
            result = client.get_stats(period="1d", network="arbitrum")
        assert result.status == "1"
        assert len(result.data) == 2
        assert result.data[0].volume_usd == "2000000000000000000"

    @respx.mock
    def test_http_error_raises(self):
        respx.get(f"{API_BASE_URL}/stat").mock(
            return_value=httpx.Response(500, text="Internal Server Error")
        )
        with pytest.raises(WOOFiHTTPError) as exc_info:
            with WOOFiClient() as client:
                client.get_stats(period="1d", network="arbitrum")
        assert exc_info.value.status_code == 500

    @respx.mock
    def test_timeout_raises(self):
        respx.get(f"{API_BASE_URL}/stat").mock(side_effect=httpx.ConnectTimeout("timeout"))
        with pytest.raises(WOOFiTimeoutError):
            with WOOFiClient() as client:
                client.get_stats(period="1d", network="arbitrum")

    @respx.mock
    def test_invalid_json_raises(self):
        respx.get(f"{API_BASE_URL}/stat").mock(
            return_value=httpx.Response(200, text="not json")
        )
        with pytest.raises(WOOFiPayloadError):
            with WOOFiClient() as client:
                client.get_stats(period="1d", network="arbitrum")

    @respx.mock
    def test_validation_error_raises(self):
        respx.get(f"{API_BASE_URL}/stat").mock(
            return_value=httpx.Response(200, json={"status": "1", "data": "invalid"})
        )
        with pytest.raises(WOOFiValidationError):
            with WOOFiClient() as client:
                client.get_stats(period="1d", network="arbitrum")


class TestGetSourceStats:
    @respx.mock
    def test_returns_raw_model(self):
        respx.get(f"{API_BASE_URL}/source_stat").mock(
            return_value=httpx.Response(200, json=SOURCE_STAT_PAYLOAD)
        )
        with WOOFiClient() as client:
            result = client.get_source_stats(period="1w", network="bsc")
        assert result.status == "1"
        assert len(result.data) == 3


class TestGetYield:
    @respx.mock
    def test_returns_raw_model(self):
        respx.get(f"{API_BASE_URL}/yield").mock(
            return_value=httpx.Response(200, json=YIELD_PAYLOAD)
        )
        with WOOFiClient() as client:
            result = client.get_yield(network="arbitrum")
        assert result.status == "1"
        assert "0xabc" in result.data.auto_compounding


class TestGetStaking:
    @respx.mock
    def test_returns_raw_model(self):
        respx.get(f"{API_BASE_URL}/stakingv2").mock(
            return_value=httpx.Response(200, json=STAKING_PAYLOAD)
        )
        with WOOFiClient() as client:
            result = client.get_staking()
        assert result.status == "1"
        assert result.data.avg_apr == 12.5


# ---------------------------------------------------------------------------
# High-level helpers
# ---------------------------------------------------------------------------


class TestGetStatSeries:
    @respx.mock
    def test_returns_normalized_buckets(self):
        respx.get(f"{API_BASE_URL}/stat").mock(
            return_value=httpx.Response(200, json=STAT_PAYLOAD)
        )
        with WOOFiClient() as client:
            result = client.get_stat_series(period="1d", network="arbitrum")
        assert len(result) == 2
        assert "timestamp_iso_utc" in result[0]
        assert "volume_usd_decimal" in result[0]

    @respx.mock
    def test_filter_from_ts(self):
        respx.get(f"{API_BASE_URL}/stat").mock(
            return_value=httpx.Response(200, json=STAT_PAYLOAD)
        )
        with WOOFiClient() as client:
            result = client.get_stat_series(period="1d", network="arbitrum", from_ts=1700003600)
        assert len(result) == 1
        assert result[0]["id"] == "2"

    @respx.mock
    def test_filter_to_ts(self):
        respx.get(f"{API_BASE_URL}/stat").mock(
            return_value=httpx.Response(200, json=STAT_PAYLOAD)
        )
        with WOOFiClient() as client:
            result = client.get_stat_series(period="1d", network="arbitrum", to_ts=1700000000)
        assert len(result) == 1
        assert result[0]["id"] == "1"


class TestGetStatSummary:
    @respx.mock
    def test_returns_summary(self):
        respx.get(f"{API_BASE_URL}/stat").mock(
            return_value=httpx.Response(200, json=STAT_PAYLOAD)
        )
        with WOOFiClient() as client:
            result = client.get_stat_summary(period="1d", network="arbitrum")
        assert result["total_volume_usd"] == "5.000000000000000000"
        assert result["total_txs"] == 13
        assert result["bucket_count"] == 2


class TestListSources:
    @respx.mock
    def test_returns_sorted_list(self):
        respx.get(f"{API_BASE_URL}/source_stat").mock(
            return_value=httpx.Response(200, json=SOURCE_STAT_PAYLOAD)
        )
        with WOOFiClient() as client:
            result = client.list_sources(period="1w", network="bsc")
        assert len(result) == 3
        assert result[0]["name"] == "OpenOcean"

    @respx.mock
    def test_with_limit(self):
        respx.get(f"{API_BASE_URL}/source_stat").mock(
            return_value=httpx.Response(200, json=SOURCE_STAT_PAYLOAD)
        )
        with WOOFiClient() as client:
            result = client.list_sources(period="1w", network="bsc", limit=1)
        assert len(result) == 1


class TestGetTopSource:
    @respx.mock
    def test_returns_top(self):
        respx.get(f"{API_BASE_URL}/source_stat").mock(
            return_value=httpx.Response(200, json=SOURCE_STAT_PAYLOAD)
        )
        with WOOFiClient() as client:
            result = client.get_top_source(period="1d", network="arbitrum")
        assert result["source"]["name"] == "OpenOcean"
        assert result["rank"] == 1


class TestListVaults:
    @respx.mock
    def test_returns_all_vaults(self):
        respx.get(f"{API_BASE_URL}/yield").mock(
            return_value=httpx.Response(200, json=YIELD_PAYLOAD)
        )
        with WOOFiClient() as client:
            result = client.list_vaults(network="arbitrum")
        assert len(result) == 2

    @respx.mock
    def test_filter_by_symbol(self):
        respx.get(f"{API_BASE_URL}/yield").mock(
            return_value=httpx.Response(200, json=YIELD_PAYLOAD)
        )
        with WOOFiClient() as client:
            result = client.list_vaults(network="arbitrum", symbol="USDC")
        assert len(result) == 1
        assert result[0]["symbol"] == "USDC"


class TestGetVault:
    @respx.mock
    def test_found(self):
        respx.get(f"{API_BASE_URL}/yield").mock(
            return_value=httpx.Response(200, json=YIELD_PAYLOAD)
        )
        with WOOFiClient() as client:
            result = client.get_vault(network="arbitrum", address="0xabc")
        assert result is not None
        assert result["symbol"] == "USDC"

    @respx.mock
    def test_not_found(self):
        respx.get(f"{API_BASE_URL}/yield").mock(
            return_value=httpx.Response(200, json=YIELD_PAYLOAD)
        )
        with WOOFiClient() as client:
            result = client.get_vault(network="arbitrum", address="0xnonexistent")
        assert result is None


class TestGetYieldSummary:
    @respx.mock
    def test_returns_summary(self):
        respx.get(f"{API_BASE_URL}/yield").mock(
            return_value=httpx.Response(200, json=YIELD_PAYLOAD)
        )
        with WOOFiClient() as client:
            result = client.get_yield_summary(network="arbitrum")
        assert "total_deposit_usd" in result
        assert result["vault_count"] == 2


class TestGetStakingInfo:
    @respx.mock
    def test_returns_info(self):
        respx.get(f"{API_BASE_URL}/stakingv2").mock(
            return_value=httpx.Response(200, json=STAKING_PAYLOAD)
        )
        with WOOFiClient() as client:
            result = client.get_staking_info()
        assert result["avg_apr"] == 12.5
        assert result["total_woo_staked_decimal"] == "1000000.000000000000000000"


# ---------------------------------------------------------------------------
# Exception hierarchy
# ---------------------------------------------------------------------------


class TestExceptionHierarchy:
    def test_all_inherit_from_woofi_error(self):
        assert issubclass(WOOFiHTTPError, WOOFiError)
        assert issubclass(WOOFiTimeoutError, WOOFiError)
        assert issubclass(WOOFiPayloadError, WOOFiError)
        assert issubclass(WOOFiValidationError, WOOFiError)

    def test_http_error_has_status_code(self):
        err = WOOFiHTTPError(status_code=404, response_body="Not Found")
        assert err.status_code == 404
        assert err.response_body == "Not Found"
        assert "404" in str(err)

    def test_catch_base_exception(self):
        with pytest.raises(WOOFiError):
            raise WOOFiHTTPError(status_code=500, response_body="error")
