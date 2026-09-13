# Filing Cabinet — Product Requirements Document

## 1. Product Overview

Filing Cabinet is a records digitization and verification platform inspired by organizations that still have important information spread across physical documents, digital files, spreadsheets, and outdated internal records.

The idea came from my experience manually searching through physical client files, finding contact information, contacting people to verify whether their information was still current, and updating records when information changed.

Filing Cabinet is meant to make that process easier.

Instead of manually searching through files, staff can turn existing documents into structured digital records, search those records, identify possible duplicates, and request verification when information needs to be confirmed or updated.

The workflow can apply to nonprofits, businesses, financial services, membership organizations, and other organizations maintaining collections of client or customer records.

## 2. Core Problem

Organizations may have records that are:

- difficult to search
- duplicated across different files
- incomplete or outdated
- difficult to verify
- updated without a clear history of what changed

Filing Cabinet provides one workflow for digitizing, searching, verifying, and maintaining those records.

## 3. Primary Users

### Staff Member

A staff member can:

- create records from reviewed document information
- upload source documents
- search existing records
- review extracted information
- review possible duplicate records
- create verification requests
- review submitted corrections
- approve or reject proposed changes
- view audit history

### Record Owner / Client

A record owner can:

- open a verification request
- review the information currently stored about them
- confirm that the information is correct
- submit corrections

Submitted corrections do not automatically replace official record information. They first enter the staff review workflow.

## 4. Core Record Information

A record supports 12 structured fields:

1. First name
2. Last name
3. Email
4. Phone number
5. Address
6. City
7. Province/state
8. Postal/ZIP code
9. Organization
10. Record/reference number
11. Record status
12. Last verified date

Fields are validated where appropriate before being stored.

## 5. Core Features

### Record Management

Staff can create, view, and search structured records.

### Document Upload

Staff can upload source documents and preserve the original file alongside the structured record.

### Information Extraction

Filing Cabinet extracts supported information from selectable-text PDFs and maps it into structured fields.

Staff review and can correct the extracted information before creating an official record.

### Search

Records can be searched using:

- name
- email
- phone number
- organization
- record/reference number

### Duplicate Detection

Before creating a record, the application checks existing records for possible duplicates.

Matching considers information such as:

- email
- phone number
- name
- address
- reference number

Potential duplicates are shown for staff review with the reasons for the match. The system does not automatically merge or delete records.

### Verification Workflow

Staff can create a verification request for an existing record.

The record owner can either confirm that the existing information is correct or submit corrections.

### Staff Review

Submitted corrections remain separate from the official record until reviewed.

Staff can:

- compare current and proposed information
- approve the proposed update
- reject the proposed update

Only approved changes modify the official record.

### Audit History

Important verification and update activity is recorded in an audit history.

This includes events such as:

- verification requests
- information confirmation
- correction submissions
- approved updates
- rejected updates

Approved updates preserve the previous and new values so changes remain traceable.

### Source Tracking

Digital records remain connected to their original source documents.

Updating structured information does not replace or destroy the original uploaded document.

## 6. Synthetic Dataset

Development and demonstrations use synthetic data rather than real client information.

The project includes **520 synthetic records**, consisting of 500 base records and 20 deliberate duplicate or near-duplicate cases.

The dataset provides realistic variations for testing:

- duplicate detection
- search
- record retrieval
- formatting differences
- similar identities

## 7. Finance Application

Filing Cabinet is a general records-management platform, but its verification workflow models a pattern found in financial services.

The project demonstrates a KYC-style record-maintenance workflow:

1. Existing customer information is stored.
2. A verification request is created.
3. The customer can confirm the information or submit corrections.
4. Corrections remain pending.
5. Staff review the proposed changes.
6. Approved changes update the official record.
7. Verification and update activity remains traceable.

Filing Cabinet is not a production regulatory KYC system and does not claim regulatory compliance.

## 8. Implemented Workflow

The completed application supports:

1. Uploading a source document.
2. Extracting supported information from PDFs.
3. Reviewing and correcting extracted fields.
4. Checking for possible duplicate records.
5. Creating a structured record.
6. Searching existing records.
7. Viewing record details and linked source documents.
8. Creating verification requests.
9. Confirming existing information.
10. Submitting corrections.
11. Reviewing proposed updates.
12. Approving or rejecting changes.
13. Recording important workflow activity in audit history.

## 9. Success Criteria

The project demonstrates:

- a working full-stack records application
- 12 structured record fields
- searchable PostgreSQL records
- source-document preservation and linking
- PDF-to-record extraction
- explainable duplicate detection
- 500+ synthetic records
- record-owner verification
- staff approval workflows
- traceable record changes
- automated backend testing

## 10. Current Scope

The current version intentionally does not include:

- real client or customer information
- production authentication or authorization
- production regulatory compliance
- banking integrations
- payment processing
- OCR for image-only scans
- automatic record merging
- automatic record changes without human review
- Redis or a background job queue