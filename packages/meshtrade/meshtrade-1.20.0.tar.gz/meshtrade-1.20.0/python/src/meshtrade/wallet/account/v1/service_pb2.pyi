from buf.validate import validate_pb2 as _validate_pb2
from meshtrade.iam.role.v1 import role_pb2 as _role_pb2
from meshtrade.option.v1 import method_type_pb2 as _method_type_pb2
from meshtrade.type.v1 import sorting_pb2 as _sorting_pb2
from meshtrade.wallet.account.v1 import account_pb2 as _account_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateAccountRequest(_message.Message):
    __slots__ = ("account",)
    ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    account: _account_pb2.Account
    def __init__(self, account: _Optional[_Union[_account_pb2.Account, _Mapping]] = ...) -> None: ...

class UpdateAccountRequest(_message.Message):
    __slots__ = ("account",)
    ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    account: _account_pb2.Account
    def __init__(self, account: _Optional[_Union[_account_pb2.Account, _Mapping]] = ...) -> None: ...

class OpenAccountRequest(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class OpenAccountResponse(_message.Message):
    __slots__ = ("account", "ledger_transaction")
    ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    LEDGER_TRANSACTION_FIELD_NUMBER: _ClassVar[int]
    account: _account_pb2.Account
    ledger_transaction: str
    def __init__(self, account: _Optional[_Union[_account_pb2.Account, _Mapping]] = ..., ledger_transaction: _Optional[str] = ...) -> None: ...

class GetAccountRequest(_message.Message):
    __slots__ = ("name", "populate_ledger_data")
    NAME_FIELD_NUMBER: _ClassVar[int]
    POPULATE_LEDGER_DATA_FIELD_NUMBER: _ClassVar[int]
    name: str
    populate_ledger_data: bool
    def __init__(self, name: _Optional[str] = ..., populate_ledger_data: bool = ...) -> None: ...

class GetAccountByNumberRequest(_message.Message):
    __slots__ = ("account_number", "populate_ledger_data")
    ACCOUNT_NUMBER_FIELD_NUMBER: _ClassVar[int]
    POPULATE_LEDGER_DATA_FIELD_NUMBER: _ClassVar[int]
    account_number: str
    populate_ledger_data: bool
    def __init__(self, account_number: _Optional[str] = ..., populate_ledger_data: bool = ...) -> None: ...

class ListAccountsRequest(_message.Message):
    __slots__ = ("sorting", "populate_ledger_data")
    class Sorting(_message.Message):
        __slots__ = ("field", "order")
        FIELD_FIELD_NUMBER: _ClassVar[int]
        ORDER_FIELD_NUMBER: _ClassVar[int]
        field: str
        order: _sorting_pb2.SortingOrder
        def __init__(self, field: _Optional[str] = ..., order: _Optional[_Union[_sorting_pb2.SortingOrder, str]] = ...) -> None: ...
    SORTING_FIELD_NUMBER: _ClassVar[int]
    POPULATE_LEDGER_DATA_FIELD_NUMBER: _ClassVar[int]
    sorting: ListAccountsRequest.Sorting
    populate_ledger_data: bool
    def __init__(self, sorting: _Optional[_Union[ListAccountsRequest.Sorting, _Mapping]] = ..., populate_ledger_data: bool = ...) -> None: ...

class ListAccountsResponse(_message.Message):
    __slots__ = ("accounts",)
    ACCOUNTS_FIELD_NUMBER: _ClassVar[int]
    accounts: _containers.RepeatedCompositeFieldContainer[_account_pb2.Account]
    def __init__(self, accounts: _Optional[_Iterable[_Union[_account_pb2.Account, _Mapping]]] = ...) -> None: ...

class SearchAccountsRequest(_message.Message):
    __slots__ = ("sorting", "display_name", "populate_ledger_data")
    class Sorting(_message.Message):
        __slots__ = ("field", "order")
        FIELD_FIELD_NUMBER: _ClassVar[int]
        ORDER_FIELD_NUMBER: _ClassVar[int]
        field: str
        order: _sorting_pb2.SortingOrder
        def __init__(self, field: _Optional[str] = ..., order: _Optional[_Union[_sorting_pb2.SortingOrder, str]] = ...) -> None: ...
    SORTING_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    POPULATE_LEDGER_DATA_FIELD_NUMBER: _ClassVar[int]
    sorting: SearchAccountsRequest.Sorting
    display_name: str
    populate_ledger_data: bool
    def __init__(self, sorting: _Optional[_Union[SearchAccountsRequest.Sorting, _Mapping]] = ..., display_name: _Optional[str] = ..., populate_ledger_data: bool = ...) -> None: ...

class SearchAccountsResponse(_message.Message):
    __slots__ = ("accounts",)
    ACCOUNTS_FIELD_NUMBER: _ClassVar[int]
    accounts: _containers.RepeatedCompositeFieldContainer[_account_pb2.Account]
    def __init__(self, accounts: _Optional[_Iterable[_Union[_account_pb2.Account, _Mapping]]] = ...) -> None: ...
