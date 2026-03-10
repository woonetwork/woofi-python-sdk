from __future__ import annotations

import httpx

from woofi.schemas.source_stats import SourceStatResponseRaw


def fetch_source_stat(
    client: httpx.Client, period: str, network: str
) -> SourceStatResponseRaw:
    response = client.get("/source_stat", params={"period": period, "network": network})
    response.raise_for_status()
    return SourceStatResponseRaw.model_validate(response.json())
