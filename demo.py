"""Интерактивное меню для работы с системой управления складом.

Запуск: python demo.py
Выход: пункт 0
"""
from warehouse import Warehouse


MENU = """
=== Управление складом ===
1. Показать все товары (таблица)
2. Добавить товар (вручную)
3. Добавить товар из заготовки
4. Удалить товар
5. Изменить количество
6. Изменить дату поступления
7. Изменить дату отгрузки
8. Поиск по названию / префиксу
9. Показать товары ниже порога
10. Итого по складу
11. Сохранить склад в файл
12. Загрузить склад из файла
13. Экспорт отчёта в CSV
0. Выход
"""


def _ask(prompt, default=None):
    value = input(prompt).strip()
    if value == "" and default is not None:
        return default
    return value


def _ask_int(prompt):
    while True:
        raw = input(prompt).strip()
        try:
            return int(raw)
        except ValueError:
            print("  Ожидается целое число, попробуйте снова.")


def _ask_date(prompt, default=""):
    """Возвращает строку YYYY-MM-DD или пустую строку, если ввели пусто и default пуст."""
    raw = input(prompt).strip()
    if raw == "":
        return default
    return raw


def show(w: Warehouse):
    if not w.get_items():
        print("\nСклад пуст.\n")
        return
    print()
    print(w.format_table())
    print()


def cmd_add(w: Warehouse):
    name = _ask("Название: ")
    quantity = _ask_int("Количество: ")
    received_at = _ask_date("Дата поступления (YYYY-MM-DD, можно пусто): ", "")
    shipped_at = _ask_date("Дата отгрузки (YYYY-MM-DD, можно пусто): ", "")
    w.add_product(name, quantity, received_at, shipped_at)
    print(f"  Добавлено: {name}")


def cmd_add_template(w: Warehouse):
    from warehouse import PRODUCT_TEMPLATES
    print("  Доступные шаблоны:", ", ".join(PRODUCT_TEMPLATES))
    name = _ask("Шаблон: ")
    quantity = _ask_int("Количество: ")
    w.add_from_template(name, quantity)
    print(f"  Добавлено из шаблона: {name}")


def cmd_remove(w: Warehouse):
    name = _ask("Название для удаления: ")
    w.remove_product(name)
    print(f"  Удалено: {name}")


def cmd_set_quantity(w: Warehouse):
    name = _ask("Название: ")
    quantity = _ask_int("Новое количество: ")
    w.set_quantity(name, quantity)
    print(f"  У {name} теперь {quantity}.")


def cmd_set_received(w: Warehouse):
    name = _ask("Название: ")
    d = _ask_date("Новая дата поступления (YYYY-MM-DD): ")
    w.set_received_date(name, d)
    print(f"  {name}: дата поступления = {d}")


def cmd_set_shipped(w: Warehouse):
    name = _ask("Название: ")
    d = _ask_date("Новая дата отгрузки (YYYY-MM-DD): ")
    w.set_shipped_date(name, d)
    print(f"  {name}: дата отгрузки = {d}")


def cmd_search(w: Warehouse):
    prefix = _ask("Префикс/название: ")
    exact = w.find_product(prefix)
    if exact is not None:
        print(f"  Точное совпадение: {exact}")
    found = w.search_by_prefix(prefix)
    if found:
        print("  Совпадения по префиксу:")
        for p in found:
            print(f"    - {p.name}: {p.quantity} (пост. {p.received_at}, отгр. {p.shipped_at})")
    elif exact is None:
        print("  Ничего не найдено.")


def cmd_low_stock(w: Warehouse):
    threshold = _ask_int("Порог (товары с количеством меньше порога): ")
    low = w.low_stock(threshold)
    if not low:
        print("  Таких товаров нет.")
        return
    print(f"  Ниже порога {threshold}:")
    for p in low:
        print(f"    - {p.name}: {p.quantity}")


def cmd_totals(w: Warehouse):
    print(f"  Всего единиц на складе: {w.total_quantity()}")
    by_product = w.total_by_product()
    if by_product:
        print("  По товарам:")
        for name, qty in by_product.items():
            print(f"    - {name}: {qty}")


def cmd_save(w: Warehouse):
    path = _ask("Путь к файлу склада: ", "warehouse.txt")
    w.save_to_file(path)
    print(f"  Сохранено в {path}")


def cmd_load(w: Warehouse):
    path = _ask("Путь к файлу склада: ", "warehouse.txt")
    w.load_from_file(path)
    print(f"  Загружено из {path}, товаров на складе: {len(w.get_items())}")


def cmd_export(w: Warehouse):
    path = _ask("Путь к CSV: ", "report.csv")
    threshold = _ask_int("Порог для отметки is_low: ")
    w.export_report(path, threshold)
    print(f"  Отчёт записан в {path}")


HANDLERS = {
    "1": show,
    "2": cmd_add,
    "3": cmd_add_template,
    "4": cmd_remove,
    "5": cmd_set_quantity,
    "6": cmd_set_received,
    "7": cmd_set_shipped,
    "8": cmd_search,
    "9": cmd_low_stock,
    "10": cmd_totals,
    "11": cmd_save,
    "12": cmd_load,
    "13": cmd_export,
}


def main():
    w = Warehouse()
    print(MENU)
    while True:
        try:
            choice = input("Выберите пункт: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nВыход.")
            return
        if choice == "0":
            print("Выход.")
            return
        handler = HANDLERS.get(choice)
        if handler is None:
            print("  Неизвестный пункт, попробуйте снова.")
            continue
        try:
            handler(w)
        except (ValueError, KeyError, OSError) as e:
            print(f"  Ошибка: {e}")
        print(MENU)


if __name__ == "__main__":
    main()
