from pydantic import BaseModel, Field
from typing import Annotated, Generic, Literal, TypeVar, overload
from uuid import UUID, uuid4
from maleo.enums.identity import OptionalGender
from maleo.enums.status import (
    DataStatus as DataStatusEnum,
    ListOfDataStatuses,
    FULL_DATA_STATUSES,
)
from maleo.schemas.mixins.identity import (
    DataIdentifier,
    IdentifierTypeValue,
    Ids,
    UUIDs,
    Name,
)
from maleo.schemas.mixins.status import DataStatus
from maleo.schemas.mixins.timestamp import DataTimestamp
from maleo.schemas.parameter import (
    ReadSingleParameter as BaseReadSingleParameter,
    ReadPaginatedMultipleParameter,
    StatusUpdateParameter as BaseStatusUpdateParameter,
    DeleteSingleParameter as BaseDeleteSingleParameter,
)
from maleo.types.datetime import OptionalDate
from maleo.types.integer import OptionalListOfIntegers
from maleo.types.string import OptionalString
from maleo.types.uuid import OptionalListOfUUIDs, OptionalUUID
from ..enums.record import IdentifierType
from ..types.record import IdentifierValueType


class CreateParameter(BaseModel):
    record_id: Annotated[UUID, Field(default_factory=uuid4, description="Record ID")]
    organization_id: Annotated[
        OptionalUUID, Field(None, description="Organization ID")
    ] = None
    user_id: Annotated[UUID, Field(..., description="User ID")]
    name: Annotated[OptionalString, Field(None, description="Name", max_length=200)] = (
        None
    )
    gender: Annotated[OptionalGender, Field(None, description="Gender")] = None
    date_of_birth: Annotated[OptionalDate, Field(None, description="Date of Birth")] = (
        None
    )
    description: Annotated[OptionalString, Field(None, description="Description")] = (
        None
    )
    impression: Annotated[OptionalString, Field(None, description="Impression")] = None
    diagnosis: Annotated[str, Field(..., description="Diagnosis")]
    content_type: Annotated[str, Field(..., description="Content type")]
    image: Annotated[bytes, Field(..., description="Image data")]
    filename: Annotated[str, Field(..., description="File name")]


class ReadMultipleParameter(
    ReadPaginatedMultipleParameter,
    UUIDs[OptionalListOfUUIDs],
    Ids[OptionalListOfIntegers],
):
    organization_ids: Annotated[
        OptionalListOfUUIDs, Field(None, description="Organization's IDs")
    ] = None
    user_ids: Annotated[OptionalListOfUUIDs, Field(None, description="User's IDs")] = (
        None
    )


class ReadSingleParameter(BaseReadSingleParameter[IdentifierType, IdentifierValueType]):
    @overload
    @classmethod
    def new(
        cls,
        identifier: Literal[IdentifierType.ID],
        value: int,
        statuses: ListOfDataStatuses = list(FULL_DATA_STATUSES),
        use_cache: bool = True,
    ) -> "ReadSingleParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier: Literal[IdentifierType.UUID],
        value: UUID,
        statuses: ListOfDataStatuses = list(FULL_DATA_STATUSES),
        use_cache: bool = True,
    ) -> "ReadSingleParameter": ...
    @classmethod
    def new(
        cls,
        identifier: IdentifierType,
        value: IdentifierValueType,
        statuses: ListOfDataStatuses = list(FULL_DATA_STATUSES),
        use_cache: bool = True,
    ) -> "ReadSingleParameter":
        return cls(
            identifier=identifier,
            value=value,
            statuses=statuses,
            use_cache=use_cache,
        )


class BaseUpdateData(
    Name[OptionalString],
):
    name: Annotated[OptionalString, Field(None, description="Name", max_length=200)] = (
        None
    )
    gender: Annotated[OptionalGender, Field(None, description="Gender")] = None
    date_of_birth: Annotated[OptionalDate, Field(None, description="Date of Birth")] = (
        None
    )
    description: Annotated[OptionalString, Field(None, description="Description")] = (
        None
    )
    impression: Annotated[OptionalString, Field(None, description="Impression")] = None


class FullUpdateData(BaseUpdateData):
    diagnosis: Annotated[str, Field(..., description="Diagnosis")]


class PartialUpdateData(BaseUpdateData):
    diagnosis: Annotated[OptionalString, Field(None, description="Diagnosis")] = None


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


class BaseRecordData(
    DataStatus[DataStatusEnum],
    DataTimestamp,
    DataIdentifier,
):
    organization_id: Annotated[
        OptionalUUID, Field(None, description="Organization ID")
    ] = None
    user_id: Annotated[UUID, Field(..., description="User ID")]
    name: Annotated[OptionalString, Field(None, description="Name", max_length=200)] = (
        None
    )
    gender: Annotated[OptionalGender, Field(None, description="Gender")] = None
    date_of_birth: Annotated[OptionalDate, Field(None, description="Date of Birth")] = (
        None
    )
    description: Annotated[OptionalString, Field(None, description="Description")] = (
        None
    )
    impression: Annotated[OptionalString, Field(None, description="Impression")] = None
    diagnosis: Annotated[str, Field(..., description="Diagnosis")]
    filename: Annotated[str, Field(..., description="File's name")]


class RecordData(BaseRecordData):
    url: Annotated[str, Field(..., description="File's URL")]
