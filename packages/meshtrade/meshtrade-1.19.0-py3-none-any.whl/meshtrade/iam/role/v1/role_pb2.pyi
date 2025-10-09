from google.protobuf import descriptor_pb2 as _descriptor_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Role(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ROLE_UNSPECIFIED: _ClassVar[Role]
    ROLE_WALLET_ADMIN: _ClassVar[Role]
    ROLE_WALLET_VIEWER: _ClassVar[Role]
    ROLE_WALLET_ACCOUNT_ADMIN: _ClassVar[Role]
    ROLE_WALLET_ACCOUNT_VIEWER: _ClassVar[Role]
    ROLE_COMPLIANCE_ADMIN: _ClassVar[Role]
    ROLE_COMPLIANCE_VIEWER: _ClassVar[Role]
    ROLE_COMPLIANCE_CLIENT_ADMIN: _ClassVar[Role]
    ROLE_COMPLIANCE_CLIENT_VIEWER: _ClassVar[Role]
    ROLE_IAM_ADMIN: _ClassVar[Role]
    ROLE_IAM_VIEWER: _ClassVar[Role]
    ROLE_IAM_API_USER_ADMIN: _ClassVar[Role]
    ROLE_IAM_API_USER_VIEWER: _ClassVar[Role]
    ROLE_IAM_GROUP_ADMIN: _ClassVar[Role]
    ROLE_IAM_GROUP_VIEWER: _ClassVar[Role]
    ROLE_IAM_USER_ADMIN: _ClassVar[Role]
    ROLE_IAM_USER_VIEWER: _ClassVar[Role]
    ROLE_STUDIO_ADMIN: _ClassVar[Role]
    ROLE_STUDIO_VIEWER: _ClassVar[Role]
    ROLE_STUDIO_INSTRUMENT_ADMIN: _ClassVar[Role]
    ROLE_STUDIO_INSTRUMENT_VIEWER: _ClassVar[Role]
    ROLE_TRADING_ADMIN: _ClassVar[Role]
    ROLE_TRADING_VIEWER: _ClassVar[Role]
    ROLE_REPORTING_ADMIN: _ClassVar[Role]
    ROLE_REPORTING_VIEWER: _ClassVar[Role]
    ROLE_LEDGER_ADMIN: _ClassVar[Role]
    ROLE_LEDGER_VIEWER: _ClassVar[Role]
    ROLE_LEDGER_TRANSACTION_ADMIN: _ClassVar[Role]
    ROLE_LEDGER_TRANSACTION_VIEWER: _ClassVar[Role]
ROLE_UNSPECIFIED: Role
ROLE_WALLET_ADMIN: Role
ROLE_WALLET_VIEWER: Role
ROLE_WALLET_ACCOUNT_ADMIN: Role
ROLE_WALLET_ACCOUNT_VIEWER: Role
ROLE_COMPLIANCE_ADMIN: Role
ROLE_COMPLIANCE_VIEWER: Role
ROLE_COMPLIANCE_CLIENT_ADMIN: Role
ROLE_COMPLIANCE_CLIENT_VIEWER: Role
ROLE_IAM_ADMIN: Role
ROLE_IAM_VIEWER: Role
ROLE_IAM_API_USER_ADMIN: Role
ROLE_IAM_API_USER_VIEWER: Role
ROLE_IAM_GROUP_ADMIN: Role
ROLE_IAM_GROUP_VIEWER: Role
ROLE_IAM_USER_ADMIN: Role
ROLE_IAM_USER_VIEWER: Role
ROLE_STUDIO_ADMIN: Role
ROLE_STUDIO_VIEWER: Role
ROLE_STUDIO_INSTRUMENT_ADMIN: Role
ROLE_STUDIO_INSTRUMENT_VIEWER: Role
ROLE_TRADING_ADMIN: Role
ROLE_TRADING_VIEWER: Role
ROLE_REPORTING_ADMIN: Role
ROLE_REPORTING_VIEWER: Role
ROLE_LEDGER_ADMIN: Role
ROLE_LEDGER_VIEWER: Role
ROLE_LEDGER_TRANSACTION_ADMIN: Role
ROLE_LEDGER_TRANSACTION_VIEWER: Role
MESSAGE_ROLES_FIELD_NUMBER: _ClassVar[int]
message_roles: _descriptor.FieldDescriptor
ROLES_FIELD_NUMBER: _ClassVar[int]
roles: _descriptor.FieldDescriptor

class RoleList(_message.Message):
    __slots__ = ("roles",)
    ROLES_FIELD_NUMBER: _ClassVar[int]
    roles: _containers.RepeatedScalarFieldContainer[Role]
    def __init__(self, roles: _Optional[_Iterable[_Union[Role, str]]] = ...) -> None: ...
