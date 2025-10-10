from pydantic import BaseModel, Field
from typing import Annotated, TYPE_CHECKING
from uuid import UUID
from maleo.enums.identity import OptionalGender
from maleo.enums.status import DataStatus as DataStatusEnum
from maleo.schemas.mixins.identity import DataIdentifier
from maleo.schemas.mixins.status import DataStatus
from maleo.schemas.mixins.timestamp import DataTimestamp
from maleo.types.datetime import OptionalDate
from maleo.types.string import OptionalString
from maleo.types.uuid import OptionalUUID


if TYPE_CHECKING:
    from .record_inference import RecordInferencesDTOMixin


class RecordCoreDTO(
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


class RecordCoreDTOMixin(BaseModel):
    record: Annotated[RecordCoreDTO, Field(..., description="Record")]


class RecordCompleteDTO(RecordInferencesDTOMixin, RecordCoreDTO):
    pass
