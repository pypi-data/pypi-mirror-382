from pydantic import Field
from typing import Annotated, TYPE_CHECKING
from maleo.enums.status import DataStatus as DataStatusEnum
from maleo.schemas.mixins.identity import DataIdentifier
from maleo.schemas.mixins.status import DataStatus
from maleo.schemas.mixins.timestamp import DataTimestamp


if TYPE_CHECKING:
    from .record import BaseRecord
    from .inference import BaseInference


class RecordInference(
    DataStatus[DataStatusEnum],
    DataTimestamp,
    DataIdentifier,
):
    inference: Annotated[BaseInference, Field(..., description="Inference")]


class InferenceRecord(
    DataStatus[DataStatusEnum],
    DataTimestamp,
    DataIdentifier,
):
    record: Annotated[BaseRecord, Field(..., description="Record")]


class RecordAndInference(
    DataStatus[DataStatusEnum],
    DataTimestamp,
    DataIdentifier,
):
    record: Annotated[BaseRecord, Field(..., description="Record")]
    inference: Annotated[BaseInference, Field(..., description="Inference")]
