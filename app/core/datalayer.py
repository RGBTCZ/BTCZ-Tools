import threading

from app.api.getbtcz_client import GetbtczClient
from app.api.insight_client import InsightClient
from app.api.market_client import MarketClient
from app.api.miningcore_client import MiningcoreClient
from app.api.nomp_client import NompClient
from app.api.zpool_client import ZpoolClient
from app.core.cache import TTLCache
from app.core.errors import DataError, NetworkError
from app.core.i18n import t
from app.core.logger import get_logger
from app.models.models import AddressStats, Block, NetworkStats, PoolLive, PoolStat, PoolWorker, Transaction
from app.utils.format import block_reward, compute_nethash, miner_reward
from config.config import (
    BLOCK_TIME_TARGET,
    CACHE_TTL,
    GETBTCZ_BASE,
    INSIGHT_PRIMARY,
    LIMIT_FULL,
    LIMIT_RECENT,
    MINING_THRESHOLD,
    POOL_WINDOW,
    POOLS,
)

log = get_logger("datalayer")


class BTCZDataLayer:
    def __init__(self):
        self.insight = InsightClient(INSIGHT_PRIMARY)
        self.getbtcz = GetbtczClient(GETBTCZ_BASE)
        self.market = MarketClient()
        self.nomp = NompClient()
        self.zpool = ZpoolClient()
        self.miningcore = MiningcoreClient()
        self.cache = TTLCache()
        self._locks = {}
        self._locks_guard = threading.Lock()

    def _key_lock(self, key):
        with self._locks_guard:
            lock = self._locks.get(key)
            if lock is None:
                lock = threading.Lock()
                self._locks[key] = lock
            return lock

    def _cached(self, key, ttl, fetch_fn):
        cached = self.cache.get(key)
        if cached is not None:
            return cached
        with self._key_lock(key):
            cached = self.cache.get(key)
            if cached is not None:
                return cached
            value = fetch_fn()
            self.cache.set(key, value, ttl)
            return value

    def get_network_stats(self):
        def fetch():
            info = self.insight.get_info()
            height = int(info.get("blocks", 0) or 0)
            difficulty = float(info.get("difficulty", 0) or 0)
            return NetworkStats(
                height=height,
                difficulty=difficulty,
                reported_hashps=float(info.get("networkhashps", 0) or 0),
                computed_hashps=compute_nethash(difficulty, BLOCK_TIME_TARGET),
                block_time=BLOCK_TIME_TARGET,
                block_reward=block_reward(height),
                miner_reward=miner_reward(height),
                connections=int(info.get("connections", 0) or 0),
                source="btcz.rocks",
            )

        return self._cached("network", CACHE_TTL["network"], fetch)

    def get_latest_blocks(self, limit=10):
        def fetch():
            blocks = []
            try:
                raw = self.insight.get_blocks(limit)
                for item in raw:
                    height = int(item.get("height", 0) or 0)
                    blocks.append(
                        Block(
                            height=height,
                            hash=item.get("hash", ""),
                            time=int(item.get("time", 0) or 0),
                            size=int(item.get("size", 0) or 0),
                            tx_count=int(item.get("txlength", 0) or 0),
                            mined_by=item.get("minedBy", ""),
                            reward=block_reward(height),
                            source="btcz.rocks",
                        )
                    )
            except (NetworkError, DataError) as exc:
                log.warning("Insight blocks failed, fallback getbtcz: %s", exc)
                raw = self.getbtcz.get_blocks(limit)
                for item in raw:
                    height = int(item.get("height", 0) or 0)
                    blocks.append(
                        Block(
                            height=height,
                            hash=item.get("hash", ""),
                            time=int(item.get("time", 0) or 0),
                            size=int(item.get("size", 0) or 0),
                            tx_count=len(item.get("tx", []) or []),
                            difficulty=float(item.get("difficulty", 0) or 0),
                            reward=block_reward(height),
                            source="getbtcz.com",
                        )
                    )
            return blocks

        return self._cached(f"blocks:{limit}", CACHE_TTL["blocks"], fetch)

    def get_block(self, block_hash):
        key = f"block:{block_hash}"
        cached = self.cache.get(key)
        if cached:
            return cached
        data = self.insight.get_block(block_hash)
        height = int(data.get("height", 0) or 0)
        block = Block(
            height=height,
            hash=data.get("hash", ""),
            time=int(data.get("time", 0) or 0),
            size=int(data.get("size", 0) or 0),
            tx_count=len(data.get("tx", []) or []),
            difficulty=float(data.get("difficulty", 0) or 0),
            reward=block_reward(height),
            source="btcz.rocks",
        )
        self.cache.set(key, block, CACHE_TTL["block"])
        return block

    def get_address(self, address):
        key = f"address:{address}"
        cached = self.cache.get(key)
        if cached:
            return cached
        try:
            data = self.getbtcz.get_address(address)
            stats = AddressStats(
                address=address,
                balance=float(data.get("balance", 0) or 0),
                total_received=float(data.get("totalReceived", 0) or 0),
                total_sent=float(data.get("totalSent", 0) or 0),
                tx_count=int(data.get("txCount", 0) or 0),
                source="getbtcz.com",
            )
        except (NetworkError, DataError) as exc:
            log.warning("getbtcz address failed, fallback insight: %s", exc)
            data = self.insight.get_addr(address)
            stats = AddressStats(
                address=address,
                balance=float(data.get("balance", 0) or 0),
                total_received=float(data.get("totalReceived", 0) or 0),
                total_sent=float(data.get("totalSent", 0) or 0),
                tx_count=int(data.get("txApperances", 0) or 0),
                source="btcz.rocks",
            )
        self.cache.set(key, stats, CACHE_TTL["address"])
        return stats

    def get_address_transactions(self, address, single_day, log_fn=None):
        key = f"address_txs:{address}:{single_day}"
        cached = self.cache.get(key)
        if cached:
            return cached
        try:
            txs = self._getbtcz_txs(address, single_day, log_fn)
        except (NetworkError, DataError) as exc:
            if log_fn:
                log_fn(t("dl.fallback", e=exc), "warn")
            log.warning("getbtcz txs failed, fallback insight: %s", exc)
            txs = self._insight_txs(address, log_fn)
        self.cache.set(key, txs, CACHE_TTL["address_txs"])
        return txs

    def _getbtcz_txs(self, address, single_day, log_fn):
        result = []
        if single_day:
            if log_fn:
                log_fn(t("dl.fast"))
            raw = self.getbtcz.get_address_txs(address, limit=LIMIT_RECENT, offset=0)
            if log_fn:
                log_fn(t("dl.loaded", n=len(raw)) + "\n", "ok")
            return self._normalize_getbtcz(raw)

        if log_fn:
            log_fn(t("dl.full"))
        offset = 0
        while True:
            raw = self.getbtcz.get_address_txs(address, limit=LIMIT_FULL, offset=offset)
            result.extend(raw)
            if log_fn:
                log_fn(t("dl.progress", n=len(result)))
            if len(raw) < LIMIT_FULL:
                break
            offset += LIMIT_FULL
        if log_fn:
            log_fn(t("dl.total", n=len(result)) + "\n", "ok")
        return self._normalize_getbtcz(result)

    def _normalize_getbtcz(self, raw):
        out = []
        for tx in raw:
            value = float(tx.get("value", 0) or 0)
            out.append(
                Transaction(
                    txid=tx.get("txid", ""),
                    time=int(tx.get("time", 0) or 0),
                    value=value,
                    is_mining=value > MINING_THRESHOLD,
                )
            )
        return out

    def _insight_txs(self, address, log_fn):
        out = []
        offset = 0
        page = 50
        while True:
            data = self.insight.get_addr_txs(address, limit=page, offset=offset)
            items = data.get("txs", [])
            for tx in items:
                value = self._net_value(tx, address)
                if value <= 0:
                    continue
                out.append(
                    Transaction(
                        txid=tx.get("txid", ""),
                        time=int(tx.get("time", 0) or 0),
                        value=value,
                        is_mining=value > MINING_THRESHOLD,
                    )
                )
            if log_fn:
                log_fn(t("dl.progress", n=len(out)))
            if len(items) < page:
                break
            offset += page
        if log_fn:
            log_fn(t("dl.total", n=len(out)) + "\n", "ok")
        return out

    def _net_value(self, tx, address):
        received = 0.0
        for vout in tx.get("vout", []):
            spk = vout.get("scriptPubKey", {}) or {}
            if address in (spk.get("addresses", []) or []):
                received += float(vout.get("value", 0) or 0)
        sent = 0.0
        for vin in tx.get("vin", []):
            if vin.get("addr") == address:
                sent += float(vin.get("value", 0) or 0)
        return received - sent

    def _match_pool(self, tag):
        low = tag.lower()
        for pool in POOLS:
            for alias in pool.get("tags", []):
                if alias == low or alias in low:
                    return pool
        return None

    def get_pool_stats(self, window=POOL_WINDOW):
        return self._cached(f"pools:{window}", CACHE_TTL["pools"], lambda: self._fetch_pool_stats(window))

    def _fetch_pool_stats(self, window):
        net = self.get_network_stats()
        raw = self.insight.get_blocks(window)
        total = len(raw) or 1

        named = {}
        solo = {"blocks": 0, "last": 0, "addrs": set()}
        for block in raw:
            mined_by = (block.get("minedBy") or "").strip()
            btime = int(block.get("time", 0) or 0)
            if not mined_by:
                continue
            if mined_by.startswith("t1") or mined_by.startswith("t3"):
                solo["blocks"] += 1
                solo["addrs"].add(mined_by)
                solo["last"] = max(solo["last"], btime)
            else:
                entry = named.setdefault(mined_by, {"blocks": 0, "last": 0})
                entry["blocks"] += 1
                entry["last"] = max(entry["last"], btime)

        network_hashps = net.network_hashps()
        stats = []
        for name, entry in named.items():
            share = entry["blocks"] / total
            pool = self._match_pool(name)
            stats.append(
                PoolStat(
                    name=pool["name"] if pool else name,
                    blocks_found=entry["blocks"],
                    share=share,
                    est_hashps=share * network_hashps,
                    last_time=entry["last"],
                    fee=pool["fee"] if pool else None,
                    scheme=pool["scheme"] if pool else "",
                    url=pool["url"] if pool else "",
                    matched=pool is not None,
                )
            )

        if solo["blocks"] > 0:
            share = solo["blocks"] / total
            stats.append(
                PoolStat(
                    name="Solo miners",
                    blocks_found=solo["blocks"],
                    share=share,
                    est_hashps=share * network_hashps,
                    last_time=solo["last"],
                    miners=len(solo["addrs"]),
                    is_solo=True,
                )
            )

        stats.sort(key=lambda s: s.blocks_found, reverse=True)
        return {"window": total, "network_hashps": network_hashps, "pools": stats}

    def get_pool_live(self):
        def fetch():
            result = {}
            for pool in POOLS:
                name = pool["name"]
                try:
                    if pool.get("api_base"):
                        result[name] = self.nomp.get_btcz(pool["api_base"], name)
                    elif pool.get("api_currencies"):
                        result[name] = self.zpool.get_btcz(pool["api_currencies"], name)
                    elif pool.get("api_miningcore"):
                        result[name] = self.miningcore.get_btcz(pool["api_miningcore"], name)
                except (NetworkError, DataError) as exc:
                    log.warning("pool live %s failed: %s", name, exc)
                    result[name] = PoolLive(name=name, ok=False)
            return result

        return self._cached("pool_live", CACHE_TTL["pools"], fetch)

    def get_worker_stats(self, pool_name, address):
        target = None
        for pool in POOLS:
            if pool["name"] == pool_name:
                target = pool
                break
        if not target:
            return None
        key = f"worker:{pool_name}:{address}"
        cached = self.cache.get(key)
        if cached:
            return cached
        try:
            if target.get("api_base"):
                worker = self.nomp.get_worker(target["api_base"], address)
            elif target.get("api_miningcore"):
                worker = self.miningcore.get_miner(target["api_miningcore"], address)
            else:
                return None
        except (NetworkError, DataError) as exc:
            log.warning("worker stats %s/%s failed: %s", pool_name, address, exc)
            return PoolWorker(miner=address, ok=False)
        self.cache.set(key, worker, CACHE_TTL["pools"])
        return worker

    def get_market(self):
        return self._cached("market", CACHE_TTL["market"], self.market.get_price)

    def get_coin_info(self):
        return self._cached("coin", CACHE_TTL["coin"], self.market.get_coin_info)
