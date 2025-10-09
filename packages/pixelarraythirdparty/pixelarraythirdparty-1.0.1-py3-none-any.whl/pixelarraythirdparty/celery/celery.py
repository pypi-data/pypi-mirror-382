from pixelarraythirdparty.client import Client


class CeleryManager(Client):
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
