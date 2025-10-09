from datetime import date, time
from typing import Literal, Sequence

from pydantic import Field, model_validator
from loguru import logger

from apc_hypaship.models.request.address import Address
from apc_hypaship.config import APCBaseModel


class Item(APCBaseModel):
    type: Literal["ALL"] = "ALL"
    weight: float | None = 12
    length: float | None = None
    width: float | None = None
    height: float | None = None
    reference: str | None = None


class Items(APCBaseModel):
    item: Sequence[Item] = Field(default_factory=list)


class ShipmentDetails(APCBaseModel):
    number_of_pieces: int
    items: Items | None = None

    @model_validator(mode="after")
    def check_items(self):
        if not self.items:
            self.items = Items(item=[Item() for _ in range(self.number_of_pieces)])
            logger.debug("Auto-filled items with weight = 12kg per box")
        return self


class GoodsInfo(APCBaseModel):
    goods_value: str = "1000"
    goods_description: str = "Radios"
    fragile: bool = False
    security: bool = False
    increased_liability: bool = False
    premium_insurance: bool = False
    premium: bool = False




class Order(APCBaseModel):
    collection_date: date
    ready_at: time = time(hour=9)
    closed_at: time = time(hour=17)
    product_code: str
    reference: str
    collection: Address | None = None
    delivery: Address
    goods_info: GoodsInfo
    shipment_details: ShipmentDetails


class Orders(APCBaseModel):
    order: Order


class Shipment(APCBaseModel):
    orders: Orders

    @classmethod
    def from_order(cls, order: Order) -> "Shipment":
        return cls(orders=Orders(order=order))
