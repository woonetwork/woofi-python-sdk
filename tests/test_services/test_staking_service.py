from woofi.schemas.staking import StakingRaw, StakingResponseRaw
from woofi.services.staking_service import normalize_staking


def _make_staking_response():
    return StakingResponseRaw(
        status="1",
        data=StakingRaw(
            avg_apr=12.5,
            base_apr=8.0,
            mp_boosted_apr=4.5,
            total_woo_staked="1000000000000000000000000",
            woo_decimals=18,
        ),
    )


class TestNormalizeStaking:
    def test_basic_normalization(self):
        raw = _make_staking_response()
        result = normalize_staking(raw)
        assert result["avg_apr"] == 12.5
        assert result["base_apr"] == 8.0
        assert result["mp_boosted_apr"] == 4.5
        assert result["total_woo_staked_decimal"] == "1000000.000000000000000000"
        assert result["woo_decimals"] == 18
