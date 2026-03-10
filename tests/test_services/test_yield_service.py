from woofi.schemas.yield_schema import YieldDataRaw, YieldResponseRaw, YieldVaultRaw
from woofi.services.yield_service import (
    compute_yield_summary,
    lookup_vault,
    normalize_vaults,
)


def _make_yield_response():
    vault_a = YieldVaultRaw(
        symbol="USDC",
        source="lending",
        apy=5.5,
        tvl="1000000000000",
        price=1.0,
        share_price="1.0",
        decimals=6,
        loan_assets_percentage=80.0,
        loan_interest_apr=4.0,
        reserve_vault_assets_percentage=20.0,
        reserve_vault_apr=1.0,
        weighted_average_apr=3.5,
        x_woo_rewards_apr=0.5,
        woo_rewards_apr=0.3,
        reward_apr=0.8,
    )
    vault_b = YieldVaultRaw(
        symbol="ETH",
        source="vault",
        apy=8.2,
        tvl="500000000000000000000",
        price=3000.0,
        share_price="1.0",
        decimals=18,
        loan_assets_percentage=60.0,
        loan_interest_apr=6.0,
        reserve_vault_assets_percentage=40.0,
        reserve_vault_apr=2.0,
        weighted_average_apr=4.5,
        x_woo_rewards_apr=1.0,
        woo_rewards_apr=0.5,
        reward_apr=1.5,
    )
    return YieldResponseRaw(
        status="1",
        data=YieldDataRaw(
            auto_compounding={
                "0xabc": vault_a,
                "0xdef": vault_b,
            },
            total_deposit="2000000000000000000000",
        ),
    )


class TestNormalizeVaults:
    def test_returns_all_vaults(self):
        raw = _make_yield_response()
        result = normalize_vaults(raw)
        assert len(result) == 2

    def test_includes_normalized_fields(self):
        raw = _make_yield_response()
        result = normalize_vaults(raw)
        for v in result:
            assert "address" in v
            assert "tvl_token_decimal" in v
            assert "tvl_usd_decimal" in v

    def test_tvl_usd_calculation(self):
        raw = _make_yield_response()
        result = normalize_vaults(raw)
        usdc_vault = next(v for v in result if v["symbol"] == "USDC")
        assert usdc_vault["tvl_usd_decimal"].startswith("1000000")

    def test_filter_by_symbol(self):
        raw = _make_yield_response()
        result = normalize_vaults(raw, symbol="ETH")
        assert len(result) == 1
        assert result[0]["symbol"] == "ETH"

    def test_sort_by_apy_desc(self):
        raw = _make_yield_response()
        result = normalize_vaults(raw, sort_by="apy", order="desc")
        assert result[0]["symbol"] == "ETH"

    def test_limit(self):
        raw = _make_yield_response()
        result = normalize_vaults(raw, limit=1)
        assert len(result) == 1


class TestLookupVault:
    def test_found(self):
        raw = _make_yield_response()
        result = lookup_vault(raw, "0xabc")
        assert result is not None
        assert result["symbol"] == "USDC"

    def test_found_case_insensitive(self):
        raw = YieldResponseRaw(
            status="1",
            data=YieldDataRaw(
                auto_compounding={"0xAbC": _make_yield_response().data.auto_compounding["0xabc"]},
                total_deposit="2000000000000000000000",
            ),
        )
        result = lookup_vault(raw, "0xabc")
        assert result is not None
        assert result["address"] == "0xAbC"

    def test_not_found(self):
        raw = _make_yield_response()
        result = lookup_vault(raw, "0xnonexistent")
        assert result is None


class TestComputeYieldSummary:
    def test_summary_fields(self):
        raw = _make_yield_response()
        result = compute_yield_summary(raw)
        assert "total_deposit_raw" in result
        assert "total_deposit_usd" in result
        assert result["vault_count"] == 2
        assert result["top_vault_by_tvl"] is not None
