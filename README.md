# Filing Cabinet

A records management platform that turns document-based information into searchable digital records and makes it easier to keep that information accurate and up to date.

## Why I Started This

The idea for Filing Cabinet came from one of my summer jobs.

I was helping update volunteer information, but a lot of the information I needed was stored in physical files. I would go through folders to find someone's contact information, call or email them to check if it was still correct, keep track of whether they responded, and then update their record.

It was a lot of manual work for what sounded like a simple task.

What stood out to me was that simply scanning all of the files wouldn't actually solve the problem. The useful information would still need to be found, organized, checked for missing or outdated details, and updated when someone responded.

That's where Filing Cabinet came from.

## What It Does

Filing Cabinet takes existing digital documents and turns the information inside them into structured, searchable records.

Staff can upload a PDF, extract supported information from it, and compare the extracted fields with the original document before creating a record. The information can be corrected during this review so that the document isn't treated as automatically correct.

Before a new record is created, Filing Cabinet also checks for possible duplicates using information such as names, emails, phone numbers, addresses, and reference numbers. Potential matches are shown for staff review rather than automatically merging or deleting records.

Once a record exists, it can be searched using details like a name, email, phone number, organization, or reference number. The original source document also stays connected to the record it came from.

When information needs to be updated, staff can create a verification request for the person connected to the record. They can review their existing information and submit corrections through a verification link instead of staff having to collect every update through individual calls and emails.

Submitted changes don't immediately overwrite the official record. They go into a review queue where staff can compare the current and proposed information before approving or rejecting the update.

Approved changes are applied to the record and added to an audit history so there is a clear trail of what changed and when.

## How It Works

```text
      Digital Document
             |
             v
       Upload Document
             |
             v
     Extract Information
             |
             v
        Staff Review
             |
             v
       Duplicate Check
             |
             v
        Digital Record
             |
             v
    Verification Request
             |
             v
     Proposed Changes
             |
             v
        Staff Review
          /       \
         v         v
      Approve    Reject
         |
         v
    Updated Record
         |
         v
      Audit History
```

## Core Features

- PDF document upload and structured field extraction
- Human review of extracted information before record creation
- Structured PostgreSQL records with searchable client information
- Search by name, email, phone number, organization, and reference number
- Original source documents linked to their records
- Explainable duplicate detection with staff review
- 500+ synthetic records with deliberate duplicate and near-duplicate cases
- Record verification links for proposed information updates
- Staff review and approval or rejection of submitted changes
- Audit history for verification activity and approved record changes
- Database migrations for evolving the PostgreSQL schema
- Automated backend testing for record, document, duplicate, and verification workflows

## Use Cases

Filing Cabinet isn't tied to one type of organization. The same record workflow can be adapted to different industries.

**Financial services** — client information, account documents, identification records, and profile verification

**Nonprofits** — volunteer profiles, certifications, contact information, and availability

**Workplaces** — employee records, certifications, contracts, and administrative forms

**Education** — student information, enrollment documents, and administrative records

The information changes between industries, but the basic problem stays the same: important records need to be easy to find, verify, update, and trace.

## Tech Stack

| **Area** | **Technology** |
| --- | --- |
| Frontend | Next.js, React, TypeScript, Tailwind CSS |
| Backend | Python, FastAPI |
| Database | PostgreSQL, SQLAlchemy |
| Database Migrations | Alembic |
| Document Processing | pypdf |
| Testing | Pytest |
| Development | Git, GitHub |
