import requests


class CeleryManager:
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

    def get_celery_status(self):
        return self._request("GET", "/api/celery/status")

    def get_celery_tasks(self):
        return self._request("GET", "/api/celery/tasks")

    def get_celery_tasks_scheduled(self):
        return self._request("GET", "/api/celery/tasks/scheduled")

    def get_celery_tasks_detail(self, task_name: str):
        return self._request("GET", f"/api/celery/tasks/{task_name}")

    def trigger_celery_task(self, task_name: str, args: list, kwargs: dict):
        return self._request(
            "POST",
            f"/api/celery/tasks/{task_name}/trigger",
            json={"args": args, "kwargs": kwargs},
        )
