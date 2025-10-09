from pydantic import BaseModel, Field
from typing import Generic, List, Literal, Optional, Type, TypeVar, Union, overload
from uuid import UUID
from maleo.enums.identity import Gender
from maleo.enums.status import (
    DataStatus as DataStatusEnum,
    ListOfDataStatuses,
    FULL_DATA_STATUSES,
)
from maleo.schemas.mixins.general import Order
from maleo.schemas.mixins.identity import (
    DataIdentifier,
    IdentifierTypeValue,
    Ids,
    UUIDs,
    Keys,
    Names,
)
from maleo.schemas.mixins.status import DataStatus
from maleo.schemas.mixins.timestamp import LifecycleTimestamp, DataTimestamp
from maleo.schemas.parameter import (
    ReadSingleParameter as BaseReadSingleParameter,
    ReadPaginatedMultipleParameter,
    StatusUpdateParameter as BaseStatusUpdateParameter,
    DeleteSingleParameter as BaseDeleteSingleParameter,
)
from maleo.types.integer import OptionalInteger, OptionalListOfIntegers
from maleo.types.string import OptionalListOfStrings, OptionalString
from maleo.types.uuid import OptionalListOfUUIDs
from ..enums.gender import (
    Granularity as GranularityEnum,
    IdentifierType,
)
from ..mixins.gender import Granularity, Key, Name
from ..types.gender import IdentifierValueType


class CommonParameter(Granularity):
    pass


class CreateData(Name[str], Key, Order[OptionalInteger]):
    pass


class CreateDataMixin(BaseModel):
    data: CreateData = Field(..., description="Create data")


class CreateParameter(
    CreateDataMixin,
):
    pass


class ReadMultipleParameter(
    CommonParameter,
    ReadPaginatedMultipleParameter,
    Names[OptionalListOfStrings],
    Keys[OptionalListOfStrings],
    UUIDs[OptionalListOfUUIDs],
    Ids[OptionalListOfIntegers],
):
    pass


class ReadSingleParameter(
    CommonParameter, BaseReadSingleParameter[IdentifierType, IdentifierValueType]
):
    @overload
    @classmethod
    def new(
        cls,
        identifier: Literal[IdentifierType.ID],
        value: int,
        statuses: ListOfDataStatuses = list(FULL_DATA_STATUSES),
        use_cache: bool = True,
        granularity: GranularityEnum = GranularityEnum.BASIC,
    ) -> "ReadSingleParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier: Literal[IdentifierType.UUID],
        value: UUID,
        statuses: ListOfDataStatuses = list(FULL_DATA_STATUSES),
        use_cache: bool = True,
        granularity: GranularityEnum = GranularityEnum.BASIC,
    ) -> "ReadSingleParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier: Literal[IdentifierType.KEY, IdentifierType.NAME],
        value: str,
        statuses: ListOfDataStatuses = list(FULL_DATA_STATUSES),
        use_cache: bool = True,
        granularity: GranularityEnum = GranularityEnum.BASIC,
    ) -> "ReadSingleParameter": ...
    @classmethod
    def new(
        cls,
        identifier: IdentifierType,
        value: IdentifierValueType,
        statuses: ListOfDataStatuses = list(FULL_DATA_STATUSES),
        use_cache: bool = True,
        granularity: GranularityEnum = GranularityEnum.BASIC,
    ) -> "ReadSingleParameter":
        return cls(
            identifier=identifier,
            value=value,
            statuses=statuses,
            use_cache=use_cache,
            granularity=granularity,
        )


class FullUpdateData(Name[str], Order[OptionalInteger]):
    pass


class PartialUpdateData(Name[OptionalString], Order[OptionalInteger]):
    pass


UpdateDataT = TypeVar("UpdateDataT", FullUpdateData, PartialUpdateData)


class UpdateDataMixin(BaseModel, Generic[UpdateDataT]):
    data: UpdateDataT = Field(..., description="Update data")


class UpdateParameter(
    UpdateDataMixin[UpdateDataT],
    IdentifierTypeValue[
        IdentifierType,
        IdentifierValueType,
    ],
    Generic[UpdateDataT],
):
    pass


class StatusUpdateParameter(
    BaseStatusUpdateParameter,
):
    pass


class DeleteSingleParameter(
    BaseDeleteSingleParameter[IdentifierType, IdentifierValueType]
):
    pass


class BaseGenderData(
    Name[str],
    Key,
    Order[OptionalInteger],
):
    pass


class BasicGenderData(
    BaseGenderData,
    DataStatus[DataStatusEnum],
    DataIdentifier,
):
    pass


class StandardGenderData(
    BaseGenderData,
    DataStatus[DataStatusEnum],
    LifecycleTimestamp,
    DataIdentifier,
):
    pass


class FullGenderData(
    BaseGenderData,
    DataStatus[DataStatusEnum],
    DataTimestamp,
    DataIdentifier,
):
    pass


AnyGenderDataType = Union[
    Type[BasicGenderData],
    Type[StandardGenderData],
    Type[FullGenderData],
]


AnyGenderData = Union[
    BasicGenderData,
    StandardGenderData,
    FullGenderData,
]


GenderDataT = TypeVar("GenderDataT", bound=AnyGenderData)


AnyGender = Union[Gender, AnyGenderData]


GenderT = TypeVar("GenderT", bound=AnyGender)


class GenderMixin(BaseModel, Generic[GenderT]):
    gender: GenderT = Field(..., description="Gender")


class OptionalGenderMixin(BaseModel, Generic[GenderT]):
    gender: Optional[GenderT] = Field(..., description="Gender")


class GendersMixin(BaseModel, Generic[GenderT]):
    genders: List[GenderT] = Field(..., description="Genders")


class OptionalGendersMixin(BaseModel, Generic[GenderT]):
    genders: Optional[List[GenderT]] = Field(..., description="Genders")
