# Filing Cabinet — Product Requirements Document

## 1. Product Overview

Filing Cabinet is a records digitization and verification platform for organizations that still have important information spread across physical documents, scanned files, spreadsheets, and outdated internal records.

The idea came from my experience manually searching through physical client files, finding contact information, contacting people to verify whether their information was still current, and updating records when information changed.

Filing Cabinet is meant to make that process easier.

Instead of manually searching through files, staff can upload existing documents, convert the information into structured digital records, search those records, identify possible duplicates, and track when information needs to be verified or updated.

The platform is designed to be general enough for nonprofits, businesses, financial services, membership organizations, and other organizations maintaining large collections of client or customer records.


## 2. Core Problem

Organizations may have records that are:

- stored in physical or scanned documents
- difficult to search
- duplicated across different files
- incomplete
- outdated
- difficult to verify
- updated without a clear history of what changed

Filing Cabinet provides one system for digitizing, searching, verifying, and maintaining those records.


## 3. Primary Users

### Staff Member

A staff member can:

- create records
- upload source documents
- search existing records
- review information extracted from documents
- identify possible duplicate records
- send information for verification
- review submitted updates
- approve or reject record changes
- view previous versions of information


### Record Owner / Client

A record owner can:

- receive a verification request
- review the information currently stored about them
- confirm information that is still correct
- submit corrections or updated information

Submitted changes do not automatically replace existing records. They must first go through the verification workflow.


## 4. Core Record Information

A profile should support at least 10 structured fields.

Initial fields:

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

Fields should be validated where appropriate before being stored.


## 5. Core Features

### Record Management

Staff can create, view, edit, and search structured records.


### Document Upload

Staff can upload source documents such as PDFs or scanned images.

Each uploaded document remains associated with the record it came from.


### Information Extraction

The system extracts relevant information from uploaded documents and converts it into proposed structured fields.

Extracted information must be reviewed before it becomes part of an official record.


### Search

Staff can search records using information such as:

- name
- email
- phone number
- organization
- record/reference number


### Duplicate Detection

When a new record is created or extracted from a document, the system checks existing records for possible duplicates.

Potential matches may be based on fields such as:

- email
- phone number
- name
- address

Possible duplicates are flagged for staff review rather than automatically deleted or merged.


### Verification Workflow

Staff can request that stored information be verified.

The record owner can:

- confirm existing information
- propose updated information

Proposed changes remain pending until reviewed by staff.


### Staff Approval

Staff can review proposed changes and either:

- approve them
- reject them

Approved changes update the current record.


### Change History

The system preserves a history of important record changes.

For an update, staff should be able to determine:

- what field changed
- previous value
- new value
- when it changed
- whether the change was approved
- who approved it


### Source Tracking

Digital records remain connected to their original source documents.

The system should not destroy or silently replace the original source information when a record is updated.


## 6. Synthetic Dataset

Development and demonstrations will use synthetic data rather than real client information.

The system should eventually be tested with at least 1,000 synthetic records.

Synthetic records should include realistic variations such as:

- duplicate records
- incomplete records
- outdated contact information
- formatting differences
- similar names

This dataset will be used to test search, validation, duplicate detection, and record-management performance.


## 7. Finance Application

Filing Cabinet is a general records-management platform, but its verification workflow can model problems found in financial services.

Financial institutions maintain customer information that may need to be reviewed and updated over time.

The project will demonstrate a KYC-style record-maintenance workflow in which:

1. Existing customer information is stored.
2. Information is submitted for verification.
3. A customer can confirm or propose changes.
4. Changes remain pending.
5. Staff review the proposed changes.
6. Approved changes update the record.
7. Previous information and the approval history remain traceable.

This project is not intended to implement a production regulatory KYC system.


## 8. MVP

The first working version should allow a staff user to:

1. Create a structured record.
2. Save the record.
3. Retrieve the record.
4. Search existing records.
5. Upload a source document.
6. Associate that document with a record.
7. View the source document from the record profile.

Document extraction, duplicate detection, verification workflows, Redis processing, and advanced functionality will be added after the basic record system works.


## 9. Success Criteria

The completed project should demonstrate:

- a working records application
- searchable structured records
- 10+ validated record fields
- source-document linking
- document-to-record extraction
- duplicate detection
- testing with 1,000+ synthetic records
- client information verification
- staff approval workflows
- traceable record changes
- clear separation between permanent records and temporary/background processing


## 10. Out of Scope for the Initial Version

The initial project will not include:

- real client or customer information
- production regulatory compliance
- real banking integrations
- payment processing
- microservices
- blockchain
- unnecessary AI features
- automatic record changes without human review