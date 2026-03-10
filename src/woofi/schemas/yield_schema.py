from __future__ import annotations

from pydantic import BaseModel


class YieldVaultRaw(BaseModel, extra="allow"):
    symbol: str
    source: str
    apy: float
    tvl: str
    price: float
    share_price: str = ""
    decimals: int
    loan_assets_percentage: float = 0
    loan_interest_apr: float = 0
    reserve_vault_assets_percentage: float = 0
    reserve_vault_apr: float = 0
    weighted_average_apr: float = 0
    x_woo_rewards_apr: float = 0
    woo_rewards_apr: float = 0
    reward_apr: float = 0


class YieldDataRaw(BaseModel):
    auto_compounding: dict[str, YieldVaultRaw]
    total_deposit: str


class YieldResponseRaw(BaseModel):
    status: str
    data: YieldDataRaw


class YieldVaultNormalized(BaseModel, extra="allow"):
    address: str
    symbol: str
    source: str
    apy: float
    tvl: str
    price: float
    share_price: str
    decimals: int
    loan_assets_percentage: float
    loan_interest_apr: float
    reserve_vault_assets_percentage: float
    reserve_vault_apr: float
    weighted_average_apr: float
    x_woo_rewards_apr: float
    woo_rewards_apr: float
    reward_apr: float
    tvl_token_decimal: str
    tvl_usd_decimal: str
