from sqlalchemy import delete, select

from app.database import SessionLocal
from app.models import (
    AuditEvent,
    ProposedUpdate,
    Record,
    SourceDocument,
    VerificationRequest,
)


SEED_REFERENCE_PREFIX = "SYN-"


def main() -> None:
    db = SessionLocal()

    try:
        seed_record_ids = db.scalars(
            select(Record.id).where(
                Record.reference_number.like(
                    f"{SEED_REFERENCE_PREFIX}%"
                )
            )
        ).all()

        if not seed_record_ids:
            print(
                "No synthetic seed records were found."
            )
            return

        print(
            f"Removing {len(seed_record_ids)} "
            "synthetic records..."
        )

        db.execute(
            delete(AuditEvent).where(
                AuditEvent.record_id.in_(
                    seed_record_ids
                )
            )
        )

        db.execute(
            delete(ProposedUpdate).where(
                ProposedUpdate.record_id.in_(
                    seed_record_ids
                )
            )
        )

        db.execute(
            delete(VerificationRequest).where(
                VerificationRequest.record_id.in_(
                    seed_record_ids
                )
            )
        )

        db.execute(
            delete(SourceDocument).where(
                SourceDocument.record_id.in_(
                    seed_record_ids
                )
            )
        )

        db.execute(
            delete(Record).where(
                Record.id.in_(
                    seed_record_ids
                )
            )
        )

        db.commit()

        print(
            "Synthetic seed records removed."
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()