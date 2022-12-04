# TODO make tests correctly automatic without using actual db
from db import Wish, db_ops, DB_PATH, Booked, book_wish, TableName


def print_db(table_name: TableName) -> None:
    with db_ops(DB_PATH) as cur:
        rows = list(cur.execute(f"SELECT * FROM {table_name.value}"))
        print(rows)


def test_wish() -> None:
    wish = Wish()
    wish.delete()
    wish.create_table()

    booked = Booked()
    booked.delete()
    booked.create_table()

    wish.add(creator_name="10", name="bla", priority=5)
    wish.add(creator_name="10", name="noprio")
    wish.add(creator_name="11", name="test", quantity=5)
    wish.add(creator_name="10", name="TEST", priority=1, quantity=10)
    with db_ops(DB_PATH) as cur:
        rows = list(cur.execute(f"SELECT name, quantity FROM {wish.table_name}"))
        print(rows)

    assert rows[0] == ("bla", None)
    assert rows[2] == ("test", 5)
    assert rows[3] == ("TEST", 10)

    print(wish.search_by_creator_and_booked_value("10"))
    assert [wish[0] for wish in wish.search_by_creator_and_booked_value("10")[0]] == [4, 1, 2]

    book_wish(wish_id=1, presenter_name="PRESENTER")
    book_wish(wish_id=2, presenter_name="PRESENTER2")
    print_db(TableName.WISH)
    print_db(TableName.BOOKED)


def test_booked() -> None:
    booked = Booked()
    booked.delete()
    booked.create_table()

    booked.add(1, 2, 3)
    booked.add(2, 5, 3)
    with db_ops(DB_PATH) as cur:
        rows = list(cur.execute(f"SELECT creator_id, date FROM {booked.table_name}"))
        print(rows)

        # check delay of adding
        assert rows[0][1] != rows[1][1]


if __name__ == "__main__":
    test_wish()
    # test_booked()
