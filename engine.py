"""Game engine — simulation logic with JSON-serializable state output."""

import random
from config import TOTAL_ROUNDS, STARTING_CASH, ASSETS_TEMPLATE, EVENT_POOL, BOT_PROFILES, WIN_TARGET, TICKS_PER_ROUND
from models import Asset, MarketEvent, TradeAction, BotPersonality, Bot
from prices import fetch_prices
import strategies


class GameEngine:
    def __init__(self):
        live_prices = fetch_prices()
        self.assets = {}
        for tmpl in ASSETS_TEMPLATE:
            sym = tmpl["symbol"]
            self.assets[sym] = Asset(
                symbol=sym,
                name=tmpl["name"],
                price=live_prices.get(sym, tmpl["price"]),
                volatility=tmpl["volatility"],
                trend=tmpl["trend"],
                history=[],
            )
        self.bots = [Bot(p, STARTING_CASH) for p in BotPersonality]
        self.round = 0
        self.sub_tick = 0
        self.game_over = False
        self.win_reason = None
        self.active_events: list[MarketEvent] = []
        self.event_timers: dict[str, int] = {}
        self.market_mood = 0.0
        self.round_actions: list[TradeAction] = []
        self.new_event = None

    def tick(self):
        if self.game_over:
            return self.get_state()

        # On first sub-tick of a new round, advance the round counter
        if self.sub_tick == 0:
            self.round += 1
            if self.round > TOTAL_ROUNDS:
                self.game_over = True
                self.win_reason = self.win_reason or "rounds_complete"
                return self.get_state()
            self.new_event = self._generate_events()
            self._update_market_mood()
        else:
            self.new_event = None

        # Sync real prices from CoinGecko then apply simulation noise
        live = fetch_prices()
        for sym, asset in self.assets.items():
            if sym in live:
                asset.price = live[sym]
            asset.tick(self.market_mood, self.active_events, TICKS_PER_ROUND)

        # Always: pick 2-3 random traders to act this sub-tick
        self.round_actions = []
        num_traders = random.randint(2, 4)
        trading_bots = random.sample(self.bots, min(num_traders, len(self.bots)))
        for bot in trading_bots:
            actions = strategies.decide(bot, self.assets, self.round, self.bots, self.active_events)
            self.round_actions.extend(actions)

        self.sub_tick += 1

        # End of round: record history, check win conditions
        if self.sub_tick >= TICKS_PER_ROUND:
            self.sub_tick = 0

            for bot in self.bots:
                bot.net_worth_history.append(bot.net_worth(self.assets))

            for bot in sorted(self.bots, key=lambda b: b.net_worth(self.assets), reverse=True):
                if bot.net_worth(self.assets) >= WIN_TARGET:
                    self.game_over = True
                    self.win_reason = "target_reached"
                    break

            if self.round >= TOTAL_ROUNDS:
                self.game_over = True
                if not self.win_reason:
                    self.win_reason = "rounds_complete"

        return self.get_state()

    def _generate_events(self):
        expired = [name for name, timer in self.event_timers.items() if timer <= 0]
        for name in expired:
            del self.event_timers[name]
            self.active_events = [e for e in self.active_events if e.name != name]

        for name in self.event_timers:
            self.event_timers[name] -= 1

        if random.random() < 0.3:
            tmpl = random.choice(EVENT_POOL)
            if tmpl["name"] not in self.event_timers:
                event = MarketEvent(
                    name=tmpl["name"],
                    description=tmpl["description"],
                    target_asset=tmpl["target_asset"],
                    price_impact=tmpl["price_impact"],
                    duration=tmpl["duration"],
                )
                self.active_events.append(event)
                self.event_timers[event.name] = event.duration
                return event
        return None

    def _update_market_mood(self):
        self.market_mood += random.gauss(0, 0.15)
        self.market_mood = max(-1, min(1, self.market_mood))
        self.market_mood *= 0.9

    def _mood_label(self):
        if self.market_mood > 0.6:
            return "EUPHORIC"
        if self.market_mood > 0.3:
            return "BULLISH"
        if self.market_mood < -0.6:
            return "PANIC"
        if self.market_mood < -0.3:
            return "BEARISH"
        return "NEUTRAL"

    def get_state(self):
        assets_data = {}
        for sym, asset in self.assets.items():
            assets_data[sym] = {
                "symbol": asset.symbol,
                "name": asset.name,
                "price": round(asset.price, 2),
                "change_pct": round(asset.change_pct, 2),
                "volatility": asset.volatility,
                "history": [round(p, 2) for p in asset.history] + [round(asset.price, 2)],
            }

        bots_data = []
        for bot in sorted(self.bots, key=lambda b: b.net_worth(self.assets), reverse=True):
            nw = bot.net_worth(self.assets)
            bots_data.append({
                "name": bot.name,
                "icon": bot.icon,
                "color": bot.color,
                "personality": bot.personality.value,
                "motto": bot.motto,
                "cash": round(bot.cash, 2),
                "net_worth": round(nw, 2),
                "pnl": round(nw - STARTING_CASH, 2),
                "holdings": dict(bot.holdings),
                "trades_made": bot.trades_made,
                "taunts_given": bot.taunts_given,
                "best_trade_pnl": round(bot.best_trade_pnl, 2),
                "worst_trade_pnl": round(bot.worst_trade_pnl, 2),
                "net_worth_history": [round(v, 2) for v in bot.net_worth_history],
            })

        events_data = []
        for ev in self.active_events:
            events_data.append({
                "name": ev.name,
                "description": ev.description,
                "target_asset": ev.target_asset,
                "price_impact": ev.price_impact,
                "remaining": self.event_timers.get(ev.name, 0),
            })

        new_event_data = None
        if self.new_event:
            new_event_data = {
                "name": self.new_event.name,
                "description": self.new_event.description,
                "target_asset": self.new_event.target_asset,
                "price_impact": self.new_event.price_impact,
            }

        actions_data = []
        for a in self.round_actions:
            bot = next((b for b in self.bots if b.name == a.bot_name), None)
            actions_data.append({
                "bot_name": a.bot_name,
                "bot_icon": bot.icon if bot else "",
                "bot_color": bot.color if bot else "#ffffff",
                "action": a.action,
                "asset": a.asset,
                "amount": a.amount,
                "price": round(a.price, 2),
                "commentary": a.commentary,
            })

        awards = None
        if self.game_over:
            ranked = sorted(self.bots, key=lambda b: b.net_worth(self.assets), reverse=True)
            winner = ranked[0]
            most_active = max(self.bots, key=lambda b: b.trades_made)
            trash_talker = max(self.bots, key=lambda b: b.taunts_given)
            best_trade = max(self.bots, key=lambda b: b.best_trade_pnl)
            worst_trade = min(self.bots, key=lambda b: b.worst_trade_pnl)
            biggest_loser = ranked[-1]
            awards = {
                "champion": {"name": winner.name, "icon": winner.icon, "color": winner.color,
                             "net_worth": round(winner.net_worth(self.assets), 2),
                             "pnl": round(winner.net_worth(self.assets) - STARTING_CASH, 2)},
                "most_active": {"name": most_active.name, "icon": most_active.icon, "trades": most_active.trades_made},
                "trash_talker": {"name": trash_talker.name, "icon": trash_talker.icon, "taunts": trash_talker.taunts_given},
                "best_trade": {"name": best_trade.name, "icon": best_trade.icon, "pnl": round(best_trade.best_trade_pnl, 2)},
                "worst_trade": {"name": worst_trade.name, "icon": worst_trade.icon, "pnl": round(worst_trade.worst_trade_pnl, 2)},
                "biggest_loser": {"name": biggest_loser.name, "icon": biggest_loser.icon, "color": biggest_loser.color,
                                  "pnl": round(biggest_loser.net_worth(self.assets) - STARTING_CASH, 2)},
            }

        return {
            "round": self.round,
            "total_rounds": TOTAL_ROUNDS,
            "game_over": self.game_over,
            "win_reason": self.win_reason,
            "market_mood": round(self.market_mood, 3),
            "market_mood_label": self._mood_label(),
            "assets": assets_data,
            "bots": bots_data,
            "active_events": events_data,
            "new_event": new_event_data,
            "round_actions": actions_data,
            "awards": awards,
        }
