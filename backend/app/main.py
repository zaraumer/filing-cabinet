from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app import models, schemas, storage
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


def get_existing_record(record_id: int, db: Session) -> models.Record:
    """Load a record or raise the shared 404 used across the record routes."""
    record = db.get(models.Record, record_id)

    if record is None:
        raise HTTPException(status_code=404, detail="Record not found")

    return record


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/records", response_model=schemas.RecordResponse)
def create_record(
    record: schemas.RecordCreate,
    db: Session = Depends(get_db),
):
    new_record = models.Record(**record.model_dump())

    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    return new_record


@app.get("/records", response_model=list[schemas.RecordResponse])
def list_records(
    search: str | None = None,
    db: Session = Depends(get_db),
):
    query = select(models.Record)

    if search and search.strip():
        # Wrapping the search text in % makes it a partial match,
        # and ilike keeps the comparison case-insensitive.
        pattern = f"%{search.strip()}%"

        query = query.where(
            or_(
                models.Record.first_name.ilike(pattern),
                models.Record.last_name.ilike(pattern),
                models.Record.email.ilike(pattern),
                models.Record.phone.ilike(pattern),
                models.Record.organization.ilike(pattern),
                models.Record.reference_number.ilike(pattern),
            )
        )

    return db.scalars(query.order_by(models.Record.id)).all()


@app.get("/records/{record_id}", response_model=schemas.RecordResponse)
def get_record(
    record_id: int,
    db: Session = Depends(get_db),
):
    return get_existing_record(record_id, db)


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
    """Store an uploaded source document and attach it to a record."""
    get_existing_record(record_id, db)

    content_type = (file.content_type or "").split(";")[0].strip().lower()

    if content_type not in storage.ALLOWED_CONTENT_TYPES:
        allowed = ", ".join(sorted(storage.ALLOWED_CONTENT_TYPES))

        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type. Allowed types: {allowed}",
        )

    stored_filename = storage.build_stored_filename(content_type)
    stored_path = storage.get_upload_dir() / stored_filename

    file_size = 0

    # "xb" fails instead of overwriting if the generated name somehow exists.
    with stored_path.open("xb") as stored_file:
        while chunk := file.file.read(storage.CHUNK_SIZE_BYTES):
            file_size += len(chunk)

            if file_size > storage.MAX_FILE_SIZE_BYTES:
                stored_file.close()
                stored_path.unlink(missing_ok=True)

                limit_mb = storage.MAX_FILE_SIZE_BYTES // (1024 * 1024)

                raise HTTPException(
                    status_code=413,
                    detail=f"File is larger than the {limit_mb} MB limit",
                )

            stored_file.write(chunk)

    if file_size == 0:
        stored_path.unlink(missing_ok=True)

        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    document = models.SourceDocument(
        record_id=record_id,
        original_filename=storage.clean_original_filename(file.filename),
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
    response_model=list[schemas.SourceDocumentResponse],
)
def list_source_documents(
    record_id: int,
    db: Session = Depends(get_db),
):
    get_existing_record(record_id, db)

    query = (
        select(models.SourceDocument)
        .where(models.SourceDocument.record_id == record_id)
        .order_by(models.SourceDocument.id)
    )

    return db.scalars(query).all()


@app.get("/records/{record_id}/documents/{document_id}")
def download_source_document(
    record_id: int,
    document_id: int,
    db: Session = Depends(get_db),
):
    """Serve a stored document, but only through the record that owns it."""
    get_existing_record(record_id, db)

    document = db.get(models.SourceDocument, document_id)

    # Matching on record_id as well means a document id from another record
    # cannot be read through this record's URL.
    if document is None or document.record_id != record_id:
        raise HTTPException(status_code=404, detail="Document not found")

    stored_path = storage.resolve_stored_path(document.stored_filename)

    if stored_path is None:
        raise HTTPException(status_code=404, detail="Stored file is missing")

    return FileResponse(
        stored_path,
        media_type=document.content_type,
        filename=document.original_filename,
        content_disposition_type="inline",
    )
