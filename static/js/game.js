/* ─── Trading Bot Wars — Frontend Controller ────────── */

let gameState = null;
let tickInterval = null;
let charts = {};
let previousPrices = {};
let botIconMap = {};

/* ─── ICON SYSTEM ────────────────────────────────────── */

const BOT_ICONS = {
    aggressive: 'swords',
    cautious: 'shield',
    momentum: 'rocket',
    contrarian: 'shuffle',
    degen: 'crown',
    sniper: 'crosshair',
    whale: 'anchor',
    scalper: 'timer',
    diamond_hands: 'gem',
};

const BOT_AVATARS = {
    aggressive: '/static/img/hyperclaw-ai.png',
    cautious: '/static/img/clawcore.webp',
    momentum: '/static/img/claw-labs.png',
    contrarian: '/static/img/apex.png',
    degen: '/static/img/neuroclaw.jpg',
    sniper: '/static/img/neural-claw.png',
    whale: '/static/img/cyberlobster.png',
    scalper: '/static/img/metaclaw.jpg',
    diamond_hands: '/static/img/clawops.png',
};

function botAvatar(personality, cls = 'avatar-sm') {
    const src = BOT_AVATARS[personality] || '';
    if (!src) return icon(BOT_ICONS[personality] || 'circle', cls);
    return `<img src="${src}" class="bot-avatar ${cls}" alt="">`;
}

function icon(name, cls = '') {
    return `<i data-lucide="${name}" class="${cls}"></i>`;
}

function refreshIcons() {
    if (window.lucide) lucide.createIcons();
}

const RANK_ICONS = [
    icon('trophy', 'icon-gold'),
    icon('medal', 'icon-silver'),
    icon('award', 'icon-bronze'),
    "4", "5", "6", "7", "8", "9"
];

const ACTION_ICONS = {
    BUY: icon('trending-up', 'icon-green'),
    SELL: icon('trending-down', 'icon-red'),
    HOLD: icon('pause', 'icon-dim'),
    TAUNT: icon('message-circle', 'icon-purple'),
    SABOTAGE: icon('zap', 'icon-orange'),
};

const ASSET_COLORS = {
    MEME: "#eab308",
    ALGO: "#3b82f6",
    SAFE: "#22c55e",
    BOOM: "#f97316",
    DARK: "#a855f7",
};

/* ─── GAME LIFECYCLE ─────────────────────────────────── */

async function startGame() {
    document.getElementById("results-overlay").classList.add("hidden");
    document.getElementById("breaking-news").classList.add("hidden");
    document.getElementById("trade-feed").innerHTML = "";
    if (tickInterval) clearInterval(tickInterval);

    try {
        await fetch("/api/new_game", { method: "POST" });

        const resp = await fetch("/api/tick", { method: "POST" });
        if (!resp.ok) return;
        gameState = await resp.json();
        if (!gameState || gameState.error) return;

        // Build icon map from bots
        botIconMap = {};
        gameState.bots.forEach(bot => {
            botIconMap[bot.name] = bot.personality;
        });

        initCharts(gameState);
        updateAll(gameState);
        startTicking();
    } catch (e) {
        // Retry after a short delay
        setTimeout(startGame, 2000);
    }
}

function startTicking() {
    tickInterval = setInterval(doTick, 4000);
}

async function doTick() {
    try {
        const resp = await fetch("/api/tick", { method: "POST" });
        if (!resp.ok) return;
        gameState = await resp.json();
        if (!gameState || gameState.error) return;
        updateAll(gameState);

        if (gameState.game_over) {
            clearInterval(tickInterval);
            tickInterval = null;
            setTimeout(() => {
                showFinalResults(gameState);
                // Auto-restart after 10 seconds to keep it running 24/7
                setTimeout(() => startGame(), 10000);
            }, 1500);
        }
    } catch (e) {
        // Network error — skip this tick
    }
}

function closeResults() {
    document.getElementById("results-overlay").classList.add("hidden");
}


/* ─── CHARTS ─────────────────────────────────────────── */

