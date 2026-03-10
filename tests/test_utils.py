from woofi.utils.decimals import from_wei
from woofi.utils.time import unix_to_iso_utc


class TestFromWei:
    def test_basic_conversion(self):
        assert from_wei("1000000000000000000") == "1.000000000000000000"

    def test_large_value(self):
        result = from_wei("123456789000000000000000000")
        assert result == "123456789.000000000000000000"

    def test_fractional(self):
        result = from_wei("500000000000000000")
        assert result == "0.500000000000000000"

    def test_zero(self):
        assert from_wei("0") == "0.000000000000000000"

    def test_custom_decimals(self):
        result = from_wei("1000000", 6)
        assert result == "1.000000"

    def test_small_custom_decimals(self):
        result = from_wei("12345678", 8)
        assert result == "0.12345678"


class TestUnixToIsoUtc:
    def test_epoch_zero(self):
        assert unix_to_iso_utc(0) == "1970-01-01T00:00:00+00:00"

    def test_known_timestamp(self):
        result = unix_to_iso_utc("1709942400")
        assert result.startswith("2024-03-09")

    def test_string_input(self):
        result = unix_to_iso_utc("1000000000")
        assert "2001" in result
