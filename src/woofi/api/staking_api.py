from __future__ import annotations

import httpx

from woofi.schemas.staking import StakingResponseRaw


def fetch_staking(client: httpx.Client) -> StakingResponseRaw:
    response = client.get("/stakingv2")
    response.raise_for_status()
    return StakingResponseRaw.model_validate(response.json())
