from app.core.errors import http_get_json


class InsightClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")

    def get_info(self):
        data = http_get_json(f"{self.base_url}/status", params={"q": "getInfo"})
        return data.get("info", {})

    def get_blocks(self, limit=10):
        data = http_get_json(f"{self.base_url}/blocks", params={"limit": limit})
        return data.get("blocks", [])

    def get_block(self, block_hash):
        return http_get_json(f"{self.base_url}/block/{block_hash}")

    def get_block_index(self, height):
        return http_get_json(f"{self.base_url}/block-index/{height}")

    def get_addr(self, address):
        return http_get_json(f"{self.base_url}/addr/{address}", params={"noTxList": 1})

    def get_addr_txs(self, address, limit=50, offset=0):
        return http_get_json(
            f"{self.base_url}/txs",
            params={"address": address, "limit": limit, "offset": offset},
        )

    def get_tx(self, txid):
        return http_get_json(f"{self.base_url}/tx/{txid}")