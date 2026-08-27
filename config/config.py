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

POOLS = [
    {"name": "zpool", "url": "https://zpool.ca", "fee": None, "scheme": "auto-exchange", "tags": ["zpool"]},
    {"name": "HimPool", "url": "https://himpool.com", "fee": None, "scheme": "", "tags": ["himpool"]},
    {"name": "SW Groupe", "url": "https://swgroupe.fr", "fee": None, "scheme": "", "tags": ["swgroupe", "swgroup"]},
    {"name": "2Mars", "url": "https://btcz.2mars.biz", "fee": None, "scheme": "", "tags": ["2mars"]},
    {"name": "Dark Fiber Mines", "url": "https://btcz.darkfibermines.com", "fee": None, "scheme": "", "tags": ["darkfiber", "dfm"]},
    {"name": "ZeroPool", "url": "https://zeropool.io", "fee": None, "scheme": "", "tags": ["zeropool"]},
    {"name": "PCMining", "url": "http://btcz.pcmining.xyz", "fee": None, "scheme": "", "tags": ["pcmining"]},
]

APP_NAME = "BTCZ Tools"
APP_VERSION = "0.1.0"
