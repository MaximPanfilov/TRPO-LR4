from dataclasses import dataclass


@dataclass
class Product:
    name: str
    quantity: int
    received_at: str = ""
    shipped_at: str = ""


class Warehouse:
    def __init__(self):
        self._items = []

    def get_items(self):
        return list(self._items)

    def load_from_file(self, path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                name, qty, received_at, shipped_at = line.split(";")
                self._items.append(
                    Product(name, int(qty), received_at, shipped_at)
                )
