from copy import deepcopy
from typing import Callable, Dict
from uuid import UUID
from maleo.schemas.resource import ResourceIdentifier
from ..enums.inference import (
    IdentifierType,
    MultiFindingClass,
    SequenceOfMultiFindingClasses,
)
from ..types.inference import IdentifierValueType
from . import RESOURCE as XRAY_RESOURCE


IDENTIFIER_TYPE_VALUE_TYPE_MAP: Dict[
    IdentifierType,
    Callable[..., IdentifierValueType],
] = {
    IdentifierType.ID: int,
    IdentifierType.UUID: UUID,
}


MULTI_FINDING_CLASSES: SequenceOfMultiFindingClasses = [
    MultiFindingClass.ATELECTASIS,
    MultiFindingClass.CALCIFICATION,
    MultiFindingClass.CARDIOMEGALY,
    MultiFindingClass.CONSOLIDATION,
    MultiFindingClass.INFILTRATION,
    MultiFindingClass.LUNG_OPACITY,
    MultiFindingClass.LUNG_CAVITY,
    MultiFindingClass.NODULE_MASS,
    MultiFindingClass.PLEURAL_EFFUSION,
    MultiFindingClass.PNEUMOTHORAX,
]


RESOURCE = deepcopy(XRAY_RESOURCE)
RESOURCE.identifiers.append(
    ResourceIdentifier(key="inferences", name="Inferences", slug="inferences")
)
