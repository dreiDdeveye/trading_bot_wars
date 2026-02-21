"""Game configuration: constants, asset templates, event pool, bot profiles."""

TOTAL_ROUNDS = 100
STARTING_CASH = 1_000.0
WIN_TARGET = 10_000.0
TICKS_PER_ROUND = 15          # sub-ticks per round (~4s each = ~60s per round)

# ─── ASSET TEMPLATES ─────────────────────────────────────────
ASSETS_TEMPLATE = [
    {"symbol": "MEME",  "name": "MemeCoin",       "price": 42.00,  "volatility": 0.9,  "trend": 0.1},
    {"symbol": "ALGO",  "name": "AlgoTech Corp",  "price": 150.00, "volatility": 0.4,  "trend": 0.2},
    {"symbol": "SAFE",  "name": "SafeHaven Bond", "price": 100.00, "volatility": 0.15, "trend": -0.05},
    {"symbol": "BOOM",  "name": "BoomEnergy",     "price": 75.00,  "volatility": 0.6,  "trend": 0.0},
    {"symbol": "DARK",  "name": "DarkPool Ltd",   "price": 200.00, "volatility": 0.5,  "trend": 0.15},
]

# ─── MARKET EVENTS ───────────────────────────────────────────
EVENT_POOL = [
    {"name": "REGULATORY CRACKDOWN", "description": "Govt bans fun. Markets panic.", "target_asset": "ALL", "price_impact": -0.04, "duration": 2},
    {"name": "MEME VIRUS", "description": "MemeCoin goes viral on social media!", "target_asset": "MEME", "price_impact": 0.12, "duration": 1},
    {"name": "ALGO BREAKTHROUGH", "description": "AlgoTech announces quantum AI chip!", "target_asset": "ALGO", "price_impact": 0.08, "duration": 2},
    {"name": "ENERGY CRISIS", "description": "BoomEnergy reactor goes offline!", "target_asset": "BOOM", "price_impact": -0.10, "duration": 2},
    {"name": "DARK POOL LEAK", "description": "DarkPool's secret trades exposed!", "target_asset": "DARK", "price_impact": -0.07, "duration": 1},
    {"name": "BULL STAMPEDE", "description": "Investors go full FOMO!", "target_asset": "ALL", "price_impact": 0.05, "duration": 1},
    {"name": "FLASH CRASH", "description": "Algorithms trigger cascade selling!", "target_asset": "ALL", "price_impact": -0.08, "duration": 1},
    {"name": "SAFE HAVEN RUSH", "description": "Everyone flees to safety!", "target_asset": "SAFE", "price_impact": 0.06, "duration": 2},
    {"name": "WHALE ALERT", "description": "Mysterious whale enters the market!", "target_asset": "MEME", "price_impact": 0.15, "duration": 1},
    {"name": "EARNINGS BEAT", "description": "AlgoTech smashes expectations!", "target_asset": "ALGO", "price_impact": 0.06, "duration": 1},
    {"name": "SHORT SQUEEZE", "description": "Shorts get obliterated on DarkPool!", "target_asset": "DARK", "price_impact": 0.12, "duration": 1},
    {"name": "FED RATE HIKE", "description": "Interest rates go brrrr UP!", "target_asset": "ALL", "price_impact": -0.03, "duration": 3},
    {"name": "STIMULUS CHECK", "description": "Money printer goes brrrr!", "target_asset": "ALL", "price_impact": 0.04, "duration": 2},
    {"name": "RUG PULL SCARE", "description": "MemeCoin dev wallet moves tokens!", "target_asset": "MEME", "price_impact": -0.15, "duration": 1},
    {"name": "TAKEOVER BID", "description": "Hostile takeover attempt on BoomEnergy!", "target_asset": "BOOM", "price_impact": 0.10, "duration": 1},
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
