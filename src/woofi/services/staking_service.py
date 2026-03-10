from __future__ import annotations

from woofi.schemas.staking import StakingNormalized, StakingResponseRaw
from woofi.utils.decimals import from_wei


def normalize_staking(raw: StakingResponseRaw) -> dict[str, object]:
    d = raw.data
    normalized = StakingNormalized(
        avg_apr=d.avg_apr,
        base_apr=d.base_apr,
        mp_boosted_apr=d.mp_boosted_apr,
        total_woo_staked=d.total_woo_staked,
        woo_decimals=d.woo_decimals,
        total_woo_staked_decimal=from_wei(d.total_woo_staked, d.woo_decimals),
    )
    return normalized.model_dump()
