from typing import Literal

import httpx
from loguru import logger

from apc_hypaship.config import APCSettings, APCBaseModel
from apc_hypaship.models.response.label_track import Tracks
from apc_hypaship.models.response.resp import BookingResponse, ServiceAvailabilityResponse
from apc_hypaship.models.response.shipment import Label
from apc_hypaship.models.request.shipment import Shipment

ResponseMode = Literal['raw'] | Literal['json'] | type


class APCClient(APCBaseModel):
    settings: APCSettings

    def do_post(
        self,
        *,
        url: str,
        data: dict | None = None,
    ) -> httpx.Response:
        headers = self.settings.headers
        res = httpx.post(url, headers=headers, json=data, timeout=30)
        res.raise_for_status()
        return res

    def do_get(
        self,
        *,
        url: str,
        params: dict | None = None,
    ) -> httpx.Response:
        headers = self.settings.headers
        res = httpx.get(url, headers=headers, params=params, timeout=30)
        res.raise_for_status()
        return res

    def fetch_service_available(
        self,
        shipment: Shipment,
    ) -> ServiceAvailabilityResponse:
        shipment_dict = shipment.model_dump(by_alias=True, mode='json')
        res = self.do_post(url=self.settings.services_endpoint, data=shipment_dict)
        return ServiceAvailabilityResponse(**res.json())

    def fetch_book_shipment(
        self,
        shipment: Shipment,
    ) -> BookingResponse:
        shipment_dict = shipment.model_dump(by_alias=True, mode='json')
        res = self.do_post(url=self.settings.orders_endpoint, data=shipment_dict)
        response = BookingResponse(**res.json())
        response.raise_for_errors()
        return response

    def fetch_label(
        self,
        shipment_num: str,
        format: Literal['PDF'] = 'PDF',
    ) -> Label:
        params = {'labelformat': format}
        label = self.do_get(
            url=self.settings.one_order_endpoint(shipment_num),
            params=params,
        )
        label = BookingResponse(**label.json())
        return label.orders.order.label

    def fetch_tracks(
        self,
        shipment_num: str,
    ) -> Tracks:
        res = self.do_get(url=self.settings.track_endpoint(shipment_num))
        res = res.json()
        t = res.get('Tracks')
        return Tracks(**t)



