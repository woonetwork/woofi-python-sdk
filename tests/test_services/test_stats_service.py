from woofi.schemas.stats import StatBucketRaw, StatResponseRaw
from woofi.schemas.source_stats import SourceStatRaw, SourceStatResponseRaw
from woofi.services.stats_service import (
    compute_stat_summary,
    compute_top_source,
    normalize_source_stats,
    normalize_stat_buckets,
)


def _make_stat_response(buckets=None):
    if buckets is None:
        buckets = [
            StatBucketRaw(
                id="1", timestamp="1700000000",
                volume_usd="2000000000000000000", traders="10", txs="5", txns="5",
            ),
            StatBucketRaw(
                id="2", timestamp="1700003600",
                volume_usd="3000000000000000000", traders="15", txs="8", txns="8",
            ),
        ]
    return StatResponseRaw(status="1", data=buckets)


def _make_source_response():
    return SourceStatResponseRaw(
        status="1",
        data=[
            SourceStatRaw(id="1", name="OpenOcean", volume_usd="5000000000000000000", txns=100, percentage=50.0),
            SourceStatRaw(id="2", name="KyberSwap", volume_usd="3000000000000000000", txns=60, percentage=30.0),
            SourceStatRaw(id="3", name="Other", volume_usd="2000000000000000000", txns=40, percentage=20.0),
        ],
    )


class TestNormalizeStatBuckets:
    def test_returns_normalized_fields(self):
        raw = _make_stat_response()
        result = normalize_stat_buckets(raw)
        assert len(result) == 2
        assert "timestamp_iso_utc" in result[0]
        assert "volume_usd_decimal" in result[0]
        assert result[0]["volume_usd_decimal"] == "2.000000000000000000"

    def test_filter_from_ts(self):
        raw = _make_stat_response()
        result = normalize_stat_buckets(raw, from_ts=1700003600)
        assert len(result) == 1
        assert result[0]["id"] == "2"

    def test_filter_to_ts(self):
        raw = _make_stat_response()
        result = normalize_stat_buckets(raw, to_ts=1700000000)
        assert len(result) == 1
        assert result[0]["id"] == "1"


class TestComputeStatSummary:
    def test_sums_volume_and_txs(self):
        raw = _make_stat_response()
        result = compute_stat_summary(raw)
        assert result["total_volume_usd"] == "5.000000000000000000"
        assert result["total_txs"] == 13
        assert result["bucket_count"] == 2

    def test_time_range(self):
        raw = _make_stat_response()
        result = compute_stat_summary(raw)
        assert result["time_range"]["from"] is not None
        assert result["time_range"]["to"] is not None


class TestNormalizeSourceStats:
    def test_default_sort_desc(self):
        raw = _make_source_response()
        result = normalize_source_stats(raw)
        assert result[0]["name"] == "OpenOcean"
        assert result[1]["name"] == "KyberSwap"

    def test_exclude_other(self):
        raw = _make_source_response()
        result = normalize_source_stats(raw, include_other=False)
        names = [r["name"] for r in result]
        assert "Other" not in names

    def test_limit(self):
        raw = _make_source_response()
        result = normalize_source_stats(raw, limit=1)
        assert len(result) == 1

    def test_asc_order(self):
        raw = _make_source_response()
        result = normalize_source_stats(raw, order="asc")
        assert result[0]["name"] == "Other"


class TestComputeTopSource:
    def test_returns_top_by_volume(self):
        raw = _make_source_response()
        result = compute_top_source(raw)
        assert result["source"]["name"] == "OpenOcean"
        assert result["rank"] == 1

    def test_exclude_other(self):
        raw = _make_source_response()
        result = compute_top_source(raw, exclude_other=True)
        assert result["source"]["name"] != "Other"
