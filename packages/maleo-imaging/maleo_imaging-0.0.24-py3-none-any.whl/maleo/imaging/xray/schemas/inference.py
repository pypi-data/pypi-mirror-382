from pydantic import BaseModel, Field, model_validator
from typing import (
    Annotated,
    Any,
    Generic,
    List,
    Literal,
    Optional,
    Self,
    TypeGuard,
    TypeVar,
    Union,
    overload,
    TYPE_CHECKING,
)
from uuid import UUID, uuid4
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
from maleo.types.any import ListOfAny
from maleo.types.integer import OptionalListOfIntegers
from maleo.types.misc import StringOrStringEnum
from maleo.types.uuid import OptionalListOfUUIDs, OptionalUUID
from ..enums.inference import (
    IdentifierType,
    InferenceType,
    InferenceTypeT,
    OptionalListOfInferenceTypes,
    MultiFindingClass,
    TuberculosisClass,
)
from ..mixins.inference import InferenceTypes
from ..types.inference import IdentifierValueType


if TYPE_CHECKING:
    from .record_inference import InferenceRecordsSchemaMixin


class BoundingBox(BaseModel):
    x_min: Annotated[float, Field(0.0, description="X Min", ge=0.0)]
    y_min: Annotated[float, Field(0.0, description="Y Min", ge=0.0)]
    x_max: Annotated[float, Field(0.0, description="X Max", ge=0.0)]
    y_max: Annotated[float, Field(0.0, description="Y Max", ge=0.0)]


OptionalBoundingBox = Optional[BoundingBox]
OptionalBoundingBoxT = TypeVar("OptionalBoundingBoxT", bound=OptionalBoundingBox)


class Finding(BaseModel, Generic[OptionalBoundingBoxT]):
    id: Annotated[int, Field(..., description="Finding's ID")]
    name: Annotated[StringOrStringEnum, Field(..., description="Finding's Name")]
    confidence: Annotated[float, Field(..., description="Confidence", ge=0.0, le=1.0)]
    box: Annotated[OptionalBoundingBoxT, Field(..., description="Bounding Box")]


class FindingWithoutBox(Finding[None]):
    pass


class FindingWithBox(Finding[BoundingBox]):
    pass


AnyFinding = Union[FindingWithoutBox, FindingWithBox]
AnyFindingT = TypeVar("AnyFindingT", bound=AnyFinding)
OptionalAnyFinding = Optional[AnyFinding]
OptionalAnyFindingT = TypeVar("OptionalAnyFindingT", bound=OptionalAnyFinding)


class GenericPredictParameter(BaseModel, Generic[InferenceTypeT]):
    inference_id: Annotated[
        UUID, Field(default_factory=uuid4, description="Inference ID")
    ]
    organization_id: Annotated[
        OptionalUUID, Field(None, description="Organization ID")
    ] = None
    user_id: Annotated[UUID, Field(..., description="User ID")]
    inference_type: Annotated[
        InferenceTypeT, Field(..., description="Inference's type")
    ]
    content_type: Annotated[str, Field(..., description="Content type")]
    image: Annotated[bytes, Field(..., description="Image data")]
    filename: Annotated[str, Field(..., description="File name")]


class BasePredictParameter(GenericPredictParameter[InferenceType]):
    inference_type: Annotated[InferenceType, Field(..., description="Inference's type")]


class MultiFindingPredictParameter(
    GenericPredictParameter[Literal[InferenceType.MULTI_FINDING]]
):
    inference_type: Annotated[
        Literal[InferenceType.MULTI_FINDING],
        Field(InferenceType.MULTI_FINDING, description="Inference's type"),
    ] = InferenceType.MULTI_FINDING


class TuberculosisPredictParameter(
    GenericPredictParameter[Literal[InferenceType.TUBERCULOSIS]]
):
    inference_type: Annotated[
        Literal[InferenceType.TUBERCULOSIS],
        Field(InferenceType.TUBERCULOSIS, description="Inference's type"),
    ] = InferenceType.TUBERCULOSIS


AnyPredictParameter = Union[
    BasePredictParameter, MultiFindingPredictParameter, TuberculosisPredictParameter
]


class GenericCreateParameter(BaseModel, Generic[InferenceTypeT]):
    uuid: Annotated[UUID, Field(default_factory=uuid4, description="Inference ID")]
    organization_id: Annotated[
        OptionalUUID, Field(None, description="Organization ID")
    ] = None
    user_id: Annotated[UUID, Field(..., description="User ID")]
    type: Annotated[InferenceTypeT, Field(..., description="Inference's type")]
    filename: Annotated[str, Field(..., description="File name")]
    duration: Annotated[float, Field(0.0, description="Inference's duration")] = 0.0
    output: Annotated[
        ListOfAny,
        Field(default_factory=list[Any], description="Inference's output"),
    ] = list[Any]()

    @classmethod
    def from_predict_parameter(
        cls,
        parameters: GenericPredictParameter[InferenceTypeT],
        duration: float,
        output: ListOfAny,
    ) -> Self:
        return cls(
            uuid=parameters.inference_id,
            organization_id=parameters.organization_id,
            user_id=parameters.user_id,
            type=parameters.inference_type,
            duration=duration,
            filename=parameters.filename,
            output=output,
        )


class BaseCreateParameter(GenericCreateParameter[InferenceType]):
    type: Annotated[InferenceType, Field(..., description="Inference's type")]


class MultiFindingCreateParameter(
    GenericCreateParameter[Literal[InferenceType.MULTI_FINDING]]
):
    type: Annotated[
        Literal[InferenceType.MULTI_FINDING],
        Field(InferenceType.MULTI_FINDING, description="Inference's type"),
    ] = InferenceType.MULTI_FINDING


