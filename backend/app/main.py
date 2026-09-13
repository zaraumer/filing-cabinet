import re
import secrets
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app import extraction, models, schemas, storage
from app.database import get_db


app = FastAPI(title="Filing Cabinet API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_existing_record(
    record_id: int,
    db: Session,
) -> models.Record:
    record = db.get(models.Record, record_id)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Record not found",
        )

    return record


def save_uploaded_file(
    file: UploadFile,
) -> tuple[str, str, int]:
    content_type = (
        (file.content_type or "")
        .split(";")[0]
        .strip()
        .lower()
    )

    if content_type not in storage.ALLOWED_CONTENT_TYPES:
        allowed = ", ".join(
            sorted(storage.ALLOWED_CONTENT_TYPES)
        )

        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type. Allowed types: {allowed}",
        )

    stored_filename = storage.build_stored_filename(
        content_type
    )

    stored_path = (
        storage.get_upload_dir()
        / stored_filename
    )

    file_size = 0

    with stored_path.open("xb") as stored_file:
        while chunk := file.file.read(
            storage.CHUNK_SIZE_BYTES
        ):
            file_size += len(chunk)

            if file_size > storage.MAX_FILE_SIZE_BYTES:
                stored_file.close()

                stored_path.unlink(
                    missing_ok=True
                )

                limit_mb = (
                    storage.MAX_FILE_SIZE_BYTES
                    // (1024 * 1024)
                )

                raise HTTPException(
                    status_code=413,
                    detail=(
                        "File is larger than the "
                        f"{limit_mb} MB limit"
                    ),
                )

            stored_file.write(chunk)

    if file_size == 0:
        stored_path.unlink(
            missing_ok=True
        )

        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty",
        )

    return (
        stored_filename,
        content_type,
        file_size,
    )


def intake_document_to_dict(
    intake: models.IntakeDocument,
) -> dict:
    return {
        "id": intake.id,
        "original_filename": intake.original_filename,
        "content_type": intake.content_type,
        "file_size": intake.file_size,
        "uploaded_at": intake.uploaded_at,
        "extraction_status": intake.extraction_status,
        "extracted_fields": intake.extracted_fields,
        "created_record_id": intake.created_record_id,
    }


def normalize_email(
    value: str | None,
) -> str:
    if not value:
        return ""

    return value.strip().lower()


def normalize_phone(
    value: str | None,
) -> str:
    return re.sub(
        r"\D",
        "",
        value or "",
    )


def normalize_text_value(
    value: str | None,
) -> str:
    return " ".join(
        (value or "")
        .lower()
        .split()
    )


def compare_duplicate(
    incoming: schemas.RecordCreate,
    existing: models.Record,
) -> tuple[int, list[str]]:
    score = 0
    reasons = []

    incoming_email = normalize_email(
        incoming.email
    )

    existing_email = normalize_email(
        existing.email
    )

    if (
        incoming_email
        and existing_email
        and incoming_email == existing_email
    ):
        score += 50
        reasons.append("Same email")

    incoming_phone = normalize_phone(
        incoming.phone
    )

    existing_phone = normalize_phone(
        existing.phone
    )

    if (
        incoming_phone
        and existing_phone
        and incoming_phone == existing_phone
    ):
        score += 35
        reasons.append("Same phone")

    incoming_reference = normalize_text_value(
        incoming.reference_number
    )

    existing_reference = normalize_text_value(
        existing.reference_number
    )

    if (
        incoming_reference
        and existing_reference
        and incoming_reference == existing_reference
    ):
        score += 50
        reasons.append(
            "Same reference number"
        )

    incoming_name = normalize_text_value(
        f"{incoming.first_name} {incoming.last_name}"
    )

    existing_name = normalize_text_value(
        f"{existing.first_name} {existing.last_name}"
    )

    name_similarity = SequenceMatcher(
        None,
        incoming_name,
        existing_name,
    ).ratio()

    if name_similarity >= 0.9:
        score += 20
        reasons.append(
            "Very similar name"
        )

    return score, reasons


