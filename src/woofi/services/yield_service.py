from __future__ import annotations

from decimal import Decimal

from woofi.schemas.yield_schema import YieldResponseRaw, YieldVaultNormalized
from woofi.utils.decimals import from_wei


def normalize_vaults(
    raw: YieldResponseRaw,
    symbol: str | None = None,
    source: str | None = None,
    sort_by: str = "apy",
    order: str = "desc",
    limit: int | None = None,
) -> list[dict[str, object]]:
    result = []
    for address, vault in raw.data.auto_compounding.items():
        if symbol and vault.symbol.lower() != symbol.lower():
            continue
        if source and vault.source.lower() != source.lower():
            continue

        tvl_token = from_wei(vault.tvl, vault.decimals)
        tvl_usd = format(Decimal(tvl_token) * Decimal(str(vault.price)), "f")

        normalized = YieldVaultNormalized(
            address=address,
            symbol=vault.symbol,
            source=vault.source,
            apy=vault.apy,
            tvl=vault.tvl,
            price=vault.price,
            share_price=vault.share_price,
            decimals=vault.decimals,
            loan_assets_percentage=vault.loan_assets_percentage,
            loan_interest_apr=vault.loan_interest_apr,
            reserve_vault_assets_percentage=vault.reserve_vault_assets_percentage,
            reserve_vault_apr=vault.reserve_vault_apr,
            weighted_average_apr=vault.weighted_average_apr,
            x_woo_rewards_apr=vault.x_woo_rewards_apr,
            woo_rewards_apr=vault.woo_rewards_apr,
            reward_apr=vault.reward_apr,
            tvl_token_decimal=tvl_token,
            tvl_usd_decimal=tvl_usd,
        )
        result.append(normalized.model_dump())

    sort_key = sort_by
    if sort_key == "tvl_usd":
        sort_key = "tvl_usd_decimal"

    reverse = order == "desc"
    result.sort(key=lambda x: _sort_value(x, sort_key), reverse=reverse)

    if limit is not None:
        result = result[:limit]

    return result


def lookup_vault(
    raw: YieldResponseRaw, address: str
) -> dict[str, object] | None:
    normalized_address = address.lower()
    matched_entry = next(
        (
            (vault_address, vault)
            for vault_address, vault in raw.data.auto_compounding.items()
            if vault_address.lower() == normalized_address
        ),
        None,
    )
    if matched_entry is None:
        return None
    actual_address, vault = matched_entry

    tvl_token = from_wei(vault.tvl, vault.decimals)
    tvl_usd = format(Decimal(tvl_token) * Decimal(str(vault.price)), "f")

    normalized = YieldVaultNormalized(
        address=actual_address,
        symbol=vault.symbol,
        source=vault.source,
        apy=vault.apy,
        tvl=vault.tvl,
        price=vault.price,
        share_price=vault.share_price,
        decimals=vault.decimals,
        loan_assets_percentage=vault.loan_assets_percentage,
        loan_interest_apr=vault.loan_interest_apr,
        reserve_vault_assets_percentage=vault.reserve_vault_assets_percentage,
        reserve_vault_apr=vault.reserve_vault_apr,
        weighted_average_apr=vault.weighted_average_apr,
        x_woo_rewards_apr=vault.x_woo_rewards_apr,
        woo_rewards_apr=vault.woo_rewards_apr,
        reward_apr=vault.reward_apr,
        tvl_token_decimal=tvl_token,
        tvl_usd_decimal=tvl_usd,
    )
    return normalized.model_dump()


def compute_yield_summary(raw: YieldResponseRaw) -> dict[str, object]:
    vaults = normalize_vaults(raw, sort_by="tvl_usd", order="desc")
    total_deposit_usd = from_wei(raw.data.total_deposit)
    top_vault = vaults[0] if vaults else None

    return {
        "total_deposit_raw": raw.data.total_deposit,
        "total_deposit_usd": total_deposit_usd,
        "vault_count": len(vaults),
        "top_vault_by_tvl": {
            "symbol": top_vault["symbol"],
            "tvl_usd_decimal": top_vault["tvl_usd_decimal"],
        } if top_vault else None,
    }


def _sort_value(item: dict[str, object], key: str) -> Decimal | str:
    val = item.get(key, 0)
    try:
        return Decimal(str(val))
    except Exception:
        return str(val)
