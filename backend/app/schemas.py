from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr


class RecordCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr | None = None
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    province_state: str | None = None
    postal_zip: str | None = None
    organization: str | None = None
    reference_number: str | None = None
    record_status: str = "active"
    last_verified_date: date | None = None


class RecordResponse(RecordCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)