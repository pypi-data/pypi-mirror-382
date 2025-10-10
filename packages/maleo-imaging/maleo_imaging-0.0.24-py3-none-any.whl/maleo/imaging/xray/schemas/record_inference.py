from pydantic import BaseModel, Field
from typing import Annotated, List, Literal, overload, TYPE_CHECKING
from uuid import UUID
from maleo.enums.status import (
    DataStatus as DataStatusEnum,
    ListOfDataStatuses,
    FULL_DATA_STATUSES,
)
from maleo.schemas.mixins.identity import (
    DataIdentifier,
    Ids,
    UUIDs,
    UUIDOrganizationIds,
    UUIDUserIds,
)
from maleo.schemas.mixins.status import DataStatus
from maleo.schemas.mixins.timestamp import DataTimestamp
from maleo.schemas.parameter import (
    ReadSingleParameter as BaseReadSingleParameter,
    ReadPaginatedMultipleParameter,
)
from maleo.types.integer import OptionalListOfIntegers
from maleo.types.uuid import OptionalListOfUUIDs
from ..enums.record_inference import IdentifierType
from ..mixins.record import RecordIds
from ..mixins.inference import InferenceIds
from ..types.record_inference import IdentifierValueType


if TYPE_CHECKING:
    from .record import RecordCoreSchemaMixin
    from .inference import AnyInferenceCoreSchema, InferenceCoreSchemaMixin


class ReadMultipleParameter(
    ReadPaginatedMultipleParameter,
    InferenceIds[OptionalListOfUUIDs],
    RecordIds[OptionalListOfUUIDs],
    UUIDUserIds[OptionalListOfUUIDs],
    UUIDOrganizationIds[OptionalListOfUUIDs],
    UUIDs[OptionalListOfUUIDs],
    Ids[OptionalListOfIntegers],
):
    pass


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


class RecordInferenceSchema(
    InferenceCoreSchemaMixin[AnyInferenceCoreSchema],
    DataStatus[DataStatusEnum],
    DataTimestamp,
    DataIdentifier,
):
    pass


class RecordInferencesSchemaMixin(BaseModel):
    inferences: Annotated[
        List[RecordInferenceSchema],
        Field(default_factory=list[RecordInferenceSchema], description="Inferences"),
    ] = list[RecordInferenceSchema]()


class InferenceRecordSchema(
    RecordCoreSchemaMixin,
    DataStatus[DataStatusEnum],
    DataTimestamp,
    DataIdentifier,
):
    pass


class InferenceRecordsSchemaMixin(BaseModel):
    records: Annotated[
        List[InferenceRecordSchema],
        Field(default_factory=list[InferenceRecordSchema], description="Records"),
    ] = list[InferenceRecordSchema]()


class RecordAndInferenceSchema(
    InferenceCoreSchemaMixin[AnyInferenceCoreSchema],
    RecordCoreSchemaMixin,
    DataStatus[DataStatusEnum],
    DataTimestamp,
    DataIdentifier,
):
    pass
