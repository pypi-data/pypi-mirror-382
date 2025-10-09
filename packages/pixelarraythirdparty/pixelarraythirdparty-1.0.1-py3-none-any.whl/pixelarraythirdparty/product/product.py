from pixelarraythirdparty.client import Client


class ProductManager(Client):
    def create_product(
        self,
        name: str,
        description: str,
        price: float,
        category: str,
        status: str,
        is_subscription: bool,
        subscription_period: str,
        features: str,
        sort_order: int,
    ):
        data = {
            "name": name,
            "description": description,
            "price": price,
            "category": category,
            "status": status,
            "is_subscription": is_subscription,
            "subscription_period": subscription_period,
            "features": features,
            "sort_order": sort_order,
        }
        return self._request("POST", "/api/products/create", json=data)

    def list_product(
        self,
        page: int = 1,
        page_size: int = 10,
        status: str = None,
        category: str = None,
        name: str = None,
    ):
        params = {
            "page": page,
            "page_size": page_size,
            "status": status,
            "category": category,
            "name": name,
        }
        if status is not None:
            params["status"] = status
        if category is not None:
            params["category"] = category
        if name is not None:
            params["name"] = name
        return self._request("GET", "/api/products/list", params=params)

    def get_product_detail(self, product_id: str):
        return self._request("GET", f"/api/products/{product_id}")

    def update_product(
        self,
        product_id: str,
        name: str,
        description: str,
        price: float,
        category: str,
        status: str,
        is_subscription: bool,
        subscription_period: str,
        features: str,
        sort_order: int,
    ):
        data = {
            "name": name,
            "description": description,
            "price": price,
            "category": category,
            "status": status,
            "is_subscription": is_subscription,
            "subscription_period": subscription_period,
            "features": features,
            "sort_order": sort_order,
        }
        return self._request("PUT", f"/api/products/{product_id}", json=data)

    def delete_product(self, product_id: str):
        return self._request("DELETE", f"/api/products/{product_id}")

    def get_product_categories(self):
        return self._request("GET", "/api/products/categories/list")
