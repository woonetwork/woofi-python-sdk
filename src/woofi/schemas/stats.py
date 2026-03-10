from __future__ import annotations

from pydantic import BaseModel


class StatBucketRaw(BaseModel):
    id: str
    timestamp: str
    volume_usd: str
    traders: str
    txs: str
    txns: str


class StatResponseRaw(BaseModel):
    status: str
    data: list[StatBucketRaw]


class StatBucketNormalized(StatBucketRaw):
    timestamp_iso_utc: str
    volume_usd_decimal: str
