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


def test_add_product_appends_to_items():
    w = Warehouse()
    w.add_product("яблоки", 10, "2024-09-01", "2024-09-10")
    items = w.get_items()
    assert len(items) == 1
    assert items[0].name == "яблоки"
    assert items[0].quantity == 10
    assert items[0].received_at == "2024-09-01"
    assert items[0].shipped_at == "2024-09-10"


def test_add_product_with_negative_quantity_raises():
    w = Warehouse()
    with pytest.raises(ValueError):
        w.add_product("яблоки", -1, "2024-09-01", "2024-09-10")


def test_add_duplicate_product_raises():
    w = Warehouse()
    w.add_product("яблоки", 10, "2024-09-01", "2024-09-10")
    with pytest.raises(ValueError):
        w.add_product("яблоки", 5, "2024-09-02", "2024-09-11")


def test_add_product_with_empty_name_raises():
    w = Warehouse()
    with pytest.raises(ValueError):
        w.add_product("", 10, "2024-09-01", "2024-09-10")


def test_remove_product_deletes_it_from_items():
    w = Warehouse()
    w.add_product("яблоки", 10, "2024-09-01", "2024-09-10")
    w.add_product("груши", 5, "2024-09-02", "2024-09-12")
    w.remove_product("яблоки")
    items = w.get_items()
    assert len(items) == 1
    assert items[0].name == "груши"


def test_remove_unknown_product_raises():
    w = Warehouse()
    with pytest.raises(KeyError):
        w.remove_product("нет-такого")


def test_remove_loaded_product_works(tmp_path):
    file = tmp_path / "products.txt"
    file.write_text(
        "яблоки;10;2024-09-01;2024-09-10\n"
        "груши;5;2024-09-02;2024-09-12\n",
        encoding="utf-8",
    )
    w = Warehouse()
    w.load_from_file(str(file))
    w.remove_product("груши")
    assert [p.name for p in w.get_items()] == ["яблоки"]


def test_set_quantity_changes_value():
    w = Warehouse()
    w.add_product("яблоки", 10, "2024-09-01", "2024-09-10")
    w.set_quantity("яблоки", 25)
    assert w.find_product("яблоки").quantity == 25


def test_set_quantity_to_zero_allowed():
    w = Warehouse()
    w.add_product("яблоки", 10, "2024-09-01", "2024-09-10")
    w.set_quantity("яблоки", 0)
    assert w.find_product("яблоки").quantity == 0


def test_set_quantity_unknown_product_raises():
    w = Warehouse()
    with pytest.raises(KeyError):
        w.set_quantity("нет-такого", 5)


def test_set_negative_quantity_raises():
    w = Warehouse()
    w.add_product("яблоки", 10, "2024-09-01", "2024-09-10")
    with pytest.raises(ValueError):
        w.set_quantity("яблоки", -1)


def test_set_received_date_changes_value():
    w = Warehouse()
    w.add_product("яблоки", 10, "2024-09-01", "2024-09-10")
    w.set_received_date("яблоки", "2024-09-05")
    assert w.find_product("яблоки").received_at == "2024-09-05"


def test_set_received_date_does_not_touch_other_products():
    w = Warehouse()
    w.add_product("яблоки", 10, "2024-09-01", "2024-09-10")
    w.add_product("груши", 5, "2024-09-02", "2024-09-12")
    w.set_received_date("яблоки", "2024-10-01")
    assert w.find_product("яблоки").received_at == "2024-10-01"
    assert w.find_product("груши").received_at == "2024-09-02"


def test_set_received_date_unknown_product_raises():
    w = Warehouse()
    with pytest.raises(KeyError):
        w.set_received_date("нет-такого", "2024-09-05")


def test_set_received_date_invalid_format_raises():
    w = Warehouse()
    w.add_product("яблоки", 10, "2024-09-01", "2024-09-10")
    with pytest.raises(ValueError):
        w.set_received_date("яблоки", "05.09.2024")


def test_set_received_date_nonsense_raises():
    w = Warehouse()
    w.add_product("яблоки", 10, "2024-09-01", "2024-09-10")
    with pytest.raises(ValueError):
        w.set_received_date("яблоки", "2024-13-40")


def test_set_shipped_date_changes_value():
    w = Warehouse()
    w.add_product("яблоки", 10, "2024-09-01", "2024-09-10")
    w.set_shipped_date("яблоки", "2024-09-15")
    assert w.find_product("яблоки").shipped_at == "2024-09-15"


def test_set_shipped_date_does_not_touch_other_products():
    w = Warehouse()
    w.add_product("яблоки", 10, "2024-09-01", "2024-09-10")
    w.add_product("груши", 5, "2024-09-02", "2024-09-12")
    w.set_shipped_date("яблоки", "2024-10-01")
    assert w.find_product("яблоки").shipped_at == "2024-10-01"
    assert w.find_product("груши").shipped_at == "2024-09-12"


def test_set_shipped_date_unknown_product_raises():
    w = Warehouse()
    with pytest.raises(KeyError):
        w.set_shipped_date("нет-такого", "2024-09-15")


def test_set_shipped_date_invalid_format_raises():
    w = Warehouse()
    w.add_product("яблоки", 10, "2024-09-01", "2024-09-10")
    with pytest.raises(ValueError):
        w.set_shipped_date("яблоки", "15.09.2024")


def test_set_shipped_date_keeps_received_and_quantity():
    w = Warehouse()
    w.add_product("яблоки", 10, "2024-09-01", "2024-09-10")
    w.set_shipped_date("яблоки", "2024-09-20")
    p = w.find_product("яблоки")
    assert p.received_at == "2024-09-01"
    assert p.quantity == 10
