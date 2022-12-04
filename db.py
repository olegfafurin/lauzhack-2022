from __future__ import annotations

import logging
import sqlite3
import time
from abc import ABC, abstractmethod
from contextlib import contextmanager
from enum import Enum
from typing import Optional, Dict, List, Tuple

DB_PATH = "../wishlist.db"

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
    def create_table(self) -> Table:
        pass

    @abstractmethod
    def add(self, *args, **kwargs):
        pass


class Creator(Table):
    def __init__(self):
        super().__init__()
        self.table_name = TableName.CREATOR.value

    def create_table(self) -> Table:
        with db_ops(self.db_path) as cur:
            query = f"""CREATE TABLE IF NOT EXISTS {self.table_name} 
                    ( 
                        creator_name TEXT NOT NULL PRIMARY KEY
                    )"""  # TODO: add name
            cur.execute(query)
        return self

    def add(self,
            creator_name: str
            ) -> None:
        with db_ops(self.db_path) as cur:
            cur.execute(
                f"""
                INSERT INTO {self.table_name} VALUES
                    (?)
                """, [creator_name, ])


class Presenter(Table):
    def __init__(self):
        super().__init__()
        self.table_name = TableName.PRESENTER.value

    def create_table(self) -> Table:
        with db_ops(self.db_path) as cur:
            query = f"""CREATE TABLE IF NOT EXISTS {self.table_name} 
                    ( 
                        presenter_name TEXT NOT NULL PRIMARY KEY
                    )"""
            cur.execute(query)
        return self

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

    def create_table(self) -> Table:
        with db_ops(self.db_path) as cur:
            query = f"""CREATE TABLE IF NOT EXISTS {self.table_name}
                    (   
                        wish_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        
                        booked BOOLEAN NOT NULL,
                        presented BOOLEAN NOT NULL,
                        
                        creator_name TEXT NOT NULL,
                        name TEXT NOT NULL,
                        
                        priority INTEGER,
                        relation_type TEXT,
                        link TEXT,
                        price REAL,
                        photo_id TEXT,
                        desc TEXT,
                        quantity INTEGER,
                        FOREIGN KEY(creator_name) REFERENCES creator(creator_name)
                    )"""
            cur.execute(query)
        return self

    def add(self,
            creator_name: str,
            name: str,
            priority: Optional[int] = None,
            relation_type: Optional[str] = None,
            link: Optional[str] = None,
            price: Optional[float] = None,
            photo_id: Optional[str] = None,
            desc: Optional[str] = None,
            quantity: Optional[int] = None
            ) -> None:
        with db_ops(self.db_path) as cur:
            cur.execute(
                f"""
                INSERT INTO {self.table_name} VALUES
                    (null, 0, 0, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, [creator_name, name, priority, relation_type, link, price, photo_id, desc, quantity])

    def search_by_creator_and_booked_value(self, creator_name: str, booked_value_needed: bool = False) -> Tuple[
        List[tuple], List[tuple]]:
        with db_ops(self.db_path) as cur:
            wishes_own = list(cur.execute(
                f"""
                SELECT *
                FROM {self.table_name} 
                WHERE creator_name = ? and booked = ? 
                ORDER BY priority ASC
                NULLS LAST
                """, [creator_name, int(booked_value_needed)]
            )
            )
            wishes_booked_ids = list(cur.execute(
                f"""
                SELECT wish_id
                FROM {TableName.BOOKED.value} 
                WHERE presenter_name = ? 
                """, [creator_name, ]
            ))
            wishes_booked = []
            for wish_id in wishes_booked_ids:
                wishes_booked.append(list(cur.execute(
                    f"""
                    SELECT * FROM {self.table_name} 
                    WHERE wish_id = ? 
                    """, [wish_id, ]
                )
                )
                                     [0])
            return wishes_own, wishes_booked

    def change_booked(self, wish_id: int, booked_value_to_set: bool):
        with db_ops(self.db_path) as cur:
            cur.execute(
                f"""
                UPDATE {self.table_name}
                SET booked = ? 
                WHERE wish_id = ?
                """, [int(booked_value_to_set), wish_id, ]
            )


class Relation(Table):
    def __init__(self):
        super().__init__()
        self.table_name = TableName.RELATION.value

    def create_table(self) -> Table:
        with db_ops(self.db_path) as cur:
            query = f"""CREATE TABLE IF NOT EXISTS {self.table_name} 
                    (
                    relation_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    creator_name TEXT NOT NULL,
                    presenter_name TEXT NOT NULL,
                    relation_type TEXT, 
                    FOREIGN KEY(relation_id) REFERENCES relation(relation_id),
                    FOREIGN KEY(creator_name) REFERENCES creator(creator_name),
                    FOREIGN KEY(presenter_name) REFERENCES presenter(presenter_name)
                    )"""
            cur.execute(query)
        return self

    def add(self,
            creator_name: str,
            presenter_name: str,
            relation_type: RelationType = None,
            ) -> None:
        with db_ops(self.db_path) as cur:
            cur.execute(
                f"""
                INSERT INTO {self.table_name} VALUES
                    (null, ?, ?, ?)
                """, [creator_name, presenter_name, relation_type.value])


class Booked(Table):
    def __init__(self):
        super().__init__()
        self.table_name = TableName.BOOKED.value

    def create_table(self) -> Table:
        with db_ops(self.db_path) as cur:
            query = f"""CREATE TABLE IF NOT EXISTS {self.table_name} 
                    (   
                        wish_id INT NOT NULL,
                        creator_name TEXT NOT NULL,
                        presenter_name TEXT NOT NULL,
                        date INT NOT NULL,
                        FOREIGN KEY(wish_id) REFERENCES present(wish_id),
                        FOREIGN KEY(creator_name) REFERENCES creator(creator_name),
                        FOREIGN KEY(presenter_name) REFERENCES presenter(presenter_name),
                        PRIMARY KEY(wish_id, presenter_name)
                    )"""
            cur.execute(query)
        return self

    def add(self,
            creator_name: str,
            presenter_name: str,
            wish_id: int,
            date: Optional[int] = None,
            ) -> None:
        if not date:
            date = current_time_in_ms_since_1970()
        with db_ops(self.db_path) as cur:
            cur.execute(
                f"""
                INSERT INTO {self.table_name} VALUES
                    (null, ?, ?, ?, ?)
                """, [creator_name, presenter_name, wish_id, date])


class Presented(Booked):
    def __init__(self):
        super().__init__()
        self.table_name = "presented"

    def do_present_wish(self, wish_id: int) -> None:
        ...


def book_wish(wish_id: int, presenter_name: str):
    sql = sqlite3.connect(DB_PATH)
    sql.isolation_level = None
    cur = sql.cursor()
    cur.execute("BEGIN")
    try:
        creator_name_list = list(cur.execute(
            f"""
                SELECT creator_name FROM {TableName.WISH.value}
                WHERE wish_id = ?
            """, [wish_id, ]
        ))
        if not creator_name_list:
            raise ValueError("This wish_id doesn't exist")
        creator_name = creator_name_list[0][0]

        cur.execute(
            f"""
                UPDATE {TableName.WISH.value}
                SET booked = 1 
                WHERE wish_id = ?
            """, [wish_id, ]
        )

        cur.execute(
            f"""
            INSERT INTO {TableName.BOOKED.value} VALUES
                (?, ?, ?, ?)
            """, [wish_id, creator_name, presenter_name, current_time_in_ms_since_1970()]
        )

        cur.execute("COMMIT")
        logger.info(f"Booked wish with wish_id={wish_id}")
    except sql.Error:
        logger.error(f"Booking failed for wish with wish_id={wish_id}")
        cur.execute("ROLLBACK")


def current_time_in_ms_since_1970() -> int:
    return int(time.time() * 1000)


def create_tables_dict() -> Dict[Enum, Table]:
    return {  # TODO make proper singletones
        TableName.CREATOR: Creator().create_table(),
        TableName.PRESENTER: Presenter().create_table(),
        TableName.WISH: Wish().create_table(),
        TableName.RELATION: Relation().create_table(),
        TableName.BOOKED: Booked().create_table(),
        TableName.PRESENTED: Presented().create_table(),
    }
