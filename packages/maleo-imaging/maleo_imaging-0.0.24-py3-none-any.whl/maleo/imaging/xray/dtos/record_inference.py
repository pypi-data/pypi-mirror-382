from pydantic import BaseModel, Field
from typing import TYPE_CHECKING, Annotated, List
from maleo.enums.status import DataStatus as DataStatusEnum
from maleo.schemas.mixins.identity import DataIdentifier
from maleo.schemas.mixins.status import DataStatus
from maleo.schemas.mixins.timestamp import DataTimestamp


if TYPE_CHECKING:
    from .record import RecordCoreDTOMixin
    from .inference import InferenceCoreDTOMixin


class RecordInferenceDTO(
    InferenceCoreDTOMixin,
    DataStatus[DataStatusEnum],
    DataTimestamp,
    DataIdentifier,
):
    pass


class RecordInferencesDTOMixin(BaseModel):
    inferences: Annotated[
        List[RecordInferenceDTO],
        Field(default_factory=list[RecordInferenceDTO], description="Inferences"),
    ] = list[RecordInferenceDTO]()


class InferenceRecordDTO(
    RecordCoreDTOMixin,
    DataStatus[DataStatusEnum],
    DataTimestamp,
    DataIdentifier,
):
    pass


class InferenceRecordsDTOMixin(BaseModel):
    records: Annotated[
        List[InferenceRecordDTO],
        Field(default_factory=list[InferenceRecordDTO], description="Records"),
    ] = list[InferenceRecordDTO]()


class RecordAndInferenceDTO(
    InferenceCoreDTOMixin,
    RecordCoreDTOMixin,
    DataStatus[DataStatusEnum],
    DataTimestamp,
    DataIdentifier,
):
    pass
