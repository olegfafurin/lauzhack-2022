import logging
import sqlite3
import time
from abc import ABC, abstractmethod
from contextlib import contextmanager
from enum import Enum
from typing import Optional, List

DB_PATH = "wishlist.db"

logging.basicConfig(level=logging.DEBUG, format='%(message)s')  # TODO make set up in main.py
logger = logging.getLogger(__name__)


class RelationType(Enum):
    PRIVATE = "private"
    FRIEND = "friend"
    FAMILY = "family"


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
                        creator_id INT NOT NULL PRIMARY KEY
                    )"""
            cur.execute(query)

    def add(self,
            telegram_id: str
            ) -> None:
        with db_ops(self.db_path) as cur:
            cur.execute(
                f"""
                INSERT INTO {self.table_name} VALUES
                    (?)
                """, [telegram_id, ])


class Presenter(Table):
    def __init__(self):
        super().__init__()
        self.table_name = "presenter"

    def create_table(self) -> None:
        with db_ops(self.db_path) as cur:
            query = f"""CREATE TABLE IF NOT EXISTS {self.table_name} 
                    ( 
                        presenter_id INT NOT NULL PRIMARY KEY
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
                        wish_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        
                        creator_id INTEGER NOT NULL,
                        name TEXT NOT NULL,
                        
                        booked BOOLEAN NOT NULL,
                        presented BOOLEAN NOT NULL,
                        
                        priority INTEGER,
                        relation_type TEXT,
                        link TEXT,
                        price REAL,
                        quantity INTEGER,
                        FOREIGN KEY(creator_id) REFERENCES creator(creator_id)
                    )"""
            cur.execute(query)

    # TODO: add photo
    def add(self,
            creator_id: int,
            name: str,
            priority: Optional[int] = None,
            relation_type: Optional[int] = None,
            link: Optional[str] = None,
            price: Optional[float] = None,
            quantity: Optional[int] = None
            ) -> None:
        with db_ops(self.db_path) as cur:
            cur.execute(
                f"""
                INSERT INTO {self.table_name} VALUES
                    (null, ?, ?, 0, 0, ?, ?, ?, ?)
                """, [creator_id, name, priority, relation_type, link, price, quantity])

    def search_by_creator(self, creator_id: int) -> List[int]:
        with db_ops(self.db_path) as cur:
            return list(res[0] for res in cur.execute(
                f"""
                SELECT wish_id FROM {self.table_name} 
                WHERE creator_id = ?
                ORDER BY priority ASC
                NULLS LAST
                """, [creator_id, ]
            )
                        )


class Relation(Table):
    def __init__(self):
        super().__init__()
        self.table_name = "relation"

    def create_table(self) -> None:
        with db_ops(self.db_path) as cur:
            query = f"""CREATE TABLE IF NOT EXISTS {self.table_name} 
                    (
                    relation_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    creator_id INT NOT NULL FOREIGN KEY REFERENCES creator(creator_id),
                    presenter_id INT NOT NULL,
                    relation_type TEXT, 
                    FOREIGN KEY(relation_id) REFERENCES relation(relation_id),
                    FOREIGN KEY(creator_id) REFERENCES creator(creator_id),
                    FOREIGN KEY(presenter_id) REFERENCES presenter(presenter_id)
                    )"""
            cur.execute(query)

    def add(self,
            creator_id: int,
            presenter_id: int,
            relation_type: RelationType = None,
            ) -> None:
        with db_ops(self.db_path) as cur:
            cur.execute(
                f"""
                INSERT INTO {self.table_name} VALUES
                    (null, ?, ?, ?)
                """, [creator_id, presenter_id, relation_type.value])


class Booked(Table):
    def __init__(self):
        super().__init__()
        self.table_name = "booked"

    def create_table(self) -> None:
        with db_ops(self.db_path) as cur:
            query = f"""CREATE TABLE IF NOT EXISTS {self.table_name} 
                    (   
                        {self.table_name}_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        wish_id INT NOT NULL,
                        creator_id INT NOT NULL,
                        presenter_id INT NOT NULL,
                        date INT NOT NULL,
                        FOREIGN KEY(wish_id) REFERENCES present(wish_id),
                        FOREIGN KEY(creator_id) REFERENCES creator(creator_id),
                        FOREIGN KEY(presenter_id) REFERENCES presenter(presenter_id)
                    )"""
            cur.execute(query)

    def add(self,
            creator_id: int,
            presenter_id: int,
            wish_id: int,
            date: Optional[int] = None
            ) -> None:
        if not date:
            date = int(time.time() * 1000)
        with db_ops(self.db_path) as cur:
            cur.execute(
                f"""
                INSERT INTO {self.table_name} VALUES
                    (null, ?, ?, ?, ?)
                """, [creator_id, presenter_id, wish_id, date])


class Presented(Booked):
    def __init__(self):
        super().__init__()
        self.table_name = "presented"

    def do_present_wish(self, wish_id: int) -> None:
        ...


# TODO make tests correctly automatic without using actual db
def test_wish() -> None:
    creator = Creator()
    creator.delete()
    creator.create_table()

    wish = Wish()
    wish.delete()
    wish.create_table()
    wish.add(creator_id=10, name="bla", priority=5)
    wish.add(creator_id=10, name="noprio")
    wish.add(creator_id=11, name="test", quantity=5)
    wish.add(creator_id=10, name="TEST", priority=1, quantity=10)
    with db_ops(DB_PATH) as cur:
        rows = list(cur.execute(f"SELECT name, quantity FROM {wish.table_name}"))
        print(rows)

        assert rows[0] == ("bla", None)
        assert rows[2] == ("test", 5)
        assert rows[3] == ("TEST", 10)

        assert wish.search_by_creator(10) == [4, 1, 2]


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
    test_booked()
