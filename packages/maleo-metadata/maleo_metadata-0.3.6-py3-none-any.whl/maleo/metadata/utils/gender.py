from typing import Literal, Type, overload
from ..schemas.gender import (
    BasicGenderData,
    StandardGenderData,
    FullGenderData,
    AnyGenderDataType,
)
from ..enums.gender import Granularity


@overload
def get_data_model(
    granularity: Literal[Granularity.BASIC],
    /,
) -> Type[BasicGenderData]: ...
@overload
def get_data_model(
    granularity: Literal[Granularity.STANDARD],
    /,
) -> Type[StandardGenderData]: ...
@overload
def get_data_model(
    granularity: Literal[Granularity.FULL],
    /,
) -> Type[FullGenderData]: ...
@overload
def get_data_model(
    granularity: Granularity,
    /,
) -> AnyGenderDataType: ...
def get_data_model(
    granularity: Granularity,
    /,
) -> AnyGenderDataType:
    if granularity is Granularity.BASIC:
        return BasicGenderData
    elif granularity is Granularity.STANDARD:
        return StandardGenderData
    elif granularity is Granularity.FULL:
        return FullGenderData
