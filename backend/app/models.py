from datetime import date, datetime

from sqlalchemy import (
    JSON,
    BigInteger,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
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
    verification_requests: Mapped[list["VerificationRequest"]] = relationship(
        back_populates="record",
    )
    proposed_updates: Mapped[list["ProposedUpdate"]] = relationship(
        back_populates="record",
    )
    audit_events: Mapped[list["AuditEvent"]] = relationship(
        back_populates="record",
    )


class SourceDocument(Base):
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


class VerificationRequest(Base):
    __tablename__ = "verification_requests"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    record_id: Mapped[int] = mapped_column(
        ForeignKey("records.id"),
        index=True,
    )
    recipient_email: Mapped[str] = mapped_column(
        String(255),
    )
    token: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    record: Mapped["Record"] = relationship(
        back_populates="verification_requests",
    )
    proposed_updates: Mapped[list["ProposedUpdate"]] = relationship(
        back_populates="verification_request",
    )
    audit_events: Mapped[list["AuditEvent"]] = relationship(
        back_populates="verification_request",
    )


class ProposedUpdate(Base):
    __tablename__ = "proposed_updates"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    record_id: Mapped[int] = mapped_column(
        ForeignKey("records.id"),
        index=True,
    )
    verification_request_id: Mapped[int] = mapped_column(
        ForeignKey("verification_requests.id"),
        index=True,
    )
    proposed_fields: Mapped[dict] = mapped_column(
        JSON,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
    )
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    review_note: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    record: Mapped["Record"] = relationship(
        back_populates="proposed_updates",
    )
    verification_request: Mapped["VerificationRequest"] = relationship(
        back_populates="proposed_updates",
    )
    audit_events: Mapped[list["AuditEvent"]] = relationship(
        back_populates="proposed_update",
    )


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    record_id: Mapped[int] = mapped_column(
        ForeignKey("records.id"),
        index=True,
    )
    verification_request_id: Mapped[int | None] = mapped_column(
        ForeignKey("verification_requests.id"),
        nullable=True,
        index=True,
    )
    proposed_update_id: Mapped[int | None] = mapped_column(
        ForeignKey("proposed_updates.id"),
        nullable=True,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(
        String(100),
    )
    actor_type: Mapped[str] = mapped_column(
        String(50),
    )
    details: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    record: Mapped["Record"] = relationship(
        back_populates="audit_events",
    )
    verification_request: Mapped["VerificationRequest | None"] = relationship(
        back_populates="audit_events",
    )
    proposed_update: Mapped["ProposedUpdate | None"] = relationship(
        back_populates="audit_events",
    )