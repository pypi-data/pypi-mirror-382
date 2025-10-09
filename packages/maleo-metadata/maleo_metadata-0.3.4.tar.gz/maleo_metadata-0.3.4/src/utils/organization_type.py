from typing import Literal, Type, overload
from ..schemas.organization_type import (
    BasicOrganizationTypeData,
    StandardOrganizationTypeData,
    FullOrganizationTypeData,
    AnyOrganizationTypeDataType,
)
from ..enums.organization_type import Granularity


@overload
def get_data_model(
    granularity: Literal[Granularity.BASIC],
    /,
) -> Type[BasicOrganizationTypeData]: ...
@overload
def get_data_model(
    granularity: Literal[Granularity.STANDARD],
    /,
) -> Type[StandardOrganizationTypeData]: ...
@overload
def get_data_model(
    granularity: Literal[Granularity.FULL],
    /,
) -> Type[FullOrganizationTypeData]: ...
@overload
def get_data_model(
    granularity: Granularity,
    /,
) -> AnyOrganizationTypeDataType: ...
def get_data_model(
    granularity: Granularity,
    /,
) -> AnyOrganizationTypeDataType:
    if granularity is Granularity.BASIC:
        return BasicOrganizationTypeData
    elif granularity is Granularity.STANDARD:
        return StandardOrganizationTypeData
    elif granularity is Granularity.FULL:
        return FullOrganizationTypeData
