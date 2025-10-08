from pydantic import Field

from apc_hypaship.config import APCBaseModel
from apc_hypaship.models.request.shipment import GoodsInfo as _GoodsInfo


class GoodsInfo(_GoodsInfo):
    goods_description: str | None = None
    non_conv: str | None = None
    charge_on_delivery: str | None = None
    goods_value: str | None = None


class Rates(APCBaseModel):
    rate: str | None = None
    extra_charges: str | None = None
    fuel_charge: str | None = None
    insurance_charge: str | None = None
    vat: str | None = None
    total_cost: str | None = None
    currency: str | None = None


class Service(APCBaseModel):
    carrier: str | None = None
    service_name: str | None = None
    product_code: str | None = None
    min_transit_days: str | None = None
    max_transit_days: str | None = None
    tracked: str | None = None
    signed: str | None = None
    max_compensation: str | None = None
    max_item_length: str | None = None
    max_item_width: str | None = None
    max_item_height: str | None = None
    item_type: str | None = None
    delivery_group: str | None = None
    collection_date: str | None = None
    estimated_delivery_date: str | None = None
    latest_booking_date_time: str | None = None
    rate: str | None = None
    extra_charges: str | None = None
    fuel_charge: str | None = None
    insurance_charge: str | None = None
    vat: str | None = None
    total_cost: str | None = None
    currency: str | None = None
    volumetric_weight: str | None = None
    weight_unit: str | None = None


class Services(APCBaseModel):
    service: list[Service] = Field(default_factory=list)