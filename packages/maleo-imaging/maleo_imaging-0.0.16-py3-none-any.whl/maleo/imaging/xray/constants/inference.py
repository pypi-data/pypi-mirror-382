from copy import deepcopy
from maleo.schemas.resource import ResourceIdentifier
from ..enums.inference import MultiFindingClass, SequenceOfMultiFindingClasses
from . import RESOURCE as XRAY_RESOURCE


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
