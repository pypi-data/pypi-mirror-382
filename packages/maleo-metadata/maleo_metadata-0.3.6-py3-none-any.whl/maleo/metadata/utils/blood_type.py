from typing import Literal, Type, overload
from ..schemas.blood_type import (
    BasicBloodTypeData,
    StandardBloodTypeData,
    FullBloodTypeData,
    AnyBloodTypeDataType,
)
from ..enums.blood_type import Granularity


@overload
def get_data_model(
    granularity: Literal[Granularity.BASIC],
    /,
) -> Type[BasicBloodTypeData]: ...
@overload
def get_data_model(
    granularity: Literal[Granularity.STANDARD],
    /,
) -> Type[StandardBloodTypeData]: ...
@overload
def get_data_model(
    granularity: Literal[Granularity.FULL],
    /,
) -> Type[FullBloodTypeData]: ...
@overload
def get_data_model(
    granularity: Granularity,
    /,
) -> AnyBloodTypeDataType: ...
def get_data_model(
    granularity: Granularity,
    /,
) -> AnyBloodTypeDataType:
    if granularity is Granularity.BASIC:
        return BasicBloodTypeData
    elif granularity is Granularity.STANDARD:
        return StandardBloodTypeData
    elif granularity is Granularity.FULL:
        return FullBloodTypeData
