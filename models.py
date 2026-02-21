"""Data models: Asset, MarketEvent, TradeAction, Bot."""

import random
from dataclasses import dataclass, field
from enum import Enum

from config import BOT_PROFILES


class BotPersonality(Enum):
    AGGRESSIVE = "aggressive"
    CAUTIOUS = "cautious"
    MOMENTUM = "momentum"
    CONTRARIAN = "contrarian"
    DEGEN = "degen"
    SNIPER = "sniper"
    WHALE = "whale"
    SCALPER = "scalper"
    DIAMOND_HANDS = "diamond_hands"


@dataclass
class Asset:
    symbol: str
    name: str
    price: float
    volatility: float
    trend: float
    history: list = field(default_factory=list)

    def tick(self, market_mood: float, events: list):
        self.history.append(self.price)
        shock = random.gauss(0, self.volatility * self.price * 0.05)
        trend_pull = self.trend * self.price * 0.002
        mood_effect = market_mood * self.price * 0.01
        event_effect = 0
        for ev in events:
            if ev.target_asset == self.symbol or ev.target_asset == "ALL":
                event_effect += ev.price_impact * self.price
        if len(self.history) > 5:
            avg = sum(self.history[-5:]) / 5
            reversion = (avg - self.price) * 0.01
        else:
            reversion = 0
        self.price += shock + trend_pull + mood_effect + event_effect + reversion
        self.price = max(0.50, self.price)
        self.trend += random.gauss(0, 0.05)
        self.trend = max(-1, min(1, self.trend))

    @property
    def change_pct(self):
        if len(self.history) < 1:
            return 0
        return ((self.price - self.history[-1]) / self.history[-1]) * 100


@dataclass
class MarketEvent:
    name: str
    description: str
    target_asset: str
    price_impact: float
    duration: int


@dataclass
class TradeAction:
    bot_name: str
    action: str
    asset: str
    amount: int
    price: float
    commentary: str


@dataclass
class Bot:
    personality: BotPersonality
    cash: float
    holdings: dict = field(default_factory=dict)
    net_worth_history: list = field(default_factory=list)
    kills: int = 0
    taunts_given: int = 0
    trades_made: int = 0
    best_trade_pnl: float = 0
    worst_trade_pnl: float = 0
    cost_basis: dict = field(default_factory=dict)

    @property
    def profile(self):
        return BOT_PROFILES[self.personality.value]

    @property
    def name(self):
        return self.profile["name"]

    @property
    def color(self):
        return self.profile["color"]

    @property
    def icon(self):
        return self.profile["icon"]

    @property
    def motto(self):
        return self.profile["motto"]

    def net_worth(self, assets: dict) -> float:
        total = self.cash
        for sym, qty in self.holdings.items():
            total += qty * assets[sym].price
        return total

    def execute_buy(self, asset: Asset, qty: int):
        cost = qty * asset.price
        if cost > self.cash or qty <= 0:
            return False
        prev_qty = self.holdings.get(asset.symbol, 0)
        prev_cost = self.cost_basis.get(asset.symbol, 0)
        self.cash -= cost
        self.holdings[asset.symbol] = prev_qty + qty
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
