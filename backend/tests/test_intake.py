from fastapi.testclient import TestClient

from app.extraction import extract_record_fields
from app.main import app


client = TestClient(app)

PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"synthetic intake image"


def create_record(**overrides):
    record = {
        "first_name": "Maya",
        "last_name": "Chen",
        "email": "maya.chen@example.com",
        "phone": "416-555-0182",
        "organization": "Northstar Health",
        "reference_number": "FC-1001",
    }

    record.update(overrides)

    response = client.post(
        "/records",
        json=record,
    )

    assert response.status_code == 200
    return response.json()


def upload_intake_document(
    filename="client.png",
    content=PNG_BYTES,
    content_type="image/png",
):
    return client.post(
        "/intake/documents",
        files={
            "file": (
                filename,
                content,
                content_type,
            )
        },
    )


def intake_record_payload(**overrides):
    record = {
        "first_name": "Maya",
        "last_name": "Chen",
        "email": "maya.chen@example.com",
        "phone": "416-555-0182",
        "address": None,
        "city": None,
        "province_state": None,
        "postal_zip": None,
        "organization": "Northstar Health",
        "reference_number": "FC-1001",
        "record_status": "active",
        "last_verified_date": None,
    }

    record.update(overrides)
    return record


def test_extract_record_fields_from_text():
    text = """
    First Name: Maya
    Last Name: Chen
    Email: maya.chen@example.com
    Phone: 416-555-0182
    Organization: Northstar Health
    Reference Number: FC-1001
    Status: Active
    """

    result = extract_record_fields(text)

    assert result["first_name"] == "Maya"
    assert result["last_name"] == "Chen"
    assert result["email"] == "maya.chen@example.com"
    assert result["phone"] == "416-555-0182"
    assert result["organization"] == "Northstar Health"
    assert result["reference_number"] == "FC-1001"
    assert result["record_status"] == "Active"


def test_extract_record_fields_supports_combined_name():
    text = """
    Name: Maya Chen
    Email: maya.chen@example.com
    Organization: Northstar Health
    """

    result = extract_record_fields(text)

    assert result["first_name"] == "Maya"
    assert result["last_name"] == "Chen"
    assert result["email"] == "maya.chen@example.com"


def test_upload_intake_document():
    response = upload_intake_document()

    assert response.status_code == 201

    data = response.json()

    assert data["original_filename"] == "client.png"
    assert data["content_type"] == "image/png"
    assert data["file_size"] == len(PNG_BYTES)
    assert data["created_record_id"] is None
    assert data["uploaded_at"]


