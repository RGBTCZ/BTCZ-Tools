# Changelog

All notable changes to BTCZ Tools are documented here.
This project adheres to [Semantic Versioning](https://semver.org/).

## [1.4.6] - 2026-09-13

Surfaces today's miner emission right in the Dashboard header.

### Added
- **Miner-emission chip in the Dashboard header** — a compact premium pill (⛏️ + amount + block count) shows how many BTCZ have gone to miners since local midnight, front and centre the moment the app opens. Same live figure as the Network Explorer card, in your selected currency's context.

[1.4.6]: https://github.com/RGBTCZ/BTCZ-Tools/releases/tag/v1.4.6

## [1.4.5] - 2026-09-13

Adds a live "miner emission today" card.

### Added
- **⛏️ Miner emission today** — a premium card in the Network Explorer showing how many BTCZ have actually been paid to miners since local midnight. It counts the real blocks found today (via the explorer's per-date block list, filtered by each block's timestamp against your local 00:00) and sums the true miner reward per block, i.e. the post-Canopy **80%** share (2,500 of the 3,125 BTCZ block reward; the other 20% goes to the community fund). The card also shows the ≈ fiat value in your selected currency and the per-block miner reward.

[1.4.5]: https://github.com/RGBTCZ/BTCZ-Tools/releases/tag/v1.4.5

## [1.4.4] - 2026-09-13

Sharpens the live pool-stats panel: shared-pool immature, remembered rigs, and auto-refresh.

### Added
- **Remembered rig addresses** — the pool-stats address field is now a dropdown that keeps the addresses you've fetched (with the last pool you used), instead of a placeholder that forgot them. A **Remove** button drops one.
- **Auto-refresh every 60s** — a switch (on by default) re-fetches your live pool stats every minute so IMMATURE, BALANCE and PAID stay current while you watch. The worker-stats cache was shortened to ~45s so each refresh brings fresh data.
- **Immature on shared pools** — on PPLNS/collective Miningcore pools, IMMATURE is now shown as your proportional share of the pending blocks (your hashrate ÷ pool hashrate × pending rewards), marked **(est.)**. Solo pools stay exact (sum of the pending blocks your address found).

### Notes
- On Miningcore, a confirmed-but-unpaid block sits in BALANCE (`pendingBalance`) until the payout threshold is met — that path was already correct and is unchanged.

[1.4.4]: https://github.com/RGBTCZ/BTCZ-Tools/releases/tag/v1.4.4

## [1.4.3] - 2026-09-13

Fixes immature balance on Miningcore pools.

### Fixed
- **Immature balance now shows on Miningcore pools** (HimPool, HimPool solo). Miningcore only credits a miner's `pendingBalance` once blocks mature, so freshly-found blocks awaiting confirmations were reported as 0. The live pool-stats panel now reads the pool's block list and sums the reward of every `pending` block found by your address, so the IMMATURE field reflects the blocks actually waiting on confirmations. If the block list can't be fetched, it falls back to 0 without affecting the rest of the stats.

[1.4.3]: https://github.com/RGBTCZ/BTCZ-Tools/releases/tag/v1.4.3

## [1.4.2] - 2026-08-29

A global EUR / USD currency switch.

### Added
- **€ / $ toggle** in the sidebar — flip the whole app between euros and dollars in one click. It carries through the Dashboard market and profitability summary, the Profitability calculator (price, revenue, costs, break-even, scenarios, and the input labels), the Holder cockpit (stack value, moonshot, ATH, milestones) and its shareable card, the Mining Assistant, and the price alert (target + current price). The choice is remembered.

### Changed
- Market value now uses CoinGecko's native EUR and USD figures (including USD market cap), so no home-made conversion is involved.

### Notes
- Currency-agnostic inputs you type yourself (electricity and hardware cost) keep their number when you switch — they're simply read in the selected currency, and their labels update to match.

[1.4.2]: https://github.com/RGBTCZ/BTCZ-Tools/releases/tag/v1.4.2

## [1.4.1] - 2026-08-29

UX polish for the notifications center.

### Added
- **Delete alerts** — each entry in the history has a ✕ to remove it, plus a **Clear all** button.

### Changed
- **Clearer price target field** — a helper line explains what to type ("the price in € at which BTCZ triggers the alert"), the input shows an example placeholder, and a live **current price** reference is displayed right under it so you know the scale.

[1.4.1]: https://github.com/RGBTCZ/BTCZ-Tools/releases/tag/v1.4.1

## [1.4.0] - 2026-08-29

Turns BTCZ Tools into an always-on companion with a system tray and desktop alerts.

### Added
- **🔔 Notifications center** — a dedicated tab to enable and tune four desktop alerts, with a live history of what fired and a "send a test notification" button.
- **Background monitor** — a lightweight watcher that runs on its own thread and fires a desktop toast on the right transition (never repeating): a **price target** reached (rising / falling / any), a **payment received** on a tracked Mining Tracker address, a **rig going offline** (a pool worker's hashrate dropping to 0, with a "back online" notice), and a **difficulty jump** past a threshold you set. The check interval is configurable.
- **System tray** — the app now lives in the tray (pystray): closing the window minimizes it there and keeps monitoring, with a one-time heads-up the first time. Right-click → Show / Quit. The tray icon also carries the toast notifications.

### Notes
- The tray and native toasts use the Windows tray backend in the packaged `.exe`; where no system tray is available, alerts still appear in the in-app history while the app is open.

[1.4.0]: https://github.com/RGBTCZ/BTCZ-Tools/releases/tag/v1.4.0

## [1.3.0] - 2026-08-29

Adds a premium Halving countdown tab.

### Added
- **⏳ Halving** — a dedicated countdown to the next BitcoinZ halving: a live days / hours / minutes / seconds counter, the estimated date, a progress bar through the current era, and the block-reward transition (current reward → reward after the halving, with the miner share on each side). Everything is derived on-chain from the block height and the emission schedule (halving every 840 000 blocks), so it needs no extra data source and always matches the network.

[1.3.0]: https://github.com/RGBTCZ/BTCZ-Tools/releases/tag/v1.3.0

## [1.2.0] - 2026-08-29

Adds a cockpit for holders, a shareable flex card, and a built-in auto-updater.

### Added
- **🐳 Holder** — a cockpit for one or more t1 addresses: total stack with live € value, a sea-creature rank (🦐 Shrimp → 🦀 Crab → 🐟 Fish → 🐬 Dolphin → 🦈 Shark → 🐳 Whale) with a progress bar to the next tier, a moonshot price simulator (slider over target prices, with the ATH line), wealth milestones (the BTCZ price needed to reach 1k / 10k / 100k / 1M €), and your share of the circulating supply. Addresses are managed with an editable dropdown (add / remove), like the Mining Tracker.
- **Shareable card** — export a premium PNG of your holder status in two formats at once (1080×1080 square and 1200×630 landscape), with an optional **Hide amounts** switch that shows only your rank and supply share.
- **Auto-update** — on launch the app checks the GitHub Releases API for a newer version and, if one exists, opens a dialog that explains the process and downloads the new `.exe` into a folder you choose. Silent when you're already up to date.

### Changed
- **Circulating supply** is now computed on-chain from the block height and the emission schedule instead of CoinGecko, so it always matches the explorer (and needs no extra request).
- The sidebar now lays out its rows dynamically, so adding modules never overlaps the language selector.

[1.2.0]: https://github.com/RGBTCZ/BTCZ-Tools/releases/tag/v1.2.0

## [1.1.1] - 2026-08-28

First Windows binary: a standalone `BTCZ-Tools.exe` you can download and run without Python.

### Added
- **Standalone Windows executable** — build a single `BTCZ-Tools.exe` with PyInstaller (`btcz_tools.spec`, `build_exe.bat` / `build_exe.sh`, `BUILD.md`).
- `make_icon.py` to generate a sharp multi-size (16→256 px) application icon from the logo.

### Fixed
- Frozen-aware data paths: when packaged, the app stores its `data/` folder next to the executable, so addresses, settings, logo, logs and history persist between runs.
- Logging no longer fails in windowed (no-console) mode.
- Window/app icon now includes 128 px and 256 px sizes for a crisp look on Windows 10/11.

[1.1.1]: https://github.com/RGBTCZ/BTCZ-Tools/releases/tag/v1.1.1

## [1.1.0] - 2026-08-28

Completes the roadmap with the Mining Assistant, plus a responsive-UI fix.

### Added
- **🚀 Mining Assistant** — rule-based analysis of your setup: estimated monthly profit (or loss), break-even BTCZ price and how far the price must move to reach it, how much of your revenue electricity eats, a recommendation to switch to the cheapest active pool (with the daily BTCZ gain), your share of the network, and hardware ROI. Honest by design — no invented "average miner" baseline; every insight is a value that can actually be computed.

### Fixed
- Stat cards are now responsive: long titles (e.g. "Electricity (EUR/kWh)", "Hardware cost") wrap to the card width instead of being clipped, on every screen.

[1.1.0]: https://github.com/RGBTCZ/BTCZ-Tools/releases/tag/v1.1.0

## [1.0.0] - 2026-08-28

First complete release. BTCZ Tools grows from a single Mining Tracker into a modular
desktop suite for BitcoinZ miners, built on a shared data layer with automatic failover.

### Added

**Architecture**
- Modular structure: `app/` (core, api, ui, models, utils), `modules/`, `config/`, `data/`.
- BTCZ Data Layer with a TTL cache and automatic failover between explorers.
- Full internationalization: English (default), French, Spanish, German — live switching, remembered in `data/settings.json`.
- BTCZ logo downloaded once and cached; window icon + sidebar branding.
- Sidebar navigation across all modules.

**Modules**
- **📊 Dashboard** — home screen: network, your mining (today / 7 days / 30 days), profitability summary, market, and quick access to every module.
- **⛏️ Mining Tracker** — rewards received on a transparent (t1) address per day or date range, summary cards, CSV export, address history, calendar picker; plus a live pool-side stats panel (balance, paid, hashrate, workers) for any t1 address.
- **💰 Profitability** — revenue, electricity, pool fee, profit per day; price scenarios; break-even BTCZ price; hardware ROI. Inputs remembered.
- **🌊 Pool Explorer** — on-chain pool distribution via block `minedBy`, live pool stats, expected earnings for your hashrate, and a known-pools directory (fee, payout, min pay, status).
- **🌐 Network Explorer** — network stats and latest blocks with miner attribution.
- **📈 History** — monthly mining history, this/last month comparison, projection (1/3/6/12 months), and snapshot-based alerts (difficulty change, new rewards).

**Live pool APIs (3 formats supported)**
- z-nomp (`/api/stats`, `/api/worker_stats`) — SW Groupe, Dark Fiber Mines.
- zpool/yiimp (`/api/currencies`) — zpool.ca.
- Miningcore (`/api/pools/{id}`, `/api/pools/{id}/miners/{address}`) — HimPool, HimPool (solo).

**Data sources**
- `explorer.btcz.rocks` (Insight) for network, blocks and miner attribution.
- `explorer.getbtcz.com` for address transactions, with btcz.rocks fallback.
- CoinGecko for BTCZ price (EUR + USD).

### Fixed
- Corrected the BitcoinZ hashrate model: BTCZ is Equihash 144,5 (Sol/s); difficulty → hashrate uses the `2^13` constant, not `2^32`. The network hashrate now matches the node value.
- Address transactions on btcz.rocks now use the correct endpoint `/api/txs?address=` with `limit`/`offset` (was `/addr/{addr}/txs` with `from`/`to`).
- Price cards no longer clip the currency label.
- `run_btcz.sh` creates the virtualenv and installs dependencies on first launch, and rejects the Windows Microsoft Store Python stub.

[1.0.0]: https://github.com/RGBTCZ/BTCZ-Tools/releases/tag/v1.0.0
