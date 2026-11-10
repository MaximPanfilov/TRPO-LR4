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


def test_add_from_template_uses_template_dates():
    w = Warehouse()
    w.add_from_template("яблоки", 7)
    p = w.find_product("яблоки")
    assert p is not None
    assert p.quantity == 7
    assert p.received_at == "2024-09-01"
    assert p.shipped_at == "2024-09-10"


def test_add_from_template_overrides_dates():
    w = Warehouse()
    w.add_from_template("яблоки", 7, received_at="2024-10-01", shipped_at="2024-10-20")
    p = w.find_product("яблоки")
    assert p.received_at == "2024-10-01"
    assert p.shipped_at == "2024-10-20"


def test_add_from_unknown_template_raises():
    w = Warehouse()
    with pytest.raises(KeyError):
        w.add_from_template("ананасы", 3)


def test_add_from_template_negative_quantity_raises():
    w = Warehouse()
    with pytest.raises(ValueError):
        w.add_from_template("яблоки", -1)


def test_add_from_template_duplicate_raises():
    w = Warehouse()
    w.add_from_template("яблоки", 7)
    with pytest.raises(ValueError):
        w.add_from_template("яблоки", 3)


def test_add_from_template_invalid_override_date_raises():
    w = Warehouse()
    with pytest.raises(ValueError):
        w.add_from_template("яблоки", 7, received_at="01.10.2024")


def test_format_table_empty_warehouse():
    w = Warehouse()
    table = w.format_table()
    lines = table.splitlines()
    # заголовок + рамка, но без строк с товарами
    assert any("Название" in line for line in lines)
    assert all("яблоки" not in line for line in lines)


def test_format_table_contains_all_products():
    w = Warehouse()
    w.add_product("яблоки", 10, "2024-09-01", "2024-09-10")
    w.add_product("груши", 5, "2024-09-02", "2024-09-12")
    table = w.format_table()
    assert "яблоки" in table
    assert "груши" in table
    assert "10" in table
    assert "5" in table
    assert "2024-09-01" in table
    assert "2024-09-12" in table


def test_format_table_has_header_and_borders():
    w = Warehouse()
    w.add_product("яблоки", 10, "2024-09-01", "2024-09-10")
    table = w.format_table()
    lines = table.splitlines()
    # минимум 4 строки: верхняя рамка, заголовок, разделитель, данные, нижняя рамка
    assert len(lines) >= 5
    assert lines[0].startswith("+")
    assert lines[0].endswith("+")
    assert lines[-1].startswith("+")
    assert lines[-1].endswith("+")
    for column in ("Название", "Кол-во", "Поступил", "Отгружен"):
        assert column in table


def test_format_table_is_aligned():
    w = Warehouse()
    w.add_product("яблоки", 10, "2024-09-01", "2024-09-10")
    w.add_product("очень-длинное-название-товара", 3, "2024-09-02", "2024-09-12")
    table = w.format_table()
    lines = table.splitlines()
    # все линии одинаковой ширины (моноширинный шрифт, ровные рамки)
    widths = {len(line) for line in lines}
    assert len(widths) == 1


def test_save_to_file_writes_all_products(tmp_path):
    w = Warehouse()
    w.add_product("яблоки", 10, "2024-09-01", "2024-09-10")
    w.add_product("груши", 5, "2024-09-02", "2024-09-12")
    file = tmp_path / "out.txt"
    w.save_to_file(str(file))
    content = file.read_text(encoding="utf-8")
    assert "яблоки;10;2024-09-01;2024-09-10" in content
    assert "груши;5;2024-09-02;2024-09-12" in content


def test_save_to_file_empty_warehouse_creates_empty_file(tmp_path):
    w = Warehouse()
    file = tmp_path / "out.txt"
    w.save_to_file(str(file))
    assert file.read_text(encoding="utf-8") == ""


def test_save_then_load_roundtrip(tmp_path):
    w1 = Warehouse()
    w1.add_product("яблоки", 10, "2024-09-01", "2024-09-10")
    w1.add_product("груши", 5, "2024-09-02", "2024-09-12")
    file = tmp_path / "dump.txt"
    w1.save_to_file(str(file))

    w2 = Warehouse()
    w2.load_from_file(str(file))

    a = [(p.name, p.quantity, p.received_at, p.shipped_at) for p in w1.get_items()]
    b = [(p.name, p.quantity, p.received_at, p.shipped_at) for p in w2.get_items()]
    assert a == b


def test_find_product_exact_match():
    w = Warehouse()
    w.add_product("яблоки", 10, "2024-09-01", "2024-09-10")
    p = w.find_product("яблоки")
    assert p is not None and p.name == "яблоки"


def test_find_product_is_case_insensitive():
    w = Warehouse()
    w.add_product("Яблоки", 10, "2024-09-01", "2024-09-10")
    assert w.find_product("яблоки") is not None
    assert w.find_product("ЯБЛОКИ") is not None


def test_find_product_returns_none_for_missing():
    w = Warehouse()
    assert w.find_product("нет-такого") is None


def test_search_by_prefix_returns_matching_products():
    w = Warehouse()
    w.add_product("яблоки", 10, "2024-09-01", "2024-09-10")
    w.add_product("яблочный сок", 3, "2024-09-02", "2024-09-12")
    w.add_product("груши", 5, "2024-09-03", "2024-09-13")
    found = w.search_by_prefix("ябл")
    names = sorted(p.name for p in found)
    assert names == ["яблоки", "яблочный сок"]


