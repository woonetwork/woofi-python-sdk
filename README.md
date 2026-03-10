# woofi

Python SDK for querying public WOOFi protocol data.

The SDK is extracted from the `woofi-cli` monorepo and exposes a typed
`WOOFiClient` for the public WOOFi endpoints:

- `/stat`
- `/source_stat`
- `/yield`
- `/stakingv2`

## Install

~~~bash
pip install woofi
~~~

## Quick Start

~~~python
from woofi import WOOFiClient

with WOOFiClient(timeout=30) as client:
    stats = client.get_stats(period="1d", network="arbitrum")
    summary = client.get_stat_summary(period="1d", network="arbitrum")
    vaults = client.list_vaults(network="arbitrum", symbol="USDC")
    staking = client.get_staking_info()
~~~

## API Style

The SDK exposes two layers:

- Raw methods such as `get_stats()`, `get_yield()`, and `get_staking()`
  return typed upstream-shaped Pydantic models.
- Helper methods such as `get_stat_summary()`, `list_vaults()`, and
  `get_staking_info()` return normalized Python dictionaries derived from the
  same public API responses.

## Exceptions

The package raises Python exceptions instead of CLI envelopes:

- `WOOFiHTTPError`
- `WOOFiTimeoutError`
- `WOOFiPayloadError`
- `WOOFiValidationError`

## Repository

Source, issues, and release workflow live in the monorepo:

- https://github.com/woonetwork/woofi-cli
