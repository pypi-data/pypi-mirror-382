from apc_hypaship.models.request.address import Address as _Address, Contact as _Contact


class Contact(_Contact):
    person_name: str | None = None
    mobile_number: str | None = None
    email: str | None = None


class Address(_Address):
    company_name: str | None = None
    address_line_1: str | None = None
    postal_code: str | None = None
    city: str | None = None
    country_code: str | None = None
    contact: Contact | None = None
