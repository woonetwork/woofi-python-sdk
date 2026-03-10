from __future__ import annotations

from pydantic import BaseModel


class SourceStatRaw(BaseModel):
    id: str
    name: str
    volume_usd: str
    txns: int
    percentage: float


class SourceStatResponseRaw(BaseModel):
    status: str
    data: list[SourceStatRaw]


class SourceStatNormalized(SourceStatRaw):
    volume_usd_decimal: str
