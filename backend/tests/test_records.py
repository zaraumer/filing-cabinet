from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_create_record():
    response = client.post(
        "/records",
        json={
            "first_name": "Test",
            "last_name": "User",
            "email": "test.user@example.com",
            "phone": "416-555-0000",
            "address": "123 Test Street",
            "city": "Toronto",
            "province_state": "Ontario",
            "postal_zip": "M1M 1M1",
            "organization": "Test Organization",
            "reference_number": "TEST-001",
            "record_status": "active",
            "last_verified_date": "2026-09-10",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["first_name"] == "Test"
    assert data["last_name"] == "User"
    assert data["email"] == "test.user@example.com"
    assert "id" in data


def test_get_missing_record():
    response = client.get("/records/999999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Record not found"}

def create_test_record(**overrides):
    record = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test.user@example.com",
        "phone": "416-555-0000",
        "address": "123 Test Street",
        "city": "Toronto",
        "province_state": "Ontario",
        "postal_zip": "M1M 1M1",
        "organization": "Test Organization",
        "reference_number": "TEST-001",
        "record_status": "active",
        "last_verified_date": "2026-09-10",
    }

    record.update(overrides)

    response = client.post("/records", json=record)
    assert response.status_code == 200

    return response.json()

def test_list_records_returns_all_records():
    create_test_record(first_name="Maya", reference_number="FC-1001")
    create_test_record(
        first_name="Jordan",
        email="jordan@example.com",
        reference_number="FC-1002",
    )

    response = client.get("/records")

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 2
    assert data[0]["first_name"] == "Maya"
    assert data[1]["first_name"] == "Jordan"


def test_list_records_with_search_returns_matches():
    create_test_record(
        first_name="Maya",
        organization="Northstar Health",
        reference_number="FC-1001",
    )
    create_test_record(
        first_name="Jordan",
        email="jordan@example.com",
        organization="Blue River Labs",
        reference_number="FC-1002",
    )

    response = client.get("/records?search=Northstar")

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["first_name"] == "Maya"


def test_search_is_case_insensitive_and_partial():
    create_test_record(first_name="Maya", reference_number="FC-1001")

    response = client.get("/records?search=may")

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["first_name"] == "Maya"


def test_search_with_no_match_returns_empty_list():
    create_test_record(first_name="Maya", reference_number="FC-1001")

    response = client.get("/records?search=zzznomatch")

    assert response.status_code == 200
    assert response.json() == []