/* ═══════════════════════════════════════════════════════════
   CLAWTOPIA — Frontend Controller
   ═══════════════════════════════════════════════════════════ */

let gameState = null;
let tickInterval = null;
let charts = {};
let previousPrices = {};
let botIconMap = {};

/* ─── ICON SYSTEM ────────────────────────────────────────── */

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
    BTC: "#f7931a",
    ETH: "#627eea",
    SOL: "#9945ff",
    BNB: "#f3ba2f",
    XRP: "#00aae4",
};

const COIN_ICONS = {
    BTC: "https://assets.coingecko.com/coins/images/1/small/bitcoin.png",
    ETH: "https://assets.coingecko.com/coins/images/279/small/ethereum.png",
    SOL: "https://assets.coingecko.com/coins/images/4128/small/solana.png",
    BNB: "https://assets.coingecko.com/coins/images/825/small/bnb-icon2_2x.png",
    XRP: "https://assets.coingecko.com/coins/images/44/small/xrp-symbol-white-128.png",
};

/* ─── GAME LIFECYCLE ─────────────────────────────────────── */

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

        botIconMap = {};
        gameState.bots.forEach(bot => {
            botIconMap[bot.name] = bot.personality;
        });

        initCharts(gameState);
        updateAll(gameState);
        startTicking();
    } catch (e) {
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

/* ─── CHARTS (CoinGecko style) ──────────────────────────── */

// Crosshair vertical line plugin
const crosshairPlugin = {
    id: 'crosshair',
    afterDraw(chart, args, opts) {
        if (chart._crosshairX == null) return;
        const { ctx, chartArea: { top, bottom, left, right } } = chart;
        const x = chart._crosshairX;
        if (x < left || x > right) return;
        ctx.save();
        /* Vertical crosshair line */
        ctx.beginPath();
        ctx.moveTo(x, top);
        ctx.lineTo(x, bottom);
        ctx.lineWidth = 1;
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.12)';
        ctx.setLineDash([3, 3]);
        ctx.stroke();
        ctx.restore();
    }
};
Chart.register(crosshairPlugin);

/* CoinGecko colors */
const CG_GREEN = "#16c784";
const CG_RED = "#ea3943";

function getChartLineColor(history) {
    if (history.length < 2) return CG_GREEN;
    return history[history.length - 1] >= history[0] ? CG_GREEN : CG_RED;
}

function createGradient(ctx, color, height) {
    const h = height || 180;
    const gradient = ctx.createLinearGradient(0, 0, 0, h);
    gradient.addColorStop(0, color + "28");
    gradient.addColorStop(0.4, color + "10");
    gradient.addColorStop(1, color + "00");
    return gradient;
}

