import sqlite3
from typing import Optional

from contextlib import contextmanager

DB_PATH = "wishlist.db"


@contextmanager
def db_ops(db_name):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    yield cur
    conn.commit()
    conn.close()


class Creator:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.table_name = "creator"

    def create_table(self) -> None:
        with db_ops(self.db_path) as cur:
            query = f"CREATE TABLE IF NOT EXISTS {self.table_name}(" \
                        f"telegram_id INT" \
                        f")"
            cur.execute(query)

    def add(self,
            telegram_id: str,
            deadline: Optional[str] = None
            ) -> None:
        with db_ops(self.db_path) as cur:
            cur.execute(
                """
                INSERT INTO creator VALUES
                    (?, ?)
                """, [telegram_id, deadline])


class Presenter:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.table_name = "presenter"

    def create_table(self) -> None:
        with db_ops(self.db_path) as cur:
            query = f"CREATE TABLE IF NOT EXISTS {self.table_name}(" \
                        f"telegram_id INT," \
                        f"name TEXT)"
            cur.execute(query)

    def add(self, telegram_id: int) -> None:
        with db_ops(self.db_path) as cur:
            cur.execute(
                f"""
                INSERT INTO {self.table_name} VALUES
                    (?)
                """, [telegram_id, ])


class Wish:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.table_name = "wish"

    def delete(self):
        with db_ops(self.db_path) as cur:
            cur.execute(f"DROP TABLE IF EXISTS {self.table_name}")

    def create_table(self) -> None:
        with db_ops(self.db_path) as cur:
            query = f"CREATE TABLE IF NOT EXISTS {self.table_name}" \
                    f"(" \
                    f"name TEXT," \
                    f"booked BOOLEAN," \
                    f"presented BOOLEAN," \
                    f"priority INT," \
                    f"link TEXT," \
                    f"price REAL," \
                    f"quantity INT" \
            f")"
            cur.execute(query)

    # TODO: add photo
    def add(self,
            name: str,
            priority: Optional[int] = None,
            link: Optional[str] = None,
            price: Optional[float] = None,
            quantity: Optional[int] = None
            ) -> None:
        with db_ops(self.db_path) as cur:
            cur.execute(
                f"""
                INSERT INTO {self.table_name} VALUES
                    (?, 0, 0, ?, ?, ?, ?)
                """, [name, priority, link, price, quantity])


if __name__ == "__main__":
    # tests?
    wish = Wish()
    wish.delete()
    wish.create_table()
    wish.add(name="bla")
    wish.add(name="blablab", quantity=5)
    with db_ops(DB_PATH) as cur:
        for row in cur.execute(f"SELECT name, quantity FROM {wish.table_name}"):
            print(row)

