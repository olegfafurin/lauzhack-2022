# TODO make tests correctly automatic without using actual db
from db import Creator, Wish, db_ops, DB_PATH, Booked


def test_wish() -> None:
    creator = Creator()
    creator.delete()
    creator.create_table()

    wish = Wish()
    wish.delete()
    wish.create_table()
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

        assert wish.search_by_creator("10") == [4, 1, 2]


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
    # test_wish()
    # test_booked()

    wish = Wish()
    wish.delete()
