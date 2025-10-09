from typing import Literal, Type, overload
from ..schemas.medical_role import (
    BasicMedicalRoleData,
    StandardMedicalRoleData,
    FullMedicalRoleData,
    AnyMedicalRoleDataType,
)
from ..enums.medical_role import Granularity


@overload
def get_data_model(
    granularity: Literal[Granularity.BASIC],
    /,
) -> Type[BasicMedicalRoleData]: ...
@overload
def get_data_model(
    granularity: Literal[Granularity.STANDARD],
    /,
) -> Type[StandardMedicalRoleData]: ...
@overload
def get_data_model(
    granularity: Literal[Granularity.FULL],
    /,
) -> Type[FullMedicalRoleData]: ...
@overload
def get_data_model(
    granularity: Granularity,
    /,
) -> AnyMedicalRoleDataType: ...
def get_data_model(
    granularity: Granularity,
    /,
) -> AnyMedicalRoleDataType:
    if granularity is Granularity.BASIC:
        return BasicMedicalRoleData
    elif granularity is Granularity.STANDARD:
        return StandardMedicalRoleData
    elif granularity is Granularity.FULL:
        return FullMedicalRoleData
