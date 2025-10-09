from typing import Literal, Type, overload
from ..schemas.medical_service import (
    BasicMedicalServiceData,
    StandardMedicalServiceData,
    FullMedicalServiceData,
    AnyMedicalServiceDataType,
)
from ..enums.medical_service import Granularity


@overload
def get_data_model(
    granularity: Literal[Granularity.BASIC],
    /,
) -> Type[BasicMedicalServiceData]: ...
@overload
def get_data_model(
    granularity: Literal[Granularity.STANDARD],
    /,
) -> Type[StandardMedicalServiceData]: ...
@overload
def get_data_model(
    granularity: Literal[Granularity.FULL],
    /,
) -> Type[FullMedicalServiceData]: ...
@overload
def get_data_model(
    granularity: Granularity,
    /,
) -> AnyMedicalServiceDataType: ...
def get_data_model(
    granularity: Granularity,
    /,
) -> AnyMedicalServiceDataType:
    if granularity is Granularity.BASIC:
        return BasicMedicalServiceData
    elif granularity is Granularity.STANDARD:
        return StandardMedicalServiceData
    elif granularity is Granularity.FULL:
        return FullMedicalServiceData
