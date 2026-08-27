from datetime import datetime, timezone

from config.config import HALVING_INTERVAL, INITIAL_REWARD, MINER_REWARD_RATIO


def block_reward(height):
    halvings = height // HALVING_INTERVAL
    return INITIAL_REWARD / (2 ** halvings)


def miner_reward(height):
    return block_reward(height) * MINER_REWARD_RATIO


def compute_nethash(difficulty, block_time):
    if block_time <= 0:
        return 0.0
    return difficulty * (2 ** 32) / block_time


def format_btcz(value, decimals=8):
    return f"{value:,.{decimals}f}"


def format_hashrate(hps):
    units = ["H/s", "KH/s", "MH/s", "GH/s", "TH/s", "PH/s"]
    value = float(hps)
    index = 0
    while value >= 1000 and index < len(units) - 1:
        value /= 1000
        index += 1
    return f"{value:.2f} {units[index]}"


def format_fiat(value, symbol="€", decimals=2):
    return f"{value:,.{decimals}f} {symbol}"


def human_age(ts):
    now = datetime.now(timezone.utc).timestamp()
    delta = int(now - ts)
    if delta < 60:
        return f"{delta} s"
    if delta < 3600:
        return f"{delta // 60} min"
    if delta < 86400:
        return f"{delta // 3600} h"
    return f"{delta // 86400} j"


def short_hash(value, size=12):
    if not value or len(value) <= size * 2:
        return value
    return f"{value[:size]}...{value[-size:]}"
