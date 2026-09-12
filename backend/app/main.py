import re
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

        # A name match on its own is too weak to flag.
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
            # Keep the original document even if text extraction fails.
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

    # Need the ID before linking the original document.
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