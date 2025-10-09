from pydantic import BaseModel, Field
from typing import Generic, List, Literal, Optional, Type, TypeVar, Union, overload
from uuid import UUID
from maleo.enums.user import UserType
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
from ..enums.user_type import (
    Granularity as GranularityEnum,
    IdentifierType,
)
from ..mixins.user_type import Granularity, Key, Name
from ..types.user_type import IdentifierValueType


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


class BaseUserTypeData(
    Name[str],
    Key,
    Order[OptionalInteger],
):
    pass


class BasicUserTypeData(
    BaseUserTypeData,
    DataStatus[DataStatusEnum],
    DataIdentifier,
):
    pass


class StandardUserTypeData(
    BaseUserTypeData,
    DataStatus[DataStatusEnum],
    LifecycleTimestamp,
    DataIdentifier,
):
    pass


class FullUserTypeData(
    BaseUserTypeData,
    DataStatus[DataStatusEnum],
    DataTimestamp,
    DataIdentifier,
):
    pass


AnyUserTypeDataType = Union[
    Type[BasicUserTypeData],
    Type[StandardUserTypeData],
    Type[FullUserTypeData],
]


AnyUserTypeData = Union[
    BasicUserTypeData,
    StandardUserTypeData,
    FullUserTypeData,
]


UserTypeDataT = TypeVar("UserTypeDataT", bound=AnyUserTypeData)


AnyUserType = Union[UserType, AnyUserTypeData]


UserTypeT = TypeVar("UserTypeT", bound=AnyUserType)


class UserTypeMixin(BaseModel, Generic[UserTypeT]):
    user_type: UserTypeT = Field(..., description="User type")


class OptionalUserTypeMixin(BaseModel, Generic[UserTypeT]):
    user_type: Optional[UserTypeT] = Field(..., description="User type")


class UserTypesMixin(BaseModel, Generic[UserTypeT]):
    user_types: List[UserTypeT] = Field(..., description="User types")


class OptionalUserTypesMixin(BaseModel, Generic[UserTypeT]):
    user_types: Optional[List[UserTypeT]] = Field(..., description="User types")
