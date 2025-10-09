from datetime import datetime
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, declared_attr, mapped_column
from sqlalchemy.types import Integer, Enum, TIMESTAMP
from uuid import UUID as PythonUUID, uuid4
from maleo.enums.status import DataStatus as DataStatusEnum
from maleo.types.datetime import OptionalDatetime
from maleo.utils.formatter import CaseFormatter


class TableName:
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return CaseFormatter.to_snake(cls.__name__)  # type: ignore


class DataIdentifier:
    id: Mapped[int] = mapped_column("id", Integer, primary_key=True)
    uuid: Mapped[PythonUUID] = mapped_column(
        "uuid", PostgresUUID(as_uuid=True), default=uuid4, unique=True, nullable=False
    )


class DataStatus:
    status: Mapped[DataStatusEnum] = mapped_column(
        "status",
        Enum(DataStatusEnum, name="statustype", create_constraints=True),
        default=DataStatusEnum.ACTIVE,
        nullable=False,
    )


class CreationTimestamp:
    created_at: Mapped[datetime] = mapped_column(
        "created_at",
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class UpdateTimestamp:
    updated_at: Mapped[datetime] = mapped_column(
        "updated_at",
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class LifecyleTimestamp(UpdateTimestamp, CreationTimestamp):
    pass


class DeletionTimestamp:
    deleted_at: Mapped[OptionalDatetime] = mapped_column(
        "deleted_at", TIMESTAMP(timezone=True)
    )


class RestorationTimestamp:
    restored_at: Mapped[OptionalDatetime] = mapped_column(
        "restored_at", TIMESTAMP(timezone=True)
    )


class DeactivationTimestamp:
    deactivated_at: Mapped[OptionalDatetime] = mapped_column(
        "deactivated_at", TIMESTAMP(timezone=True)
    )


class ActivationTimestamp:
    activated_at: Mapped[datetime] = mapped_column(
        "activated_at",
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class StatusTimestamp(
    ActivationTimestamp, DeactivationTimestamp, RestorationTimestamp, DeletionTimestamp
):
    pass


class DataTimestamp(StatusTimestamp, LifecyleTimestamp):
    pass
