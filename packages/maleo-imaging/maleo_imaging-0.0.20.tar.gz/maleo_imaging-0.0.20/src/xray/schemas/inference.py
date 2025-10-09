from pydantic import BaseModel, Field
from typing import Annotated, Generic, Tuple
from uuid import UUID
from maleo.enums.identity import OptionalGender
from maleo.types.datetime import OptionalDate
from maleo.types.misc import StringOrStringEnumT
from maleo.types.string import OptionalString
from maleo.types.uuid import OptionalUUID


class CreateParameter(BaseModel):
    organization_id: Annotated[
        OptionalUUID, Field(None, description="Organization ID")
    ] = None
    user_id: Annotated[UUID, Field(..., description="User ID")]
    name: Annotated[
        OptionalString, Field(None, description="Patient's Name", max_length=200)
    ] = None
    gender: Annotated[OptionalGender, Field(None, description="Patient's Gender")] = (
        None
    )
    date_of_birth: Annotated[
        OptionalDate, Field(None, description="Patient's Date of Birth")
    ] = None
    content_type: Annotated[str, Field(..., description="Content type")]
    image: Annotated[bytes, Field(..., description="Image data")]
    filename: Annotated[str, Field(..., description="File name")]


class Finding(BaseModel, Generic[StringOrStringEnumT]):
    id: Annotated[int, Field(..., description="Finding's ID")]
    name: Annotated[StringOrStringEnumT, Field(..., description="Finding's Name")]
    confidence: Annotated[float, Field(..., description="Confidence", ge=0.0, le=1.0)]


class BoundedFinding(Finding[StringOrStringEnumT], Generic[StringOrStringEnumT]):
    box: Annotated[
        Tuple[float, float, float, float], Field(..., description="Bounding Box")
    ]
