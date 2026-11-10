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