def find_duplicate_matches(
    record_data: schemas.RecordCreate,
    db: Session,
) -> list[dict]:
    records = db.scalars(
        select(models.Record)
    ).all()

    matches = []

    for record in records:
        score, reasons = compare_duplicate(
            record_data,
            record,
        )

        # A name match on its own is too weak to flag
        if score >= 35:
            matches.append(
                {
                    "record": record,
                    "score": score,
                    "reasons": reasons,
                }
            )

    matches.sort(
        key=lambda match: match["score"],
        reverse=True,
    )

    return matches


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }


# Records


@app.post(
    "/records",
    response_model=schemas.RecordResponse,
)
def create_record(
    record: schemas.RecordCreate,
    db: Session = Depends(get_db),
):
    new_record = models.Record(
        **record.model_dump()
    )

    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    return new_record


@app.get(
    "/records",
    response_model=list[
        schemas.RecordResponse
    ],
)
def list_records(
    search: str | None = None,
    db: Session = Depends(get_db),
):
    query = select(
        models.Record
    )

    if search and search.strip():
        pattern = (
            f"%{search.strip()}%"
        )

        query = query.where(
            or_(
                models.Record.first_name.ilike(
                    pattern
                ),
                models.Record.last_name.ilike(
                    pattern
                ),
                models.Record.email.ilike(
                    pattern
                ),
                models.Record.phone.ilike(
                    pattern
                ),
                models.Record.organization.ilike(
                    pattern
                ),
                models.Record.reference_number.ilike(
                    pattern
                ),
            )
        )

    return db.scalars(
        query.order_by(
            models.Record.id
        )
    ).all()


@app.get(
    "/records/{record_id}",
    response_model=schemas.RecordResponse,
)
def get_record(
    record_id: int,
    db: Session = Depends(get_db),
):
    return get_existing_record(
        record_id,
        db,
    )


# Record documents


