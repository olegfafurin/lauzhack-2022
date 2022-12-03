from dataclasses import dataclass
from typing import Optional

PHOTO_PLACEHOLDER = "Some photo"


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

    def __repr__(self):
        d = self.__dict__
        if d["photo"]:
            d["photo"] = PHOTO_PLACEHOLDER
        return d.__repr__()
