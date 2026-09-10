from datetime import date

from sqlalchemy import Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

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