# BTCZ Tools v1.1.0 🚀

This release completes the roadmap: **BTCZ Tools now advises, not just reports.**

## ✨ New: Mining Assistant

A new **🚀 Assistant** module reads your setup and turns your numbers into plain,
actionable advice. Examples on a real (unprofitable) setup:

> ⚠️ You're mining at a loss: −3.03 €/day
> ⚠️ Electricity alone exceeds your revenue by 103x
> 🎯 Break-even BTCZ price: 0.0000125 € (current: 0.00000012 €)
> 🎯 BTCZ must rise ~104x to break even
> 💡 Switching to SW Groupe (0.50% fee) would add ~1236 BTCZ/day
> 💡 Your hashrate is 17.17% of the network

On a profitable setup it switches to estimated monthly profit, "you're already on the
lowest-fee active pool", and hardware ROI in X days.

**Honest by design:** no invented "average miner" baseline — every insight is a real,
computed value.

## 🔧 Fixed

- Stat cards are now responsive: long titles wrap to the card width instead of being clipped.

## 🌍 Still fully multilingual

English, Français, Español, Deutsch.

## 🚀 Upgrade

```bash
git pull
./run_btcz.sh
```

The roadmap (Phase 0 → 7) is now complete. Thank you to the BitcoinZ community — and to
the pool operators (SW Groupe, Dark Fiber Mines, HimPool) who shared their APIs. 💚

**Full changelog:** see [CHANGELOG.md](./CHANGELOG.md)
