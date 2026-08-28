from app.core.errors import http_get_json
from app.models.models import PoolLive


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
