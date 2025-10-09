import requests
from typing import Dict, Any, Optional


class Client:
    """基础认证类，提供公共的 API key 认证和请求方法"""
    def __init__(self, api_key: str):
        self.base_url = "https://thirdparty.pixelarrayai.com"
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
        }

    def _request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """统一的请求方法"""
        resp = requests.request(
            method, f"{self.base_url}{url}", headers=self.headers, **kwargs
        )
        if resp.status_code == 200:
            return resp.json().get("data", {})
        return {}
