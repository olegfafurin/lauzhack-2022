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


def from_tuple(t):
    return WishData(
        wish_id=t[0],
        booked=t[1],
        presented=t[2],
        creator_name=t[3],
        name=t[4],
        priority=t[5],
        relation_type=t[6],
        link=t[7],
        price=t[8],
        photo=t[9],
        desc=t[10],
        quantity=t[11],
    )
