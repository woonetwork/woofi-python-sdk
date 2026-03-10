from decimal import Decimal


def from_wei(value: str | int, decimals: int = 18) -> str:
    """Convert a wei-denominated integer string to a decimal string.

    Returns a string to preserve precision in JSON output.
    Always includes exactly `decimals` digits after the decimal point.
    """
    scale = Decimal(10) ** decimals
    result = Decimal(str(value)) / scale
    quantizer = Decimal(10) ** (-decimals)
    return format(result.quantize(quantizer), "f")
