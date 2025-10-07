from enum import StrEnum
from typing import List, Optional, Sequence
from maleo.types.string import ListOfStrings


class Class(StrEnum):
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


OptionalClass = Optional[Class]
ListOfClasses = List[Class]
OptionalListOfClasses = Optional[ListOfClasses]
SequenceOfClasses = Sequence[Class]
OptionalSequenceOfClasses = Optional[SequenceOfClasses]
