from __future__ import annotations

import httpx

from woofi.schemas.yield_schema import YieldResponseRaw


def fetch_yield(client: httpx.Client, network: str) -> YieldResponseRaw:
    response = client.get("/yield", params={"network": network})
    response.raise_for_status()
    return YieldResponseRaw.model_validate(response.json())
