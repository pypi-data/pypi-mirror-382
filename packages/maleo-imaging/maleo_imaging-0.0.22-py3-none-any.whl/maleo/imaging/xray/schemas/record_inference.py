from pydantic import Field
from typing import Annotated, Literal, overload, TYPE_CHECKING
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
    from .record import BaseRecord
    from .inference import BaseInference


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


class RecordInference(
    DataStatus[DataStatusEnum],
    DataTimestamp,
    DataIdentifier,
):
    inference: Annotated[BaseInference, Field(..., description="Inference's row")]


class InferenceRecord(
    DataStatus[DataStatusEnum],
    DataTimestamp,
    DataIdentifier,
):
    record: Annotated[BaseRecord, Field(..., description="Record's row")]


class RecordAndInference(
    DataStatus[DataStatusEnum],
    DataTimestamp,
    DataIdentifier,
):
    record: Annotated[BaseRecord, Field(..., description="Record's row")]
    inference: Annotated[BaseInference, Field(..., description="Inference's row")]
