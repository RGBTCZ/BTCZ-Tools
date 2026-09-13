from app.core.errors import http_get_json
from app.models.models import PoolLive, PoolWorker


class MiningcoreClient:
    def get_miner(self, pool_url, address, solo=True, timeout=8):
        base = pool_url.rstrip("/")
        data = http_get_json(f"{base}/miners/{address}", timeout=timeout)
        if not isinstance(data, dict):
            return PoolWorker(miner=address, ok=False)
        perf = data.get("performance") or {}
        worker_map = perf.get("workers", {}) or {}
        hashps = sum(float(w.get("hashrate", 0) or 0) for w in worker_map.values())
        immature, estimated = self._pending_immature(base, address, hashps, solo, timeout)
        return PoolWorker(
            miner=address,
            hashps=hashps,
            total_shares=float(data.get("pendingShares", 0) or 0),
            balance=float(data.get("pendingBalance", 0) or 0),
            immature=immature,
            immature_estimated=estimated,
            paid=float(data.get("totalPaid", 0) or 0),
            workers=len(worker_map),
            ok=True,
        )

    def _pending_blocks(self, base, timeout):
        try:
            data = http_get_json(f"{base}/blocks", params={"page": 0, "pageSize": 100}, timeout=timeout)
        except Exception:
            return None
        blocks = data.get("result") or data.get("blocks") if isinstance(data, dict) else data
        if not isinstance(blocks, list):
            return None
        return [b for b in blocks if isinstance(b, dict) and str(b.get("status", "")).lower() == "pending"]

    def _pool_hashrate(self, base, timeout):
        try:
            data = http_get_json(base, timeout=timeout)
        except Exception:
            return 0.0
        pool = (data or {}).get("pool") or {}
        stats = pool.get("poolStats", {}) or {}
        return float(stats.get("poolHashrate", 0) or 0)

    def _pending_immature(self, base, address, miner_hashps, solo, timeout=8):
        pending = self._pending_blocks(base, timeout)
        if not pending:
            return 0.0, False
        if solo:
            target = address.strip().lower()
            total = sum(float(b.get("reward", 0) or 0) for b in pending
                        if not b.get("miner") or str(b.get("miner")).strip().lower() == target)
            return total, False
        pending_total = sum(float(b.get("reward", 0) or 0) for b in pending)
        pool_hashps = self._pool_hashrate(base, timeout)
        if pool_hashps > 0 and miner_hashps > 0:
            return pending_total * (miner_hashps / pool_hashps), True
        return 0.0, True

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
