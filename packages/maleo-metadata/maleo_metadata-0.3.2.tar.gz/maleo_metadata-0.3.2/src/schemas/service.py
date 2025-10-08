from pydantic import BaseModel, Field
from typing import Generic, List, Literal, Optional, Type, TypeVar, Union, overload
from uuid import UUID
from maleo.enums.service import (
    ServiceType as ServiceTypeEnum,
    Category as CategoryEnum,
    Key as ServiceKey,
)
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
from ..enums.service import (
    Granularity as GranularityEnum,
    IdentifierType,
)
from ..mixins.service import Granularity, ServiceType, Category, Key, Name, Secret
from ..types.service import IdentifierValueType


class CommonParameter(Granularity):
    pass


class CreateData(
    Name[str],
    Key,
    ServiceType[ServiceTypeEnum],
    Category[CategoryEnum],
    Order[OptionalInteger],
):
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


class FullUpdateData(
    Name[str],
    ServiceType[ServiceTypeEnum],
    Category[CategoryEnum],
    Order[OptionalInteger],
):
    pass


class PartialUpdateData(
    Name[OptionalString],
    ServiceType[Optional[ServiceTypeEnum]],
    Category[Optional[CategoryEnum]],
    Order[OptionalInteger],
):
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


class BaseServiceData(
    Name[str],
    Key,
    ServiceType[ServiceTypeEnum],
    Category[CategoryEnum],
    Order[OptionalInteger],
):
    pass


class BasicServiceData(
    BaseServiceData,
    DataStatus[DataStatusEnum],
    DataIdentifier,
):
    pass


class StandardServiceData(
    BaseServiceData,
    DataStatus[DataStatusEnum],
    LifecycleTimestamp,
    DataIdentifier,
):
    pass


class FullServiceData(
    Secret,
    BaseServiceData,
    DataStatus[DataStatusEnum],
    DataTimestamp,
    DataIdentifier,
):
    pass


AnyServiceDataType = Union[
    Type[BasicServiceData],
    Type[StandardServiceData],
    Type[FullServiceData],
]


AnyServiceData = Union[
    BasicServiceData,
    StandardServiceData,
    FullServiceData,
]


ServiceDataT = TypeVar("ServiceDataT", bound=AnyServiceData)


AnyService = Union[ServiceKey, AnyServiceData]


ServiceT = TypeVar("ServiceT", bound=AnyService)


class ServiceMixin(BaseModel, Generic[ServiceT]):
    service: ServiceT = Field(..., description="Service")


class OptionalServiceMixin(BaseModel, Generic[ServiceT]):
    service: Optional[ServiceT] = Field(..., description="Service")


class ServicesMixin(BaseModel, Generic[ServiceT]):
    services: List[ServiceT] = Field(..., description="Services")


class OptionalServicesMixin(BaseModel, Generic[ServiceT]):
    services: Optional[List[ServiceT]] = Field(..., description="Services")
