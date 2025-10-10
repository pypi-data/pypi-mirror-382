import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from meshtrade.type.v1 import token_pb2 as _token_pb2
from meshtrade.type.v1 import address_pb2 as _address_pb2
from meshtrade.reporting.account_report.v1 import fee_entry_pb2 as _fee_entry_pb2
from meshtrade.reporting.account_report.v1 import income_entry_pb2 as _income_entry_pb2
from meshtrade.reporting.account_report.v1 import trading_statement_entry_pb2 as _trading_statement_entry_pb2
from meshtrade.reporting.account_report.v1 import disclaimer_pb2 as _disclaimer_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AccountReport(_message.Message):
    __slots__ = ("income_entries", "fee_entries", "trading_statement_entries", "reporting_currency", "period", "generation_date", "account_number", "disclaimers", "client_address", "client_name", "copyright")
    class Period(_message.Message):
        __slots__ = ("period_start", "period_end")
        PERIOD_START_FIELD_NUMBER: _ClassVar[int]
        PERIOD_END_FIELD_NUMBER: _ClassVar[int]
        period_start: _timestamp_pb2.Timestamp
        period_end: _timestamp_pb2.Timestamp
        def __init__(self, period_start: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., period_end: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
    INCOME_ENTRIES_FIELD_NUMBER: _ClassVar[int]
    FEE_ENTRIES_FIELD_NUMBER: _ClassVar[int]
    TRADING_STATEMENT_ENTRIES_FIELD_NUMBER: _ClassVar[int]
    REPORTING_CURRENCY_FIELD_NUMBER: _ClassVar[int]
    PERIOD_FIELD_NUMBER: _ClassVar[int]
    GENERATION_DATE_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_NUMBER_FIELD_NUMBER: _ClassVar[int]
    DISCLAIMERS_FIELD_NUMBER: _ClassVar[int]
    CLIENT_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    CLIENT_NAME_FIELD_NUMBER: _ClassVar[int]
    COPYRIGHT_FIELD_NUMBER: _ClassVar[int]
    income_entries: _containers.RepeatedCompositeFieldContainer[_income_entry_pb2.IncomeEntry]
    fee_entries: _containers.RepeatedCompositeFieldContainer[_fee_entry_pb2.FeeEntry]
    trading_statement_entries: _containers.RepeatedCompositeFieldContainer[_trading_statement_entry_pb2.TradingStatementEntry]
    reporting_currency: _token_pb2.Token
    period: AccountReport.Period
    generation_date: _timestamp_pb2.Timestamp
    account_number: str
    disclaimers: _containers.RepeatedCompositeFieldContainer[_disclaimer_pb2.Disclaimer]
    client_address: _address_pb2.Address
    client_name: str
    copyright: str
    def __init__(self, income_entries: _Optional[_Iterable[_Union[_income_entry_pb2.IncomeEntry, _Mapping]]] = ..., fee_entries: _Optional[_Iterable[_Union[_fee_entry_pb2.FeeEntry, _Mapping]]] = ..., trading_statement_entries: _Optional[_Iterable[_Union[_trading_statement_entry_pb2.TradingStatementEntry, _Mapping]]] = ..., reporting_currency: _Optional[_Union[_token_pb2.Token, _Mapping]] = ..., period: _Optional[_Union[AccountReport.Period, _Mapping]] = ..., generation_date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., account_number: _Optional[str] = ..., disclaimers: _Optional[_Iterable[_Union[_disclaimer_pb2.Disclaimer, _Mapping]]] = ..., client_address: _Optional[_Union[_address_pb2.Address, _Mapping]] = ..., client_name: _Optional[str] = ..., copyright: _Optional[str] = ...) -> None: ...