@app.post(
    "/records/{record_id}/documents",
    response_model=schemas.SourceDocumentResponse,
    status_code=201,
)
def upload_source_document(
    record_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    get_existing_record(
        record_id,
        db,
    )

    (
        stored_filename,
        content_type,
        file_size,
    ) = save_uploaded_file(
        file
    )

    document = models.SourceDocument(
        record_id=record_id,
        original_filename=(
            storage.clean_original_filename(
                file.filename
            )
        ),
        stored_filename=stored_filename,
        content_type=content_type,
        file_size=file_size,
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document


@app.get(
    "/records/{record_id}/documents",
    response_model=list[
        schemas.SourceDocumentResponse
    ],
)
def list_source_documents(
    record_id: int,
    db: Session = Depends(get_db),
):
    get_existing_record(
        record_id,
        db,
    )

    query = (
        select(
            models.SourceDocument
        )
        .where(
            models.SourceDocument.record_id
            == record_id
        )
        .order_by(
            models.SourceDocument.id
        )
    )

    return db.scalars(
        query
    ).all()


@app.get(
    "/records/{record_id}/documents/{document_id}"
)
def download_source_document(
    record_id: int,
    document_id: int,
    db: Session = Depends(get_db),
):
    get_existing_record(
        record_id,
        db,
    )

    document = db.get(
        models.SourceDocument,
        document_id,
    )

    if (
        document is None
        or document.record_id != record_id
    ):
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    stored_path = (
        storage.resolve_stored_path(
            document.stored_filename
        )
    )

    if stored_path is None:
        raise HTTPException(
            status_code=404,
            detail="Stored file is missing",
        )

    return FileResponse(
        stored_path,
        media_type=document.content_type,
        filename=document.original_filename,
        content_disposition_type="inline",
    )


# Document intake


@app.post(
    "/intake/documents",
    response_model=schemas.IntakeDocumentResponse,
    status_code=201,
)
def upload_intake_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    (
        stored_filename,
        content_type,
        file_size,
    ) = save_uploaded_file(
        file
    )

    stored_path = (
        storage.get_upload_dir()
        / stored_filename
    )

    extracted_fields = (
        extraction.extract_record_fields(
            ""
        )
    )

    extraction_status = (
        "manual_review"
    )

    if content_type == "application/pdf":
        try:
            pdf_text = (
                extraction.extract_pdf_text(
                    stored_path
                )
            )

            extracted_fields = (
                extraction.extract_record_fields(
                    pdf_text
                )
            )

            if any(
                value
                for value
                in extracted_fields.values()
            ):
                extraction_status = (
                    "extracted"
                )

        except Exception:
            # Keep the original document
            extraction_status = (
                "manual_review"
            )

    intake = models.IntakeDocument(
        original_filename=(
            storage.clean_original_filename(
                file.filename
            )
        ),
        stored_filename=stored_filename,
        content_type=content_type,
        file_size=file_size,
        extraction_status=extraction_status,
        extracted_fields=extracted_fields,
    )

    db.add(intake)
    db.commit()
    db.refresh(intake)

    return intake_document_to_dict(
        intake
    )


@app.get(
    "/intake/documents/{intake_id}",
    response_model=schemas.IntakeDocumentResponse,
)
def get_intake_document(
    intake_id: int,
    db: Session = Depends(get_db),
):
    intake = db.get(
        models.IntakeDocument,
        intake_id,
    )

    if intake is None:
        raise HTTPException(
            status_code=404,
            detail="Intake document not found",
        )

    return intake_document_to_dict(
        intake
    )


@app.post(
    "/intake/documents/{intake_id}/duplicates",
    response_model=schemas.DuplicateCheckResponse,
)
def check_intake_duplicates(
    intake_id: int,
    record_data: schemas.RecordCreate,
    db: Session = Depends(get_db),
):
    intake = db.get(
        models.IntakeDocument,
        intake_id,
    )

    if intake is None:
        raise HTTPException(
            status_code=404,
            detail="Intake document not found",
        )

    matches = find_duplicate_matches(
        record_data,
        db,
    )

    return {
        "matches": matches
    }


@app.post(
    "/intake/documents/{intake_id}/create-record",
    response_model=schemas.RecordResponse,
    status_code=201,
)
def create_record_from_intake(
    intake_id: int,
    record_data: schemas.IntakeRecordCreate,
    db: Session = Depends(get_db),
):
    intake = db.get(
        models.IntakeDocument,
        intake_id,
    )

    if intake is None:
        raise HTTPException(
            status_code=404,
            detail="Intake document not found",
        )

    if intake.created_record_id is not None:
        raise HTTPException(
            status_code=409,
            detail=(
                "A record has already been "
                "created from this document"
            ),
        )

    matches = find_duplicate_matches(
        record_data,
        db,
    )

    if matches and not record_data.duplicate_reviewed:
        raise HTTPException(
            status_code=409,
            detail=(
                "Possible duplicate records found. "
                "Review them before creating this record."
            ),
        )

    record = models.Record(
        **record_data.model_dump(
            exclude={"duplicate_reviewed"}
        )
    )

    db.add(record)

    # Need the ID before linking the original document
    db.flush()

    source_document = models.SourceDocument(
        record_id=record.id,
        original_filename=intake.original_filename,
        stored_filename=intake.stored_filename,
        content_type=intake.content_type,
        file_size=intake.file_size,
    )

    db.add(source_document)

    intake.created_record_id = record.id

    db.commit()
    db.refresh(record)

    return record

# Verification


@app.post(
    "/records/{record_id}/verification-requests",
    response_model=schemas.VerificationRequestResponse,
    status_code=201,
)
def create_verification_request(
    record_id: int,
    request_data: schemas.VerificationRequestCreate,
    db: Session = Depends(get_db),
):
    record = get_existing_record(
        record_id,
        db,
    )

    recipient_email = (
        str(request_data.recipient_email)
        if request_data.recipient_email
        else record.email
    )

    if not recipient_email:
        raise HTTPException(
            status_code=400,
            detail=(
                "A recipient email is required because "
                "this record does not have an email address."
            ),
        )

    now = datetime.now(timezone.utc)

    verification_request = models.VerificationRequest(
        record_id=record.id,
        recipient_email=recipient_email,
        token=secrets.token_urlsafe(32),
        status="pending",
        expires_at=now + timedelta(
            days=request_data.expires_in_days
        ),
    )

    db.add(verification_request)

    # The request ID is needed for audit event
    db.flush()

    audit_event = models.AuditEvent(
        record_id=record.id,
        verification_request_id=verification_request.id,
        event_type="verification_requested",
        actor_type="staff",
        details={
            "recipient_email": recipient_email,
            "expires_in_days": request_data.expires_in_days,
        },
    )

    db.add(audit_event)
    db.commit()
    db.refresh(verification_request)

    return verification_request


@app.get(
    "/verification/{token}",
    response_model=schemas.VerificationViewResponse,
)
def get_verification(
    token: str,
    db: Session = Depends(get_db),
):
    verification_request = db.scalar(
        select(models.VerificationRequest).where(
            models.VerificationRequest.token == token
        )
    )

    if verification_request is None:
        raise HTTPException(
            status_code=404,
            detail="Verification request not found",
        )

    if verification_request.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=410,
            detail="Verification request has expired",
        )

    record = get_existing_record(
        verification_request.record_id,
        db,
    )

    return {
        "verification_request": verification_request,
        "record": record,
    }


@app.post(
    "/verification/{token}/confirm",
    response_model=schemas.VerificationRequestResponse,
)
def confirm_verification(
    token: str,
    db: Session = Depends(get_db),
):
    verification_request = db.scalar(
        select(models.VerificationRequest).where(
            models.VerificationRequest.token == token
        )
    )

    if verification_request is None:
        raise HTTPException(
            status_code=404,
            detail="Verification request not found",
        )

    if verification_request.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=410,
            detail="Verification request has expired",
        )

    if verification_request.status != "pending":
        raise HTTPException(
            status_code=409,
            detail="This verification request has already been completed",
        )

    record = get_existing_record(
        verification_request.record_id,
        db,
    )

    completed_at = datetime.now(timezone.utc)

    # Nothing changed, request can finish without staff review
    verification_request.status = "completed"
    verification_request.completed_at = completed_at
    record.last_verified_date = completed_at.date()

    audit_event = models.AuditEvent(
        record_id=record.id,
        verification_request_id=verification_request.id,
        event_type="verification_confirmed",
        actor_type="record_owner",
        details=None,
    )

    db.add(audit_event)
    db.commit()
    db.refresh(verification_request)

    return verification_request


