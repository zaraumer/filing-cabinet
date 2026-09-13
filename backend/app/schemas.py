from datetime import date, datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    model_validator,
)


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


class VerificationRequestCreate(BaseModel):
    recipient_email: EmailStr | None = None
    expires_in_days: int = Field(
        default=7,
        ge=1,
        le=30,
    )


class VerificationRequestResponse(BaseModel):
    id: int
    record_id: int
    recipient_email: EmailStr
    token: str
    status: str
    created_at: datetime
    expires_at: datetime
    completed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class ProposedRecordFields(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    province_state: str | None = None
    postal_zip: str | None = None
    organization: str | None = None

    model_config = ConfigDict(extra="forbid")


class ProposedUpdateCreate(BaseModel):
    proposed_fields: ProposedRecordFields

    @model_validator(mode="after")
    def require_at_least_one_field(self):
        if not self.proposed_fields.model_fields_set:
            raise ValueError(
                "At least one proposed field is required."
            )

        return self


class ProposedUpdateResponse(BaseModel):
    id: int
    record_id: int
    verification_request_id: int
    proposed_fields: dict[str, str | None]
    status: str
    submitted_at: datetime
    reviewed_at: datetime | None
    review_note: str | None

    model_config = ConfigDict(from_attributes=True)


class ProposedUpdateReview(BaseModel):
    review_note: str | None = Field(
        default=None,
        max_length=1000,
    )


class AuditEventResponse(BaseModel):
    id: int
    record_id: int
    verification_request_id: int | None
    proposed_update_id: int | None
    event_type: str
    actor_type: str
    details: dict | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class VerificationViewResponse(BaseModel):
    verification_request: VerificationRequestResponse
    record: RecordResponse