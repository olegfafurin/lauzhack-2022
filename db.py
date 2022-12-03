import logging
import sqlite3
from abc import ABC, abstractmethod
from contextlib import contextmanager
from enum import Enum
from typing import Optional

DB_PATH = "wishlist.db"

logging.basicConfig(level=logging.DEBUG, format='%(message)s')  # TODO make set up in main.py
logger = logging.getLogger(__name__)


class RelationType(Enum):
    FRIEND = "friend"


@contextmanager
def db_ops(db_name):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    yield cur
    conn.commit()
    conn.close()


class Table(ABC):
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.table_name = ""

    def delete(self):
        with db_ops(self.db_path) as cur:
            cur.execute(f"DROP TABLE IF EXISTS {self.table_name}")

    @abstractmethod
    def create_table(self):
        pass

    @abstractmethod
    def add(self, *args, **kwargs):
        pass


class Creator(Table):
    def __init__(self):
        super().__init__()
        self.table_name = "creator"

    def create_table(self) -> None:
        with db_ops(self.db_path) as cur:
            query = f"""CREATE TABLE IF NOT EXISTS {self.table_name} 
                    ( 
                        telegram_id INT 
                        deadline DATE
                    )"""
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


class Presenter(Table):
    def __init__(self):
        super().__init__()
        self.table_name = "presenter"

    def create_table(self) -> None:
        with db_ops(self.db_path) as cur:
            query = f"""CREATE TABLE IF NOT EXISTS {self.table_name} 
                    ( 
                        telegram_id INT
                    )"""
            cur.execute(query)

    def add(self, telegram_id: int) -> None:
        with db_ops(self.db_path) as cur:
            cur.execute(
                f"""
                INSERT INTO {self.table_name} VALUES
                    (?)
                """, [telegram_id, ])


class Wish(Table):
    def __init__(self):
        super().__init__()
        self.table_name = "wish"

    def create_table(self) -> None:
        with db_ops(self.db_path) as cur:
            query = f"""CREATE TABLE IF NOT EXISTS {self.table_name}
                    (
                        name TEXT,
                        booked BOOLEAN,
                        presented BOOLEAN,
                        priority INT,
                        link TEXT,
                        price REAL,
                        quantity INT
                    )"""
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


class Friendship(Table):
    def __init__(self):
        super().__init__()
        self.table_name = "friendship"

    def create_table(self) -> None:
        with db_ops(self.db_path) as cur:
            query = f"""CREATE TABLE IF NOT EXISTS {self.table_name} 
                    ( 
                    creator_id INT, 
                    presenter_id INT, 
                    type TEXT 
                    )"""
            cur.execute(query)

    def add(self,
            creator_id: int,
            presenter_id: int,
            relation_type: RelationType = RelationType.FRIEND,
            ) -> None:
        with db_ops(self.db_path) as cur:
            cur.execute(
                f"""
                INSERT INTO {self.table_name} VALUES
                    (?, ?, ?)
                """, [creator_id, presenter_id, relation_type.value])


class Presented(Table):
    def __init__(self):
        super().__init__()
        self.table_name = "presented"

    def create_table(self) -> None:
        with db_ops(self.db_path) as cur:
            query = f"""CREATE TABLE IF NOT EXISTS {self.table_name} 
                    ( 
                        present_id INT,
                        creator_id INT, 
                        presenter_id INT
                    )"""
            cur.execute(query)

    def add(self,
            creator_id: int,
            presenter_id: int,
            present_id: int,
            ) -> None:
        with db_ops(self.db_path) as cur:
            cur.execute(
                f"""
                INSERT INTO {self.table_name} VALUES
                    (?, ?, ?)
                """, [creator_id, presenter_id, present_id])


# TODO make test normal without using actual db
def test_wish() -> None:
    wish = Wish()
    wish.delete()
    wish.create_table()
    wish.add(name="bla")
    wish.add(name="blablab", quantity=5)
    with db_ops(DB_PATH) as cur:
        rows = list(cur.execute(f"SELECT name, quantity FROM {wish.table_name}"))
        assert rows[0] == ("bla", None)
        assert rows[1] == ("blablab", 5)


if __name__ == "__main__":
    test_wish()
