# Filing Cabinet

A records platform for turning document-based information into searchable digital records and keeping it up to date.

## Why I Built It

Filing Cabinet came from one of my summer jobs, where I spent a lot of time digging through physical files to find contact information, reaching out to people to see if it was still correct, and then updating their records.

At some point I thought: there has to be a less painful way to do this.

Scanning everything wasn't really the answer either. A folder full of PDFs is still a folder full of PDFs. The useful information needs to be searchable, checked, and easy to update... So I built Filing Cabinet.

## What It Does

Staff can upload a PDF and turn supported information into a structured record. Before anything is saved, the extracted fields can be reviewed and corrected.

Filing Cabinet also checks for possible duplicates using details like names, emails, phone numbers, addresses, and reference numbers. It flags possible matches instead of making the decision automatically.

Once records are created, staff can search them, view their original source documents, and send verification requests when information might be outdated. If someone submits a correction, it stays pending until a staff member approves or rejects it.

Basically:

```text
Document → Extract → Review → Duplicate Check → Record
                                                ↓
                                  Verification Request
                                                ↓
                                   Confirm or Correct
                                                ↓
                                      Staff Review
                                                ↓
                                        Audit History
```

## Features

- PDF information extraction with human review
- Searchable PostgreSQL records
- Explainable duplicate detection
- Original source-document tracking
- Record verification and correction requests
- Staff approval/rejection workflow
- Audit history for record changes
- 520 synthetic records, including deliberate duplicate cases
- Automated backend tests

## Tech Stack

| | |
| --- | --- |
| Frontend | Next.js, React, TypeScript, Tailwind CSS |
| Backend | Python, FastAPI |
| Database | PostgreSQL, SQLAlchemy, Alembic |
| Document Processing | pypdf |
| Testing | Pytest |

## Running Locally

### Backend

Create a PostgreSQL database and add a `.env` file inside `backend`:

```text
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/filing_cabinet
```

Then:

```bash
cd backend
python -m venv .venv
pip install -r requirements.txt
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

### Frontend

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

### Demo Data

To populate the database with synthetic records:

```bash
cd backend
python scripts/seed_records.py
```
