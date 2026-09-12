from pathlib import Path

from fastapi.testclient import TestClient

from app import storage
from app.main import app


client = TestClient(app)

# Enough of a PDF header that the bytes are not obviously nonsense.
PDF_BYTES = b"%PDF-1.4\nsynthetic test document\n%%EOF\n"
PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"synthetic test image"


def create_record(**overrides):
    record = {
        "first_name": "Doc",
        "last_name": "Owner",
        "email": "doc.owner@example.com",
        "reference_number": "FC-2001",
    }

    record.update(overrides)

    response = client.post("/records", json=record)
    assert response.status_code == 200

    return response.json()


def upload_document(
    record_id: int,
    filename: str = "scan.pdf",
    content: bytes = PDF_BYTES,
    content_type: str = "application/pdf",
):
    return client.post(
        f"/records/{record_id}/documents",
        files={"file": (filename, content, content_type)},
    )


def test_upload_document_succeeds_for_valid_file():
    record = create_record()

    response = upload_document(record["id"])

    assert response.status_code == 201

    data = response.json()

    assert data["record_id"] == record["id"]
    assert data["original_filename"] == "scan.pdf"
    assert data["content_type"] == "application/pdf"
    assert data["file_size"] == len(PDF_BYTES)
    assert data["uploaded_at"]

    # The storage filename is a backend detail and stays out of the response.
    assert "stored_filename" not in data


def test_upload_accepts_png_and_jpeg():
    record = create_record()

    png_response = upload_document(
        record["id"],
        filename="scan.png",
        content=PNG_BYTES,
        content_type="image/png",
    )
    jpeg_response = upload_document(
        record["id"],
        filename="scan.jpg",
        content=b"synthetic jpeg bytes",
        content_type="image/jpeg",
    )

    assert png_response.status_code == 201
    assert jpeg_response.status_code == 201


def test_uploaded_document_belongs_to_the_correct_record():
    first_record = create_record(reference_number="FC-2001")
    second_record = create_record(reference_number="FC-2002")

    upload_document(first_record["id"], filename="first.pdf")

    first_documents = client.get(f"/records/{first_record['id']}/documents").json()
    second_documents = client.get(f"/records/{second_record['id']}/documents").json()

    assert len(first_documents) == 1
    assert first_documents[0]["record_id"] == first_record["id"]
    assert first_documents[0]["original_filename"] == "first.pdf"

    assert second_documents == []


def test_list_documents_for_a_record():
    record = create_record()

    upload_document(record["id"], filename="page-one.pdf")
    upload_document(record["id"], filename="page-two.pdf")

    response = client.get(f"/records/{record['id']}/documents")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert [document["original_filename"] for document in data] == [
        "page-one.pdf",
        "page-two.pdf",
    ]


def test_uploading_the_same_filename_twice_keeps_both_documents():
    record = create_record()

    first = upload_document(record["id"], filename="scan.pdf", content=b"first version")
    second = upload_document(
        record["id"],
        filename="scan.pdf",
        content=b"second version, longer",
    )

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["id"] != second.json()["id"]

    # Both files are still readable, so neither overwrote the other.
    first_download = client.get(
        f"/records/{record['id']}/documents/{first.json()['id']}"
    )
    second_download = client.get(
        f"/records/{record['id']}/documents/{second.json()['id']}"
    )

    assert first_download.content == b"first version"
    assert second_download.content == b"second version, longer"


def test_unsupported_file_type_is_rejected():
    record = create_record()

    response = upload_document(
        record["id"],
        filename="notes.txt",
        content=b"plain text",
        content_type="text/plain",
    )

    assert response.status_code == 415
    assert "Unsupported file type" in response.json()["detail"]

    # Nothing was recorded for the record.
    assert client.get(f"/records/{record['id']}/documents").json() == []


def test_upload_to_missing_record_returns_404():
    response = upload_document(999999)

    assert response.status_code == 404
    assert response.json() == {"detail": "Record not found"}


def test_listing_documents_for_missing_record_returns_404():
    response = client.get("/records/999999/documents")

    assert response.status_code == 404
    assert response.json() == {"detail": "Record not found"}


def test_downloading_a_document_returns_the_stored_file():
    record = create_record()

    document = upload_document(record["id"]).json()

    response = client.get(f"/records/{record['id']}/documents/{document['id']}")

    assert response.status_code == 200
    assert response.content == PDF_BYTES
    assert response.headers["content-type"] == "application/pdf"


def test_missing_document_returns_404():
    record = create_record()

    response = client.get(f"/records/{record['id']}/documents/999999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Document not found"}


def test_document_cannot_be_retrieved_under_the_wrong_record():
    owning_record = create_record(reference_number="FC-2001")
    other_record = create_record(reference_number="FC-2002")

    document = upload_document(owning_record["id"]).json()

    response = client.get(f"/records/{other_record['id']}/documents/{document['id']}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Document not found"}


def test_stored_filename_does_not_reuse_the_uploaded_filename():
    record = create_record()

    upload_dir = Path(storage.get_upload_dir())
    names_before = {path.name for path in upload_dir.iterdir()}

    upload_document(record["id"], filename="../../escape attempt.pdf")

    new_names = {path.name for path in upload_dir.iterdir()} - names_before

    assert len(new_names) == 1

    stored_name = new_names.pop()

    assert "escape" not in stored_name
    assert stored_name.endswith(".pdf")

    # The readable name is kept for display, without any directory part.
    documents = client.get(f"/records/{record['id']}/documents").json()

    assert documents[0]["original_filename"] == "escape attempt.pdf"


def test_file_larger_than_the_limit_is_rejected():
    record = create_record()

    oversized = b"x" * (storage.MAX_FILE_SIZE_BYTES + 1)

    response = upload_document(record["id"], content=oversized)

    assert response.status_code == 413
    assert client.get(f"/records/{record['id']}/documents").json() == []
