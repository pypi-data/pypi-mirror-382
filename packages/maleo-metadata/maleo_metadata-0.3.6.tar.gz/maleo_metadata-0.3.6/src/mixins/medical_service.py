from pydantic import BaseModel, Field
from typing import Generic
from maleo.types.string import OptionalStringT
from ..enums.medical_service import Granularity as GranularityEnum


class Granularity(BaseModel):
    granularity: GranularityEnum = Field(
        GranularityEnum.BASIC, description="Granularity"
    )


class Key(BaseModel):
    key: str = Field(..., max_length=20, description="Medical service's key")


class Name(BaseModel, Generic[OptionalStringT]):
    name: OptionalStringT = Field(
        ..., max_length=20, description="Medical service's name"
    )
