from typing import Literal, Type, overload
from ..schemas.system_role import (
    BasicSystemRoleData,
    StandardSystemRoleData,
    FullSystemRoleData,
    AnySystemRoleDataType,
)
from ..enums.system_role import Granularity


@overload
def get_data_model(
    granularity: Literal[Granularity.BASIC],
    /,
) -> Type[BasicSystemRoleData]: ...
@overload
def get_data_model(
    granularity: Literal[Granularity.STANDARD],
    /,
) -> Type[StandardSystemRoleData]: ...
@overload
def get_data_model(
    granularity: Literal[Granularity.FULL],
    /,
) -> Type[FullSystemRoleData]: ...
@overload
def get_data_model(
    granularity: Granularity,
    /,
) -> AnySystemRoleDataType: ...
def get_data_model(
    granularity: Granularity,
    /,
) -> AnySystemRoleDataType:
    if granularity is Granularity.BASIC:
        return BasicSystemRoleData
    elif granularity is Granularity.STANDARD:
        return StandardSystemRoleData
    elif granularity is Granularity.FULL:
        return FullSystemRoleData