class TuberculosisCreateParameter(
    GenericCreateParameter[Literal[InferenceType.TUBERCULOSIS]]
):
    type: Annotated[
        Literal[InferenceType.TUBERCULOSIS],
        Field(InferenceType.TUBERCULOSIS, description="Inference's type"),
    ] = InferenceType.TUBERCULOSIS


AnyCreateParameter = Union[
    BaseCreateParameter, MultiFindingCreateParameter, TuberculosisCreateParameter
]


class ReadMultipleParameter(
    ReadPaginatedMultipleParameter,
    InferenceTypes[OptionalListOfInferenceTypes],
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


class GenericInferenceCoreSchema(
    DataStatus[DataStatusEnum],
    DataTimestamp,
    DataIdentifier,
    Generic[InferenceTypeT, AnyFindingT],
):
    organization_id: Annotated[
        OptionalUUID, Field(None, description="Organization ID")
    ] = None
    user_id: Annotated[UUID, Field(..., description="User ID")]
    type: Annotated[InferenceTypeT, Field(..., description="Inference's type")]
    duration: Annotated[float, Field(0.0, description="Inference's duration")] = 0.0
    findings: Annotated[
        List[AnyFindingT],
        Field(default_factory=list[AnyFindingT], description="Findings", min_length=1),
    ] = list[AnyFindingT]()

    @model_validator(mode="after")
    def validate_findings(self) -> Self:
        if self.type is InferenceType.MULTI_FINDING:
            for index, finding in enumerate(self.findings):
                if finding.name not in MultiFindingClass.choices():
                    raise ValueError(
                        f"Invalid finding's name for {InferenceType.MULTI_FINDING} inference",
                        f"Received: {finding.name}",
                        f"Expected: [{MultiFindingClass.choices()}]",
                    )
                if finding.box is None:
                    raise ValueError(
                        f"Attribute 'box' can not be None for {InferenceType.MULTI_FINDING} inference",
                        f"index: {index}, id: {finding.id}, name: {finding.name}",
                    )
        elif self.type is InferenceType.TUBERCULOSIS:
            if len(self.findings) != 1:
                raise ValueError(
                    f"{InferenceType.TUBERCULOSIS} inference can only have one finding"
                )
            for index, finding in enumerate(self.findings):
                if finding.name not in TuberculosisClass.choices():
                    raise ValueError(
                        f"Invalid finding's name for {InferenceType.TUBERCULOSIS} inference",
                        f"Received: {finding.name}",
                        f"Expected: [{TuberculosisClass.choices()}]",
                    )
                if finding.box is not None:
                    raise ValueError(
                        f"Attribute 'box' must be None for {InferenceType.TUBERCULOSIS} inference",
                        f"index: {index}, id: {finding.id}, name: {finding.name}",
                    )
        return self


class MultiFindingInferenceCoreSchema(
    GenericInferenceCoreSchema[Literal[InferenceType.MULTI_FINDING], FindingWithBox]
):
    pass


class TuberculosisInferenceCoreSchema(
    GenericInferenceCoreSchema[Literal[InferenceType.TUBERCULOSIS], FindingWithoutBox]
):
    pass


AnyInferenceCoreSchema = Union[
    MultiFindingInferenceCoreSchema, TuberculosisInferenceCoreSchema
]


def is_multi_finding_core_schema(
    schema: AnyInferenceCoreSchema,
) -> TypeGuard[MultiFindingInferenceCoreSchema]:
    return schema.type is InferenceType.MULTI_FINDING and all(
        [isinstance(finding, FindingWithBox) for finding in schema.findings]
    )


def is_tuberculosis_core_schema(
    schema: AnyInferenceCoreSchema,
) -> TypeGuard[TuberculosisInferenceCoreSchema]:
    return (
        schema.type is InferenceType.TUBERCULOSIS
        and len(schema.findings) == 1
        and all([isinstance(finding, FindingWithBox) for finding in schema.findings])
    )


AnyInferenceCoreSchemaT = TypeVar(
    "AnyInferenceCoreSchemaT", bound=AnyInferenceCoreSchema
)


class InferenceCoreSchemaMixin(BaseModel, Generic[AnyInferenceCoreSchemaT]):
    inference: Annotated[AnyInferenceCoreSchemaT, Field(..., description="Inference")]


class GenericInferenceCompleteSchema(
    InferenceRecordsSchemaMixin,
    GenericInferenceCoreSchema[InferenceTypeT, AnyFindingT],
    Generic[InferenceTypeT, AnyFindingT],
):
    pass


class MultiFindingInferenceCompleteSchema(
    GenericInferenceCompleteSchema[Literal[InferenceType.MULTI_FINDING], FindingWithBox]
):
    pass


class TuberculosisInferenceCompleteSchema(
    GenericInferenceCompleteSchema[
        Literal[InferenceType.TUBERCULOSIS], FindingWithoutBox
    ]
):
    pass


AnyInferenceCompleteSchema = Union[
    MultiFindingInferenceCompleteSchema, TuberculosisInferenceCompleteSchema
]


def is_multi_finding_complete_schema(
    schema: AnyInferenceCompleteSchema,
) -> TypeGuard[MultiFindingInferenceCompleteSchema]:
    return schema.type is InferenceType.MULTI_FINDING and all(
        [isinstance(finding, FindingWithBox) for finding in schema.findings]
    )


def is_tuberculosis_complete_schema(
    schema: AnyInferenceCompleteSchema,
) -> TypeGuard[TuberculosisInferenceCompleteSchema]:
    return (
        schema.type is InferenceType.TUBERCULOSIS
        and len(schema.findings) == 1
        and all([isinstance(finding, FindingWithBox) for finding in schema.findings])
    )
