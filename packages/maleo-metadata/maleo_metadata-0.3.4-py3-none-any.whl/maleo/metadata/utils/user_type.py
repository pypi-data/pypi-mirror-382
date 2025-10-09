from typing import Literal, Type, overload
from ..schemas.user_type import (
    BasicUserTypeData,
    StandardUserTypeData,
    FullUserTypeData,
    AnyUserTypeDataType,
)
from ..enums.user_type import Granularity


@overload
def get_data_model(
    granularity: Literal[Granularity.BASIC],
    /,
) -> Type[BasicUserTypeData]: ...
@overload
def get_data_model(
    granularity: Literal[Granularity.STANDARD],
    /,
) -> Type[StandardUserTypeData]: ...
@overload
def get_data_model(
    granularity: Literal[Granularity.FULL],
    /,
) -> Type[FullUserTypeData]: ...
@overload
def get_data_model(
    granularity: Granularity,
    /,
) -> AnyUserTypeDataType: ...
def get_data_model(
    granularity: Granularity,
    /,
) -> AnyUserTypeDataType:
    if granularity is Granularity.BASIC:
        return BasicUserTypeData
    elif granularity is Granularity.STANDARD:
        return StandardUserTypeData
    elif granularity is Granularity.FULL:
        return FullUserTypeData
