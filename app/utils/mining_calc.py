SECONDS_PER_DAY = 86400


def coins_per_day(hashrate_solps, network_solps, block_time, miner_reward):
    if network_solps <= 0 or block_time <= 0:
        return 0.0
    blocks_per_day = SECONDS_PER_DAY / block_time
    return (hashrate_solps / network_solps) * blocks_per_day * miner_reward


def electricity_cost_day(power_w, elec_price):
    return (power_w / 1000.0) * 24.0 * elec_price


def profitability(hashrate_solps, power_w, elec_price, pool_fee_pct, price,
                  network_solps, block_time, miner_reward):
    gross = coins_per_day(hashrate_solps, network_solps, block_time, miner_reward)
    revenue = gross * price
    fee = revenue * (pool_fee_pct / 100.0)
    electricity = electricity_cost_day(power_w, elec_price)
    profit = revenue - fee - electricity
    return {
        "coins": gross,
        "revenue": revenue,
        "fee": fee,
        "electricity": electricity,
        "profit": profit,
    }


def breakeven_price(gross_coins, power_w, elec_price, pool_fee_pct):
    electricity = electricity_cost_day(power_w, elec_price)
    denom = gross_coins * (1 - pool_fee_pct / 100.0)
    if denom <= 0:
        return 0.0
    return electricity / denom


def roi_days(hardware_cost, profit_per_day):
    if hardware_cost <= 0 or profit_per_day <= 0:
        return None
    return hardware_cost / profit_per_day


def price_scenarios(current_price, gross_coins, power_w, elec_price, pool_fee_pct, multipliers):
    electricity = electricity_cost_day(power_w, elec_price)
    out = []
    for mult in multipliers:
        price = current_price * mult
        revenue = gross_coins * price
        fee = revenue * (pool_fee_pct / 100.0)
        profit = revenue - fee - electricity
        out.append({"mult": mult, "price": price, "profit": profit})
    return out