function initCharts(state) {
    const container = document.getElementById("charts-container");
    container.innerHTML = "";
    charts = {};
    previousPrices = {};

    const symbols = Object.keys(state.assets);

    symbols.forEach((sym, idx) => {
        const asset = state.assets[sym];
        const card = document.createElement("div");
        card.className = "chart-card";
        card.id = `card-${sym}`;

        if (symbols.length % 2 !== 0 && idx === symbols.length - 1) {
            card.classList.add("chart-full");
        }

        const chg = asset.change_pct || 0;
        const badgeClass = chg >= 0 ? "up" : "down";
        const chgSign = chg >= 0 ? "+" : "";
        const lineColor = getChartLineColor(asset.history);
        const priceColor = chg >= 0 ? CG_GREEN : CG_RED;
        const coinIcon = COIN_ICONS[sym] || "";

        card.innerHTML = `
            <div class="chart-header">
                <div class="chart-header-left">
                    ${coinIcon ? `<img src="${coinIcon}" class="chart-coin-icon" alt="${sym}">` : ''}
                    <div class="chart-coin-info">
                        <span class="chart-sym">${asset.name}</span>
                        <span class="chart-name">${sym}/USD</span>
                    </div>
                </div>
                <div class="chart-header-right">
                    <span class="chart-price" id="price-${sym}" style="color:${priceColor}">$${formatNum(asset.price)}</span>
                    <span class="chart-badge ${badgeClass}" id="badge-${sym}">${chgSign}${chg.toFixed(2)}%</span>
                </div>
            </div>
        `;

        const canvas = document.createElement("canvas");
        canvas.id = `chart-${sym}`;
        card.appendChild(canvas);
        container.appendChild(card);

        previousPrices[sym] = asset.price;

        const ctx = canvas.getContext("2d");
        const chartHeight = card.classList.contains('chart-full') ? 160 : 180;

        const chartInstance = new Chart(ctx, {
            type: "line",
            data: {
                labels: asset.history.map((_, i) => i),
                datasets: [{
                    data: asset.history,
                    borderColor: lineColor,
                    backgroundColor: createGradient(ctx, lineColor, chartHeight),
                    borderWidth: 2,
                    pointRadius: 0,
                    pointHoverRadius: 5,
                    pointHoverBackgroundColor: lineColor,
                    pointHoverBorderColor: "#fff",
                    pointHoverBorderWidth: 2,
                    tension: 0.3,
                    fill: true,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        enabled: true,
                        backgroundColor: '#1e2028',
                        borderColor: 'rgba(255, 255, 255, 0.08)',
                        borderWidth: 1,
                        titleFont: { family: "'Inter', sans-serif", size: 11, weight: '500' },
                        bodyFont: { family: "'Inter', sans-serif", size: 13, weight: '700' },
                        titleColor: '#8b8e96',
                        bodyColor: '#fff',
                        padding: { top: 10, bottom: 10, left: 14, right: 14 },
                        cornerRadius: 8,
                        displayColors: false,
                        callbacks: {
                            title: () => `${asset.name} (${sym})`,
                            label: (c) => `$${formatNum(c.parsed.y)}`,
                        },
                    },
                    crosshair: {},
                },
                onHover: (event, elements, chart) => {
                    if (event.type === 'mousemove' && event.x != null) {
                        chart._crosshairX = event.x;
                    } else {
                        chart._crosshairX = null;
                    }
                },
                scales: {
                    x: { display: false },
                    y: {
                        position: 'right',
                        display: true,
                        grid: {
                            color: "rgba(255, 255, 255, 0.04)",
                            drawBorder: false,
                            lineWidth: 1,
                        },
                        border: { display: false },
                        ticks: {
                            color: "#5b5e6b",
                            font: { size: 10, family: "'Inter', sans-serif", weight: '500' },
                            maxTicksLimit: 5,
                            padding: 10,
                            callback: (val) => '$' + formatCompact(val),
                        },
                    },
                },
            },
        });

        // Clear crosshair on mouse leave
        canvas.addEventListener('mouseleave', () => {
            chartInstance._crosshairX = null;
            chartInstance.draw();
        });

        charts[sym] = chartInstance;
    });
}

function updateCharts(state) {
    Object.keys(state.assets).forEach(sym => {
        const chart = charts[sym];
        if (!chart) return;
        const asset = state.assets[sym];
        const history = asset.history;

        // Dynamic green/red line based on session trend
        const lineColor = getChartLineColor(history);
        chart.data.labels = history.map((_, i) => i);
        chart.data.datasets[0].data = history;
        chart.data.datasets[0].borderColor = lineColor;
        chart.data.datasets[0].pointHoverBackgroundColor = lineColor;
        chart.data.datasets[0].backgroundColor = createGradient(
            chart.ctx, lineColor, chart.chartArea ? chart.chartArea.height : 180
        );
        chart.update("none");

        // Update live price with CoinGecko colors
        const priceEl = document.getElementById(`price-${sym}`);
        if (priceEl) {
            priceEl.textContent = `$${formatNum(asset.price)}`;
            const prev = previousPrices[sym] || asset.price;
            const up = asset.price >= prev;
            priceEl.style.color = up ? CG_GREEN : CG_RED;
            previousPrices[sym] = asset.price;
        }

        // Update % change badge
        const badgeEl = document.getElementById(`badge-${sym}`);
        if (badgeEl) {
            const chg = asset.change_pct || 0;
            const chgSign = chg >= 0 ? "+" : "";
            badgeEl.textContent = `${chgSign}${chg.toFixed(2)}%`;
            badgeEl.className = `chart-badge ${chg >= 0 ? "up" : "down"}`;
        }
    });
}

