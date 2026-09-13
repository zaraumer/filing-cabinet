from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def create_test_record(
    email: str | None = "maya.chen@example.com",
) -> dict:
    response = client.post(
        "/records",
        json={
            "first_name": "Maya",
            "last_name": "Chen",
            "email": email,
            "phone": "416-555-0123",
            "address": "100 King Street",
            "city": "Toronto",
            "province_state": "Ontario",
            "postal_zip": "M5H 1J9",
            "organization": "Northstar Health",
            "reference_number": "FC-1001",
            "record_status": "active",
            "last_verified_date": None,
        },
    )

    assert response.status_code == 200
    return response.json()


def create_verification_request(
    record_id: int,
) -> dict:
    response = client.post(
        f"/records/{record_id}/verification-requests",
        json={
            "expires_in_days": 7,
        },
    )

    assert response.status_code == 201
    return response.json()


def submit_update(
    token: str,
    proposed_fields: dict,
) -> dict:
    response = client.post(
        f"/verification/{token}/proposed-updates",
        json={
            "proposed_fields": proposed_fields,
        },
    )

    assert response.status_code == 201
    return response.json()


def test_create_verification_request():
    record = create_test_record()

    response = client.post(
        f"/records/{record['id']}/verification-requests",
        json={
            "expires_in_days": 7,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["record_id"] == record["id"]
    assert data["recipient_email"] == "maya.chen@example.com"
    assert data["status"] == "pending"
    assert data["token"]
    assert data["completed_at"] is None


def test_verification_request_can_override_recipient_email():
    record = create_test_record()

    response = client.post(
        f"/records/{record['id']}/verification-requests",
        json={
            "recipient_email": "alternate@example.com",
            "expires_in_days": 5,
        },
    )

    assert response.status_code == 201
    assert (
        response.json()["recipient_email"]
        == "alternate@example.com"
    )


def test_verification_request_requires_email():
    record = create_test_record(
        email=None,
    )

    response = client.post(
        f"/records/{record['id']}/verification-requests",
        json={
            "expires_in_days": 7,
        },
    )

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == (
            "A recipient email is required because "
            "this record does not have an email address."
        )
    )


def test_get_verification_by_token():
    record = create_test_record()
    request = create_verification_request(
        record["id"]
    )

    response = client.get(
        f"/verification/{request['token']}"
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["verification_request"]["id"]
        == request["id"]
    )
    assert data["record"]["id"] == record["id"]
    assert data["record"]["first_name"] == "Maya"


def test_invalid_verification_token_returns_404():
    response = client.get(
        "/verification/not-a-real-token"
    )

    assert response.status_code == 404
    assert (
        response.json()["detail"]
        == "Verification request not found"
    )


def test_submit_proposed_update():
    record = create_test_record()
    request = create_verification_request(
        record["id"]
    )

    response = client.post(
        f"/verification/{request['token']}/proposed-updates",
        json={
            "proposed_fields": {
                "phone": "647-555-0199",
            },
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["record_id"] == record["id"]
    assert (
        data["verification_request_id"]
        == request["id"]
    )
    assert data["status"] == "pending"
    assert data["proposed_fields"] == {
        "phone": "647-555-0199",
    }


def test_proposed_update_does_not_change_record():
    record = create_test_record()
    request = create_verification_request(
        record["id"]
    )

    submit_update(
        request["token"],
        {
            "phone": "647-555-0199",
        },
    )

    response = client.get(
        f"/records/{record['id']}"
    )

    assert response.status_code == 200
    assert (
        response.json()["phone"]
        == "416-555-0123"
    )


def test_verification_request_only_accepts_one_submission():
    record = create_test_record()
    request = create_verification_request(
        record["id"]
    )

    submit_update(
        request["token"],
        {
            "phone": "647-555-0199",
        },
    )

    response = client.post(
        f"/verification/{request['token']}/proposed-updates",
        json={
            "proposed_fields": {
                "city": "Ottawa",
            },
        },
    )

    assert response.status_code == 409


def test_empty_proposed_update_is_rejected():
    record = create_test_record()
    request = create_verification_request(
        record["id"]
    )

    response = client.post(
        f"/verification/{request['token']}/proposed-updates",
        json={
            "proposed_fields": {},
        },
    )

    assert response.status_code == 422


def test_client_cannot_propose_system_fields():
    record = create_test_record()
    request = create_verification_request(
        record["id"]
    )

    response = client.post(
        f"/verification/{request['token']}/proposed-updates",
        json={
            "proposed_fields": {
                "record_status": "inactive",
            },
        },
    )

    assert response.status_code == 422


def test_list_pending_proposed_updates():
    record = create_test_record()
    request = create_verification_request(
        record["id"]
    )

    proposed_update = submit_update(
        request["token"],
        {
            "phone": "647-555-0199",
        },
    )

    response = client.get(
        "/proposed-updates",
        params={
            "status": "pending",
        },
    )

    assert response.status_code == 200

    updates = response.json()

    assert len(updates) == 1
    assert updates[0]["id"] == proposed_update["id"]


def test_approve_proposed_update_changes_record():
    record = create_test_record()
    request = create_verification_request(
        record["id"]
    )

    proposed_update = submit_update(
        request["token"],
        {
            "phone": "647-555-0199",
            "city": "Ottawa",
        },
    )

    response = client.post(
        (
            f"/proposed-updates/"
            f"{proposed_update['id']}/approve"
        ),
        json={
            "review_note": "Verified correction.",
        },
    )

    assert response.status_code == 200

    reviewed_update = response.json()

    assert reviewed_update["status"] == "approved"
    assert (
        reviewed_update["review_note"]
        == "Verified correction."
    )
    assert reviewed_update["reviewed_at"] is not None

    record_response = client.get(
        f"/records/{record['id']}"
    )

    assert record_response.status_code == 200

    updated_record = record_response.json()

    assert updated_record["phone"] == "647-555-0199"
    assert updated_record["city"] == "Ottawa"
    assert updated_record["last_verified_date"] is not None


def test_approved_update_cannot_be_reviewed_twice():
    record = create_test_record()
    request = create_verification_request(
        record["id"]
    )

    proposed_update = submit_update(
        request["token"],
        {
            "phone": "647-555-0199",
        },
    )

    first_response = client.post(
        (
            f"/proposed-updates/"
            f"{proposed_update['id']}/approve"
        ),
        json={
            "review_note": None,
        },
    )

    assert first_response.status_code == 200

    second_response = client.post(
        (
            f"/proposed-updates/"
            f"{proposed_update['id']}/approve"
        ),
        json={
            "review_note": None,
        },
    )

    assert second_response.status_code == 409


def test_reject_proposed_update_preserves_record():
    record = create_test_record()
    request = create_verification_request(
        record["id"]
    )

    proposed_update = submit_update(
        request["token"],
        {
            "phone": "647-555-0199",
        },
    )

    response = client.post(
        (
            f"/proposed-updates/"
            f"{proposed_update['id']}/reject"
        ),
        json={
            "review_note": "Could not verify this change.",
        },
    )

    assert response.status_code == 200

    reviewed_update = response.json()

    assert reviewed_update["status"] == "rejected"
    assert (
        reviewed_update["review_note"]
        == "Could not verify this change."
    )

    record_response = client.get(
        f"/records/{record['id']}"
    )

    assert record_response.status_code == 200

    unchanged_record = record_response.json()

    assert (
        unchanged_record["phone"]
        == "416-555-0123"
    )
    assert unchanged_record["last_verified_date"] is None