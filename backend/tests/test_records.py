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