/* ─── UPDATE ALL ─────────────────────────────────────────── */

function updateAll(state) {
    updateRoundDisplay(state);
    updateCharts(state);
    updateEvents(state);
    updateBreakingNews(state);
    updateLeaderboard(state);
    updateTradeFeed(state);
    refreshIcons();
}

/* ─── ROUND & MOOD ───────────────────────────────────────── */

function updateRoundDisplay(state) {
    document.getElementById("round-display").textContent =
        `R${state.round}/${state.total_rounds}`;

    const moodEl = document.getElementById("mood-display");
    moodEl.textContent = `${state.market_mood_label}`;
    moodEl.className = "";
    moodEl.classList.add(state.market_mood_label.toLowerCase());
}

/* ─── EVENTS ─────────────────────────────────────────────── */

function updateEvents(state) {
    const list = document.getElementById("events-list");
    list.innerHTML = "";
    state.active_events.forEach(ev => {
        const card = document.createElement("div");
        card.className = `event-card ${ev.price_impact > 0 ? "positive" : "negative"}`;
        card.innerHTML = `
            <div class="event-name">${ev.name}</div>
            <div class="event-desc">${ev.description}</div>
            <div class="event-meta">${ev.target_asset} &middot; ${ev.remaining}r left</div>
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

/* ─── LEADERBOARD ────────────────────────────────────────── */

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

/* ─── TRADE FEED ─────────────────────────────────────────── */

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

/* ─── FINAL RESULTS ──────────────────────────────────────── */

function showFinalResults(state) {
    const overlay = document.getElementById("results-overlay");
    overlay.classList.remove("hidden");

    const aw = state.awards;
    const champPersonality = botIconMap[aw.champion.name] || '';

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
            <td><span style="color:#ffffff">${botAvatar(bot.personality, 'avatar-sm')} ${bot.name}</span></td>
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

/* ─── HELPERS ────────────────────────────────────────────── */

function formatNum(n) {
    return Number(n).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function formatCompact(n) {
    if (n >= 1000) return (n / 1000).toFixed(1) + 'K';
    if (n >= 1) return n.toFixed(2);
    return n.toFixed(4);
}

function copyCA() {
    const text = document.getElementById("ca-text").textContent;
    navigator.clipboard.writeText(text).then(() => {
        const box = document.getElementById("ca-box");
        box.classList.add("copied");
        setTimeout(() => box.classList.remove("copied"), 1500);
    });
}

/* ─── REAL-TIME PRICE POLLING ────────────────────────────── */

let priceInterval = null;

async function pollPrices() {
    try {
        const resp = await fetch("/api/prices");
        if (!resp.ok) return;
        const prices = await resp.json();

        Object.keys(prices).forEach(sym => {
            const priceEl = document.getElementById(`price-${sym}`);
            if (priceEl) {
                const newPrice = prices[sym];
                const prev = previousPrices[sym] || newPrice;
                priceEl.textContent = `$${formatNum(newPrice)}`;
                priceEl.style.color = newPrice >= prev ? CG_GREEN : CG_RED;
                previousPrices[sym] = newPrice;
            }
        });
    } catch (e) {
        // skip
    }
}

function startPricePolling() {
    if (priceInterval) clearInterval(priceInterval);
    priceInterval = setInterval(pollPrices, 3000);
}

// Auto-start
document.addEventListener("DOMContentLoaded", () => {
    refreshIcons();
    startGame();
    startPricePolling();
});
