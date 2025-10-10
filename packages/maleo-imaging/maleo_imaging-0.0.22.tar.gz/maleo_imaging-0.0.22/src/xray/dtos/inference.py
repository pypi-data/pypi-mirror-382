from pydantic import Field
from typing import Annotated, List, TYPE_CHECKING
from uuid import UUID
from maleo.enums.status import DataStatus as DataStatusEnum
from maleo.schemas.mixins.identity import DataIdentifier
from maleo.schemas.mixins.status import DataStatus
from maleo.schemas.mixins.timestamp import DataTimestamp
from maleo.types.any import ListOfAny
from maleo.types.uuid import OptionalUUID
from ..enums.inference import InferenceType


if TYPE_CHECKING:
    from .record_inference import InferenceRecord


class BaseInference(
    DataStatus[DataStatusEnum],
    DataTimestamp,
    DataIdentifier,
):
    organization_id: Annotated[
        OptionalUUID, Field(None, description="Organization ID")
    ] = None
    user_id: Annotated[UUID, Field(..., description="User ID")]
    type: Annotated[InferenceType, Field(..., description="Inference's type")]
    duration: Annotated[float, Field(0.0, description="Inference's duration")] = 0.0
    output: Annotated[ListOfAny, Field(..., description="Inference's output")]


class Inference(BaseInference):
    # Relationships
    records: Annotated[
        List["InferenceRecord"],
        Field(default_factory=list["InferenceRecord"], description="Records"),
    ] = list["InferenceRecord"]()
