"""Fetch live crypto prices from CoinGecko (free API, no key needed)."""

import time
import requests

COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"
COIN_IDS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "BNB": "binancecoin",
    "XRP": "ripple",
}

# Cache: {symbol: price}, refreshed every 5s
_cache = {}
_cache_time = 0
CACHE_TTL = 5  # seconds

# Fallback prices if API fails
FALLBACK = {
    "BTC": 97000.00,
    "ETH": 2700.00,
    "SOL": 175.00,
    "BNB": 650.00,
    "XRP": 2.50,
}


def fetch_prices() -> dict[str, float]:
    """Return {symbol: usd_price} for all tracked coins. Uses cache."""
    global _cache, _cache_time

    if _cache and (time.time() - _cache_time) < CACHE_TTL:
        return dict(_cache)

    try:
        ids = ",".join(COIN_IDS.values())
        resp = requests.get(
            COINGECKO_URL,
            params={"ids": ids, "vs_currencies": "usd"},
            timeout=5,
        )
        resp.raise_for_status()
        data = resp.json()

        prices = {}
        for symbol, cg_id in COIN_IDS.items():
            if cg_id in data and "usd" in data[cg_id]:
                prices[symbol] = float(data[cg_id]["usd"])
            else:
                prices[symbol] = FALLBACK[symbol]

        _cache = prices
        _cache_time = time.time()
        return dict(prices)

    except Exception:
        if _cache:
            return dict(_cache)
        return dict(FALLBACK)
