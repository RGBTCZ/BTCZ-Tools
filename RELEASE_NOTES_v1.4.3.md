# BTCZ Tools v1.4.3 🧱

**Fix: immature balance now shows on Miningcore pools.**

## ⬇️ Download

Grab **`BTCZ-Tools.exe`** from the Assets below, double-click, done.
Already on v1.2.0+? The app will offer this update for you the next time you launch it. 🚀

## 🔧 What's fixed

- 🧱 **IMMATURE now works on Miningcore pools** (HimPool, HimPool solo). Miningcore only credits your `pendingBalance` once blocks mature, so blocks you just found — still waiting on confirmations — showed up as `0`. The live pool-stats panel now reads the pool's block list and adds up the reward of every **pending** block found by your address, so IMMATURE finally reflects the blocks actually confirming.

Example: 5 solo blocks awaiting confirmations now correctly show **12,500 BTCZ** immature instead of `0`.

Everything from v1.4.2 (the € / $ toggle, tray + alerts, Holder, Halving) is included.

## 🧑‍💻 Run from source

```bash
git clone https://github.com/RGBTCZ/BTCZ-Tools.git
cd BTCZ-Tools
./run_btcz.sh
```

Built for the BitcoinZ community. 💚

**Full changelog:** see [CHANGELOG.md](./CHANGELOG.md)
