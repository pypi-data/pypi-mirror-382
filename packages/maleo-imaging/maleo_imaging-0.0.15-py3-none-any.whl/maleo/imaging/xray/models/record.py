from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Date, Enum, String, Text, UUID as SQLAlchemyUUID
from uuid import UUID
from maleo.database.orm.mixins import DataIdentifier, DataStatus, DataTimestamp
from maleo.enums.identity import Gender, OptionalGender
from maleo.types.datetime import OptionalDate
from maleo.types.string import OptionalString
from maleo.types.uuid import OptionalUUID


class Record(DataTimestamp, DataStatus, DataIdentifier):
    __tablename__ = "xray_records"
    organization_id: Mapped[OptionalUUID] = mapped_column(
        name="organization_id", type_=SQLAlchemyUUID
    )
    user_id: Mapped[UUID] = mapped_column(
        name="user_id", type_=SQLAlchemyUUID, nullable=False
    )
    name: Mapped[OptionalString] = mapped_column(name="name", type_=String(200))
    gender: Mapped[OptionalGender] = mapped_column(
        name="gender", type_=Enum(Gender, name="gender")
    )
    date_of_birth: Mapped[OptionalDate] = mapped_column(
        name="date_of_birth", type_=Date
    )
    description: Mapped[OptionalString] = mapped_column(name="description", type_=Text)
    impression: Mapped[OptionalString] = mapped_column(name="impression", type_=Text)
    diagnosis: Mapped[str] = mapped_column(name="diagnosis", type_=Text, nullable=False)
    filename: Mapped[str] = mapped_column(name="filename", type_=Text, nullable=False)