def test_search_by_prefix_is_case_insensitive():
    w = Warehouse()
    w.add_product("Яблоки", 10, "2024-09-01", "2024-09-10")
    assert [p.name for p in w.search_by_prefix("ябл")] == ["Яблоки"]


def test_search_by_prefix_empty_result():
    w = Warehouse()
    w.add_product("яблоки", 10, "2024-09-01", "2024-09-10")
    assert w.search_by_prefix("xyz") == []


def test_total_quantity_on_empty_warehouse_is_zero():
    w = Warehouse()
    assert w.total_quantity() == 0


def test_total_quantity_sums_all_products():
    w = Warehouse()
    w.add_product("яблоки", 10, "2024-09-01", "2024-09-10")
    w.add_product("груши", 5, "2024-09-02", "2024-09-12")
    w.add_product("сливы", 3, "2024-09-03", "2024-09-13")
    assert w.total_quantity() == 18


def test_total_quantity_reflects_updates():
    w = Warehouse()
    w.add_product("яблоки", 10, "2024-09-01", "2024-09-10")
    w.set_quantity("яблоки", 4)
    assert w.total_quantity() == 4


def test_total_by_product_on_empty_warehouse():
    w = Warehouse()
    assert w.total_by_product() == {}


def test_total_by_product_returns_mapping():
    w = Warehouse()
    w.add_product("яблоки", 10, "2024-09-01", "2024-09-10")
    w.add_product("груши", 5, "2024-09-02", "2024-09-12")
    assert w.total_by_product() == {"яблоки": 10, "груши": 5}


def test_total_by_product_reflects_updates():
    w = Warehouse()
    w.add_product("яблоки", 10, "2024-09-01", "2024-09-10")
    w.set_quantity("яблоки", 25)
    assert w.total_by_product() == {"яблоки": 25}


def test_low_stock_empty_warehouse():
    w = Warehouse()
    assert w.low_stock(10) == []


def test_low_stock_returns_products_below_threshold():
    w = Warehouse()
    w.add_product("яблоки", 10, "2024-09-01", "2024-09-10")
    w.add_product("груши", 5, "2024-09-02", "2024-09-12")
    w.add_product("сливы", 3, "2024-09-03", "2024-09-13")
    low = w.low_stock(6)
    assert [p.name for p in low] == ["сливы", "груши"]


def test_low_stock_is_sorted_ascending_by_quantity():
    w = Warehouse()
    w.add_product("a", 3, "2024-09-01", "2024-09-10")
    w.add_product("b", 1, "2024-09-02", "2024-09-12")
    w.add_product("c", 2, "2024-09-03", "2024-09-13")
    assert [p.name for p in w.low_stock(5)] == ["b", "c", "a"]


def test_low_stock_does_not_include_equal_to_threshold():
    w = Warehouse()
    w.add_product("яблоки", 10, "2024-09-01", "2024-09-10")
    assert w.low_stock(10) == []


def test_low_stock_zero_threshold_returns_empty():
    w = Warehouse()
    w.add_product("яблоки", 0, "2024-09-01", "2024-09-10")
    assert w.low_stock(0) == []


def test_low_stock_negative_threshold_returns_empty():
    w = Warehouse()
    w.add_product("яблоки", 1, "2024-09-01", "2024-09-10")
    assert w.low_stock(-5) == []


def test_export_report_creates_file_with_header(tmp_path):
    w = Warehouse()
    w.add_product("яблоки", 10, "2024-09-01", "2024-09-10")
    file = tmp_path / "report.csv"
    w.export_report(str(file), threshold=5)
    content = file.read_text(encoding="utf-8")
    lines = content.strip().splitlines()
    assert lines[0] == "name,quantity,received_at,shipped_at,is_low"
    assert lines[1] == "яблоки,10,2024-09-01,2024-09-10,False"


def test_export_report_marks_low_stock(tmp_path):
    w = Warehouse()
    w.add_product("яблоки", 10, "2024-09-01", "2024-09-10")
    w.add_product("груши", 3, "2024-09-02", "2024-09-12")
    file = tmp_path / "report.csv"
    w.export_report(str(file), threshold=5)
    lines = file.read_text(encoding="utf-8").strip().splitlines()
    assert "яблоки,10,2024-09-01,2024-09-10,False" in lines
    assert "груши,3,2024-09-02,2024-09-12,True" in lines


def test_export_report_on_empty_warehouse_has_only_header(tmp_path):
    w = Warehouse()
    file = tmp_path / "report.csv"
    w.export_report(str(file), threshold=5)
    lines = file.read_text(encoding="utf-8").strip().splitlines()
    assert lines == ["name,quantity,received_at,shipped_at,is_low"]


def test_export_report_preserves_insertion_order(tmp_path):
    w = Warehouse()
    w.add_product("b", 1, "2024-09-01", "2024-09-10")
    w.add_product("a", 2, "2024-09-02", "2024-09-12")
    w.add_product("c", 3, "2024-09-03", "2024-09-13")
    file = tmp_path / "report.csv"
    w.export_report(str(file), threshold=5)
    lines = file.read_text(encoding="utf-8").strip().splitlines()[1:]
    assert [line.split(",")[0] for line in lines] == ["b", "a", "c"]


def test_export_report_threshold_zero_no_items_are_low(tmp_path):
    w = Warehouse()
    w.add_product("яблоки", 0, "2024-09-01", "2024-09-10")
    file = tmp_path / "report.csv"
    w.export_report(str(file), threshold=0)
    lines = file.read_text(encoding="utf-8").strip().splitlines()
    assert lines[1].endswith(",False")
