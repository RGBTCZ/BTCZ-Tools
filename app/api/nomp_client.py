from app.core.errors import http_get_json
from app.models.models import PoolLive
from app.utils.format import parse_hashrate_string


class NompClient:
    def get_btcz(self, api_base, name, timeout=6):
        data = http_get_json(f"{api_base.rstrip('/')}/stats", timeout=timeout)
        pools = data.get("pools", {}) or {}
        pool = pools.get("bitcoinz") or pools.get("BitcoinZ") or {}
        if not pool:
            return PoolLive(name=name, ok=False)
        blocks = pool.get("blocks", {}) or {}
        return PoolLive(
            name=name,
            hashps=parse_hashrate_string(pool.get("hashrateString", "")),
            miner_count=int(pool.get("minerCount", 0) or 0),
            worker_count=int(pool.get("workerCount", 0) or 0),
            blocks_confirmed=int(blocks.get("confirmed", 0) or 0),
            blocks_pending=int(blocks.get("pending", 0) or 0),
            fee=self._fee(pool.get("poolFees")),
            ok=True,
        )

    def _fee(self, raw):
        if raw is None:
            return None
        if isinstance(raw, dict):
            values = [float(v) for v in raw.values() if isinstance(v, (int, float))]
            return sum(values) if values else None
        try:
            return float(raw)
        except (TypeError, ValueError):
            return None
