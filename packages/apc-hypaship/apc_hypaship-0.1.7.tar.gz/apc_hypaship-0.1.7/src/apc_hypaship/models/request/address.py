# from pawdantic.paw_types import str_length_const

from apc_hypaship.config import APCBaseModel, str_length_const


class Contact(APCBaseModel):
    person_name: str
    phone_number: str | None = None
    mobile_number: str
    email: str | None


class Address(APCBaseModel):
    contact: Contact
    company_name: str = str_length_const(34)
    address_line_1: str_length_const(64)
    address_line_2: str_length_const(64) | None = None
    city: str
    county: str | None = None
    postal_code: str
    country_code: str = 'GB'
    country_name: str | None = None
    instructions: str | None = None
    safeplace: str | None = None


class AddressDelivery(Address):
    instructions: str = ''

