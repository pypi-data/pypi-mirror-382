from base64 import b64decode
from typing import Union, List

from pydantic import model_validator

from apc_hypaship.config import APCBaseModel
from apc_hypaship.models.response.address import Address
from apc_hypaship.models.response.common import Messages
from apc_hypaship.models.response.service import GoodsInfo, Rates


class Label(APCBaseModel):
    content: bytes | None = None
    format: str | None = None
    decoded: bool = False


class Item(APCBaseModel):
    item_number: str | None = None
    tracking_number: str | None = None
    type: str | None = None
    weight: str | None = None
    length: str | None = None
    width: str | None = None
    height: str | None = None
    value: str | None = None
    reference: str | None = None
    label: Label | None = None


class Items(APCBaseModel):
    item: Item | None = None


class ShipmentDetails(APCBaseModel):
    items: Union[Item, List[Item]] | None = None
    number_of_pieces: str | None = None
    total_weight: str | None = None
    volumetric_weight: str | None = None


class Depots(APCBaseModel):
    collecting_depot: str | None = None
    delivery_depot: str | None = None
    delivery_route: str | None = None
    is_scottish: str | None = None
    presort: str | None = None
    request_depot: str | None = None
    route: str | None = None
    seg_code: str | None = None
    zone: str | None = None


class Order(APCBaseModel):
    messages: Messages | None = None
    account_number: list[str] | None = None
    entry_type: str | None = None
    collection_date: str | None = None
    ready_at: str | None = None
    closed_at: str | None = None
    product_code: str | None = None
    rule_name: str | None = None
    item_option: str | None = None
    order_number: str | None = None
    way_bill: str | None = None
    reference: str | None = None
    custom_reference1: str | None = None
    custom_reference2: str | None = None
    custom_reference3: str | None = None
    adult_signature: str | None = None
    depots: Depots | None = None
    collection: Address | None = None
    delivery: Address | None = None
    goods_info: GoodsInfo | None = None
    shipment_details: ShipmentDetails | None = None
    rates: Rates | None = None
    barcode: str | None = None
    delivery_date: str | None = None
    label: Label | None = None
    network_name: str | None = None


class Orders(APCBaseModel):
    account_number: str | None = None
    messages: Messages | None = None
    order: Order | None = None
