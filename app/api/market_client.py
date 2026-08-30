from app.core.errors import http_get_json
from app.models.models import CoinInfo, MarketData
from config.config import COINGECKO_COIN, COINGECKO_ID, COINGECKO_PRICE


class MarketClient:
    def get_price(self):
        data = http_get_json(
            COINGECKO_PRICE,
            params={
                "ids": COINGECKO_ID,
                "vs_currencies": "eur,usd",
                "include_24hr_change": "true",
                "include_market_cap": "true",
                "include_24hr_vol": "true",
            },
        )
        coin = data.get(COINGECKO_ID, {})
        return MarketData(
            price_eur=float(coin.get("eur", 0) or 0),
            price_usd=float(coin.get("usd", 0) or 0),
            change_24h=float(coin.get("eur_24h_change", 0) or 0),
            market_cap_eur=float(coin.get("eur_market_cap", 0) or 0),
            market_cap_usd=float(coin.get("usd_market_cap", 0) or 0),
            volume_24h_eur=float(coin.get("eur_24h_vol", 0) or 0),
        )

    def get_coin_info(self):
        data = http_get_json(
            COINGECKO_COIN,
            params={
                "localization": "false",
                "tickers": "false",
                "market_data": "true",
                "community_data": "false",
                "developer_data": "false",
            },
        )
        md = data.get("market_data", {}) or {}

        def pick(field, cur):
            return float((md.get(field) or {}).get(cur, 0) or 0)

        return CoinInfo(
            price_eur=pick("current_price", "eur"),
            price_usd=pick("current_price", "usd"),
            change_24h=float(md.get("price_change_percentage_24h", 0) or 0),
            ath_eur=pick("ath", "eur"),
            ath_usd=pick("ath", "usd"),
            circulating_supply=float(md.get("circulating_supply", 0) or 0),
            market_cap_eur=pick("market_cap", "eur"),
        )
