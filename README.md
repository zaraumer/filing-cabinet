# Filing Cabinet

A records management platform that turns physical and scanned files into searchable digital records and makes it easier to keep that information accurate and up to date.

## Why I Started This

The idea for Filing Cabinet came from one of my summer jobs.

I was helping update volunteer information, but a lot of the information I needed was stored in physical files. I would go through folders to find someone's contact information, call or email them to check if it was still correct, keep track of whether they responded, and then update their record.

It was a lot of manual work for what sounded like a simple task.

What stood out to me was that simply scanning all of the files wouldn't actually solve the problem. The useful information would still need to be found, organized, checked for missing or outdated details, and updated when someone responded.

That's where Filing Cabinet came from.

## What It Does

Filing Cabinet takes scanned documents and existing digital files and turns the information inside them into structured, searchable records.

Staff can compare extracted information with the original document before accepting it. Once a record exists, the system can identify missing or outdated information and flag possible duplicate profiles.

When information needs to be updated, a verification request can be sent directly to the person connected to the record. They can confirm existing information or submit changes without staff having to collect every update through individual calls and emails.

Submitted changes go through a review process before becoming part of the official record. Previous values are kept so there is a clear history of what changed, when it changed, and where the information came from.

## How It Works

```text
Physical / Scanned File
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
      Digital Record
          |
          v
 Missing / Outdated?
          |
          v
 Request Information
          |
          v
    Review Changes
          |
          v
     Updated Record
```

## Core Features

* Document and PDF upload
* Information extraction from existing records
* Human review of extracted fields
* Structured and searchable profiles
* Source tracking for individual fields
* Missing and outdated information detection
* Duplicate record detection
* Secure information verification requests
* Staff review and approval of submitted changes
* Record version history and audit logging
* Role-based access
* Search and filtering

## Use Cases

Filing Cabinet isn't tied to one type of organization. The same record workflow can be adapted to different industries.

**Financial services** — client information, account documents, identification records, and profile verification

**Nonprofits** — volunteer profiles, certifications, contact information, and availability

**Workplaces** — employee records, certifications, contracts, and administrative forms

**Education** — student information, enrollment documents, and administrative records

The information changes between industries, but the basic problem stays the same: important records need to be easy to find, verify, update, and trace.

## Tech Stack

|                          | Technology                               |
| ------------------------ | ---------------------------------------- |
| Frontend                 | Next.js, React, TypeScript, Tailwind CSS |
| Backend                  | Python, FastAPI                          |
| Database                 | PostgreSQL                               |
| Background Processing    | Redis, Celery                            |
| Testing                  | Pytest, Playwright                       |
| Development & Deployment | Docker, Git, GitHub                      |
