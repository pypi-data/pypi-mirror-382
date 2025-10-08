from enum import Enum

from apc_hypaship.config import APCBaseModel


class ParcelSpec(APCBaseModel):
    name: str
    service_code: str
    max_len: float
    max_width: float
    max_height: float | None
    max_weight: float
    max_items: int
    notes: str | None = None


class ParcelSpecs(Enum):
    MAILPACK = ParcelSpec(
        name='MailPack',
        service_code='MP',
        max_len=37.5,
        max_width=29.5,
        max_height=None,
        max_weight=1,
        max_items=1,
        notes='must fit in provided or pre-approved packaging',
    )
    COURIERPACK = ParcelSpec(
        name='CourierPack',
        service_code='CP',
        max_len=54.5,
        max_width=45.5,
        max_height=None,
        max_weight=5,
        max_items=1,
        notes='must fit in provided or pre-approved packaging',
    )
    LIGHTWEIGHTPARCEL = ParcelSpec(
        name='Lightweight Parcel',
        service_code='LW',
        max_len=45.0,
        max_width=35.0,
        max_height=20.0,
        max_weight=5,
        max_items=1,
    )
    STANDARDNEXTDAYPARCEL = ParcelSpec(
        name='Standard Next Day Parcel',
        service_code='ND',
        max_len=120.0,
        max_width=55.0,
        max_height=50.0,
        max_weight=30,
        max_items=20,
        notes='max 60x60x60 also ok',
    )
    NONCONVEYABLEPARCEL = ParcelSpec(
        name='Non-Conveyable Parcel',
        service_code='NC',
        max_len=160.0,
        max_width=60.0,
        max_height=60.0,
        max_weight=30,
        max_items=2,
        notes='width+height < 120 also ok',
    )
