# Changelog

All notable changes to BTCZ Tools are documented here.
This project adheres to [Semantic Versioning](https://semver.org/).

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
