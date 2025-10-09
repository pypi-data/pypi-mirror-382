import requests


class OrderManager:
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

    def create_order(
        self,
        product_name: str,
        product_id: str,
        amount: float,
        body: str,
        remark: str,
        payment_channel: str,
    ):
        data = {
            "product_name": product_name,
            "product_id": product_id,
            "amount": amount,
            "body": body,
            "remark": remark,
            "payment_channel": payment_channel,
        }
        return self._request("POST", "/api/orders/create", json=data)

    def list_order(
        self,
        page: int = 1,
        page_size: int = 10,
        payment_status: str = None,
        order_no: str = None,
    ):
        params = {
            "page": page,
            "page_size": page_size,
            "payment_status": payment_status,
            "order_no": order_no,
        }
        return self._request("GET", "/api/orders/list", params=params)

    def get_order_detail(self, order_no: str):
        return self._request("GET", f"/api/orders/{order_no}")

    def update_order(
        self,
        order_no: str,
        payment_status: str,
        wx_order_no: str,
        transaction_id: str,
        openid: str,
        trade_type: str,
        bank_type: str,
        fee_type: str,
        is_subscribe: str,
        time_end: str,
        remark: str,
    ):
        data = {
            "payment_status": payment_status,
            "wx_order_no": wx_order_no,
            "transaction_id": transaction_id,
            "openid": openid,
            "trade_type": trade_type,
            "bank_type": bank_type,
            "fee_type": fee_type,
            "is_subscribe": is_subscribe,
            "time_end": time_end,
            "remark": remark,
        }
        return self._request("PUT", f"/api/orders/{order_no}", json=data)

    def delete_order(self, order_no: str):
        return self._request("DELETE", f"/api/orders/{order_no}")

    def get_order_stats(self):
        return self._request("GET", "/api/orders/stats/summary")
