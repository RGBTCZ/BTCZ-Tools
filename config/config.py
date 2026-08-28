INSIGHT_PRIMARY = "https://explorer.btcz.rocks/api"
GETBTCZ_BASE = "https://explorer.getbtcz.com/api"

COINGECKO_PRICE = "https://api.coingecko.com/api/v3/simple/price"
COINGECKO_ID = "bitcoinz"

LOGO_URLS = [
    "https://cryptologos.cc/logos/bitcoinz-btcz-logo.png",
    "https://icons.iconarchive.com/icons/cjdowner/cryptocurrency-flat/256/BitcoinZ-BTCZ-icon.png",
]

HTTP_TIMEOUT = 15

CACHE_TTL = {
    "network": 30,
    "blocks": 15,
    "block": 60,
    "market": 60,
    "address": 30,
    "address_txs": 45,
    "pools": 60,
}

HALVING_INTERVAL = 840000
INITIAL_REWARD = 12500
BLOCK_TIME_TARGET = 150
MINER_REWARD_RATIO = 0.8

MINING_THRESHOLD = 20
LIMIT_RECENT = 200
LIMIT_FULL = 100

POOL_WINDOW = 100
NOMP_HASH_DIVISOR = 500000

POOLS = [
    {"name": "zpool.ca", "url": "https://zpool.ca", "api_currencies": "https://www.zpool.ca/api/currencies", "fee": 1.0, "scheme": "PROP", "min_pay": 10, "active": True, "tags": ["zpool"]},
    {"name": "SW Groupe", "url": "https://swgroupe.fr", "api_base": "https://swgroupe.fr/api", "fee": 0.5, "scheme": "PPLNS", "min_pay": None, "active": True, "tags": ["swgroupe", "swgroup"]},
    {"name": "Dark Fiber Mines", "url": "https://btcz.darkfibermines.com", "api_base": "https://btcz.darkfibermines.com/api", "fee": 1.0, "scheme": "PROP / SOLO", "min_pay": None, "active": True, "tags": ["darkfiber", "dfm"]},
    {"name": "HimPool", "url": "https://himpool.com", "api_miningcore": "https://himpool.com/api/pools/bitcoinz", "fee": 1.0, "scheme": "PPLNS", "min_pay": 250, "active": False, "tags": ["himpool"]},
    {"name": "HimPool (solo)", "url": "https://himpool.com", "api_miningcore": "https://himpool.com/api/pools/bitcoinz-solo", "fee": 2.0, "scheme": "SOLO", "min_pay": 250, "active": False, "tags": ["himpool-solo"]},
    {"name": "Pooly", "url": "https://pooly.ca", "fee": 1.5, "scheme": "PPLNS", "min_pay": 1, "active": False, "tags": ["pooly"]},
    {"name": "AikaPool", "url": "https://aikapool.com", "fee": 0.5, "scheme": "PROP / SOLO", "min_pay": 0.01, "active": False, "tags": ["aikapool"]},
    {"name": "ZeroPool", "url": "https://zeropool.io", "fee": 2.0, "scheme": "PPLNT / SOLO", "min_pay": None, "active": False, "tags": ["zeropool"]},
]

APP_NAME = "BTCZ Tools"
APP_VERSION = "1.1.0"
