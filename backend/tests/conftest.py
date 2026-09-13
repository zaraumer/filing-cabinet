import os
import shutil
import tempfile

import pytest
from sqlalchemy import create_engine, delete
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

from app import models
from app.database import Base, DATABASE_URL, get_db
from app.main import app


# Use the same PostgreSQL login as development,
# but connect to the separate test database.
test_database_url = make_url(DATABASE_URL).set(
    database="filing_cabinet_test"
)

test_engine = create_engine(test_database_url)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


# Test uploads go to a temporary directory outside the repo.
test_upload_dir = tempfile.mkdtemp(
    prefix="filing-cabinet-test-uploads-"
)
os.environ["UPLOAD_DIR"] = test_upload_dir


def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)
    shutil.rmtree(
        test_upload_dir,
        ignore_errors=True,
    )


@pytest.fixture(autouse=True)
def clear_tables(setup_test_database):
    db = TestingSessionLocal()

    try:
        # Delete child rows before the records they reference.
        db.execute(delete(models.AuditEvent))
        db.execute(delete(models.ProposedUpdate))
        db.execute(delete(models.VerificationRequest))
        db.execute(delete(models.SourceDocument))
        db.execute(delete(models.IntakeDocument))
        db.execute(delete(models.Record))
        db.commit()

    finally:
        db.close()

    yield