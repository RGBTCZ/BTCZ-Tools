from app.core.errors import http_get_json


class GetbtczClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")

    def get_address(self, address):
        return http_get_json(f"{self.base_url}/addresses/{address}")

    def get_address_txs(self, address, limit=200, offset=0):
        data = http_get_json(
            f"{self.base_url}/addresses/{address}/transactions",
            params={"limit": limit, "offset": offset},
        )
        return data.get("transactions", [])

    def get_blocks(self, limit=10):
        data = http_get_json(f"{self.base_url}/blocks", params={"limit": limit})
        return data.get("blocks", [])
