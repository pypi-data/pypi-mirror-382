from buf.validate import validate_pb2 as _validate_pb2
from meshtrade.iam.role.v1 import role_pb2 as _role_pb2
from meshtrade.option.v1 import method_type_pb2 as _method_type_pb2
from meshtrade.ledger.transaction.v1 import transaction_state_pb2 as _transaction_state_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetTransactionStateRequest(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class GetTransactionStateResponse(_message.Message):
    __slots__ = ("state",)
    STATE_FIELD_NUMBER: _ClassVar[int]
    state: _transaction_state_pb2.TransactionState
    def __init__(self, state: _Optional[_Union[_transaction_state_pb2.TransactionState, str]] = ...) -> None: ...

class MonitorTransactionStateRequest(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class MonitorTransactionStateResponse(_message.Message):
    __slots__ = ("state",)
    STATE_FIELD_NUMBER: _ClassVar[int]
    state: _transaction_state_pb2.TransactionState
    def __init__(self, state: _Optional[_Union[_transaction_state_pb2.TransactionState, str]] = ...) -> None: ...
