# BTCZ Tools v1.2.0 🐳

**A cockpit for holders, a shareable flex card, and a built-in auto-updater.**

## ⬇️ Download

Grab **`BTCZ-Tools.exe`** from the Assets below, double-click, done. No Python, no setup.
From now on, the app tells you when a newer version is out and can download it for you.

> First launch needs an internet connection to download the BTCZ logo and fetch live data.
> Windows SmartScreen may warn on an unsigned app — click "More info" → "Run anyway".

## 🔧 What's new

- 🐳 **Holder cockpit** — track one or more t1 addresses: your total stack with live € value, a sea-creature rank (🦐 → 🦀 → 🐟 → 🐬 → 🦈 → 🐳) with progress to the next tier, a **moonshot simulator**, wealth milestones (price needed to hit 1k / 10k / 100k / 1M €), and your share of the circulating supply.
- 🖼️ **Shareable card** — export a premium PNG of your holder status in **two formats at once** (1080×1080 for Instagram/mobile, 1200×630 for X/Discord/Telegram), with an optional **Hide amounts** mode to flex your rank without revealing your stack.
- 🚀 **Auto-update** — on launch the app checks GitHub for a newer release and, if one exists, offers to download the new `.exe`. It explains every step first, and stays completely silent when you're already up to date.

## 🧮 Under the hood

- **Circulating supply is now computed on-chain** from the block height (halving every 840 000 blocks), so it always matches the explorer — no more lag from third-party numbers.
- Sidebar layout is dynamic, so future modules never collide with the language selector.

Everything from v1.1.1 (8 modules, live pool stats, standalone Windows build, 4 languages) is included — the Holder tab makes it 9 modules.

## 🧑‍💻 Run from source

```bash
git clone https://github.com/RGBTCZ/BTCZ-Tools.git
cd BTCZ-Tools
./run_btcz.sh
```

Built for the BitcoinZ community. 💚

**Full changelog:** see [CHANGELOG.md](./CHANGELOG.md)