@app.post(
    "/verification/{token}/proposed-updates",
    response_model=schemas.ProposedUpdateResponse,
    status_code=201,
)
def submit_proposed_update(
    token: str,
    update_data: schemas.ProposedUpdateCreate,
    db: Session = Depends(get_db),
):
    verification_request = db.scalar(
        select(models.VerificationRequest).where(
            models.VerificationRequest.token == token
        )
    )

    if verification_request is None:
        raise HTTPException(
            status_code=404,
            detail="Verification request not found",
        )

    if verification_request.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=410,
            detail="Verification request has expired",
        )

    if verification_request.status != "pending":
        raise HTTPException(
            status_code=409,
            detail="This verification request is no longer accepting updates",
        )

    existing_update = db.scalar(
        select(models.ProposedUpdate).where(
            models.ProposedUpdate.verification_request_id
            == verification_request.id
        )
    )

    if existing_update is not None:
        raise HTTPException(
            status_code=409,
            detail=(
                "A proposed update has already been submitted "
                "for this verification request."
            ),
        )

    proposed_fields = update_data.proposed_fields.model_dump(
        exclude_unset=True
    )

    proposed_update = models.ProposedUpdate(
        record_id=verification_request.record_id,
        verification_request_id=verification_request.id,
        proposed_fields=proposed_fields,
        status="pending",
    )

    db.add(proposed_update)
    db.flush()

    verification_request.status = "submitted"

    audit_event = models.AuditEvent(
        record_id=verification_request.record_id,
        verification_request_id=verification_request.id,
        proposed_update_id=proposed_update.id,
        event_type="proposed_update_submitted",
        actor_type="record_owner",
        details={
            "fields": list(proposed_fields.keys()),
        },
    )

    db.add(audit_event)
    db.commit()
    db.refresh(proposed_update)

    return proposed_update

# Proposed update review


@app.get(
    "/proposed-updates",
    response_model=list[schemas.ProposedUpdateResponse],
)
def list_proposed_updates(
    status: str | None = None,
    db: Session = Depends(get_db),
):
    query = select(models.ProposedUpdate)

    if status:
        query = query.where(
            models.ProposedUpdate.status == status
        )

    query = query.order_by(
        models.ProposedUpdate.submitted_at.desc()
    )

    return db.scalars(query).all()


