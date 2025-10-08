from pydantic import BaseModel, Field
from typing import Generic
from maleo.types.string import OptionalStringT
from ..enums.blood_type import Granularity as GranularityEnum


class Granularity(BaseModel):
    granularity: GranularityEnum = Field(
        GranularityEnum.BASIC, description="Granularity"
    )


class Key(BaseModel):
    key: str = Field(..., max_length=2, description="Blood type's key")


class Name(BaseModel, Generic[OptionalStringT]):
    name: OptionalStringT = Field(..., max_length=2, description="Blood type's name")
