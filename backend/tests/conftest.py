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


@pytest.fixture(autouse=True)
def clear_records_table(setup_test_database):
    db = TestingSessionLocal()

    try:
        db.execute(delete(models.Record))
        db.commit()
    finally:
        db.close()

    yield