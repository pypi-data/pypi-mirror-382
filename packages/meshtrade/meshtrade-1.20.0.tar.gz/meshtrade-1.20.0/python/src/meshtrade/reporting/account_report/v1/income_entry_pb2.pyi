import datetime

from meshtrade.type.v1 import token_pb2 as _token_pb2
from meshtrade.type.v1 import amount_pb2 as _amount_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class IncomeNarrative(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    INCOME_NARRATIVE_UNSPECIFIED: _ClassVar[IncomeNarrative]
    INCOME_NARRATIVE_YIELD: _ClassVar[IncomeNarrative]
    INCOME_NARRATIVE_DIVIDEND: _ClassVar[IncomeNarrative]
    INCOME_NARRATIVE_INTEREST: _ClassVar[IncomeNarrative]
    INCOME_NARRATIVE_PRINCIPAL: _ClassVar[IncomeNarrative]
    INCOME_NARRATIVE_DISTRIBUTION: _ClassVar[IncomeNarrative]
    INCOME_NARRATIVE_PROFIT_DISTRIBUTION: _ClassVar[IncomeNarrative]
INCOME_NARRATIVE_UNSPECIFIED: IncomeNarrative
INCOME_NARRATIVE_YIELD: IncomeNarrative
INCOME_NARRATIVE_DIVIDEND: IncomeNarrative
INCOME_NARRATIVE_INTEREST: IncomeNarrative
INCOME_NARRATIVE_PRINCIPAL: IncomeNarrative
INCOME_NARRATIVE_DISTRIBUTION: IncomeNarrative
INCOME_NARRATIVE_PROFIT_DISTRIBUTION: IncomeNarrative

class IncomeEntry(_message.Message):
    __slots__ = ("asset_name", "token", "date", "description", "narrative", "amount", "reported_currency_value")
    ASSET_NAME_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    NARRATIVE_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    REPORTED_CURRENCY_VALUE_FIELD_NUMBER: _ClassVar[int]
    asset_name: str
    token: _token_pb2.Token
    date: _timestamp_pb2.Timestamp
    description: str
    narrative: IncomeNarrative
    amount: _amount_pb2.Amount
    reported_currency_value: _amount_pb2.Amount
    def __init__(self, asset_name: _Optional[str] = ..., token: _Optional[_Union[_token_pb2.Token, _Mapping]] = ..., date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., description: _Optional[str] = ..., narrative: _Optional[_Union[IncomeNarrative, str]] = ..., amount: _Optional[_Union[_amount_pb2.Amount, _Mapping]] = ..., reported_currency_value: _Optional[_Union[_amount_pb2.Amount, _Mapping]] = ...) -> None: ...
