from typing import List
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Enum, Float, Text, UUID as SQLAlchemyUUID
from typing import TYPE_CHECKING
from uuid import UUID
from maleo.database.orm.mixins import DataIdentifier, DataStatus, DataTimestamp
from maleo.types.any import ListOfAny
from maleo.types.uuid import OptionalUUID
from ..enums.inference import InferenceType


if TYPE_CHECKING:
    from .record_inference import RecordAndInference


class Inference(DataTimestamp, DataStatus, DataIdentifier):
    __tablename__ = "xray_inferences"
    organization_id: Mapped[OptionalUUID] = mapped_column(
        name="organization_id", type_=SQLAlchemyUUID
    )
    user_id: Mapped[UUID] = mapped_column(
        name="user_id", type_=SQLAlchemyUUID, nullable=False
    )
    type: Mapped[InferenceType] = mapped_column(
        name="type", type_=Enum(InferenceType, name="xray_inference_type")
    )
    filename: Mapped[str] = mapped_column(name="filename", type_=Text, nullable=False)
    duration: Mapped[float] = mapped_column(
        name="duration", type_=Float, nullable=False
    )
    output: Mapped[ListOfAny] = mapped_column(
        name="output", type_=JSONB, nullable=False
    )

    # Relationships
    records: Mapped[List["RecordAndInference"]] = relationship(
        "RecordAndInference",
        back_populates="inference",
        cascade="all, delete-orphan",
    )
