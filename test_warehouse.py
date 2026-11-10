from warehouse import Warehouse


def test_load_products_from_file_returns_list_of_products(tmp_path):
    file = tmp_path / "products.txt"
    file.write_text(
        "яблоки;10;2024-09-01;2024-09-10\n"
        "груши;5;2024-09-02;2024-09-12\n",
        encoding="utf-8",
    )

    w = Warehouse()
    w.load_from_file(str(file))
    items = w.get_items()

    assert len(items) == 2
    assert items[0].name == "яблоки"
    assert items[0].quantity == 10
    assert items[1].name == "груши"
    assert items[1].quantity == 5

import pytest
from warehouse import Warehouse, is_valid_product_line


def test_valid_line_is_accepted():
    assert is_valid_product_line("яблоки;10;2024-09-01;2024-09-10") is True


def test_line_with_too_few_fields_is_rejected():
    assert is_valid_product_line("яблоки;10;2024-09-01") is False


def test_line_with_too_many_fields_is_rejected():
    assert is_valid_product_line("яблоки;10;2024-09-01;2024-09-10;лишнее") is False


def test_line_with_non_numeric_quantity_is_rejected():
    assert is_valid_product_line("яблоки;десять;2024-09-01;2024-09-10") is False


def test_line_with_empty_name_is_rejected():
    assert is_valid_product_line(";10;2024-09-01;2024-09-10") is False


def test_line_with_negative_quantity_is_rejected():
    assert is_valid_product_line("яблоки;-5;2024-09-01;2024-09-10") is False


def test_load_skips_invalid_lines(tmp_path):
    file = tmp_path / "products.txt"
    file.write_text(
        "яблоки;10;2024-09-01;2024-09-10\n"       # валидная
        "груши;пять;2024-09-02;2024-09-12\n"       # невалидная: количество не число
        "сливы;3;2024-09-03\n"                     # невалидная: 3 поля
        "бананы;7;2024-09-04;2024-09-14\n",        # валидная
        encoding="utf-8",
    )

    w = Warehouse()
    w.load_from_file(str(file))
    items = w.get_items()

    assert len(items) == 2
    assert items[0].name == "яблоки"
    assert items[1].name == "бананы"


def test_load_returns_only_valid_when_all_invalid(tmp_path):
    file = tmp_path / "products.txt"
    file.write_text(
        "груши;пять;2024-09-02;2024-09-12\n"
        "сливы;3;2024-09-03\n",
        encoding="utf-8",
    )

    w = Warehouse()
    w.load_from_file(str(file))
    assert w.get_items() == []


def test_load_empty_file_leaves_warehouse_empty(tmp_path):
    file = tmp_path / "products.txt"
    file.write_text("", encoding="utf-8")

    w = Warehouse()
    w.load_from_file(str(file))
    assert w.get_items() == []
