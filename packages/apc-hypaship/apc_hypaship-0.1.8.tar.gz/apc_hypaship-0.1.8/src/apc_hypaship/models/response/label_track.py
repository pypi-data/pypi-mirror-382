from apc_hypaship.config import APCBaseModel
from apc_hypaship.models.response.address import Address
from apc_hypaship.models.response.common import Messages
from apc_hypaship.models.response.service import GoodsInfo
from apc_hypaship.models.response.shipment import Depots, ShipmentDetails


class Track(APCBaseModel):
    adult_signature: str | None = None
    closed_at: str | None = None
    collection: Address | None = None
    collection_date: str | None = None
    custom_reference1: str | None = None
    custom_reference2: str | None = None
    custom_reference3: str | None = None
    delivery: Address | None = None
    depots: Depots | None = None
    goods_info: GoodsInfo | None = None
    item_option: str | None = None
    order_number: str | None = None
    product_code: str | None = None
    ready_at: str | None = None
    reference: str | None = None
    shipment_details: ShipmentDetails | None = None
    way_bill: str | None = None


class Tracks(APCBaseModel):
    account_number: str | None = None
    messages: Messages | None = None
    track: Track | None = None
