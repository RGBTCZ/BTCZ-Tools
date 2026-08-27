from app.core.errors import http_get_json
from app.models.models import MarketData
from config.config import COINGECKO_ID, COINGECKO_PRICE


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
            volume_24h_eur=float(coin.get("eur_24h_vol", 0) or 0),
        )
