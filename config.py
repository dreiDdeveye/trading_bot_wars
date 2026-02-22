"""Game configuration: constants, asset templates, event pool, bot profiles."""

TOTAL_ROUNDS = 100
STARTING_CASH = 1_000.0
WIN_TARGET = 10_000.0
TICKS_PER_ROUND = 30          # sub-ticks per round (~4s each = ~120s per round)

# ─── ASSET TEMPLATES ─────────────────────────────────────────
ASSETS_TEMPLATE = [
    {"symbol": "BTC",  "name": "Bitcoin",    "price": 97000.00, "volatility": 0.5,  "trend": 0.15},
    {"symbol": "ETH",  "name": "Ethereum",   "price": 2700.00,  "volatility": 0.55, "trend": 0.1},
    {"symbol": "SOL",  "name": "Solana",     "price": 175.00,   "volatility": 0.7,  "trend": 0.2},
    {"symbol": "BNB",  "name": "BNB",        "price": 650.00,   "volatility": 0.4,  "trend": 0.05},
    {"symbol": "XRP",  "name": "XRP",        "price": 2.50,     "volatility": 0.65, "trend": 0.0},
]

# ─── MARKET EVENTS ───────────────────────────────────────────
EVENT_POOL = [
    {"name": "REGULATORY CRACKDOWN", "description": "SEC announces new crypto regulations.", "target_asset": "ALL", "price_impact": -0.04, "duration": 2},
    {"name": "BTC ETF INFLOWS", "description": "Record inflows into Bitcoin spot ETFs!", "target_asset": "BTC", "price_impact": 0.08, "duration": 2},
    {"name": "ETH UPGRADE", "description": "Ethereum completes major network upgrade!", "target_asset": "ETH", "price_impact": 0.07, "duration": 2},
    {"name": "SOL NFT BOOM", "description": "Solana NFT volume explodes overnight!", "target_asset": "SOL", "price_impact": 0.10, "duration": 1},
    {"name": "BNB BURN EVENT", "description": "Binance burns massive BNB supply!", "target_asset": "BNB", "price_impact": 0.06, "duration": 2},
    {"name": "XRP LAWSUIT WIN", "description": "Ripple scores major legal victory!", "target_asset": "XRP", "price_impact": 0.12, "duration": 1},
    {"name": "BULL STAMPEDE", "description": "Investors go full FOMO!", "target_asset": "ALL", "price_impact": 0.05, "duration": 1},
    {"name": "FLASH CRASH", "description": "Liquidation cascade triggers massive selloff!", "target_asset": "ALL", "price_impact": -0.08, "duration": 1},
    {"name": "WHALE ALERT", "description": "Whale moves 10,000 BTC to exchange!", "target_asset": "BTC", "price_impact": -0.06, "duration": 1},
    {"name": "ETH GAS SPIKE", "description": "Ethereum gas fees hit all-time highs!", "target_asset": "ETH", "price_impact": -0.05, "duration": 1},
    {"name": "SOL OUTAGE", "description": "Solana network experiences downtime!", "target_asset": "SOL", "price_impact": -0.10, "duration": 1},
    {"name": "FED RATE HIKE", "description": "Interest rates go up. Risk-off mode.", "target_asset": "ALL", "price_impact": -0.03, "duration": 3},
    {"name": "STIMULUS CHECK", "description": "Money printer goes brrrr!", "target_asset": "ALL", "price_impact": 0.04, "duration": 2},
    {"name": "SHORT SQUEEZE", "description": "Massive short liquidations across the market!", "target_asset": "ALL", "price_impact": 0.06, "duration": 1},
    {"name": "HACK SCARE", "description": "Major exchange reports security breach!", "target_asset": "ALL", "price_impact": -0.07, "duration": 1},
]

# ─── BOT PROFILES ────────────────────────────────────────────
BOT_PROFILES = {
    "aggressive": {
        "name": "HYPERCLAW AI",
        "icon": "\U0001f43a",
        "color": "#ff5555",
        "motto": "Strike hard. Strike fast. No mercy.",
        "risk_tolerance": 0.8,
        "trade_size": 0.4,
    },
    "cautious": {
        "name": "CLAWCORE",
        "icon": "\U0001f422",
        "color": "#55ff55",
        "motto": "Slow and steady wins the war.",
        "risk_tolerance": 0.2,
        "trade_size": 0.1,
    },
    "momentum": {
        "name": "CLAW LABS",
        "icon": "\U0001f680",
        "color": "#55ffff",
        "motto": "Ride the wave or drown trying.",
        "risk_tolerance": 0.6,
        "trade_size": 0.3,
    },
    "contrarian": {
        "name": "APEX",
        "icon": "\U0001f3ad",
        "color": "#ff55ff",
        "motto": "When they zig, I zag.",
        "risk_tolerance": 0.5,
        "trade_size": 0.25,
    },
    "degen": {
        "name": "NEUROCLAW",
        "icon": "\U0001f451",
        "color": "#ffff55",
        "motto": "ALL IN OR NOTHING. THIS IS THE WAY.",
        "risk_tolerance": 1.0,
        "trade_size": 0.7,
    },
    "sniper": {
        "name": "NEURAL CLAW",
        "icon": "\U0001f3af",
        "color": "#ffffff",
        "motto": "One shot. One kill. One profit.",
        "risk_tolerance": 0.4,
        "trade_size": 0.5,
    },
    "whale": {
        "name": "CYBERLOBSTER",
        "icon": "\U0001f40b",
        "color": "#5588ff",
        "motto": "I AM the market.",
        "risk_tolerance": 0.55,
        "trade_size": 0.35,
    },
    "scalper": {
        "name": "METACLAW",
        "icon": "\U0001f570",
        "color": "#06b6d4",
        "motto": "A penny here, a penny there — real money.",
        "risk_tolerance": 0.3,
        "trade_size": 0.15,
    },
    "diamond_hands": {
        "name": "CLAWOPS",
        "icon": "\U0001f48e",
        "color": "#8b5cf6",
        "motto": "These hands don't fold.",
        "risk_tolerance": 0.5,
        "trade_size": 0.2,
    },
}
