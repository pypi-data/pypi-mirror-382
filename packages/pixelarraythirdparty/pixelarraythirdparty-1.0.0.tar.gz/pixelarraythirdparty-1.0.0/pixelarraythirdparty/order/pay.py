import requests


class WeChatPayManager:
    def __init__(self, api_key: str):
        self.base_url = "https://thirdparty.pixelarrayai.com"
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
        }

    def _request(self, method, url, **kwargs):
        resp = requests.request(
            method, f"{self.base_url}{url}", headers=self.headers, **kwargs
        )
        if resp.status_code == 200:
            return resp.json().get("data", {})
        return {}

    def generate_qr_code(
        self,
        out_trade_no: str,
        total_fee: int,
        body: str,
        product_name: str,
        product_id: str,
    ):
        return self._request(
            "POST",
            "/api/wx_pay/generate_qr_code",
            json={
                "out_trade_no": out_trade_no,
                "total_fee": total_fee,
                "body": body,
                "product_name": product_name,
                "product_id": product_id,
            },
        )

    def query_order(self, out_trade_no: str):
        return self._request(
            "POST", "/api/wx_pay/query_order", json={"out_trade_no": out_trade_no}
        )

    def refund(self, out_trade_no: str, total_fee: int):
        return self._request(
            "POST",
            "/api/wx_pay/refund",
            json={"out_trade_no": out_trade_no, "total_fee": total_fee},
        )
