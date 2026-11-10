from dataclasses import dataclass


@dataclass
class Product:
    name: str
    quantity: int
    received_at: str = ""
    shipped_at: str = ""


def is_valid_product_line(line: str) -> bool:
    parts = line.split(";")
    if len(parts) != 4:
        return False
    name, qty, _received_at, _shipped_at = parts
    if not name.strip():
        return False
    try:
        quantity = int(qty)
    except ValueError:
        return False
    if quantity < 0:
        return False
    return True


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
