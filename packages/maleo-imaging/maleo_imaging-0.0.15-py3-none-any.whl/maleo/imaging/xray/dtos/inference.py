from pydantic import BaseModel, Field
from typing import Annotated, Generic, Tuple, TypeVar
from maleo.types.misc import StringOrStringEnum


NameT = TypeVar("NameT", bound=StringOrStringEnum)


class Finding(BaseModel, Generic[NameT]):
    id: Annotated[int, Field(..., description="Finding's ID")]
    name: Annotated[NameT, Field(..., description="Finding's Name")]
    confidence: Annotated[float, Field(..., description="Confidence", ge=0.0, le=1.0)]


class BoundedFinding(Finding[NameT], Generic[NameT]):
    box: Annotated[
        Tuple[float, float, float, float], Field(..., description="Bounding Box")
    ]
