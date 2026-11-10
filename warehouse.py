import csv
from dataclasses import dataclass
from datetime import date


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


def _parse_date(value: str):
    """Разбирает строку YYYY-MM-DD и возвращает date; ValueError если формат/дата неверные."""
    if not isinstance(value, str) or len(value) != 10 or value[4] != "-" or value[7] != "-":
        raise ValueError(f"Дата должна быть в формате YYYY-MM-DD, получено: {value!r}")
    try:
        return date.fromisoformat(value)
    except ValueError as e:
        raise ValueError(f"Некорректная дата {value!r}: {e}")


PRODUCT_TEMPLATES = {
    "яблоки": {"received_at": "2024-09-01", "shipped_at": "2024-09-10"},
    "груши":  {"received_at": "2024-09-02", "shipped_at": "2024-09-12"},
    "сливы":  {"received_at": "2024-09-03", "shipped_at": "2024-09-13"},
    "бананы": {"received_at": "2024-09-04", "shipped_at": "2024-09-14"},
}


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

    def set_quantity(self, name, quantity):
        if quantity < 0:
            raise ValueError("Количество не может быть отрицательным")
        p = self.find_product(name)
        if p is None:
            raise KeyError(f"Товар '{name}' не найден")
        p.quantity = quantity

    def set_received_date(self, name, received_at):
        self._set_date_field(name, "received_at", received_at)

    def set_shipped_date(self, name, shipped_at):
        self._set_date_field(name, "shipped_at", shipped_at)

    def _set_date_field(self, name, attr, value):
        _parse_date(value)
        p = self.find_product(name)
        if p is None:
            raise KeyError(f"Товар '{name}' не найден")
        setattr(p, attr, value)

    def add_from_template(self, template_name, quantity, received_at=None, shipped_at=None):
        if template_name not in PRODUCT_TEMPLATES:
            raise KeyError(f"Шаблон '{template_name}' не найден")
        tpl = PRODUCT_TEMPLATES[template_name]
        received_at = received_at if received_at is not None else tpl["received_at"]
        shipped_at = shipped_at if shipped_at is not None else tpl["shipped_at"]
        # даты-переопределения валидируем; шаблонные уже проверены при создании шаблона
        if received_at != tpl["received_at"]:
            _parse_date(received_at)
        if shipped_at != tpl["shipped_at"]:
            _parse_date(shipped_at)
        self.add_product(template_name, quantity, received_at, shipped_at)

    def format_table(self):
        headers = ["Название", "Кол-во", "Поступил", "Отгружен"]
        rows = [
            [p.name, str(p.quantity), p.received_at, p.shipped_at]
            for p in self._items
        ]
        widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                widths[i] = max(widths[i], len(str(cell)))

        def sep():
            return "+" + "+".join("-" * (w + 2) for w in widths) + "+"

        def fmt(row):
            cells = []
            for i, cell in enumerate(row):
                cells.append(" " + str(cell).ljust(widths[i]) + " ")
            return "|" + "|".join(cells) + "|"

        lines = [sep(), fmt(headers), sep()]
        for row in rows:
            lines.append(fmt(row))
        lines.append(sep())
        return "\n".join(lines)

    def save_to_file(self, path):
        with open(path, "w", encoding="utf-8") as f:
            for p in self._items:
                f.write(f"{p.name};{p.quantity};{p.received_at};{p.shipped_at}\n")

    def total_quantity(self):
        return sum(p.quantity for p in self._items)

    def total_by_product(self):
        return {p.name: p.quantity for p in self._items}

    def low_stock(self, threshold):
        if threshold <= 0:
            return []
        result = [p for p in self._items if p.quantity < threshold]
        result.sort(key=lambda p: p.quantity)
        return result

    def export_report(self, path, threshold):
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["name", "quantity", "received_at", "shipped_at", "is_low"])
            for p in self._items:
                writer.writerow([
                    p.name,
                    p.quantity,
                    p.received_at,
                    p.shipped_at,
                    p.quantity < threshold,
                ])

    def find_product(self, name):
        needle = name.casefold()
        for p in self._items:
            if p.name.casefold() == needle:
                return p
        return None

    def search_by_prefix(self, prefix):
        needle = prefix.casefold()
        return [p for p in self._items if p.name.casefold().startswith(needle)]