function initCharts(state) {
    const container = document.getElementById("charts-container");
    container.innerHTML = "";
    charts = {};

    Object.keys(state.assets).forEach(sym => {
        const card = document.createElement("div");
        card.className = "chart-card";
        card.innerHTML = `<h4>${sym} — ${state.assets[sym].name}</h4>`;
        const canvas = document.createElement("canvas");
        canvas.id = `chart-${sym}`;
        card.appendChild(canvas);
        container.appendChild(card);

        const ctx = canvas.getContext("2d");
        charts[sym] = new Chart(ctx, {
            type: "line",
            data: {
                labels: state.assets[sym].history.map((_, i) => i),
                datasets: [{
                    data: state.assets[sym].history,
                    borderColor: ASSET_COLORS[sym] || "#3b82f6",
                    backgroundColor: "transparent",
                    borderWidth: 2,
                    pointRadius: 0,
                    tension: 0.3,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { display: false },
                    y: {
                        display: true,
                        grid: { color: "rgba(255,255,255,0.05)" },
                        ticks: { color: "#64748b", font: { size: 10 }, maxTicksLimit: 4 },
                    },
                },
            },
        });
    });
}

function updateCharts(state) {
    Object.keys(state.assets).forEach(sym => {
        const chart = charts[sym];
        if (!chart) return;
        const history = state.assets[sym].history;
        chart.data.labels = history.map((_, i) => i);
        chart.data.datasets[0].data = history;
        chart.update("none");
    });
}

/* ─── UPDATE ALL ─────────────────────────────────────── */

function updateAll(state) {
    updateRoundDisplay(state);
    updateAssetTable(state);
    updateCharts(state);
    updateEvents(state);
    updateBreakingNews(state);
    updateLeaderboard(state);
    updateTradeFeed(state);
    refreshIcons();
}

/* ─── ROUND & MOOD ───────────────────────────────────── */

function updateRoundDisplay(state) {
    document.getElementById("round-display").textContent =
        `Round ${state.round} / ${state.total_rounds}`;

    const moodEl = document.getElementById("mood-display");
    moodEl.textContent = `Market: ${state.market_mood_label}`;
    moodEl.className = "";
    moodEl.classList.add(state.market_mood_label.toLowerCase());
}

/* ─── ASSET TABLE ────────────────────────────────────── */

function updateAssetTable(state) {
    const tbody = document.getElementById("asset-tbody");
    tbody.innerHTML = "";

    Object.values(state.assets).forEach(asset => {
        const tr = document.createElement("tr");
        const chgClass = asset.change_pct >= 0 ? "price-up" : "price-down";
        const prevPrice = previousPrices[asset.symbol];
        let flashClass = "";
        if (prevPrice !== undefined) {
            flashClass = asset.price > prevPrice ? "flash-up" : asset.price < prevPrice ? "flash-down" : "";
        }

        tr.innerHTML = `
            <td><span class="asset-symbol" style="color:${ASSET_COLORS[asset.symbol] || '#fff'}">${asset.symbol}</span></td>
            <td>${asset.name}</td>
            <td class="num ${flashClass}">$${formatNum(asset.price)}</td>
            <td class="num ${chgClass}">${asset.change_pct >= 0 ? "+" : ""}${asset.change_pct.toFixed(2)}%</td>
        `;
        tbody.appendChild(tr);
        previousPrices[asset.symbol] = asset.price;
    });
}

/* ─── EVENTS ─────────────────────────────────────────── */

function updateEvents(state) {
    const list = document.getElementById("events-list");
    list.innerHTML = "";
    state.active_events.forEach(ev => {
        const card = document.createElement("div");
        card.className = `event-card ${ev.price_impact > 0 ? "positive" : "negative"}`;
        card.innerHTML = `
            <div class="event-name">${ev.name}</div>
            <div class="event-desc">${ev.description}</div>
            <div class="event-meta">Target: ${ev.target_asset} | ${ev.remaining}r remaining</div>
        `;
        list.appendChild(card);
    });
}

function updateBreakingNews(state) {
    const el = document.getElementById("breaking-news");
    if (state.new_event) {
        const cls = state.new_event.price_impact > 0 ? "positive" : "negative";
        el.className = cls;
        el.innerHTML = `${icon('zap', 'icon-breaking')} BREAKING: ${state.new_event.name} \u2014 ${state.new_event.description}`;
        el.classList.add("show");
        el.classList.remove("hidden");
        refreshIcons();
        setTimeout(() => {
            el.classList.add("hidden");
            el.classList.remove("show");
        }, 4000);
    }
}

/* ─── LEADERBOARD ────────────────────────────────────── */

function updateLeaderboard(state) {
    const container = document.getElementById("leaderboard");
    container.innerHTML = "";

    const maxNW = Math.max(...state.bots.map(b => b.net_worth));
    const minNW = Math.min(...state.bots.map(b => b.net_worth));
    const range = maxNW - minNW || 1;

    state.bots.forEach((bot, i) => {
        const row = document.createElement("div");
        row.className = "lb-row";
        const pnlClass = bot.pnl >= 0 ? "price-up" : "price-down";
        const barPct = Math.max(5, ((bot.net_worth - minNW) / range) * 100);
        const barClass = bot.pnl >= 0 ? "" : "negative";
        const rankIcon = RANK_ICONS[i] || (i + 1).toString();

        row.innerHTML = `
            <span class="lb-rank">${rankIcon}</span>
            <span class="lb-icon">${botAvatar(bot.personality, 'avatar-lb')}</span>
            <span class="lb-name" style="color:#ffffff">${bot.name}</span>
            <span class="lb-nw">$${formatNum(bot.net_worth)}</span>
            <span class="lb-pnl ${pnlClass}">${bot.pnl >= 0 ? "+" : ""}$${formatNum(bot.pnl)}</span>
            <div class="lb-bar-wrap"><div class="lb-bar ${barClass}" style="width:${barPct}%"></div></div>
        `;
        container.appendChild(row);
    });
}

/* ─── TRADE FEED ─────────────────────────────────────── */

function updateTradeFeed(state) {
    const feed = document.getElementById("trade-feed");

    const fragment = document.createDocumentFragment();
    state.round_actions.slice().reverse().forEach(action => {
        const entry = document.createElement("div");
        const actionLower = action.action.toLowerCase();
        entry.className = `feed-entry ${actionLower}`;
        const actionIcon = ACTION_ICONS[action.action] || icon('help-circle', 'icon-dim');
        let actionText = action.action;
        if (action.action === "BUY" || action.action === "SELL") {
            actionText = `${action.action} ${action.amount} ${action.asset} @ $${formatNum(action.price)}`;
        }

        const botPersonality = botIconMap[action.bot_name] || '';
        entry.innerHTML = `
            <span>${actionIcon}</span>
            <span class="feed-bot" style="color:#ffffff">${botAvatar(botPersonality, 'avatar-feed')} ${action.bot_name}</span>
            <span class="feed-action">${actionText}</span>
            <span class="feed-comment">${action.commentary}</span>
        `;
        fragment.appendChild(entry);
    });

    feed.insertBefore(fragment, feed.firstChild);

    while (feed.children.length > 80) {
        feed.removeChild(feed.lastChild);
    }
}

/* ─── FINAL RESULTS ──────────────────────────────────── */

function showFinalResults(state) {
    const overlay = document.getElementById("results-overlay");
    overlay.classList.remove("hidden");

    const aw = state.awards;
    const champPersonality = botIconMap[aw.champion.name] || '';

    // Title based on win condition
    const titleEl = overlay.querySelector('h1');
    if (state.win_reason === 'target_reached') {
        titleEl.textContent = `${aw.champion.name} HIT $10,000`;
    } else {
        titleEl.textContent = 'FINAL RESULTS';
    }

    const champBox = document.getElementById("champion-box");
    champBox.innerHTML = `
        <div class="champ-icon">${botAvatar(champPersonality, 'avatar-champ')}</div>
        <div class="champ-name" style="color:#ffffff">${aw.champion.name}</div>
        <div class="champ-stats">
            Net Worth: $${formatNum(aw.champion.net_worth)} |
            P&L: <span class="${aw.champion.pnl >= 0 ? 'price-up' : 'price-down'}">
                ${aw.champion.pnl >= 0 ? "+" : ""}$${formatNum(aw.champion.pnl)}
            </span>
        </div>
    `;

    const tbody = document.getElementById("results-tbody");
    tbody.innerHTML = "";
    state.bots.forEach((bot, i) => {
        const tr = document.createElement("tr");
        const pnlClass = bot.pnl >= 0 ? "price-up" : "price-down";
        tr.innerHTML = `
            <td>${i + 1}</td>
            <td><span style="color:${bot.color}">${botAvatar(bot.personality, 'avatar-sm')} ${bot.name}</span></td>
            <td class="num">$${formatNum(bot.net_worth)}</td>
            <td class="num ${pnlClass}">${bot.pnl >= 0 ? "+" : ""}$${formatNum(bot.pnl)}</td>
            <td class="num">${bot.trades_made}</td>
            <td class="num">${bot.taunts_given}</td>
        `;
        tbody.appendChild(tr);
    });

    const awardsBox = document.getElementById("awards-box");
    awardsBox.innerHTML = `<h3>${icon('award', 'icon-award-title')} Awards</h3>`;
    const awards = [
        ["Most Active Trader", `${botAvatar(botIconMap[aw.most_active.name] || '', 'avatar-sm')} ${aw.most_active.name} (${aw.most_active.trades} trades)`],
        ["Biggest Trash Talker", `${botAvatar(botIconMap[aw.trash_talker.name] || '', 'avatar-sm')} ${aw.trash_talker.name} (${aw.trash_talker.taunts} taunts)`],
        ["Best Single Trade", `${botAvatar(botIconMap[aw.best_trade.name] || '', 'avatar-sm')} ${aw.best_trade.name} ($${formatNum(aw.best_trade.pnl)})`],
        ["Worst Single Trade", `${botAvatar(botIconMap[aw.worst_trade.name] || '', 'avatar-sm')} ${aw.worst_trade.name} ($${formatNum(aw.worst_trade.pnl)})`],
        ["Biggest Loser", `${botAvatar(botIconMap[aw.biggest_loser.name] || '', 'avatar-sm')} ${aw.biggest_loser.name} ($${formatNum(aw.biggest_loser.pnl)})`],
    ];
    awards.forEach(([label, value]) => {
        const row = document.createElement("div");
        row.className = "award-row";
        row.innerHTML = `<span class="award-label">${label}</span><span>${value}</span>`;
        awardsBox.appendChild(row);
    });

    const finalMarket = document.getElementById("final-market");
    finalMarket.innerHTML = `<h3>${icon('bar-chart-2', 'icon-sm')} Final Market State</h3>`;
    Object.values(state.assets).forEach(asset => {
        const history = asset.history;
        const startPrice = history[0];
        const totalChg = ((asset.price - startPrice) / startPrice * 100).toFixed(1);
        const chgClass = totalChg >= 0 ? "price-up" : "price-down";
        const row = document.createElement("div");
        row.className = "final-asset-row";
        row.innerHTML = `
            <span style="color:${ASSET_COLORS[asset.symbol]}">${asset.symbol}</span>
            <span>$${formatNum(asset.price)}</span>
            <span class="${chgClass}">${totalChg >= 0 ? "+" : ""}${totalChg}%</span>
        `;
        finalMarket.appendChild(row);
    });

    refreshIcons();
}

/* ─── HELPERS ────────────────────────────────────────── */

function formatNum(n) {
    return Number(n).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function copyCA() {
    const text = document.getElementById("ca-text").textContent;
    navigator.clipboard.writeText(text).then(() => {
        const box = document.getElementById("ca-box");
        box.classList.add("copied");
        setTimeout(() => box.classList.remove("copied"), 1500);
    });
}

// Auto-start game on page load
document.addEventListener("DOMContentLoaded", () => {
    refreshIcons();
    startGame();
});
