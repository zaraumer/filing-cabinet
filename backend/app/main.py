from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

app = FastAPI(title="Filing Cabinet API")


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


@app.get("/records/{record_id}", response_model=schemas.RecordResponse)
def get_record(
    record_id: int,
    db: Session = Depends(get_db),
):
    record = db.get(models.Record, record_id)

    if record is None:
        raise HTTPException(status_code=404, detail="Record not found")

    return record