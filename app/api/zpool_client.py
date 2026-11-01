from app.core.errors import http_get_json
from app.models.models import PoolLive, PoolWorker


class ZpoolClient:
    def get_btcz(self, currencies_url, name, timeout=8):
        data = http_get_json(currencies_url, timeout=timeout)
        coin = data.get("BTCZ") or {}
        if not coin:
            return PoolLive(name=name, ok=False)
        workers = int(coin.get("workers", 0) or 0)
        return PoolLive(
            name=name,
            hashps=float(coin.get("hashrate", 0) or 0),
            miner_count=workers,
            worker_count=workers,
            blocks_confirmed=int(coin.get("24h_blocks", 0) or 0),
            fee=float(coin.get("fees", 0) or 0),
            ok=True,
        )

    def get_worker(self, wallet_url, address, timeout=8):
        data = http_get_json(wallet_url, params={"address": address}, timeout=timeout)
        if not isinstance(data, dict) or not data:
            return PoolWorker(miner=address, ok=False)
        raw_miners = data.get("miners") or []
        if not isinstance(raw_miners, list):
            raw_miners = []
        miners = [m for m in raw_miners if isinstance(m, dict)]
        equihash = [m for m in miners if "equihash144" in str(m.get("algo", "")).lower()]
        active = equihash or miners
        hashps = sum(float(m.get("accepted", 0) or 0) for m in active)
        return PoolWorker(
            miner=address,
            hashps=hashps,
            balance=float(data.get("balance", 0) or 0),
            immature=float(data.get("unsold", 0) or 0),
            paid=float(data.get("paidtotal", 0) or 0),
            workers=len(active),
            ok=True,
        )
