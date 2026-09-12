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


# Use the same PostgreSQL login as the development database,
# but connect to the separate testing database.
test_database_url = make_url(DATABASE_URL).set(database="filing_cabinet_test")

test_engine = create_engine(test_database_url)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)

# Uploads during tests go to a temporary directory outside the repository,
# so no test file is ever left behind in backend/uploads.
test_upload_dir = tempfile.mkdtemp(prefix="filing-cabinet-test-uploads-")

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
    # Create the tables needed for the tests.
    Base.metadata.create_all(bind=test_engine)

    yield

    # Remove the test tables after the full test run.
    Base.metadata.drop_all(bind=test_engine)

    shutil.rmtree(test_upload_dir, ignore_errors=True)


@pytest.fixture(autouse=True)
def clear_tables(setup_test_database):
    db = TestingSessionLocal()

    try:
        # Source documents reference records, so they are removed first.
        db.execute(delete(models.SourceDocument))
        db.execute(delete(models.Record))
        db.commit()
    finally:
        db.close()

    yield
