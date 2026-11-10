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
