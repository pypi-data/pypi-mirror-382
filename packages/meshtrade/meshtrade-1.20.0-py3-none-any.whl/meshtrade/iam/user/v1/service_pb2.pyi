from buf.validate import validate_pb2 as _validate_pb2
from meshtrade.iam.role.v1 import role_pb2 as _role_pb2
from meshtrade.iam.user.v1 import user_pb2 as _user_pb2
from meshtrade.option.v1 import method_type_pb2 as _method_type_pb2
from meshtrade.type.v1 import sorting_pb2 as _sorting_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AssignRoleToUserRequest(_message.Message):
    __slots__ = ("name", "role")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    name: str
    role: str
    def __init__(self, name: _Optional[str] = ..., role: _Optional[str] = ...) -> None: ...

class GetUserRequest(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class ListUsersRequest(_message.Message):
    __slots__ = ("sorting",)
    class Sorting(_message.Message):
        __slots__ = ("field", "order")
        FIELD_FIELD_NUMBER: _ClassVar[int]
        ORDER_FIELD_NUMBER: _ClassVar[int]
        field: str
        order: _sorting_pb2.SortingOrder
        def __init__(self, field: _Optional[str] = ..., order: _Optional[_Union[_sorting_pb2.SortingOrder, str]] = ...) -> None: ...
    SORTING_FIELD_NUMBER: _ClassVar[int]
    sorting: ListUsersRequest.Sorting
    def __init__(self, sorting: _Optional[_Union[ListUsersRequest.Sorting, _Mapping]] = ...) -> None: ...

class ListUsersResponse(_message.Message):
    __slots__ = ("users",)
    USERS_FIELD_NUMBER: _ClassVar[int]
    users: _containers.RepeatedCompositeFieldContainer[_user_pb2.User]
    def __init__(self, users: _Optional[_Iterable[_Union[_user_pb2.User, _Mapping]]] = ...) -> None: ...

class SearchUsersRequest(_message.Message):
    __slots__ = ("email", "sorting")
    class Sorting(_message.Message):
        __slots__ = ("field", "order")
        FIELD_FIELD_NUMBER: _ClassVar[int]
        ORDER_FIELD_NUMBER: _ClassVar[int]
        field: str
        order: _sorting_pb2.SortingOrder
        def __init__(self, field: _Optional[str] = ..., order: _Optional[_Union[_sorting_pb2.SortingOrder, str]] = ...) -> None: ...
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    SORTING_FIELD_NUMBER: _ClassVar[int]
    email: str
    sorting: SearchUsersRequest.Sorting
    def __init__(self, email: _Optional[str] = ..., sorting: _Optional[_Union[SearchUsersRequest.Sorting, _Mapping]] = ...) -> None: ...

class SearchUsersResponse(_message.Message):
    __slots__ = ("users",)
    USERS_FIELD_NUMBER: _ClassVar[int]
    users: _containers.RepeatedCompositeFieldContainer[_user_pb2.User]
    def __init__(self, users: _Optional[_Iterable[_Union[_user_pb2.User, _Mapping]]] = ...) -> None: ...

class CreateUserRequest(_message.Message):
    __slots__ = ("user",)
    USER_FIELD_NUMBER: _ClassVar[int]
    user: _user_pb2.User
    def __init__(self, user: _Optional[_Union[_user_pb2.User, _Mapping]] = ...) -> None: ...

class UpdateUserRequest(_message.Message):
    __slots__ = ("user",)
    USER_FIELD_NUMBER: _ClassVar[int]
    user: _user_pb2.User
    def __init__(self, user: _Optional[_Union[_user_pb2.User, _Mapping]] = ...) -> None: ...
