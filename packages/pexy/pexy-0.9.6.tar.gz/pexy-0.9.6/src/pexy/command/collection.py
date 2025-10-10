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


class CreateCollection:

    def __init__(self, name, token):
        self.console = Console()
        self.shopify = Shopify(name, token)

    def exec(self, collection_data):
        try:
            collect = self.shopify.create_collection(collection_data)
            click.echo(self.console.print_json(json.dumps(collect)))
        except Exception as err:
            click.echo(self.console.print_json(json.dumps({"error": str(err)})))
            sys.exit(1)


class UpdateCollection:

    def __init__(self, name, token):
        self.console = Console()
        self.shopify = Shopify(name, token)

    def exec(self, collection_id, collection_data):
        try:
            collect = self.shopify.update_collection(collection_id, collection_data)
            click.echo(self.console.print_json(json.dumps(collect)))
        except Exception as err:
            click.echo(self.console.print_json(json.dumps({"error": str(err)})))
            sys.exit(1)


class ListCollection:

    def __init__(self, name, token):
        self.console = Console()
        self.shopify = Shopify(name, token)

    def exec(self, collection_ids=None):
        try:
            collects = self.shopify.get_collections(collection_ids)
            click.echo(self.console.print_json(json.dumps(collects)))
        except Exception as err:
            click.echo(self.console.print_json(json.dumps({"error": str(err)})))
            sys.exit(1)


class GetCollection:

    def __init__(self, name, token):
        self.console = Console()
        self.shopify = Shopify(name, token)

    def exec(self, collection_id):
        try:
            collect = self.shopify.get_collection(collection_id)
            click.echo(self.console.print_json(json.dumps(collect)))
        except Exception as err:
            click.echo(self.console.print_json(json.dumps({"error": str(err)})))
            sys.exit(1)


class CountCollection:

    def __init__(self, name, token):
        self.console = Console()
        self.shopify = Shopify(name, token)

    def exec(self):
        try:
            count = self.shopify.get_collection_count()
            click.echo(self.console.print_json(json.dumps(count)))
        except Exception as err:
            click.echo(self.console.print_json(json.dumps({"error": str(err)})))
            sys.exit(1)


class DeleteCollection:

    def __init__(self, name, token):
        self.console = Console()
        self.shopify = Shopify(name, token)

    def exec(self, collection_id):
        try:
            deleted = self.shopify.delete_collection(collection_id)
            if deleted:
                click.echo("Collect deleted successfully.")
        except Exception as err:
            click.echo(self.console.print_json(json.dumps({"error": str(err)})))
            sys.exit(1)
