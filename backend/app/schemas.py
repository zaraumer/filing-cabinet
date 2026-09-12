from datetime import date, datetime

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


class IntakeRecordCreate(RecordCreate):
    duplicate_reviewed: bool = False


class RecordResponse(RecordCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class SourceDocumentResponse(BaseModel):
    id: int
    record_id: int
    original_filename: str
    content_type: str
    file_size: int
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class IntakeDocumentResponse(BaseModel):
    id: int
    original_filename: str
    content_type: str
    file_size: int
    uploaded_at: datetime
    extraction_status: str
    extracted_fields: dict[str, str | None] | None
    created_record_id: int | None

    model_config = ConfigDict(from_attributes=True)


class DuplicateMatch(BaseModel):
    record: RecordResponse
    score: int
    reasons: list[str]


class DuplicateCheckResponse(BaseModel):
    matches: list[DuplicateMatch]