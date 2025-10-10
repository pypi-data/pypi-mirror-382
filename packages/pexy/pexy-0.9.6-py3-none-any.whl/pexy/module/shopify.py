# MIT License
#
# Copyright (c) 2023 Clivern
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import requests


class Shopify:

    def __init__(self, name, token, api_version="2024-07"):
        self.name = name
        self.token = token
        self.api_version = api_version
        self.base_url = f"https://{self.name}.myshopify.com"

    def get_shop_info(self):
        url = f"{self.base_url}/admin/api/{self.api_version}/shop.json"

        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": self.token,
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def get_access_scopes(self):
        url = f"{self.base_url}/admin/oauth/access_scopes.json"

        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": self.token,
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def create_product(self, product_data):
        url = f"{self.base_url}/admin/api/{self.api_version}/products.json"

        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": self.token,
        }

        response = requests.post(url, headers=headers, json=product_data)

        if response.status_code == 201:
            return response.json()
        else:
            response.raise_for_status()

    def get_product(self, product_id):
        url = f"{self.base_url}/admin/api/{self.api_version}/products/{product_id}.json"

        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": self.token,
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def get_product_count(self):
        url = f"{self.base_url}/admin/api/{self.api_version}/products/count.json"

        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": self.token,
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def get_products(self, product_ids=None):
        if not product_ids:
            url = f"{self.base_url}/admin/api/{self.api_version}/products.json"
        else:
            url = f"{self.base_url}/admin/api/2024-07/products.json?ids={product_ids}"

        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": self.token,
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def update_product(self, product_id, product_data):
        url = f"{self.base_url}/admin/api/{self.api_version}/products/{product_id}.json"

        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": self.token,
        }

        response = requests.put(url, headers=headers, json=product_data)

        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def delete_product(self, product_id):
        url = f"{self.base_url}/admin/api/{self.api_version}/products/{product_id}.json"

        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": self.token,
        }

        response = requests.delete(url, headers=headers)

        if response.status_code == 200:
            return True
        else:
            response.raise_for_status()

    def create_collection(self, collection_data):
        url = f"{self.base_url}/admin/api/{self.api_version}/custom_collections.json"

        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": self.token,
        }

        response = requests.post(url, headers=headers, json=collection_data)

        if response.status_code == 201:
            return response.json()
        else:
            response.raise_for_status()

    def update_collection(self, collection_id, collection_data):
        url = f"{self.base_url}/admin/api/{self.api_version}/custom_collections/{collection_id}.json"

        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": self.token,
        }

        response = requests.put(url, headers=headers, json=collection_data)

        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def get_collections(self, collection_ids=None):
        if not collection_ids:
            url = (
                f"{self.base_url}/admin/api/{self.api_version}/custom_collections.json"
            )
        else:
            url = f"{self.base_url}/admin/api/{self.api_version}/custom_collections.json?ids={collection_ids}"

        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": self.token,
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def get_collection(self, collection_id):
        url = f"{self.base_url}/admin/api/{self.api_version}/custom_collections/{collection_id}.json"

        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": self.token,
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def get_collection_count(self):
        url = f"{self.base_url}/admin/api/{self.api_version}/custom_collections/count.json"

        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": self.token,
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def delete_collection(self, collection_id):
        url = f"{self.base_url}/admin/api/{self.api_version}/custom_collections/{collection_id}.json"

        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": self.token,
        }

        response = requests.delete(url, headers=headers)

        if response.status_code == 200:
            return True
        else:
            response.raise_for_status()
