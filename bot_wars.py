#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║            TRADING BOT WARS — TRADE WARS EDITION            ║
║         Where algorithms clash and fortunes are made         ║
╚══════════════════════════════════════════════════════════════╝

A LARP-style trading bot battle simulator.
Watch AI bots with distinct personalities wage economic warfare.
"""

import random
import time
import os
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

# ─── CONFIG ──────────────────────────────────────────────────
TOTAL_ROUNDS = 30
STARTING_CASH = 10_000.0
TICK_DELAY = 0.6  # seconds between rounds (set to 0 for instant)

# ─── COLORS ──────────────────────────────────────────────────
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"
    BG_RED  = "\033[41m"
    BG_GREEN= "\033[42m"
    BG_BLUE = "\033[44m"
    ORANGE  = "\033[38;5;208m"

# ─── MARKET ASSETS ───────────────────────────────────────────
@dataclass
class Asset:
    symbol: str
    name: str
    price: float
    volatility: float  # 0.0 - 1.0
    trend: float  # momentum bias
    history: list = field(default_factory=list)

    def tick(self, market_mood: float, events: list):
        """Advance price by one tick."""
        self.history.append(self.price)
        # Base random walk
        shock = random.gauss(0, self.volatility * self.price * 0.05)
        # Trend component
        trend_pull = self.trend * self.price * 0.002
        # Market mood
        mood_effect = market_mood * self.price * 0.01
        # Event effects
        event_effect = 0
        for ev in events:
            if ev.target_asset == self.symbol or ev.target_asset == "ALL":
                event_effect += ev.price_impact * self.price
        # Mean reversion (mild)
        if len(self.history) > 5:
            avg = sum(self.history[-5:]) / 5
            reversion = (avg - self.price) * 0.01
        else:
            reversion = 0
        self.price += shock + trend_pull + mood_effect + event_effect + reversion
        self.price = max(0.50, self.price)  # floor
        # Drift the trend
        self.trend += random.gauss(0, 0.05)
        self.trend = max(-1, min(1, self.trend))

    @property
    def change_pct(self):
        if len(self.history) < 1:
            return 0
        return ((self.price - self.history[-1]) / self.history[-1]) * 100

ASSETS_TEMPLATE = [
    Asset("MEME",  "MemeCoin",       42.00,  0.9,   0.1),
    Asset("ALGO",  "AlgoTech Corp",  150.00, 0.4,   0.2),
    Asset("SAFE",  "SafeHaven Bond", 100.00, 0.15, -0.05),
    Asset("BOOM",  "BoomEnergy",     75.00,  0.6,   0.0),
    Asset("DARK",  "DarkPool Ltd",   200.00, 0.5,   0.15),
]

# ─── EVENTS ──────────────────────────────────────────────────
@dataclass
class MarketEvent:
    name: str
    description: str
    target_asset: str  # symbol or "ALL"
    price_impact: float  # multiplier on price
    duration: int  # rounds

EVENT_POOL = [
    MarketEvent("REGULATORY CRACKDOWN", "Govt bans fun. Markets panic.", "ALL", -0.04, 2),
    MarketEvent("MEME VIRUS", "MemeCoin goes viral on social media!", "MEME", 0.12, 1),
    MarketEvent("ALGO BREAKTHROUGH", "AlgoTech announces quantum AI chip!", "ALGO", 0.08, 2),
    MarketEvent("ENERGY CRISIS", "BoomEnergy reactor goes offline!", "BOOM", -0.10, 2),
    MarketEvent("DARK POOL LEAK", "DarkPool's secret trades exposed!", "DARK", -0.07, 1),
    MarketEvent("BULL STAMPEDE", "Investors go full FOMO!", "ALL", 0.05, 1),
    MarketEvent("FLASH CRASH", "Algorithms trigger cascade selling!", "ALL", -0.08, 1),
    MarketEvent("SAFE HAVEN RUSH", "Everyone flees to safety!", "SAFE", 0.06, 2),
    MarketEvent("WHALE ALERT", "Mysterious whale enters the market!", "MEME", 0.15, 1),
    MarketEvent("EARNINGS BEAT", "AlgoTech smashes expectations!", "ALGO", 0.06, 1),
    MarketEvent("SHORT SQUEEZE", "Shorts get obliterated on DarkPool!", "DARK", 0.12, 1),
    MarketEvent("FED RATE HIKE", "Interest rates go brrrr UP!", "ALL", -0.03, 3),
    MarketEvent("STIMULUS CHECK", "Money printer goes brrrr!", "ALL", 0.04, 2),
    MarketEvent("RUG PULL SCARE", "MemeCoin dev wallet moves tokens!", "MEME", -0.15, 1),
    MarketEvent("TAKEOVER BID", "Hostile takeover attempt on BoomEnergy!", "BOOM", 0.10, 1),
]

# ─── BOT ARCHETYPES ─────────────────────────────────────────
class BotPersonality(Enum):
    AGGRESSIVE  = "aggressive"
    CAUTIOUS    = "cautious"
    MOMENTUM    = "momentum"
    CONTRARIAN  = "contrarian"
    DEGEN       = "degen"
    SNIPER      = "sniper"
    WHALE       = "whale"
    SABOTEUR    = "saboteur"

BOT_PROFILES = {
    BotPersonality.AGGRESSIVE: {
        "name": "ALPHA WOLF",
        "icon": "🐺",
        "color": C.RED,
        "motto": "Strike hard. Strike fast. No mercy.",
        "risk_tolerance": 0.8,
        "trade_size": 0.4,  # % of cash per trade
    },
    BotPersonality.CAUTIOUS: {
        "name": "IRON TURTLE",
        "icon": "🐢",
        "color": C.GREEN,
        "motto": "Slow and steady wins the war.",
        "risk_tolerance": 0.2,
        "trade_size": 0.1,
    },
    BotPersonality.MOMENTUM: {
        "name": "ROCKET RIDER",
        "icon": "🚀",
        "color": C.CYAN,
        "motto": "Ride the wave or drown trying.",
        "risk_tolerance": 0.6,
        "trade_size": 0.3,
    },
    BotPersonality.CONTRARIAN: {
        "name": "CHAOS BARON",
        "icon": "🎭",
        "color": C.MAGENTA,
        "motto": "When they zig, I zag.",
        "risk_tolerance": 0.5,
        "trade_size": 0.25,
    },
    BotPersonality.DEGEN: {
        "name": "YOLO KING",
        "icon": "👑",
        "color": C.YELLOW,
        "motto": "ALL IN OR NOTHING. THIS IS THE WAY.",
        "risk_tolerance": 1.0,
        "trade_size": 0.7,
    },
    BotPersonality.SNIPER: {
        "name": "GHOST SNIPER",
        "icon": "🎯",
        "color": C.WHITE,
        "motto": "One shot. One kill. One profit.",
        "risk_tolerance": 0.4,
        "trade_size": 0.5,
    },
    BotPersonality.WHALE: {
        "name": "DEEP BLUE",
        "icon": "🐋",
        "color": C.BLUE,
        "motto": "I AM the market.",
        "risk_tolerance": 0.55,
        "trade_size": 0.35,
    },
    BotPersonality.SABOTEUR: {
        "name": "THE JESTER",
        "icon": "🃏",
        "color": C.ORANGE,
        "motto": "If I can't win, nobody can.",
        "risk_tolerance": 0.7,
        "trade_size": 0.3,
    },
}

@dataclass
class TradeAction:
    bot_name: str
    action: str   # "BUY", "SELL", "HOLD", "SABOTAGE", "TAUNT"
    asset: str
    amount: int
    price: float
    commentary: str

@dataclass
class Bot:
    personality: BotPersonality
    cash: float
    holdings: dict = field(default_factory=dict)  # symbol -> qty
    net_worth_history: list = field(default_factory=list)
    kills: int = 0  # times they profited off another's loss
    taunts_given: int = 0
    trades_made: int = 0
    best_trade_pnl: float = 0
    worst_trade_pnl: float = 0
    cost_basis: dict = field(default_factory=dict)  # symbol -> avg cost

    @property
    def profile(self):
        return BOT_PROFILES[self.personality]

    @property
    def name(self):
        return self.profile["name"]

    @property
    def color(self):
        return self.profile["color"]

    @property
    def icon(self):
        return self.profile["icon"]

    def net_worth(self, assets: dict) -> float:
        total = self.cash
        for sym, qty in self.holdings.items():
            total += qty * assets[sym].price
        return total

    def decide(self, assets: dict, round_num: int, all_bots: list, active_events: list) -> list[TradeAction]:
        """Each bot personality has its own trading logic."""
        actions = []
        p = self.profile

        if self.personality == BotPersonality.AGGRESSIVE:
            actions = self._strategy_aggressive(assets, round_num)
        elif self.personality == BotPersonality.CAUTIOUS:
            actions = self._strategy_cautious(assets, round_num)
        elif self.personality == BotPersonality.MOMENTUM:
            actions = self._strategy_momentum(assets, round_num)
        elif self.personality == BotPersonality.CONTRARIAN:
            actions = self._strategy_contrarian(assets, round_num)
        elif self.personality == BotPersonality.DEGEN:
            actions = self._strategy_degen(assets, round_num)
        elif self.personality == BotPersonality.SNIPER:
            actions = self._strategy_sniper(assets, round_num, active_events)
        elif self.personality == BotPersonality.WHALE:
            actions = self._strategy_whale(assets, round_num, all_bots)
        elif self.personality == BotPersonality.SABOTEUR:
            actions = self._strategy_saboteur(assets, round_num, all_bots)

        # Maybe taunt
        if random.random() < 0.15:
            actions.append(self._generate_taunt(all_bots))

        return actions

    def execute_buy(self, asset: Asset, qty: int):
        cost = qty * asset.price
        if cost > self.cash or qty <= 0:
            return False
        prev_qty = self.holdings.get(asset.symbol, 0)
        prev_cost = self.cost_basis.get(asset.symbol, 0)
        self.cash -= cost
        self.holdings[asset.symbol] = prev_qty + qty
        # Update cost basis
        total_cost = prev_cost * prev_qty + cost
        self.cost_basis[asset.symbol] = total_cost / (prev_qty + qty) if (prev_qty + qty) > 0 else 0
        self.trades_made += 1
        return True

    def execute_sell(self, asset: Asset, qty: int):
        held = self.holdings.get(asset.symbol, 0)
        qty = min(qty, held)
        if qty <= 0:
            return False
        revenue = qty * asset.price
        pnl = (asset.price - self.cost_basis.get(asset.symbol, asset.price)) * qty
        self.best_trade_pnl = max(self.best_trade_pnl, pnl)
        self.worst_trade_pnl = min(self.worst_trade_pnl, pnl)
        self.cash += revenue
        self.holdings[asset.symbol] = held - qty
        if self.holdings[asset.symbol] == 0:
            del self.holdings[asset.symbol]
            if asset.symbol in self.cost_basis:
                del self.cost_basis[asset.symbol]
        self.trades_made += 1
        return True

    # ── STRATEGIES ───────────────────────────────────────────
    def _strategy_aggressive(self, assets, rnd):
        """Buy volatile stuff, sell quickly for gains."""
        actions = []
        for sym, asset in assets.items():
            held = self.holdings.get(sym, 0)
            if asset.volatility > 0.5 and self.cash > asset.price * 2:
                qty = int((self.cash * 0.4) / asset.price)
                if qty > 0 and random.random() < 0.6:
                    actions.append(TradeAction(self.name, "BUY", sym, qty, asset.price,
                        random.choice([
                            f"Going HARD on {sym}! Blood in the water!",
                            f"Smells like money. Loading {sym}.",
                            f"Weakness is opportunity. Buying {sym} NOW.",
                        ])))
                    self.execute_buy(asset, qty)
            if held > 0 and asset.change_pct > 2:
                sell_qty = max(1, held // 2)
                actions.append(TradeAction(self.name, "SELL", sym, sell_qty, asset.price,
                    f"Taking profits on {sym}. The weak hold, the strong sell."))
                self.execute_sell(asset, sell_qty)
            elif held > 0 and asset.change_pct < -5:
                actions.append(TradeAction(self.name, "SELL", sym, held, asset.price,
                    f"Cutting losses on {sym}. No sentiment. Only survival."))
                self.execute_sell(asset, held)
        return actions

    def _strategy_cautious(self, assets, rnd):
        actions = []
        safe = assets.get("SAFE")
        algo = assets.get("ALGO")
        for sym, asset in assets.items():
            held = self.holdings.get(sym, 0)
            if asset.volatility < 0.3 and self.cash > asset.price * 3:
                qty = int((self.cash * 0.1) / asset.price)
                if qty > 0 and random.random() < 0.5:
                    actions.append(TradeAction(self.name, "BUY", sym, qty, asset.price,
                        random.choice([
                            f"Carefully adding {sym} to portfolio.",
                            f"Diversifying into {sym}. Patience pays.",
                            f"Small position in {sym}. Risk managed.",
                        ])))
                    self.execute_buy(asset, qty)
            if held > 0 and asset.change_pct > 3:
                sell_qty = max(1, held // 3)
                actions.append(TradeAction(self.name, "SELL", sym, sell_qty, asset.price,
                    f"Trimming {sym}. Locking in gains responsibly."))
                self.execute_sell(asset, sell_qty)
        # Also buy low-vol stuff
        if safe and self.cash > safe.price * 5:
            qty = int((self.cash * 0.15) / safe.price)
            if qty > 0 and random.random() < 0.4:
                actions.append(TradeAction(self.name, "BUY", "SAFE", qty, safe.price,
                    "Safety first. Always."))
                self.execute_buy(safe, qty)
        return actions

    def _strategy_momentum(self, assets, rnd):
        actions = []
        for sym, asset in assets.items():
            held = self.holdings.get(sym, 0)
            if len(asset.history) >= 3:
                recent = asset.history[-3:]
                trending_up = all(recent[i] < recent[i+1] for i in range(len(recent)-1))
                trending_down = all(recent[i] > recent[i+1] for i in range(len(recent)-1))
                if trending_up and self.cash > asset.price * 2:
                    qty = int((self.cash * 0.3) / asset.price)
                    if qty > 0:
                        actions.append(TradeAction(self.name, "BUY", sym, qty, asset.price,
                            random.choice([
                                f"{sym} is LAUNCHING! Hopping on the rocket!",
                                f"Momentum confirmed on {sym}. LFG!",
                                f"{sym} to the MOON! Trend is my friend!",
                            ])))
                        self.execute_buy(asset, qty)
                elif trending_down and held > 0:
                    actions.append(TradeAction(self.name, "SELL", sym, held, asset.price,
                        f"Trend broken on {sym}. Ejecting!"))
                    self.execute_sell(asset, held)
        return actions

    def _strategy_contrarian(self, assets, rnd):
        actions = []
        for sym, asset in assets.items():
            held = self.holdings.get(sym, 0)
            if asset.change_pct < -3 and self.cash > asset.price * 2:
                qty = int((self.cash * 0.25) / asset.price)
                if qty > 0:
                    actions.append(TradeAction(self.name, "BUY", sym, qty, asset.price,
                        random.choice([
                            f"Everyone's selling {sym}? I'm BUYING.",
                            f"Blood in the streets on {sym}. Time to feast.",
                            f"The herd is wrong about {sym}. Classic.",
                        ])))
                    self.execute_buy(asset, qty)
            elif asset.change_pct > 4 and held > 0:
                actions.append(TradeAction(self.name, "SELL", sym, held, asset.price,
                    f"Too much euphoria on {sym}. Selling into strength."))
                self.execute_sell(asset, held)
        return actions

    def _strategy_degen(self, assets, rnd):
        actions = []
        meme = assets.get("MEME")
        # YOLO into meme coins
        if meme and self.cash > meme.price * 3 and random.random() < 0.7:
            qty = int((self.cash * 0.7) / meme.price)
            if qty > 0:
                actions.append(TradeAction(self.name, "BUY", "MEME", qty, meme.price,
                    random.choice([
                        "YOLO!!! MEME TO THE MOON!!!",
                        "APE IN APE IN APE IN!!!",
                        "Sir, this is a casino. ALL IN on MEME!",
                        "DIAMOND HANDS BABY! BUYING MORE MEME!",
                        "My wife's boyfriend said buy MEME. I'm in.",
                    ])))
                self.execute_buy(meme, qty)
        # Random sells when bored
        for sym in list(self.holdings.keys()):
            if random.random() < 0.3:
                held = self.holdings[sym]
                asset = assets[sym]
                actions.append(TradeAction(self.name, "SELL", sym, held, asset.price,
                    random.choice([
                        f"Paper handing {sym} for more MEME money!",
                        f"Selling {sym} because I got bored.",
                        f"Need cash for the next YOLO. Dumping {sym}.",
                    ])))
                self.execute_sell(asset, held)
        return actions

    def _strategy_sniper(self, assets, rnd, events):
        actions = []
        # Only trade on events
        event_assets = set()
        for ev in events:
            if ev.target_asset != "ALL":
                event_assets.add(ev.target_asset)
        for sym in event_assets:
            if sym not in assets:
                continue
            asset = assets[sym]
            held = self.holdings.get(sym, 0)
            # Find the event
            relevant = [e for e in events if e.target_asset == sym]
            for ev in relevant:
                if ev.price_impact > 0 and self.cash > asset.price:
                    qty = int((self.cash * 0.5) / asset.price)
                    if qty > 0:
                        actions.append(TradeAction(self.name, "BUY", sym, qty, asset.price,
                            f"Event detected: {ev.name}. Sniping {sym}."))
                        self.execute_buy(asset, qty)
                elif ev.price_impact < 0 and held > 0:
                    actions.append(TradeAction(self.name, "SELL", sym, held, asset.price,
                        f"Negative event on {sym}. Precision exit."))
                    self.execute_sell(asset, held)
        if not actions and rnd % 3 == 0:
            actions.append(TradeAction(self.name, "HOLD", "", 0, 0,
                random.choice([
                    "Waiting... Patience is a weapon.",
                    "No signal. No trade. Discipline.",
                    "*scans the market through the scope*",
                ])))
        return actions

    def _strategy_whale(self, assets, rnd, bots):
        actions = []
        # Buy whatever is cheapest relative to start, dominate that market
        cheapest = min(assets.values(), key=lambda a: a.price / (a.history[0] if a.history else a.price))
        if self.cash > cheapest.price * 5:
            qty = int((self.cash * 0.35) / cheapest.price)
            if qty > 0 and random.random() < 0.5:
                actions.append(TradeAction(self.name, "BUY", cheapest.symbol, qty, cheapest.price,
                    random.choice([
                        f"Accumulating {cheapest.symbol}. They don't see me coming.",
                        f"Adding to my {cheapest.symbol} position. I own this market.",
                        f"*splashes into {cheapest.symbol}* The ocean is mine.",
                    ])))
                self.execute_buy(cheapest, qty)
        # Sell winners
        for sym, qty in list(self.holdings.items()):
            asset = assets[sym]
            if asset.change_pct > 3 and qty > 5:
                sell = qty // 2
                actions.append(TradeAction(self.name, "SELL", sym, sell, asset.price,
                    f"Redistributing {sym}. The market bends to my will."))
                self.execute_sell(asset, sell)
        return actions

    def _strategy_saboteur(self, assets, rnd, bots):
        actions = []
        # Buy what the leader is selling, sell what they're buying (approximate)
        leader = max(bots, key=lambda b: b.net_worth(assets) if b != self else 0)
        leader_holdings = leader.holdings
        for sym, asset in assets.items():
            held = self.holdings.get(sym, 0)
            leader_has = leader_holdings.get(sym, 0)
            if leader_has > 0 and held == 0 and self.cash > asset.price * 2:
                # Counter the leader
                qty = int((self.cash * 0.3) / asset.price)
                if qty > 0 and random.random() < 0.4:
                    actions.append(TradeAction(self.name, "BUY", sym, qty, asset.price,
                        f"Mirroring {leader.name}'s {sym} position... for now."))
                    self.execute_buy(asset, qty)
            elif leader_has == 0 and held > 0 and random.random() < 0.3:
                actions.append(TradeAction(self.name, "SELL", sym, held, asset.price,
                    f"{leader.name} dumped {sym}? I'll dump harder!"))
                self.execute_sell(asset, held)

        if random.random() < 0.2:
            actions.append(TradeAction(self.name, "SABOTAGE", "", 0, 0,
                random.choice([
                    f"*whispers FUD about {leader.name}'s positions*",
                    "Spreading rumors in the dark pools...",
                    "If I'm going down, I'm taking everyone with me!",
                    f"Nice portfolio, {leader.name}. Would be a shame if someone... disrupted it.",
                ])))
        return actions

    def _generate_taunt(self, bots) -> TradeAction:
        others = [b for b in bots if b != self]
        target = random.choice(others) if others else self
        taunts = [
            f"Hey {target.name}, is that a portfolio or a dumpster fire?",
            f"{target.name} trades like a goldfish with a credit card.",
            f"My algorithm is so advanced, {target.name}'s bot just filed for bankruptcy.",
            f"While {target.name} was sleeping, I was TRADING.",
            f"Imagine losing money in THIS market. Couldn't be me. *looks at {target.name}*",
            f"{target.name}, your strategy is basically 'buy high sell low' right?",
            f"*{self.name} flexes on {target.name}*",
            f"GG EZ, {target.name}. GG EZ.",
            f"I've seen better trades from a random number generator. Looking at you, {target.name}.",
            f"Just checked the leaderboard. {target.name} is speed-running poverty.",
        ]
        self.taunts_given += 1
        return TradeAction(self.name, "TAUNT", "", 0, 0, random.choice(taunts))


# ─── GAME ENGINE ─────────────────────────────────────────────
class TradingBotWars:
    def __init__(self):
        self.assets = {a.symbol: Asset(a.symbol, a.name, a.price, a.volatility, a.trend, [])
                       for a in ASSETS_TEMPLATE}
        self.bots = [Bot(p, STARTING_CASH) for p in BotPersonality]
        self.round = 0
        self.active_events: list[MarketEvent] = []
        self.event_timers: dict[str, int] = {}
        self.market_mood = 0.0
        self.battle_log: list[str] = []
        self.width = 80

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_banner(self):
        print(f"""
{C.RED}{C.BOLD}╔══════════════════════════════════════════════════════════════════════════════╗
║  ████████╗██████╗  █████╗ ██████╗ ██╗███╗   ██╗ ██████╗                     ║
║  ╚══██╔══╝██╔══██╗██╔══██╗██╔══██╗██║████╗  ██║██╔════╝                     ║
║     ██║   ██████╔╝███████║██║  ██║██║██╔██╗ ██║██║  ███╗                    ║
║     ██║   ██╔══██╗██╔══██║██║  ██║██║██║╚██╗██║██║   ██║                    ║
║     ██║   ██║  ██║██║  ██║██████╔╝██║██║ ╚████║╚██████╔╝                    ║
║     ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚═╝╚═╝  ╚═══╝ ╚═════╝                    ║
║  {C.YELLOW}██████╗  ██████╗ ████████╗    ██╗    ██╗ █████╗ ██████╗ ███████╗{C.RED}           ║
║  {C.YELLOW}██╔══██╗██╔═══██╗╚══██╔══╝    ██║    ██║██╔══██╗██╔══██╗██╔════╝{C.RED}           ║
║  {C.YELLOW}██████╔╝██║   ██║   ██║       ██║ █╗ ██║███████║██████╔╝███████╗{C.RED}           ║
║  {C.YELLOW}██╔══██╗██║   ██║   ██║       ██║███╗██║██╔══██║██╔══██╗╚════██║{C.RED}           ║
║  {C.YELLOW}██████╔╝╚██████╔╝   ██║       ╚███╔███╔╝██║  ██║██║  ██║███████║{C.RED}           ║
║  {C.YELLOW}╚═════╝  ╚═════╝    ╚═╝        ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝{C.RED}           ║
╠══════════════════════════════════════════════════════════════════════════════╣
║{C.WHITE}          Where algorithms clash and fortunes are made...{C.RED}                   ║
╚══════════════════════════════════════════════════════════════════════════════╝{C.RESET}
""")

    def print_combatants(self):
        print(f"\n{C.BOLD}{C.YELLOW}  ⚔  COMBATANTS  ⚔{C.RESET}\n")
        for bot in self.bots:
            p = bot.profile
            print(f"  {p['color']}{p['icon']}  {p['name']:15s}{C.RESET} {C.DIM}│{C.RESET} \"{p['motto']}\"")
        print()

    def generate_events(self):
        """Maybe spawn new events."""
        # Remove expired events
        expired = [name for name, timer in self.event_timers.items() if timer <= 0]
        for name in expired:
            del self.event_timers[name]
            self.active_events = [e for e in self.active_events if e.name != name]

        # Tick down timers
        for name in self.event_timers:
            self.event_timers[name] -= 1

        # Maybe spawn new event
        if random.random() < 0.3:  # 30% chance per round
            event = random.choice(EVENT_POOL)
            if event.name not in self.event_timers:
                self.active_events.append(event)
                self.event_timers[event.name] = event.duration
                return event
        return None

    def update_market_mood(self):
        """Shift overall market sentiment."""
        self.market_mood += random.gauss(0, 0.15)
        self.market_mood = max(-1, min(1, self.market_mood))
        # Mean revert mood
        self.market_mood *= 0.9

    def render_market(self):
        mood_str = "NEUTRAL"
        mood_color = C.WHITE
        if self.market_mood > 0.3:
            mood_str = "BULLISH"
            mood_color = C.GREEN
        elif self.market_mood > 0.6:
            mood_str = "EUPHORIC"
            mood_color = C.GREEN + C.BOLD
        elif self.market_mood < -0.3:
            mood_str = "BEARISH"
            mood_color = C.RED
        elif self.market_mood < -0.6:
            mood_str = "PANIC"
            mood_color = C.RED + C.BOLD

        print(f"\n{C.BOLD}{'═'*78}{C.RESET}")
        print(f"{C.BOLD}  ROUND {self.round}/{TOTAL_ROUNDS}    "
              f"Market Mood: {mood_color}{mood_str}{C.RESET}    "
              f"{C.DIM}mood={self.market_mood:+.2f}{C.RESET}")
        print(f"{C.BOLD}{'═'*78}{C.RESET}")

        # Asset table
        print(f"\n  {'ASSET':<8} {'NAME':<18} {'PRICE':>10} {'CHANGE':>10} {'CHART':>20}")
        print(f"  {'─'*8} {'─'*18} {'─'*10} {'─'*10} {'─'*20}")
        for sym, asset in self.assets.items():
            chg = asset.change_pct
            chg_color = C.GREEN if chg >= 0 else C.RED
            chg_str = f"{chg:+.2f}%"
            # Mini sparkline
            chart = self._mini_chart(asset)
            print(f"  {C.BOLD}{sym:<8}{C.RESET} {asset.name:<18} "
                  f"${asset.price:>9.2f} {chg_color}{chg_str:>10}{C.RESET} {chart}")

    def _mini_chart(self, asset: Asset) -> str:
        if len(asset.history) < 2:
            return ""
        history = (asset.history + [asset.price])[-15:]
        mn, mx = min(history), max(history)
        if mx == mn:
            return "▁" * len(history)
        chars = "▁▂▃▄▅▆▇█"
        spark = ""
        for v in history:
            idx = int((v - mn) / (mx - mn) * (len(chars) - 1))
            c = C.GREEN if v >= history[0] else C.RED
            spark += f"{c}{chars[idx]}{C.RESET}"
        return spark

    def render_events(self):
        if self.active_events:
            print(f"\n  {C.BOLD}{C.YELLOW}⚡ ACTIVE EVENTS:{C.RESET}")
            for ev in self.active_events:
                impact_color = C.GREEN if ev.price_impact > 0 else C.RED
                remaining = self.event_timers.get(ev.name, 0)
                print(f"    {impact_color}● {ev.name}{C.RESET} — {ev.description} "
                      f"{C.DIM}[{remaining}r remaining]{C.RESET}")

    def render_actions(self, all_actions: list[TradeAction]):
        if not all_actions:
            return
        print(f"\n  {C.BOLD}📡 TRADE FEED:{C.RESET}")
        for action in all_actions[-12:]:  # Show last 12 actions
            bot = next((b for b in self.bots if b.name == action.bot_name), None)
            if not bot:
                continue
            color = bot.color
            if action.action == "BUY":
                icon = "🟢"
                act = f"BUY  {action.amount:>4} {action.asset} @ ${action.price:.2f}"
            elif action.action == "SELL":
                icon = "🔴"
                act = f"SELL {action.amount:>4} {action.asset} @ ${action.price:.2f}"
            elif action.action == "HOLD":
                icon = "⏸ "
                act = "HOLD"
            elif action.action == "TAUNT":
                icon = "💬"
                act = "TAUNT"
            elif action.action == "SABOTAGE":
                icon = "💣"
                act = "SABOTAGE"
            else:
                icon = "❓"
                act = action.action

            name_str = f"{color}{bot.icon} {action.bot_name:15s}{C.RESET}"
            print(f"    {icon} {name_str} {act:<35} {C.DIM}{action.commentary}{C.RESET}")

    def render_leaderboard(self):
        print(f"\n  {C.BOLD}🏆 LEADERBOARD:{C.RESET}")
        ranked = sorted(self.bots, key=lambda b: b.net_worth(self.assets), reverse=True)
        for i, bot in enumerate(ranked):
            nw = bot.net_worth(self.assets)
            pnl = nw - STARTING_CASH
            pnl_color = C.GREEN if pnl >= 0 else C.RED
            bar_len = max(0, int((nw / (STARTING_CASH * 3)) * 30))
            bar = "█" * bar_len
            rank_icon = ["👑", "🥈", "🥉", "4.", "5.", "6.", "7.", "8."][i]
            print(f"    {rank_icon} {bot.color}{bot.icon} {bot.name:15s}{C.RESET} "
                  f"${nw:>10,.2f} {pnl_color}({pnl:+,.2f}){C.RESET} "
                  f" {C.GREEN}{bar}{C.RESET}")

    def render_new_event(self, event: Optional[MarketEvent]):
        if event:
            color = C.GREEN if event.price_impact > 0 else C.RED
            print(f"\n  {C.BOLD}{color}{'!'*30}{C.RESET}")
            print(f"  {C.BOLD}{color}⚡ BREAKING: {event.name}{C.RESET}")
            print(f"  {color}  {event.description}{C.RESET}")
            target = event.target_asset if event.target_asset != "ALL" else "ALL ASSETS"
            print(f"  {color}  Target: {target}  |  Impact: {event.price_impact:+.0%}{C.RESET}")
            print(f"  {C.BOLD}{color}{'!'*30}{C.RESET}")

    def render_final_results(self):
        self.clear_screen()
        print(f"""
{C.RED}{C.BOLD}
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                      ⚔   FINAL BATTLE RESULTS   ⚔                          ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
{C.RESET}""")
        ranked = sorted(self.bots, key=lambda b: b.net_worth(self.assets), reverse=True)
        winner = ranked[0]

        print(f"\n  {C.BOLD}{C.YELLOW}{'★'*40}")
        print(f"  ★  CHAMPION: {winner.icon} {winner.name:20s}  ★")
        print(f"  ★  Net Worth: ${winner.net_worth(self.assets):>12,.2f}          ★")
        print(f"  ★  P&L: {C.GREEN}${winner.net_worth(self.assets)-STARTING_CASH:>+12,.2f}{C.YELLOW}              ★")
        print(f"  {'★'*40}{C.RESET}\n")

        print(f"  {C.BOLD}{'RANK':<6} {'BOT':20s} {'NET WORTH':>12} {'P&L':>12} {'TRADES':>8} {'TAUNTS':>8}{C.RESET}")
        print(f"  {'─'*6} {'─'*20} {'─'*12} {'─'*12} {'─'*8} {'─'*8}")

        for i, bot in enumerate(ranked):
            nw = bot.net_worth(self.assets)
            pnl = nw - STARTING_CASH
            pnl_color = C.GREEN if pnl >= 0 else C.RED
            rank = i + 1
            print(f"  {rank:<6} {bot.color}{bot.icon} {bot.name:18s}{C.RESET} "
                  f"${nw:>11,.2f} {pnl_color}${pnl:>+11,.2f}{C.RESET} "
                  f"{bot.trades_made:>8} {bot.taunts_given:>8}")

        # Awards
        print(f"\n  {C.BOLD}{C.CYAN}🏅 AWARDS:{C.RESET}")
        most_trades = max(self.bots, key=lambda b: b.trades_made)
        print(f"    Most Active Trader:  {most_trades.icon} {most_trades.name} ({most_trades.trades_made} trades)")
        most_taunts = max(self.bots, key=lambda b: b.taunts_given)
        print(f"    Biggest Trash Talker: {most_taunts.icon} {most_taunts.name} ({most_taunts.taunts_given} taunts)")
        best_single = max(self.bots, key=lambda b: b.best_trade_pnl)
        print(f"    Best Single Trade:   {best_single.icon} {best_single.name} (${best_single.best_trade_pnl:+,.2f})")
        worst_single = min(self.bots, key=lambda b: b.worst_trade_pnl)
        print(f"    Worst Single Trade:  {worst_single.icon} {worst_single.name} (${worst_single.worst_trade_pnl:+,.2f})")
        biggest_loser = ranked[-1]
        print(f"    Biggest Loser:       {biggest_loser.icon} {biggest_loser.name} "
              f"(${biggest_loser.net_worth(self.assets)-STARTING_CASH:+,.2f})")

        # Final asset prices
        print(f"\n  {C.BOLD}📊 FINAL MARKET STATE:{C.RESET}")
        for sym, asset in self.assets.items():
            start = asset.history[0] if asset.history else asset.price
            total_chg = ((asset.price - start) / start) * 100
            chg_color = C.GREEN if total_chg >= 0 else C.RED
            print(f"    {sym:8s} ${asset.price:>9.2f}  {chg_color}({total_chg:+.1f}% overall){C.RESET}")

        print(f"\n{C.DIM}  Game over. The bots rest... until the next war.{C.RESET}\n")

    def run(self):
        self.clear_screen()
        self.print_banner()
        self.print_combatants()
        input(f"\n  {C.BOLD}Press ENTER to start the war...{C.RESET}")

        for rnd in range(1, TOTAL_ROUNDS + 1):
            self.round = rnd
            self.clear_screen()

            # 1. Generate events
            new_event = self.generate_events()

            # 2. Update market mood
            self.update_market_mood()

            # 3. Tick assets
            for asset in self.assets.values():
                asset.tick(self.market_mood, self.active_events)

            # 4. Bots decide and trade
            all_actions = []
            random.shuffle(self.bots)  # Random order each round
            for bot in self.bots:
                actions = bot.decide(self.assets, rnd, self.bots, self.active_events)
                all_actions.extend(actions)

            # 5. Record net worths
            for bot in self.bots:
                bot.net_worth_history.append(bot.net_worth(self.assets))

            # 6. Render
            self.render_market()
            self.render_new_event(new_event)
            self.render_events()
            self.render_actions(all_actions)
            self.render_leaderboard()

            if TICK_DELAY > 0:
                time.sleep(TICK_DELAY)
            if rnd < TOTAL_ROUNDS:
                # Auto-advance or wait
                pass

        # Final
        input(f"\n  {C.BOLD}Press ENTER for final results...{C.RESET}")
        self.render_final_results()


# ─── ENTRY POINT ─────────────────────────────────────────────
if __name__ == "__main__":
    try:
        game = TradingBotWars()
        game.run()
    except KeyboardInterrupt:
        print(f"\n\n  {C.RED}War aborted. The bots will remember this...{C.RESET}\n")
