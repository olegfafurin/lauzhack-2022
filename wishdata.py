from dataclasses import dataclass
from typing import Optional


@dataclass
class WishData:
    creator_name: str

    booked: bool
    presented: bool

    wish_id: Optional[int] = None
    name: Optional[str] = None

    priority: Optional[int] = None
    relation_type: Optional[str] = None
    link: Optional[str] = None
    price: Optional[str] = None
    photo: Optional[bytearray] = None
    desc: Optional[str] = None
    quantity: Optional[str] = None
