import datetime

from buf.validate import validate_pb2 as _validate_pb2
from meshtrade.type.v1 import ledger_pb2 as _ledger_pb2
from meshtrade.type.v1 import amount_pb2 as _amount_pb2
from meshtrade.studio.instrument.v1 import instrument_type_pb2 as _instrument_type_pb2
from meshtrade.studio.instrument.v1 import unit_pb2 as _unit_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AccountState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ACCOUNT_STATE_UNSPECIFIED: _ClassVar[AccountState]
    ACCOUNT_STATE_CLOSED: _ClassVar[AccountState]
    ACCOUNT_STATE_OPEN: _ClassVar[AccountState]
ACCOUNT_STATE_UNSPECIFIED: AccountState
ACCOUNT_STATE_CLOSED: AccountState
ACCOUNT_STATE_OPEN: AccountState

class Account(_message.Message):
    __slots__ = ("name", "owner", "number", "ledger_id", "ledger", "display_name", "live_data_retrieved_at", "state", "balances")
    NAME_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    LEDGER_ID_FIELD_NUMBER: _ClassVar[int]
    LEDGER_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    LIVE_DATA_RETRIEVED_AT_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    BALANCES_FIELD_NUMBER: _ClassVar[int]
    name: str
    owner: str
    number: str
    ledger_id: str
    ledger: _ledger_pb2.Ledger
    display_name: str
    live_data_retrieved_at: _timestamp_pb2.Timestamp
    state: AccountState
    balances: _containers.RepeatedCompositeFieldContainer[Balance]
    def __init__(self, name: _Optional[str] = ..., owner: _Optional[str] = ..., number: _Optional[str] = ..., ledger_id: _Optional[str] = ..., ledger: _Optional[_Union[_ledger_pb2.Ledger, str]] = ..., display_name: _Optional[str] = ..., live_data_retrieved_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., state: _Optional[_Union[AccountState, str]] = ..., balances: _Optional[_Iterable[_Union[Balance, _Mapping]]] = ...) -> None: ...

class InstrumentMetaData(_message.Message):
    __slots__ = ("name", "type", "unit")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    UNIT_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: _instrument_type_pb2.InstrumentType
    unit: _unit_pb2.Unit
    def __init__(self, name: _Optional[str] = ..., type: _Optional[_Union[_instrument_type_pb2.InstrumentType, str]] = ..., unit: _Optional[_Union[_unit_pb2.Unit, str]] = ...) -> None: ...

class Balance(_message.Message):
    __slots__ = ("amount", "instrument_metadata")
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_METADATA_FIELD_NUMBER: _ClassVar[int]
    amount: _amount_pb2.Amount
    instrument_metadata: InstrumentMetaData
    def __init__(self, amount: _Optional[_Union[_amount_pb2.Amount, _Mapping]] = ..., instrument_metadata: _Optional[_Union[InstrumentMetaData, _Mapping]] = ...) -> None: ...
