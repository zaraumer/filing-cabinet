from datetime import date, datetime

from sqlalchemy import (
    JSON,
    BigInteger,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Record(Base):
    __tablename__ = "records"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    first_name: Mapped[str] = mapped_column(
        String(100),
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    address: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    city: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    province_state: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    postal_zip: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    organization: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    reference_number: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    record_status: Mapped[str] = mapped_column(
        String(50),
        default="active",
    )

    last_verified_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    source_documents: Mapped[list["SourceDocument"]] = relationship(
        back_populates="record",
    )


class SourceDocument(Base):
    """A source document already linked to an existing record.

    Only metadata is stored in PostgreSQL.
    The actual file remains in the local upload directory.
    """

    __tablename__ = "source_documents"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    record_id: Mapped[int] = mapped_column(
        ForeignKey("records.id"),
        index=True,
    )

    original_filename: Mapped[str] = mapped_column(
        String(255),
    )

    stored_filename: Mapped[str] = mapped_column(
        String(255),
        unique=True,
    )

    content_type: Mapped[str] = mapped_column(
        String(100),
    )

    file_size: Mapped[int] = mapped_column(
        BigInteger,
    )

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    record: Mapped["Record"] = relationship(
        back_populates="source_documents",
    )


class IntakeDocument(Base):
    """A document uploaded before a client record is created.

    The original file is preserved on disk.
    Extracted fields are stored here so staff can review and correct them
    before creating an official Record.
    """

    __tablename__ = "intake_documents"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    original_filename: Mapped[str] = mapped_column(
        String(255),
    )

    stored_filename: Mapped[str] = mapped_column(
        String(255),
        unique=True,
    )

    content_type: Mapped[str] = mapped_column(
        String(100),
    )

    file_size: Mapped[int] = mapped_column(
        BigInteger,
    )

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    extraction_status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
    )

    extracted_fields: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    created_record_id: Mapped[int | None] = mapped_column(
        ForeignKey("records.id"),
        nullable=True,
        index=True,
    )