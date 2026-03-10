from __future__ import annotations

import httpx

from woofi.schemas.stats import StatResponseRaw


def fetch_stat(client: httpx.Client, period: str, network: str) -> StatResponseRaw:
    response = client.get("/stat", params={"period": period, "network": network})
    response.raise_for_status()
    return StatResponseRaw.model_validate(response.json())
