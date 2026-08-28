from app.core.errors import http_get_json
from app.models.models import PoolLive


class MiningcoreClient:
    def get_btcz(self, pool_url, name, timeout=8):
        data = http_get_json(pool_url, timeout=timeout)
        pool = data.get("pool") or {}
        if not pool:
            return PoolLive(name=name, ok=False)
        stats = pool.get("poolStats", {}) or {}
        miners = int(stats.get("connectedMiners", 0) or 0)
        confirmed = pool.get("totalConfirmedBlocks")
        if confirmed is None:
            confirmed = pool.get("totalBlocks", 0)
        return PoolLive(
            name=name,
            hashps=float(stats.get("poolHashrate", 0) or 0),
            miner_count=miners,
            worker_count=miners,
            blocks_confirmed=int(confirmed or 0),
            fee=float(pool.get("poolFeePercent", 0) or 0),
            ok=True,
        )
