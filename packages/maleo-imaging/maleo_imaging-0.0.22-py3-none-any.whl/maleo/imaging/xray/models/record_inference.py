from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Integer
from typing import TYPE_CHECKING
from maleo.database.orm.mixins import DataIdentifier, DataStatus, DataTimestamp


if TYPE_CHECKING:
    from .record import Record
    from .inference import Inference


class RecordAndInference(DataTimestamp, DataStatus, DataIdentifier):
    __tablename__ = "xray_record_inferences"
    record_id: Mapped[int] = mapped_column(
        name="record_id", type_=Integer, nullable=False
    )
    inference_id: Mapped[int] = mapped_column(
        name="inference_id", type_=Integer, nullable=False
    )

    # Relationships
    record: Mapped["Record"] = relationship("Record", back_populates="inferences")
    inference: Mapped["Inference"] = relationship("Inference", back_populates="records")
