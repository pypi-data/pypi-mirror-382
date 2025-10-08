import json
from enum import StrEnum

from httpx import HTTPStatusError
from loguru import logger

from apc_hypaship.config import APCBaseModel


class AlertType(StrEnum):
    ERROR = 'ERROR'
    WARNING = 'WARNING'
    NOTIFICATION = 'NOTIFICATION'


class Alert(APCBaseModel):
    code: int | None = None
    message: str
    type: AlertType = AlertType.NOTIFICATION

    def __eq__(self, other):
        if not isinstance(other, Alert):
            return NotImplemented
        return (self.code, self.message, self.type) == (other.code, other.message, other.type)

    def __hash__(self):
        return hash((self.code, self.message, self.type))

    @classmethod
    def from_exception(cls, e: Exception):
        return cls(message=str(e), type=AlertType.ERROR)

async def apc_http_status_alerts(exception: HTTPStatusError) -> list[Alert]:
    error_dict = extract_http_error_message_json(exception)
    return [Alert(message=f'{error_dict.get('Code')}:  {error_dict.get('Description')}', type=AlertType.ERROR)]


def extract_http_error_message(exception: HTTPStatusError) -> str:
    if hasattr(exception, 'response') and exception.response is not None:
        return exception.response.text
    logger.warning('HTTPStatusError has no response attribute')
    return str(exception)


def extract_http_error_message_json(exception: HTTPStatusError) -> dict:
    error_string = extract_http_error_message(exception)
    try:
        error_data = json.loads(error_string)
        return error_data.get('Messages')

    except json.JSONDecodeError:
        logger.warning('Error.response.text is not valid JSON')
        return {'Code': error_string, 'Description': ''}

