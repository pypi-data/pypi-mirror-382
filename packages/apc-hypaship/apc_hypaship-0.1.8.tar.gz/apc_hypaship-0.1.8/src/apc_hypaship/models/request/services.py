from types import MappingProxyType

from pydantic import ConfigDict

from apc_hypaship.config import APCBaseModel

APC_SERVICES_DICT = dict(
    NEXT_DAY="ND16",
    NEXT_DAY_12="ND12",
    NEXT_DAY_9="ND09",
)


class ServiceSpec(APCBaseModel):
    model_config = ConfigDict(extra="ignore")
    Carrier: str
    CollectionDate: str
    Currency: str
    DeliveryGroup: str
    EstimatedDeliveryDate: str
    ExtraCharges: str
    FuelCharge: str
    InsuranceCharge: str
    ItemType: str
    LatestBookingDateTime: str
    MaxCompensation: str
    MaxItemHeight: str
    MaxItemLength: str
    MaxItemWidth: str
    MaxTransitDays: str
    MinTransitDays: str
    ProductCode: str
    Rate: str
    ServiceName: str
    Signed: str
    TotalCost: str
    Tracked: str
    Vat: str
    VolumetricWeight: str
    WeightUnit: str


