# BTCZ Tools v1.5.0 🖥️

**Multiple rigs, and an Assistant that reads your real live hashrate.**

## ⬇️ Download

Grab **`BTCZ-Tools.exe`** from the Assets below, double-click, done.
Already on v1.2.0+? The app will offer this update for you the next time you launch it. 🚀

## 🔧 What's new

- 🖥️ **Multi-rig setup** — Profitability now lets you add **several rigs**, each with its own name, hashrate and power. Fill the fields, hit **➕ Add rig**, and they stack in a list with a remove button and a live **Total (Σ hashrate · Σ W)**. The calculation uses the totals — so if you run more than one machine, the electricity and profit are finally right. Your existing single setup is carried over automatically.
- 🚀 **Live Assistant** — the Mining Assistant no longer analyses a number you typed: it pulls your **real hashrate** from *My Live Pool Stats* (your remembered pool + address) and, when you're offline, falls back to the sum of your configured rigs. The setup shows whether the hashrate is **live** or **configured**, and the power is the sum of all your rigs.

Everything from v1.4.x (emission card, currency toggle, tray + alerts, badge…) is included.

## 🧑‍💻 Run from source

```bash
git clone https://github.com/RGBTCZ/BTCZ-Tools.git
cd BTCZ-Tools
./run_btcz.sh
```

Built for the BitcoinZ community. 💚

**Full changelog:** see [CHANGELOG.md](./CHANGELOG.md)
