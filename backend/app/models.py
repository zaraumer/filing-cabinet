from datetime import date, datetime

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Record(Base):
    __tablename__ = "records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)

    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    province_state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    postal_zip: Mapped[str | None] = mapped_column(String(20), nullable=True)

    organization: Mapped[str | None] = mapped_column(String(150), nullable=True)
    reference_number: Mapped[str | None] = mapped_column(String(100), nullable=True)

    record_status: Mapped[str] = mapped_column(String(50), default="active")
    last_verified_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    source_documents: Mapped[list["SourceDocument"]] = relationship(
        back_populates="record",
    )


class SourceDocument(Base):
    """An uploaded source document (PDF or scanned image) kept with its record.

    Only metadata is stored here. The file itself stays on disk under the
    upload directory, named by stored_filename.
    """

    __tablename__ = "source_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    record_id: Mapped[int] = mapped_column(
        ForeignKey("records.id"),
        index=True,
    )

    # What the uploader called the file, kept for display only.
    original_filename: Mapped[str] = mapped_column(String(255))

    # The generated name actually used on disk. Unique so a repeated upload of
    # the same filename never overwrites an existing source document.
    stored_filename: Mapped[str] = mapped_column(String(255), unique=True)

    content_type: Mapped[str] = mapped_column(String(100))

    # BigInteger leaves room for files larger than the current 10 MB limit.
    file_size: Mapped[int] = mapped_column(BigInteger)

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    record: Mapped["Record"] = relationship(back_populates="source_documents")
