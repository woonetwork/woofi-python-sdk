API_BASE_URL = "https://api.woofi.com"
DEFAULT_TIMEOUT = 30

NETWORKS = [
    "bsc", "avax", "polygon", "arbitrum", "optimism", "linea",
    "base", "mantle", "sonic", "berachain", "hyperevm", "monad", "solana",
]

NETWORKS_SOURCE_STAT = [n for n in NETWORKS if n != "solana"]

YIELD_NETWORKS = [
    "bsc", "avax", "polygon", "arbitrum", "optimism", "linea",
    "base", "mantle", "sonic", "berachain",
]

PERIODS = ["1d", "1w", "1m", "3m", "1y", "all"]