@app.post(
    "/proposed-updates/{proposed_update_id}/approve",
    response_model=schemas.ProposedUpdateResponse,
)
def approve_proposed_update(
    proposed_update_id: int,
    review_data: schemas.ProposedUpdateReview,
    db: Session = Depends(get_db),
):
    proposed_update = db.get(
        models.ProposedUpdate,
        proposed_update_id,
    )

    if proposed_update is None:
        raise HTTPException(
            status_code=404,
            detail="Proposed update not found",
        )

    if proposed_update.status != "pending":
        raise HTTPException(
            status_code=409,
            detail="This proposed update has already been reviewed",
        )

    record = get_existing_record(
        proposed_update.record_id,
        db,
    )

    verification_request = db.get(
        models.VerificationRequest,
        proposed_update.verification_request_id,
    )

    if verification_request is None:
        raise HTTPException(
            status_code=404,
            detail="Verification request not found",
        )

    changes = {}

    for field_name, new_value in proposed_update.proposed_fields.items():
        old_value = getattr(record, field_name)

        if old_value != new_value:
            changes[field_name] = {
                "old": old_value,
                "new": new_value,
            }

            setattr(
                record,
                field_name,
                new_value,
            )

    today = datetime.now(timezone.utc).date()
    record.last_verified_date = today

    reviewed_at = datetime.now(timezone.utc)

    proposed_update.status = "approved"
    proposed_update.reviewed_at = reviewed_at
    proposed_update.review_note = review_data.review_note

    verification_request.status = "completed"
    verification_request.completed_at = reviewed_at

    approval_event = models.AuditEvent(
        record_id=record.id,
        verification_request_id=verification_request.id,
        proposed_update_id=proposed_update.id,
        event_type="proposed_update_approved",
        actor_type="staff",
        details={
            "review_note": review_data.review_note,
        },
    )

    db.add(approval_event)

    if changes:
        record_updated_event = models.AuditEvent(
            record_id=record.id,
            verification_request_id=verification_request.id,
            proposed_update_id=proposed_update.id,
            event_type="record_updated",
            actor_type="staff",
            details={
                "changes": changes,
            },
        )

        db.add(record_updated_event)

    db.commit()
    db.refresh(proposed_update)

    return proposed_update


@app.post(
    "/proposed-updates/{proposed_update_id}/reject",
    response_model=schemas.ProposedUpdateResponse,
)
def reject_proposed_update(
    proposed_update_id: int,
    review_data: schemas.ProposedUpdateReview,
    db: Session = Depends(get_db),
):
    proposed_update = db.get(
        models.ProposedUpdate,
        proposed_update_id,
    )

    if proposed_update is None:
        raise HTTPException(
            status_code=404,
            detail="Proposed update not found",
        )

    if proposed_update.status != "pending":
        raise HTTPException(
            status_code=409,
            detail="This proposed update has already been reviewed",
        )

    verification_request = db.get(
        models.VerificationRequest,
        proposed_update.verification_request_id,
    )

    if verification_request is None:
        raise HTTPException(
            status_code=404,
            detail="Verification request not found",
        )

    reviewed_at = datetime.now(timezone.utc)

    proposed_update.status = "rejected"
    proposed_update.reviewed_at = reviewed_at
    proposed_update.review_note = review_data.review_note

    verification_request.status = "completed"
    verification_request.completed_at = reviewed_at

    audit_event = models.AuditEvent(
        record_id=proposed_update.record_id,
        verification_request_id=verification_request.id,
        proposed_update_id=proposed_update.id,
        event_type="proposed_update_rejected",
        actor_type="staff",
        details={
            "review_note": review_data.review_note,
        },
    )

    db.add(audit_event)
    db.commit()
    db.refresh(proposed_update)

    return proposed_update

    # Audit history


@app.get(
    "/records/{record_id}/audit-events",
    response_model=list[schemas.AuditEventResponse],
)
def list_audit_events(
    record_id: int,
    db: Session = Depends(get_db),
):
    get_existing_record(
        record_id,
        db,
    )

    query = (
        select(models.AuditEvent)
        .where(
            models.AuditEvent.record_id == record_id
        )
        .order_by(
            models.AuditEvent.created_at.desc()
        )
    )

    return db.scalars(query).all()