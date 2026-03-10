from __future__ import annotations

from decimal import Decimal

from woofi.schemas.stats import StatBucketNormalized, StatResponseRaw
from woofi.schemas.source_stats import SourceStatNormalized, SourceStatResponseRaw
from woofi.utils.decimals import from_wei
from woofi.utils.time import unix_to_iso_utc


def normalize_stat_buckets(
    raw: StatResponseRaw,
    from_ts: int | None = None,
    to_ts: int | None = None,
) -> list[dict[str, str]]:
    buckets = raw.data
    if from_ts is not None:
        buckets = [b for b in buckets if int(b.timestamp) >= from_ts]
    if to_ts is not None:
        buckets = [b for b in buckets if int(b.timestamp) <= to_ts]

    result = []
    for b in buckets:
        normalized = StatBucketNormalized(
            id=b.id,
            timestamp=b.timestamp,
            volume_usd=b.volume_usd,
            traders=b.traders,
            txs=b.txs,
            txns=b.txns,
            timestamp_iso_utc=unix_to_iso_utc(b.timestamp),
            volume_usd_decimal=from_wei(b.volume_usd),
        )
        result.append(normalized.model_dump())
    return result


def compute_stat_summary(
    raw: StatResponseRaw,
    from_ts: int | None = None,
    to_ts: int | None = None,
) -> dict[str, object]:
    buckets = raw.data
    if from_ts is not None:
        buckets = [b for b in buckets if int(b.timestamp) >= from_ts]
    if to_ts is not None:
        buckets = [b for b in buckets if int(b.timestamp) <= to_ts]

    total_volume_wei = sum(Decimal(b.volume_usd) for b in buckets)
    total_txs = sum(int(b.txs) for b in buckets)
    total_volume_usd = from_wei(str(total_volume_wei))

    timestamps = [int(b.timestamp) for b in buckets]
    time_range = {
        "from": unix_to_iso_utc(min(timestamps)) if timestamps else None,
        "to": unix_to_iso_utc(max(timestamps)) if timestamps else None,
    }

    return {
        "total_volume_usd": total_volume_usd,
        "total_txs": total_txs,
        "bucket_count": len(buckets),
        "time_range": time_range,
    }


def normalize_source_stats(
    raw: SourceStatResponseRaw,
    sort_by: str = "volume_usd",
    order: str = "desc",
    limit: int | None = None,
    include_other: bool = True,
) -> list[dict[str, object]]:
    items = raw.data
    if not include_other:
        items = [s for s in items if s.name != "Other"]

    result = []
    for s in items:
        normalized = SourceStatNormalized(
            id=s.id,
            name=s.name,
            volume_usd=s.volume_usd,
            txns=s.txns,
            percentage=s.percentage,
            volume_usd_decimal=from_wei(s.volume_usd),
        )
        result.append(normalized.model_dump())

    reverse = order == "desc"
    result.sort(key=lambda x: _sort_value(x, sort_by), reverse=reverse)

    if limit is not None:
        result = result[:limit]

    return result


def compute_top_source(
    raw: SourceStatResponseRaw,
    exclude_other: bool = True,
) -> dict[str, object]:
    items = raw.data
    if exclude_other:
        items = [s for s in items if s.name != "Other"]

    if not items:
        return {"source": None, "rank": 0}

    top = max(items, key=lambda s: Decimal(s.volume_usd))
    return {
        "source": SourceStatNormalized(
            id=top.id,
            name=top.name,
            volume_usd=top.volume_usd,
            txns=top.txns,
            percentage=top.percentage,
            volume_usd_decimal=from_wei(top.volume_usd),
        ).model_dump(),
        "rank": 1,
    }


def _sort_value(item: dict[str, object], key: str) -> Decimal | str:
    val = item.get(key, 0)
    try:
        return Decimal(str(val))
    except Exception:
        return str(val)
