from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app import models, schemas
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
    record = db.get(models.Record, record_id)

    if record is None:
        raise HTTPException(status_code=404, detail="Record not found")

    return record