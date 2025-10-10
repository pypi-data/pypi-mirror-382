import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from meshtrade.type.v1 import amount_pb2 as _amount_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TradingStatementEntry(_message.Message):
    __slots__ = ("transaction_date", "transaction_id", "token_code", "description", "amount", "price", "cost", "balance")
    TRANSACTION_DATE_FIELD_NUMBER: _ClassVar[int]
    TRANSACTION_ID_FIELD_NUMBER: _ClassVar[int]
    TOKEN_CODE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    COST_FIELD_NUMBER: _ClassVar[int]
    BALANCE_FIELD_NUMBER: _ClassVar[int]
    transaction_date: _timestamp_pb2.Timestamp
    transaction_id: str
    token_code: str
    description: str
    amount: _amount_pb2.Amount
    price: _amount_pb2.Amount
    cost: _amount_pb2.Amount
    balance: _amount_pb2.Amount
    def __init__(self, transaction_date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., transaction_id: _Optional[str] = ..., token_code: _Optional[str] = ..., description: _Optional[str] = ..., amount: _Optional[_Union[_amount_pb2.Amount, _Mapping]] = ..., price: _Optional[_Union[_amount_pb2.Amount, _Mapping]] = ..., cost: _Optional[_Union[_amount_pb2.Amount, _Mapping]] = ..., balance: _Optional[_Union[_amount_pb2.Amount, _Mapping]] = ...) -> None: ...
