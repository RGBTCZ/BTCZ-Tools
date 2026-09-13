# BTCZ Tools v1.4.4 ⛏️

**A sharper live pool-stats panel: shared-pool immature, remembered rigs, auto-refresh.**

## ⬇️ Download

Grab **`BTCZ-Tools.exe`** from the Assets below, double-click, done.
Already on v1.2.0+? The app will offer this update for you the next time you launch it. 🚀

## 🔧 What's new

- 💾 **Your rig addresses are remembered** — the pool-stats address is now a dropdown that keeps the addresses you've used (and the last pool), so you don't retype them. A **Remove** button drops one.
- ⟳ **Auto-refresh every 60s** — a switch (on by default) keeps IMMATURE, BALANCE and PAID up to date while you watch, and the stats cache was shortened so each refresh is genuinely fresh.
- 🧱 **Immature now works on shared pools too** — on PPLNS / collective Miningcore pools, IMMATURE shows your **proportional share** of the pending blocks (your hashrate ÷ pool hashrate), marked **(est.)**. Solo pools stay exact.

Reminder: a confirmed-but-unpaid block sits in **BALANCE** until the pool's payout threshold is reached, then moves to **PAID** — that's Miningcore's normal flow.

Everything from v1.4.3 (solo immature fix) and earlier (€/$ toggle, tray + alerts, Holder, Halving) is included.

## 🧑‍💻 Run from source

```bash
git clone https://github.com/RGBTCZ/BTCZ-Tools.git
cd BTCZ-Tools
./run_btcz.sh
```

Built for the BitcoinZ community. 💚

**Full changelog:** see [CHANGELOG.md](./CHANGELOG.md)
