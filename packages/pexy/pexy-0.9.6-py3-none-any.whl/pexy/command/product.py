# MIT License
#
# Copyright (c) 2024 Clivern
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

import sys
import json
import click

from rich.json import JSON
from pexy.module import Shopify
from rich.console import Console


class ListProducts:

    def __init__(self, name, token):
        self.console = Console()
        self.shopify = Shopify(name, token)

    def exec(self, product_ids=None):
        try:
            products = self.shopify.get_products(product_ids)
            click.echo(self.console.print_json(json.dumps(products)))
        except Exception as err:
            click.echo(self.console.print_json(json.dumps({"error": str(err)})))
            sys.exit(1)


class CountProducts:

    def __init__(self, name, token):
        self.console = Console()
        self.shopify = Shopify(name, token)

    def exec(self):
        try:
            count = self.shopify.get_product_count()
            click.echo(self.console.print_json(json.dumps(count)))
        except Exception as err:
            click.echo(self.console.print_json(json.dumps({"error": str(err)})))
            sys.exit(1)


class GetProduct:

    def __init__(self, name, token):
        self.console = Console()
        self.shopify = Shopify(name, token)

    def exec(self, product_id):
        try:
            product = self.shopify.get_product(product_id)
            click.echo(self.console.print_json(json.dumps(product)))
        except Exception as err:
            click.echo(self.console.print_json(json.dumps({"error": str(err)})))
            sys.exit(1)


class CreateProduct:

    def __init__(self, name, token):
        self.console = Console()
        self.shopify = Shopify(name, token)

    def exec(self, product_data):
        try:
            product = self.shopify.create_product(product_data)
            click.echo(self.console.print_json(json.dumps(product)))
        except Exception as err:
            click.echo(self.console.print_json(json.dumps({"error": str(err)})))
            sys.exit(1)


class UpdateProduct:

    def __init__(self, name, token):
        self.console = Console()
        self.shopify = Shopify(name, token)

    def exec(self, product_id, product_data):
        try:
            product = self.shopify.update_product(product_id, product_data)
            click.echo(self.console.print_json(json.dumps(product)))
        except Exception as err:
            click.echo(self.console.print_json(json.dumps({"error": str(err)})))
            sys.exit(1)


class DeleteProduct:

    def __init__(self, name, token):
        self.console = Console()
        self.shopify = Shopify(name, token)

    def exec(self, product_id):
        try:
            deleted = self.shopify.delete_product(product_id)
            if deleted:
                click.echo("Product deleted successfully.")
        except Exception as err:
            click.echo(self.console.print_json(json.dumps({"error": str(err)})))
            sys.exit(1)
