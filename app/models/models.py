from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class NetworkStats:
    height: int = 0
    difficulty: float = 0.0
    reported_hashps: float = 0.0
    computed_hashps: float = 0.0
    block_time: int = 0
    block_reward: float = 0.0
    miner_reward: float = 0.0
    connections: int = 0
    source: str = ""

    def network_hashps(self):
        return self.reported_hashps if self.reported_hashps > 0 else self.computed_hashps


@dataclass
class Block:
    height: int = 0
    hash: str = ""
    time: int = 0
    size: int = 0
    tx_count: int = 0
    mined_by: str = ""
    difficulty: float = 0.0
    reward: float = 0.0
    source: str = ""


@dataclass
class Transaction:
    txid: str = ""
    time: int = 0
    value: float = 0.0
    is_mining: bool = False


@dataclass
class AddressStats:
    address: str = ""
    balance: float = 0.0
    total_received: float = 0.0
    total_sent: float = 0.0
    tx_count: int = 0
    source: str = ""


@dataclass
class MarketData:
    price_eur: float = 0.0
    price_usd: float = 0.0
    change_24h: float = 0.0
    market_cap_eur: float = 0.0
    volume_24h_eur: float = 0.0
    source: str = "coingecko"


@dataclass
class PoolStat:
    name: str = ""
    blocks_found: int = 0
    share: float = 0.0
    est_hashps: float = 0.0
    last_time: int = 0
    miners: int = 1
    is_solo: bool = False
    fee: Optional[float] = None
    scheme: str = ""
    url: str = ""
    matched: bool = False


@dataclass
class PoolLive:
    name: str = ""
    hashps: float = 0.0
    miner_count: int = 0
    worker_count: int = 0
    blocks_confirmed: int = 0
    blocks_pending: int = 0
    fee: Optional[float] = None
    ok: bool = False


@dataclass
class PoolWorker:
    miner: str = ""
    hashps: float = 0.0
    total_hash: float = 0.0
    total_shares: float = 0.0
    network_sols: float = 0.0
    immature: float = 0.0
    balance: float = 0.0
    paid: float = 0.0
    workers: int = 0
    ok: bool = False


@dataclass
class DailyResult:
    date: str = ""
    total: float = 0.0
    mining_count: int = 0


@dataclass
class AnalysisResult:
    address: str = ""
    start: str = ""
    end: str = ""
    days: List[DailyResult] = field(default_factory=list)
    total_period: float = 0.0
    mining_total: int = 0
    biggest_reward: float = 0.0
