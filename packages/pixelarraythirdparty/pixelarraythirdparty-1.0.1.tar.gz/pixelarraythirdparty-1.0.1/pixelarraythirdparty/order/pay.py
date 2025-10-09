from pixelarraythirdparty.client import Client


class WeChatPayManager(Client):
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
