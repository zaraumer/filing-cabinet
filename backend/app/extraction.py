import re
from pathlib import Path

from pypdf import PdfReader


SUPPORTED_FIELDS = [
    "first_name",
    "last_name",
    "email",
    "phone",
    "address",
    "city",
    "province_state",
    "postal_zip",
    "organization",
    "reference_number",
    "record_status",
    "last_verified_date",
]

NEXT_LABEL = (
    r"(?:"
    r"Name|"
    r"First Name|"
    r"Last Name|"
    r"Email|"
    r"Phone|"
    r"Address|"
    r"City|"
    r"Province|"
    r"State|"
    r"Postal Code|"
    r"ZIP|"
    r"Zip Code|"
    r"Organization|"
    r"Reference Number|"
    r"Reference #|"
    r"Status|"
    r"Last Verified Date"
    r")"
)


def extract_pdf_text(file_path: Path) -> str:
    reader = PdfReader(str(file_path))
    pages = []

    for page in reader.pages:
        text = page.extract_text()

        if text:
            pages.append(text)

    return "\n".join(pages)


def normalize_text(text: str) -> str:
    # PDF layouts can split a value across several lines, so flatten the
    # whitespace before looking for field labels.
    return " ".join(text.split())


def extract_label_value(
    text: str,
    label_pattern: str,
) -> str | None:
    pattern = (
        rf"{label_pattern}\s*:\s*"
        rf"(.+?)"
        rf"(?=\s+{NEXT_LABEL}\s*:|$)"
    )

    match = re.search(
        pattern,
        text,
        flags=re.IGNORECASE,
    )

    if not match:
        return None

    value = match.group(1).strip()
    return value or None


def extract_record_fields(
    text: str,
) -> dict[str, str | None]:
    text = normalize_text(text)

    extracted: dict[str, str | None] = {
        field: None
        for field in SUPPORTED_FIELDS
    }

    extracted["first_name"] = extract_label_value(
        text,
        r"First Name",
    )
    extracted["last_name"] = extract_label_value(
        text,
        r"Last Name",
    )
    extracted["email"] = extract_label_value(
        text,
        r"Email",
    )
    extracted["phone"] = extract_label_value(
        text,
        r"Phone",
    )
    extracted["address"] = extract_label_value(
        text,
        r"Address",
    )
    extracted["city"] = extract_label_value(
        text,
        r"City",
    )
    extracted["province_state"] = extract_label_value(
        text,
        r"(?:Province|State)",
    )
    extracted["postal_zip"] = extract_label_value(
        text,
        r"(?:Postal Code|ZIP|Zip Code)",
    )
    extracted["organization"] = extract_label_value(
        text,
        r"Organization",
    )
    extracted["reference_number"] = extract_label_value(
        text,
        r"(?:Reference Number|Reference #)",
    )
    extracted["record_status"] = extract_label_value(
        text,
        r"Status",
    )
    extracted["last_verified_date"] = extract_label_value(
        text,
        r"Last Verified Date",
    )

    # Adjust since some forms have one Name field instead of separate first/last fields.
    if not extracted["first_name"] and not extracted["last_name"]:
        full_name = extract_label_value(
            text,
            r"Name",
        )

        if full_name:
            parts = full_name.split()

            if len(parts) >= 2:
                extracted["first_name"] = parts[0]
                extracted["last_name"] = " ".join(parts[1:])
            elif len(parts) == 1:
                extracted["first_name"] = parts[0]

    return extracted