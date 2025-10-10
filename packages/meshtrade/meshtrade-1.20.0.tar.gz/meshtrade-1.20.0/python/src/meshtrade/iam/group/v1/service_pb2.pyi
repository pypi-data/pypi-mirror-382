from buf.validate import validate_pb2 as _validate_pb2
from meshtrade.iam.group.v1 import group_pb2 as _group_pb2
from meshtrade.iam.role.v1 import role_pb2 as _role_pb2
from meshtrade.option.v1 import method_type_pb2 as _method_type_pb2
from meshtrade.type.v1 import sorting_pb2 as _sorting_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateGroupRequest(_message.Message):
    __slots__ = ("group",)
    GROUP_FIELD_NUMBER: _ClassVar[int]
    group: _group_pb2.Group
    def __init__(self, group: _Optional[_Union[_group_pb2.Group, _Mapping]] = ...) -> None: ...

class UpdateGroupRequest(_message.Message):
    __slots__ = ("group",)
    GROUP_FIELD_NUMBER: _ClassVar[int]
    group: _group_pb2.Group
    def __init__(self, group: _Optional[_Union[_group_pb2.Group, _Mapping]] = ...) -> None: ...

class ListGroupsRequest(_message.Message):
    __slots__ = ("sorting",)
    class Sorting(_message.Message):
        __slots__ = ("field", "order")
        FIELD_FIELD_NUMBER: _ClassVar[int]
        ORDER_FIELD_NUMBER: _ClassVar[int]
        field: str
        order: _sorting_pb2.SortingOrder
        def __init__(self, field: _Optional[str] = ..., order: _Optional[_Union[_sorting_pb2.SortingOrder, str]] = ...) -> None: ...
    SORTING_FIELD_NUMBER: _ClassVar[int]
    sorting: ListGroupsRequest.Sorting
    def __init__(self, sorting: _Optional[_Union[ListGroupsRequest.Sorting, _Mapping]] = ...) -> None: ...

class ListGroupsResponse(_message.Message):
    __slots__ = ("groups",)
    GROUPS_FIELD_NUMBER: _ClassVar[int]
    groups: _containers.RepeatedCompositeFieldContainer[_group_pb2.Group]
    def __init__(self, groups: _Optional[_Iterable[_Union[_group_pb2.Group, _Mapping]]] = ...) -> None: ...

class SearchGroupsRequest(_message.Message):
    __slots__ = ("display_name", "description", "sorting")
    class Sorting(_message.Message):
        __slots__ = ("field", "order")
        FIELD_FIELD_NUMBER: _ClassVar[int]
        ORDER_FIELD_NUMBER: _ClassVar[int]
        field: str
        order: _sorting_pb2.SortingOrder
        def __init__(self, field: _Optional[str] = ..., order: _Optional[_Union[_sorting_pb2.SortingOrder, str]] = ...) -> None: ...
    DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SORTING_FIELD_NUMBER: _ClassVar[int]
    display_name: str
    description: str
    sorting: SearchGroupsRequest.Sorting
    def __init__(self, display_name: _Optional[str] = ..., description: _Optional[str] = ..., sorting: _Optional[_Union[SearchGroupsRequest.Sorting, _Mapping]] = ...) -> None: ...

class SearchGroupsResponse(_message.Message):
    __slots__ = ("groups",)
    GROUPS_FIELD_NUMBER: _ClassVar[int]
    groups: _containers.RepeatedCompositeFieldContainer[_group_pb2.Group]
    def __init__(self, groups: _Optional[_Iterable[_Union[_group_pb2.Group, _Mapping]]] = ...) -> None: ...

class GetGroupRequest(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...
