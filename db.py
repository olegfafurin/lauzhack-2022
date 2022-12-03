import logging
import sqlite3
import time
from abc import ABC, abstractmethod
from contextlib import contextmanager
from enum import Enum
from typing import Optional, List, Dict

DB_PATH = "wishlist.db"

logger = logging.getLogger(__name__)


class TableName(Enum):
    CREATOR = "creator"
    PRESENTER = "presenter"
    WISH = "wish"
    RELATION = "relation"
    BOOKED = "booked"
    PRESENTED = "presented"


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
        self.table_name = TableName.CREATOR.value

    def create_table(self) -> None:
        with db_ops(self.db_path) as cur:
            query = f"""CREATE TABLE IF NOT EXISTS {self.table_name} 
                    ( 
                        creator_id TEXT NOT NULL PRIMARY KEY
                    )"""  # TODO: add name
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
        self.table_name = TableName.PRESENTER.value

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
        self.table_name = TableName.WISH.value

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

    # TODO: add photo https://pynative.com/python-sqlite-blob-insert-and-retrieve-digital-data/
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
        self.table_name = TableName.RELATION.value

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
        self.table_name = TableName.BOOKED.value

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


def create_tables_dict() -> Dict[Enum, Table]:
    return {
        TableName.CREATOR: Creator(),
        TableName.PRESENTER: Presenter(),
        TableName.WISH: Wish(),
        TableName.RELATION: Relation(),
        TableName.BOOKED: Booked(),
        TableName.PRESENTED: Presented(),
    }
