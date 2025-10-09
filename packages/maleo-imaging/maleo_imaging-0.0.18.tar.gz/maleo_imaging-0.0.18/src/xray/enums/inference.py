from enum import StrEnum
from typing import List, Optional, Sequence
from maleo.types.string import ListOfStrings


class InferenceType(StrEnum):
    MULTI_FINDING = "multi_finding"
    TUBERCULOSIS = "tuberculosis"

    @classmethod
    def choices(cls) -> ListOfStrings:
        return [e.value for e in cls]


OptionalInferenceType = Optional[InferenceType]
ListOfInferenceTypes = List[InferenceType]
OptionalListOfInferenceTypes = Optional[ListOfInferenceTypes]
SequenceOfInferenceTypes = Sequence[InferenceType]
OptionalSequenceOfInferenceTypes = Optional[SequenceOfInferenceTypes]


class MultiFindingClass(StrEnum):
    ATELECTASIS = "atelectasis"
    CALCIFICATION = "calcification"
    CARDIOMEGALY = "cardiomegaly"
    CONSOLIDATION = "consolidation"
    INFILTRATION = "infiltration"
    LUNG_OPACITY = "lung opacity"
    LUNG_CAVITY = "lung cavity"
    NODULE_MASS = "nodule/mass"
    PLEURAL_EFFUSION = "pleural effusion"
    PNEUMOTHORAX = "pneumothorax"

    @classmethod
    def choices(cls) -> ListOfStrings:
        return [e.value for e in cls]


OptionalMultiFindingClass = Optional[MultiFindingClass]
ListOfMultiFindingClasses = List[MultiFindingClass]
OptionalListOfMultiFindingClasses = Optional[ListOfMultiFindingClasses]
SequenceOfMultiFindingClasses = Sequence[MultiFindingClass]
OptionalSequenceOfMultiFindingClasses = Optional[SequenceOfMultiFindingClasses]
