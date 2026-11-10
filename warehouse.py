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
                if not is_valid_product_line(line):
                    continue
                name, qty, received_at, shipped_at = line.split(";")
                self._items.append(
                    Product(name, int(qty), received_at, shipped_at)
                )

    def add_product(self, name, quantity, received_at="", shipped_at=""):
        if not name.strip():
            raise ValueError("Название товара не может быть пустым")
        if quantity < 0:
            raise ValueError("Количество не может быть отрицательным")
        if self.find_product(name) is not None:
            raise ValueError(f"Товар '{name}' уже существует")
        self._items.append(Product(name, quantity, received_at, shipped_at))

    def remove_product(self, name):
        p = self.find_product(name)
        if p is None:
            raise KeyError(f"Товар '{name}' не найден")
        self._items.remove(p)

    def find_product(self, name):
        for p in self._items:
            if p.name == name:
                return p
        return None
