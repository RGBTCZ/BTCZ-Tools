# BTCZ Tools v1.0.0 🎉

The first complete release — a modular desktop toolkit for **BitcoinZ (BTCZ)** miners.
What started as a simple Mining Tracker is now a full suite built on a shared data layer,
with live pool APIs, four languages, and everything a miner checks daily in one place.

## ✨ Highlights

- **📊 Dashboard** — one home screen: network, your mining (today / 7d / 30d), profitability, price, and shortcuts to every tool.
- **⛏️ Mining Tracker** — rewards per day or date range, CSV export, address history + **live pool-side stats** for any address.
- **💰 Profitability** — revenue, cost, profit, price scenarios, break-even price and hardware ROI.
- **🌊 Pool Explorer** — on-chain pool distribution, **live stats from 3 pool software formats** (z-nomp, zpool/yiimp, Miningcore), and pool recommendations for your hashrate.
- **🌐 Network Explorer** — network stats + latest blocks with miner attribution.
- **📈 History** — monthly history, month-over-month comparison, projections, and alerts (difficulty change, new rewards).

## 🌍 Multilingual

English (default), Français, Español, Deutsch — switch on the fly, remembered between sessions.

## 🔧 Under the hood

- Shared BTCZ Data Layer with TTL cache and automatic failover between explorers.
- Correct Equihash 144,5 hashrate model (Sol/s).
- Live pool integrations: SW Groupe, Dark Fiber Mines, zpool.ca, HimPool (+ solo).

## 🚀 Getting started

```bash
git clone https://github.com/RGBTCZ/BTCZ-Tools.git
cd BTCZ-Tools
./run_btcz.sh
```

`run_btcz.sh` creates the virtualenv, installs dependencies on first launch, and starts the app.
Requires Python 3.10+ and an internet connection.

## 🗺️ What's next

Phase 7 — the **BTCZ Mining Assistant** (V2): analyze your setup and get actionable advice
(electricity cost vs. average, best pool for you, break-even, and more).

Built for the BitcoinZ community. 💚

**Full changelog:** see [CHANGELOG.md](./CHANGELOG.md)
