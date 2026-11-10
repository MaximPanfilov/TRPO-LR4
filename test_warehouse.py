from warehouse import Warehouse


def test_new_warehouse_is_empty():
    w = Warehouse()
    assert w.get_items() == []
