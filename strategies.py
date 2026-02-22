"""Bot trading strategies — one function per personality."""

import random
from models import TradeAction, BotPersonality


def decide(bot, assets, round_num, all_bots, active_events):
    """Dispatch to the correct strategy based on bot personality."""
    dispatch = {
        BotPersonality.AGGRESSIVE: strategy_aggressive,
        BotPersonality.CAUTIOUS: strategy_cautious,
        BotPersonality.MOMENTUM: strategy_momentum,
        BotPersonality.CONTRARIAN: strategy_contrarian,
        BotPersonality.DEGEN: strategy_degen,
        BotPersonality.SNIPER: strategy_sniper,
        BotPersonality.WHALE: strategy_whale,
        BotPersonality.SCALPER: strategy_scalper,
        BotPersonality.DIAMOND_HANDS: strategy_diamond_hands,
    }
    fn = dispatch[bot.personality]
    if bot.personality == BotPersonality.SNIPER:
        actions = fn(bot, assets, round_num, active_events)
    elif bot.personality == BotPersonality.WHALE:
        actions = fn(bot, assets, round_num, all_bots)
    else:
        actions = fn(bot, assets, round_num)

    if random.random() < 0.15:
        actions.append(generate_taunt(bot, all_bots))

    return actions


def strategy_aggressive(bot, assets, rnd):
    actions = []
    for sym, asset in assets.items():
        held = bot.holdings.get(sym, 0)
        if asset.volatility > 0.5 and bot.cash > asset.price * 2:
            qty = int((bot.cash * 0.4) / asset.price)
            if qty > 0 and random.random() < 0.6:
                actions.append(TradeAction(bot.name, "BUY", sym, qty, asset.price,
                    random.choice([
                        f"Going HARD on {sym}! Blood in the water!",
                        f"Smells like money. Loading {sym}.",
                        f"Weakness is opportunity. Buying {sym} NOW.",
                    ])))
                bot.execute_buy(asset, qty)
        if held > 0 and asset.change_pct > 2:
            sell_qty = max(1, held // 2)
            actions.append(TradeAction(bot.name, "SELL", sym, sell_qty, asset.price,
                f"Taking profits on {sym}. The weak hold, the strong sell."))
            bot.execute_sell(asset, sell_qty)
        elif held > 0 and asset.change_pct < -5:
            actions.append(TradeAction(bot.name, "SELL", sym, held, asset.price,
                f"Cutting losses on {sym}. No sentiment. Only survival."))
            bot.execute_sell(asset, held)
    return actions


def strategy_cautious(bot, assets, rnd):
    actions = []
    bnb = assets.get("BNB")
    for sym, asset in assets.items():
        held = bot.holdings.get(sym, 0)
        if asset.volatility < 0.5 and bot.cash > asset.price * 3:
            qty = int((bot.cash * 0.1) / asset.price)
            if qty > 0 and random.random() < 0.5:
                actions.append(TradeAction(bot.name, "BUY", sym, qty, asset.price,
                    random.choice([
                        f"Carefully adding {sym} to portfolio.",
                        f"Diversifying into {sym}. Patience pays.",
                        f"Small position in {sym}. Risk managed.",
                    ])))
                bot.execute_buy(asset, qty)
        if held > 0 and asset.change_pct > 3:
            sell_qty = max(1, held // 3)
            actions.append(TradeAction(bot.name, "SELL", sym, sell_qty, asset.price,
                f"Trimming {sym}. Locking in gains responsibly."))
            bot.execute_sell(asset, sell_qty)
    if bnb and bot.cash > bnb.price * 5:
        qty = int((bot.cash * 0.15) / bnb.price)
        if qty > 0 and random.random() < 0.4:
            actions.append(TradeAction(bot.name, "BUY", "BNB", qty, bnb.price,
                "BNB is the safe play. Always."))
            bot.execute_buy(bnb, qty)
    return actions


def strategy_momentum(bot, assets, rnd):
    actions = []
    for sym, asset in assets.items():
        held = bot.holdings.get(sym, 0)
        if len(asset.history) >= 3:
            recent = asset.history[-3:]
            trending_up = all(recent[i] < recent[i + 1] for i in range(len(recent) - 1))
            trending_down = all(recent[i] > recent[i + 1] for i in range(len(recent) - 1))
            if trending_up and bot.cash > asset.price * 2:
                qty = int((bot.cash * 0.3) / asset.price)
                if qty > 0:
                    actions.append(TradeAction(bot.name, "BUY", sym, qty, asset.price,
                        random.choice([
                            f"{sym} is LAUNCHING! Hopping on the rocket!",
                            f"Momentum confirmed on {sym}. LFG!",
                            f"{sym} to the MOON! Trend is my friend!",
                        ])))
                    bot.execute_buy(asset, qty)
            elif trending_down and held > 0:
                actions.append(TradeAction(bot.name, "SELL", sym, held, asset.price,
                    f"Trend broken on {sym}. Ejecting!"))
                bot.execute_sell(asset, held)
    return actions


def strategy_contrarian(bot, assets, rnd):
    actions = []
    for sym, asset in assets.items():
        held = bot.holdings.get(sym, 0)
        if asset.change_pct < -3 and bot.cash > asset.price * 2:
            qty = int((bot.cash * 0.25) / asset.price)
            if qty > 0:
                actions.append(TradeAction(bot.name, "BUY", sym, qty, asset.price,
                    random.choice([
                        f"Everyone's selling {sym}? I'm BUYING.",
                        f"Blood in the streets on {sym}. Time to feast.",
                        f"The herd is wrong about {sym}. Classic.",
                    ])))
                bot.execute_buy(asset, qty)
        elif asset.change_pct > 4 and held > 0:
            actions.append(TradeAction(bot.name, "SELL", sym, held, asset.price,
                f"Too much euphoria on {sym}. Selling into strength."))
            bot.execute_sell(asset, held)
    return actions


def strategy_degen(bot, assets, rnd):
    actions = []
    sol = assets.get("SOL")
    if sol and bot.cash > sol.price * 3 and random.random() < 0.7:
        qty = int((bot.cash * 0.7) / sol.price)
        if qty > 0:
            actions.append(TradeAction(bot.name, "BUY", "SOL", qty, sol.price,
                random.choice([
                    "YOLO!!! SOL TO THE MOON!!!",
                    "APE IN APE IN APE IN!!!",
                    "Sir, this is a casino. ALL IN on SOL!",
                    "DIAMOND HANDS BABY! BUYING MORE SOL!",
                    "Solana ecosystem is cooking. I'm in.",
                ])))
            bot.execute_buy(sol, qty)
    for sym in list(bot.holdings.keys()):
        if random.random() < 0.3:
            held = bot.holdings[sym]
            asset = assets[sym]
            actions.append(TradeAction(bot.name, "SELL", sym, held, asset.price,
                random.choice([
                    f"Paper handing {sym} for more SOL money!",
                    f"Selling {sym} because I got bored.",
                    f"Need cash for the next YOLO. Dumping {sym}.",
                ])))
            bot.execute_sell(asset, held)
    return actions


def strategy_sniper(bot, assets, rnd, events):
    actions = []
    event_assets = set()
    for ev in events:
        if ev.target_asset != "ALL":
            event_assets.add(ev.target_asset)
    for sym in event_assets:
        if sym not in assets:
            continue
        asset = assets[sym]
        held = bot.holdings.get(sym, 0)
        relevant = [e for e in events if e.target_asset == sym]
        for ev in relevant:
            if ev.price_impact > 0 and bot.cash > asset.price:
                qty = int((bot.cash * 0.5) / asset.price)
                if qty > 0:
                    actions.append(TradeAction(bot.name, "BUY", sym, qty, asset.price,
                        f"Event detected: {ev.name}. Sniping {sym}."))
                    bot.execute_buy(asset, qty)
            elif ev.price_impact < 0 and held > 0:
                actions.append(TradeAction(bot.name, "SELL", sym, held, asset.price,
                    f"Negative event on {sym}. Precision exit."))
                bot.execute_sell(asset, held)
    if not actions and rnd % 3 == 0:
        actions.append(TradeAction(bot.name, "HOLD", "", 0, 0,
            random.choice([
                "Waiting... Patience is a weapon.",
                "No signal. No trade. Discipline.",
                "*scans the market through the scope*",
            ])))
    return actions


def strategy_whale(bot, assets, rnd, bots):
    actions = []
    cheapest = min(assets.values(), key=lambda a: a.price / (a.history[0] if a.history else a.price))
    if bot.cash > cheapest.price * 5:
        qty = int((bot.cash * 0.35) / cheapest.price)
        if qty > 0 and random.random() < 0.5:
            actions.append(TradeAction(bot.name, "BUY", cheapest.symbol, qty, cheapest.price,
                random.choice([
                    f"Accumulating {cheapest.symbol}. They don't see me coming.",
                    f"Adding to my {cheapest.symbol} position. I own this market.",
                    f"*splashes into {cheapest.symbol}* The ocean is mine.",
                ])))
            bot.execute_buy(cheapest, qty)
    for sym, qty in list(bot.holdings.items()):
        asset = assets[sym]
        if asset.change_pct > 3 and qty > 5:
            sell = qty // 2
            actions.append(TradeAction(bot.name, "SELL", sym, sell, asset.price,
                f"Redistributing {sym}. The market bends to my will."))
            bot.execute_sell(asset, sell)
    return actions


def strategy_scalper(bot, assets, rnd):
    actions = []
    for sym, asset in assets.items():
        held = bot.holdings.get(sym, 0)
        if asset.change_pct < -0.5 and bot.cash > asset.price:
            qty = max(1, int((bot.cash * 0.15) / asset.price))
            if random.random() < 0.7:
                actions.append(TradeAction(bot.name, "BUY", sym, qty, asset.price,
                    random.choice([
                        f"Scalping {sym}. In and out, quick profit.",
                        f"Tiny dip on {sym}. Free money.",
                        f"Tick by tick. Buying {sym}.",
                    ])))
                bot.execute_buy(asset, qty)
        if held > 0 and asset.change_pct > 0.5:
            sell_qty = max(1, held // 2)
            actions.append(TradeAction(bot.name, "SELL", sym, sell_qty, asset.price,
                random.choice([
                    f"Booking the tick on {sym}. Every cent counts.",
                    f"Quick flip on {sym}. Next.",
                    f"Scalped {sym}. Rinse and repeat.",
                ])))
            bot.execute_sell(asset, sell_qty)
    return actions


def strategy_diamond_hands(bot, assets, rnd):
    actions = []
    for sym, asset in assets.items():
        held = bot.holdings.get(sym, 0)
        if bot.cash > asset.price * 2 and random.random() < 0.4:
            qty = int((bot.cash * 0.2) / asset.price)
            if qty > 0:
                actions.append(TradeAction(bot.name, "BUY", sym, qty, asset.price,
                    random.choice([
                        f"Adding {sym} to the vault. Never selling.",
                        f"Accumulating {sym}. Diamond hands don't waver.",
                        f"HODL {sym}. Time in market > timing the market.",
                    ])))
                bot.execute_buy(asset, qty)
        if held > 0 and asset.change_pct < -10:
            sell_qty = max(1, held // 4)
            actions.append(TradeAction(bot.name, "SELL", sym, sell_qty, asset.price,
                f"Even diamond hands crack sometimes... trimming {sym}."))
            bot.execute_sell(asset, sell_qty)
    if rnd % 2 == 0 and not actions:
        actions.append(TradeAction(bot.name, "HOLD", "", 0, 0,
            random.choice([
                "HODL. It's not just a strategy, it's a lifestyle.",
                "Still holding. Still winning.",
                "Paper hands get paper gains. I want diamonds.",
            ])))
    return actions


def generate_taunt(bot, bots):
    others = [b for b in bots if b != bot]
    target = random.choice(others) if others else bot
    taunts = [
        f"Hey {target.name}, is that a portfolio or a dumpster fire?",
        f"{target.name} trades like a goldfish with a credit card.",
        f"My strategy is so advanced, {target.name}'s account just filed for bankruptcy.",
        f"While {target.name} was sleeping, I was TRADING.",
        f"Imagine losing money in THIS market. Couldn't be me. *looks at {target.name}*",
        f"{target.name}, your strategy is basically 'buy high sell low' right?",
        f"*{bot.name} flexes on {target.name}*",
        f"GG EZ, {target.name}. GG EZ.",
        f"I've seen better trades from a random number generator. Looking at you, {target.name}.",
        f"Just checked the leaderboard. {target.name} is speed-running poverty.",
    ]
    bot.taunts_given += 1
    return TradeAction(bot.name, "TAUNT", "", 0, 0, random.choice(taunts))
