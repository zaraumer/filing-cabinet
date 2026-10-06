import sys
from itertools import combinations
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal
from app import models
from app.main import compare_duplicate

THRESHOLD = 35

DUPLICATE_INDEXES = [
    8, 26, 43, 71, 94, 118, 143, 167, 189, 211,
    236, 258, 281, 309, 337, 361, 386, 411, 438, 472,
]


def is_dup(record):
    return "DUP-" in (record.reference_number or "")


def main():
    db = SessionLocal()
    try:
        records = (
            db.query(models.Record)
            .order_by(models.Record.id)
            .all()
        )
        print(f"Total records in database: {len(records)}")

        base = [r for r in records if not is_dup(r)]
        dups = sorted(
            [r for r in records if is_dup(r)],
            key=lambda r: r.reference_number,
        )
        print(f"Base: {len(base)}, seeded duplicates: {len(dups)}")

        # duplicate n was copied from base[DUPLICATE_INDEXES[n-1]]
        truth = {}
        for dup, idx in zip(dups, DUPLICATE_INDEXES):
            source = base[idx]
            assert (source.first_name, source.last_name) == (
                dup.first_name,
                dup.last_name,
            ), f"Ground truth mismatch for {dup.reference_number}"
            truth[frozenset((source.id, dup.id))] = dup.reference_number

        # Score every pair
        flagged = {}
        for a, b in combinations(records, 2):
            score, reasons = compare_duplicate(a, b)
            if score >= THRESHOLD:
                flagged[frozenset((a.id, b.id))] = (score, reasons)

        caught = set(truth) & set(flagged)
        missed = set(truth) - set(flagged)
        false_pos = set(flagged) - set(truth)

        print(f"\nSeeded duplicates caught: {len(caught)} / {len(truth)}")
        print(f"Missed: {len(missed)}")
        for pair in missed:
            print("  missed", truth[pair])
        print(f"False positives: {len(false_pos)}")
        for pair in list(false_pos)[:10]:
            score, reasons = flagged[pair]
            print("  ", sorted(pair), score, reasons)
    finally:
        db.close()


if __name__ == "__main__":
    main()