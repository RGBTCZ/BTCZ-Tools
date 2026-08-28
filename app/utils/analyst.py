from app.utils.mining_calc import breakeven_price, coins_per_day, profitability


def analyze(hashrate_solps, power_w, elec_price, pool_fee, hardware,
            price, network_solps, block_time, miner_reward, best_pool):
    insights = []
    gross = coins_per_day(hashrate_solps, network_solps, block_time, miner_reward)
    prof = profitability(hashrate_solps, power_w, elec_price, pool_fee, price,
                         network_solps, block_time, miner_reward)
    revenue = prof["revenue"]
    electricity = prof["electricity"]
    profit = prof["profit"]

    if profit >= 0:
        insights.append(("ok", "assist.profit_ok", {"v": f"{profit * 30:.2f}"}))
    else:
        insights.append(("warn", "assist.profit_loss", {"v": f"{profit:.4f}"}))

    if revenue > 0:
        pct = electricity / revenue * 100
        if pct > 100:
            insights.append(("warn", "assist.elec_over", {"x": f"{electricity / revenue:.1f}"}))
        elif pct > 70:
            insights.append(("warn", "assist.elec_high", {"pct": f"{pct:.0f}"}))
        else:
            insights.append(("info", "assist.elec_ok", {"pct": f"{pct:.0f}"}))
    elif electricity > 0:
        insights.append(("warn", "assist.no_revenue", {}))

    be = breakeven_price(gross, power_w, elec_price, pool_fee)
    insights.append(("target", "assist.breakeven", {"be": f"{be:.10f}", "cur": f"{price:.10f}"}))
    if price > 0 and be > price:
        insights.append(("target", "assist.breakeven_mult", {"x": f"{be / price:.0f}"}))

    if best_pool and best_pool.get("fee") is not None and best_pool["fee"] < pool_fee:
        extra = gross * (pool_fee - best_pool["fee"]) / 100
        insights.append(("info", "assist.pool_switch",
                         {"pool": best_pool["name"], "fee": f"{best_pool['fee']:.2f}", "v": f"{extra:.2f}"}))
    elif best_pool:
        insights.append(("ok", "assist.pool_best", {"pool": best_pool["name"]}))

    if network_solps > 0:
        insights.append(("info", "assist.share", {"pct": f"{hashrate_solps / network_solps * 100:.2f}"}))

    if hardware > 0 and profit > 0:
        insights.append(("info", "assist.roi", {"d": f"{hardware / profit:.0f}"}))

    summary = {"gross": gross, "profit": profit, "revenue": revenue,
               "electricity": electricity, "breakeven": be}
    return insights, summary
