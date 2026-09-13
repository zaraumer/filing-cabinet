from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import func, select

from app.database import SessionLocal
from app.models import Record


BASE_RECORD_COUNT = 500
DUPLICATE_COUNT = 20
SEED_REFERENCE_PREFIX = "SYN-"

ANCHOR_DATE = date(2026, 9, 1)

FIRST_NAMES = [
    "Maya",
    "Aaliyah",
    "Noah",
    "Liam",
    "Emma",
    "Olivia",
    "Ethan",
    "Sophia",
    "Lucas",
    "Ava",
    "Amir",
    "Nadia",
    "Daniel",
    "Priya",
    "Marcus",
    "Elena",
    "Jordan",
    "Leila",
    "Owen",
    "Zoe",
    "Adam",
    "Sarah",
    "Isaac",
    "Layla",
    "Nathan",
    "Hannah",
    "Samir",
    "Chloe",
    "Jonah",
    "Amara",
]

LAST_NAMES = [
    "Chen",
    "Patel",
    "Williams",
    "Nguyen",
    "Brown",
    "Singh",
    "Martin",
    "Wilson",
    "Garcia",
    "Khan",
    "Taylor",
    "Anderson",
    "Thomas",
    "Moore",
    "Clark",
    "Lopez",
    "Young",
    "Scott",
    "Hall",
    "Lewis",
    "Ahmed",
    "Shah",
    "Campbell",
    "Robinson",
    "Bennett",
    "Morgan",
    "Reid",
    "Foster",
    "Turner",
    "Carter",
]

STREET_NAMES = [
    "King Street",
    "Queen Street",
    "Danforth Avenue",
    "Bloor Street",
    "Yonge Street",
    "Eglinton Avenue",
    "Lawrence Avenue",
    "Kennedy Road",
    "Victoria Park Avenue",
    "Sheppard Avenue",
]

CITIES = [
    ("Toronto", "ON"),
    ("Scarborough", "ON"),
    ("North York", "ON"),
    ("Mississauga", "ON"),
    ("Brampton", "ON"),
    ("Markham", "ON"),
    ("Vaughan", "ON"),
]

ORGANIZATIONS = [
    "Northstar Health",
    "Maple Community Services",
    "Harbour Support Network",
    "BrightPath Consulting",
    "Cedar Wellness Group",
    "Metro Family Services",
    "Evergreen Outreach",
    "Lakeside Support Centre",
    "Compass Employment Services",
    "Oakridge Community Care",
]

STATUSES = [
    "active",
    "active",
    "active",
    "active",
    "pending",
    "inactive",
]


def build_phone(index: int) -> str:
    area_codes = [
        "416",
        "647",
        "437",
        "905",
    ]

    area_code = area_codes[
        index % len(area_codes)
    ]

    middle = 200 + ((index * 7) % 700)
    last = 1000 + ((index * 37) % 9000)

    return (
        f"{area_code}-"
        f"{middle:03d}-"
        f"{last:04d}"
    )


def build_postal_code(index: int) -> str:
    letters = "ABCEGHJKLMNPRSTVWXYZ"

    first = letters[
        index % len(letters)
    ]

    second = (index * 3) % 10

    third = letters[
        (index * 5) % len(letters)
    ]

    fourth = (index * 7) % 10

    fifth = letters[
        (index * 11) % len(letters)
    ]

    sixth = (index * 13) % 10

    return (
        f"{first}{second}{third} "
        f"{fourth}{fifth}{sixth}"
    )


def build_record(index: int) -> Record:
    first_name = FIRST_NAMES[
        index % len(FIRST_NAMES)
    ]

    last_name = LAST_NAMES[
        (index // len(FIRST_NAMES))
        % len(LAST_NAMES)
    ]

    city, province = CITIES[
        index % len(CITIES)
    ]

    street_number = 100 + index

    email = (
        f"{first_name.lower()}."
        f"{last_name.lower()}."
        f"{index}@example.com"
    )

    last_verified_date = (
        ANCHOR_DATE
        - timedelta(
            days=(index * 11) % 365
        )
    )

    return Record(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=build_phone(index),
        address=(
            f"{street_number} "
            f"{STREET_NAMES[index % len(STREET_NAMES)]}"
        ),
        city=city,
        province_state=province,
        postal_zip=build_postal_code(index),
        organization=ORGANIZATIONS[
            index % len(ORGANIZATIONS)
        ],
        reference_number=(
            f"{SEED_REFERENCE_PREFIX}"
            f"{index + 1:04d}"
        ),
        record_status=STATUSES[
            index % len(STATUSES)
        ],
        last_verified_date=last_verified_date,
    )


def build_duplicate_records(
    source_records: list[Record],
) -> list[Record]:
    duplicate_indexes = [
        8,
        26,
        43,
        71,
        94,
        118,
        143,
        167,
        189,
        211,
        236,
        258,
        281,
        309,
        337,
        361,
        386,
        411,
        438,
        472,
    ]

    duplicates: list[Record] = []

    for duplicate_number, source_index in enumerate(
        duplicate_indexes,
        start=1,
    ):
        source = source_records[
            source_index
        ]

        duplicate = Record(
            first_name=source.first_name,
            last_name=source.last_name,
            email=source.email,
            phone=source.phone,
            address=source.address,
            city=source.city,
            province_state=source.province_state,
            postal_zip=source.postal_zip,
            organization=source.organization,
            reference_number=(
                f"{SEED_REFERENCE_PREFIX}"
                f"DUP-{duplicate_number:03d}"
            ),
            record_status="active",
            last_verified_date=(
                source.last_verified_date
            ),
        )

        if duplicate_number % 2 == 0:
            duplicate.phone = (
                duplicate.phone.replace(
                    "-",
                    "",
                )
                if duplicate.phone
                else None
            )

        if duplicate_number % 3 == 0:
            duplicate.address = (
                duplicate.address.replace(
                    "Street",
                    "St",
                )
                if duplicate.address
                else None
            )

        if duplicate_number % 4 == 0:
            duplicate.email = (
                duplicate.email.replace(
                    "@example.com",
                    "+old@example.com",
                )
                if duplicate.email
                else None
            )

        duplicates.append(duplicate)

    return duplicates


def count_existing_seed_records(db) -> int:
    count = db.scalar(
        select(func.count())
        .select_from(Record)
        .where(
            Record.reference_number.like(
                f"{SEED_REFERENCE_PREFIX}%"
            )
        )
    )

    return count or 0


def main() -> None:
    db = SessionLocal()

    try:
        existing_count = (
            count_existing_seed_records(db)
        )

        if existing_count > 0:
            print(
                "Synthetic seed data already exists."
            )

            print(
                f"Found {existing_count} "
                "records with SYN- reference numbers."
            )

            print(
                "No records were added."
            )

            return

        base_records = [
            build_record(index)
            for index in range(
                BASE_RECORD_COUNT
            )
        ]

        duplicates = (
            build_duplicate_records(
                base_records
            )
        )

        all_records = (
            base_records + duplicates
        )

        db.add_all(all_records)
        db.commit()

        print(
            f"Created "
            f"{len(base_records)} "
            "base synthetic records."
        )

        print(
            f"Created "
            f"{len(duplicates)} "
            "deliberate duplicate cases."
        )

        print(
            f"Total synthetic records: "
            f"{len(all_records)}"
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()