from apc_hypaship.config import APCBaseModel

error_dict = {
    '201': 'Invalid Postcode',
    '202': 'Invalid Date',
    'ERROR': 'General Error',
}


class APCException(Exception):
    def __init__(self, message, code=None, error_fields=None):
        super().__init__(message)
        self.code = code
        self.error_fields = error_fields
        self.error_dict_message = error_dict.get(code, 'Unknown error code')


class ErrorField(APCBaseModel):
    field_name: str | None = None
    error_message: str | None = None


class ErrorFields(APCBaseModel):
    error_field: ErrorField | None = None


class Messages(APCBaseModel):
    code: str | None = None
    description: str | None = None
    error_fields: ErrorFields | None = None

    def raise_for_errors(self):
        if self.code == 'SUCCESS':
            return
        if self.code not in error_dict:
            raise ValueError(f'Unknown error code: {self.code} Please add to dictionary.')
        msg = 'APC Message'
        msg += f' {self.code}' if self.code else ''
        msg += f': {self.description}' if self.description else ''
        if self.error_fields:
            if ef := self.error_fields.error_field:
                msg += f' - {ef.field_name}: {ef.error_message}'
        raise APCException(
            msg,
            code=self.code,
            error_fields=self.error_fields.error_field if self.error_fields else None,
        )
