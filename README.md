# WOOFi Python SDK

[![PyPI version](https://img.shields.io/pypi/v/woofi.svg)](https://pypi.org/project/woofi/)
[![Python versions](https://img.shields.io/pypi/pyversions/woofi.svg)](https://pypi.org/project/woofi/)
[![License](https://img.shields.io/github/license/woonetwork/woofi-python-sdk.svg)](LICENSE)

A lightweight, synchronous Python SDK for querying public WOOFi protocol data. This SDK provides a typed interface to WOOFi's public APIs, offering both raw Pydantic models and normalized Python dictionaries for ease of use.

## Features

- **Fully Typed**: Built with Pydantic v2 for robust data validation and IDE autocompletion.
- **Dual-Layer API**:
  - **Raw Layer**: Returns models matching the upstream API structure exactly.
  - **Helper Layer**: Returns normalized, human-readable data (e.g., converted decimals, ISO timestamps).
- **Clean Exception Hierarchy**: Specific exceptions for HTTP errors, timeouts, and validation failures.
- **Production Ready**: Used internally by the WOOFi CLI.

## Installation

```bash
pip install woofi
```

For development:

```bash
git clone https://github.com/woonetwork/woofi-python-sdk.git
cd woofi-python-sdk
pip install -e ".[dev]"
```

## Quick Start

```python
from woofi import WOOFiClient

# Use as a context manager for automatic cleanup
with WOOFiClient() as client:
    # Get high-level summary for Arbitrum
    summary = client.get_stat_summary(period="1d", network="arbitrum")
    print(f"Total Volume: ${summary['total_volume_usd']}")
    
    # List vaults with the highest APY
    vaults = client.list_vaults(network="arbitrum", sort_by="apy", limit=5)
    for v in vaults:
        print(f"Vault: {v['symbol']} | APY: {v['apy']}% | TVL: ${v['tvl_usd_decimal']}")
```

## SDK Integration Examples

### 1. Analyzing Protocol Statistics

You can retrieve a time-series of protocol stats or a simplified summary.

```python
with WOOFiClient() as client:
    # Get a list of data points (buckets)
    series = client.get_stat_series(period="1w", network="bsc")
    
    for bucket in series[:3]:
        print(f"Time: {bucket['timestamp_iso_utc']} | Volume: ${bucket['volume_usd_decimal']}")

    # Get the top volume source
    top = client.get_top_source(period="1d", network="polygon")
    print(f"Top Source: {top['source']['name']} with {top['rank']} rank")
```

### 2. Exploring Yield Opportunities

The SDK allows filtering and sorting vaults across different networks.

```python
with WOOFiClient() as client:
    # List all USDC vaults across Arbitrum, sorted by APY
    usdc_vaults = client.list_vaults(
        network="arbitrum", 
        symbol="USDC", 
        sort_by="apy", 
        order="desc"
    )
    
    # Get a summary of all yields on a specific network
    yield_info = client.get_yield_summary(network="avax")
    print(f"Total Deposit: ${yield_info['total_deposit_usd']}")
    print(f"Active Vaults: {yield_info['vault_count']}")
```

### 3. Staking Information

Retrieve global WOO staking statistics.

```python
with WOOFiClient() as client:
    staking = client.get_staking_info()
    print(f"Average APR: {staking['avg_apr']}%")
    print(f"Total WOO Staked: {staking['total_woo_staked_decimal']}")
```

### 4. Error Handling

The SDK provides clear exceptions for different failure modes.

```python
from woofi import WOOFiClient, WOOFiHTTPError, WOOFiTimeoutError

try:
    with WOOFiClient(timeout=5) as client:
        stats = client.get_stats(period="invalid", network="arbitrum")
except WOOFiHTTPError as e:
    print(f"API Error: {e.status_code} - {e.response_body}")
except WOOFiTimeoutError:
    print("The request timed out.")
```

## API Reference

### `WOOFiClient` Methods

#### Raw Methods (return Pydantic models)
- `get_stats(period, network)`: Returns `StatResponseRaw`
- `get_source_stats(period, network)`: Returns `SourceStatResponseRaw`
- `get_yield(network)`: Returns `YieldResponseRaw`
- `get_staking()`: Returns `StakingResponseRaw`

#### Helper Methods (return normalized dicts)
- `get_stat_series(period, network, from_ts, to_ts)`
- `get_stat_summary(period, network, from_ts, to_ts)`
- `list_sources(period, network, sort_by, order, limit)`
- `get_top_source(period, network)`
- `list_vaults(network, symbol, source, sort_by, order, limit)`
- `get_vault(network, address)`
- `get_yield_summary(network)`
- `get_staking_info()`

## Constants

The SDK exports several useful constants:
- `NETWORKS`: List of all supported networks.
- `PERIODS`: Supported time periods (`1d`, `1w`, `1m`, etc.).
- `API_BASE_URL`: Default WOOFi API endpoint.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Links

- **Repository**: [https://github.com/woonetwork/woofi-python-sdk](https://github.com/woonetwork/woofi-python-sdk)
- **Issues**: [https://github.com/woonetwork/woofi-python-sdk/issues](https://github.com/woonetwork/woofi-python-sdk/issues)
- **WOOFi Official**: [https://woo.org/](https://woo.org/)
