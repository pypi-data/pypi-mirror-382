import requests
import aiohttp
from typing import Optional


class UserManager:
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

    def list_user(
        self,
        page: int = 1,
        page_size: int = 10,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
    ):
        params = {"page": page, "page_size": page_size}
        if role is not None:
            params["role"] = role
        if is_active is not None:
            params["is_active"] = is_active
        return self._request("GET", "/api/users/list", params=params)

    def create_user(self, username: str, password: str, email: str, role: str):
        data = {
            "username": username,
            "password": password,
            "email": email,
            "role": role,
        }
        return self._request("POST", "/api/users/create", json=data)

    def update_user(
        self, user_id: int, username: str, email: str, role: str, is_active: bool
    ):
        data = {
            "username": username,
            "email": email,
            "role": role,
            "is_active": is_active,
        }
        return self._request("PUT", f"/api/users/{user_id}", json=data)

    def delete_user(self, user_id: int):
        return self._request("DELETE", f"/api/users/{user_id}")

    def get_user_detail(self, user_id: int):
        return self._request("GET", f"/api/users/{user_id}")

    def reset_user_password(self, user_id: int, new_password: str):
        data = {"new_password": new_password}
        return self._request("POST", f"/api/users/{user_id}/reset-password", json=data)
