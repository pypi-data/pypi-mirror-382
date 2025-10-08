from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Enum, Text, UUID as SQLAlchemyUUID
from sqlalchemy.dialects.postgresql import JSONB
from uuid import UUID
from maleo.database.orm.mixins import DataIdentifier, DataStatus, DataTimestamp
from maleo.types.misc import ListOrStringDictOfAny
from maleo.types.uuid import OptionalUUID
from ..enums.inference import InferenceType


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
    output: Mapped[ListOrStringDictOfAny] = mapped_column(
        name="output", type_=JSONB, nullable=False
    )
