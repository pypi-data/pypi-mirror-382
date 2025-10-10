import datetime

from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from meshtrade.iam.role.v1 import role_pb2 as _role_pb2
from meshtrade.option.v1 import method_type_pb2 as _method_type_pb2
from meshtrade.reporting.account_report.v1 import account_report_pb2 as _account_report_pb2
from meshtrade.type.v1 import token_pb2 as _token_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetAccountReportRequest(_message.Message):
    __slots__ = ("account_number", "period_start", "period_end", "reporting_asset_token")
    ACCOUNT_NUMBER_FIELD_NUMBER: _ClassVar[int]
    PERIOD_START_FIELD_NUMBER: _ClassVar[int]
    PERIOD_END_FIELD_NUMBER: _ClassVar[int]
    REPORTING_ASSET_TOKEN_FIELD_NUMBER: _ClassVar[int]
    account_number: str
    period_start: _timestamp_pb2.Timestamp
    period_end: _timestamp_pb2.Timestamp
    reporting_asset_token: _token_pb2.Token
    def __init__(self, account_number: _Optional[str] = ..., period_start: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., period_end: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., reporting_asset_token: _Optional[_Union[_token_pb2.Token, _Mapping]] = ...) -> None: ...

class GetExcelAccountReportRequest(_message.Message):
    __slots__ = ("account_number", "period_start", "period_end", "reporting_asset_token")
    ACCOUNT_NUMBER_FIELD_NUMBER: _ClassVar[int]
    PERIOD_START_FIELD_NUMBER: _ClassVar[int]
    PERIOD_END_FIELD_NUMBER: _ClassVar[int]
    REPORTING_ASSET_TOKEN_FIELD_NUMBER: _ClassVar[int]
    account_number: str
    period_start: _timestamp_pb2.Timestamp
    period_end: _timestamp_pb2.Timestamp
    reporting_asset_token: _token_pb2.Token
    def __init__(self, account_number: _Optional[str] = ..., period_start: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., period_end: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., reporting_asset_token: _Optional[_Union[_token_pb2.Token, _Mapping]] = ...) -> None: ...

class GetExcelAccountReportResponse(_message.Message):
    __slots__ = ("excel_base64",)
    EXCEL_BASE64_FIELD_NUMBER: _ClassVar[int]
    excel_base64: str
    def __init__(self, excel_base64: _Optional[str] = ...) -> None: ...
