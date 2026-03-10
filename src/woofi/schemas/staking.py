from __future__ import annotations

from pydantic import BaseModel


class StakingRaw(BaseModel):
    avg_apr: float
    base_apr: float
    mp_boosted_apr: float
    total_woo_staked: str
    woo_decimals: int


class StakingResponseRaw(BaseModel):
    status: str
    data: StakingRaw


class StakingNormalized(BaseModel):
    avg_apr: float
    base_apr: float
    mp_boosted_apr: float
    total_woo_staked: str
    woo_decimals: int
    total_woo_staked_decimal: str