def test_get_intake_document():
    uploaded = upload_intake_document().json()

    response = client.get(
        f"/intake/documents/{uploaded['id']}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == uploaded["id"]
    assert data["original_filename"] == "client.png"


def test_missing_intake_document_returns_404():
    response = client.get(
        "/intake/documents/999999"
    )

    assert response.status_code == 404


def test_duplicate_check_finds_exact_match():
    existing = create_record()
    intake = upload_intake_document().json()

    response = client.post(
        f"/intake/documents/{intake['id']}/duplicates",
        json=intake_record_payload(),
    )

    assert response.status_code == 200

    matches = response.json()["matches"]

    assert len(matches) == 1

    match = matches[0]

    assert match["record"]["id"] == existing["id"]
    assert match["score"] > 0
    assert "Same email" in match["reasons"]
    assert "Same phone" in match["reasons"]
    assert "Same reference number" in match["reasons"]
    assert "Very similar name" in match["reasons"]


def test_duplicate_check_normalizes_phone_numbers():
    create_record(
        phone="4165550182",
        email=None,
        reference_number=None,
    )

    intake = upload_intake_document().json()

    payload = intake_record_payload(
        phone="(416) 555-0182",
        email=None,
        reference_number=None,
    )

    response = client.post(
        f"/intake/documents/{intake['id']}/duplicates",
        json=payload,
    )

    assert response.status_code == 200

    matches = response.json()["matches"]

    assert len(matches) == 1
    assert "Same phone" in matches[0]["reasons"]


def test_similar_name_alone_is_not_flagged_as_duplicate():
    create_record(
        email=None,
        phone=None,
        reference_number=None,
    )

    intake = upload_intake_document().json()

    payload = intake_record_payload(
        email=None,
        phone=None,
        reference_number=None,
    )

    response = client.post(
        f"/intake/documents/{intake['id']}/duplicates",
        json=payload,
    )

    assert response.status_code == 200
    assert response.json()["matches"] == []


def test_unique_record_has_no_duplicate_matches():
    create_record()

    intake = upload_intake_document().json()

    payload = intake_record_payload(
        first_name="Jordan",
        last_name="Singh",
        email="jordan.singh@example.com",
        phone="647-555-0144",
        organization="Harbour Clinic",
        reference_number="FC-9001",
    )

    response = client.post(
        f"/intake/documents/{intake['id']}/duplicates",
        json=payload,
    )

    assert response.status_code == 200
    assert response.json()["matches"] == []


def test_create_record_from_intake():
    intake = upload_intake_document(
        filename="new-client.png"
    ).json()

    payload = intake_record_payload(
        first_name="Jordan",
        last_name="Singh",
        email="jordan.singh@example.com",
        phone="647-555-0144",
        organization="Harbour Clinic",
        reference_number="FC-9001",
    )

    payload["duplicate_reviewed"] = False

    response = client.post(
        f"/intake/documents/{intake['id']}/create-record",
        json=payload,
    )

    assert response.status_code == 201

    record = response.json()

    assert record["first_name"] == "Jordan"
    assert record["last_name"] == "Singh"
    assert record["email"] == "jordan.singh@example.com"


def test_created_record_keeps_source_document():
    intake = upload_intake_document(
        filename="source-client.png"
    ).json()

    payload = intake_record_payload(
        first_name="Jordan",
        last_name="Singh",
        email="jordan.singh@example.com",
        phone="647-555-0144",
        reference_number="FC-9001",
    )

    payload["duplicate_reviewed"] = False

    create_response = client.post(
        f"/intake/documents/{intake['id']}/create-record",
        json=payload,
    )

    assert create_response.status_code == 201

    record = create_response.json()

    documents_response = client.get(
        f"/records/{record['id']}/documents"
    )

    assert documents_response.status_code == 200

    documents = documents_response.json()

    assert len(documents) == 1
    assert documents[0]["record_id"] == record["id"]
    assert documents[0]["original_filename"] == "source-client.png"


def test_duplicate_record_creation_requires_review():
    create_record()

    intake = upload_intake_document().json()

    payload = intake_record_payload()
    payload["duplicate_reviewed"] = False

    response = client.post(
        f"/intake/documents/{intake['id']}/create-record",
        json=payload,
    )

    assert response.status_code == 409
    assert "duplicate" in response.json()["detail"].lower()


def test_duplicate_record_can_be_created_after_review():
    create_record()

    intake = upload_intake_document().json()

    payload = intake_record_payload()
    payload["duplicate_reviewed"] = True

    response = client.post(
        f"/intake/documents/{intake['id']}/create-record",
        json=payload,
    )

    assert response.status_code == 201


def test_same_intake_cannot_create_two_records():
    intake = upload_intake_document().json()

    payload = intake_record_payload(
        first_name="Jordan",
        last_name="Singh",
        email="jordan.singh@example.com",
        phone="647-555-0144",
        reference_number="FC-9001",
    )

    payload["duplicate_reviewed"] = False

    first_response = client.post(
        f"/intake/documents/{intake['id']}/create-record",
        json=payload,
    )

    second_response = client.post(
        f"/intake/documents/{intake['id']}/create-record",
        json=payload,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_duplicate_check_for_missing_intake_returns_404():
    response = client.post(
        "/intake/documents/999999/duplicates",
        json=intake_record_payload(),
    )

    assert response.status_code == 404


def test_create_record_from_missing_intake_returns_404():
    payload = intake_record_payload()
    payload["duplicate_reviewed"] = False

    response = client.post(
        "/intake/documents/999999/create-record",
        json=payload,
    )

    assert response.status_code == 404