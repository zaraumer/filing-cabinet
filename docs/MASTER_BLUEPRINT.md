# Filing Cabinet — Master Blueprint

## 1. Architecture

Filing Cabinet uses a simple full-stack architecture:

Frontend:
Next.js + TypeScript

Backend:
FastAPI + Python

Primary Database:
PostgreSQL

Background / Temporary Processing:
Redis

The application should remain a single frontend and single backend unless there is a demonstrated reason to change the architecture.


## 2. System Flow

Basic application flow:

User
↓
Next.js frontend
↓
FastAPI REST API
↓
PostgreSQL


Document workflow:

Source document
↓
Upload through Next.js
↓
FastAPI receives and validates file
↓
Document processing
↓
Extracted fields
↓
Staff review
↓
Validated record
↓
PostgreSQL


Verification workflow:

Existing record
↓
Verification request
↓
Client reviews information
↓
Client confirms or proposes changes
↓
Pending update
↓
Staff review
↓
Approve or reject
↓
PostgreSQL record updated if approved
↓
Change recorded in audit history


## 3. Frontend

Technology:

Next.js + TypeScript

Responsibilities:

- user interface
- record creation forms
- record search
- record profile pages
- document upload interface
- extracted-field review
- duplicate warnings
- verification forms
- approval interface
- change-history display

The frontend should communicate with the backend through REST API requests.

Business rules that protect data integrity should not exist only in the frontend.


## 4. Backend

Technology:

FastAPI + Python

Responsibilities:

- REST API endpoints
- request validation
- record-management logic
- document processing
- duplicate detection
- verification workflow logic
- approval logic
- database access
- audit-history creation
- background-job coordination

The backend is responsible for enforcing important business rules even if a frontend validation check is bypassed.


## 5. PostgreSQL

PostgreSQL stores permanent application data.

Expected entities include:

### Record

Stores the current structured information for a person or organization.

### Source Document

Stores information about an uploaded document and associates it with a record.

### Proposed Update

Stores information submitted during verification before it is approved.

### Verification Request

Tracks verification status.

### Audit Event

Stores traceable information about important record changes.

The exact database schema will be designed incrementally as features are implemented.


## 6. Redis

Redis should not be used as the primary database.

PostgreSQL remains the source of truth for permanent records.

Redis will be introduced only when the application has a real need for temporary or background processing.

Potential uses include:

- document-processing jobs
- verification jobs
- temporary workflow state
- retryable background tasks

Redis should not be added until the core PostgreSQL application works.


## 7. Document Processing

Uploaded files may include:

- PDF
- PNG
- JPG/JPEG

The system should:

1. validate the uploaded file
2. preserve the source document
3. extract relevant information
4. convert extracted information into proposed structured fields
5. validate field formats
6. show the extracted information to staff
7. require review before saving it as an official record

The extraction implementation should be selected based on actual project requirements rather than adding AI unnecessarily.


## 8. Duplicate Detection

Duplicate detection should begin with explainable matching rules.

Potential signals include:

- exact normalized email match
- exact normalized phone match
- similar name
- matching address
- matching reference number

The system should produce a possible-match result for staff review.

It should not automatically delete or merge records.


## 9. Data Integrity

Important principles:

- source documents are preserved
- submitted changes do not immediately overwrite records
- approved updates are traceable
- rejected updates do not modify official records
- important backend operations are validated
- permanent data belongs in PostgreSQL
- temporary processing should not become the permanent source of truth


## 10. Testing

Testing should eventually cover:

- API endpoints
- field validation
- record creation
- record retrieval
- search
- duplicate detection
- proposed updates
- approvals
- rejected updates
- audit-history creation
- invalid document uploads

Features should not be considered complete only because the interface appears to work.


## 11. Development Principles

Prefer:

- simple architecture
- clear naming
- small modules
- explicit business logic
- testable functions
- documented decisions

Avoid unnecessary:

- microservices
- Kubernetes
- Kafka
- vector databases
- blockchain
- LLM dependencies
- abstractions with no current use
- libraries added only to make the technology stack look larger


## 12. Technology Decisions

### Why Next.js + TypeScript?

Provides a modern typed frontend suitable for building interactive forms, dashboards, search interfaces, and record-management workflows.

### Why FastAPI + Python?

Provides a typed API layer while supporting Python-based document processing, validation, data processing, and matching logic.

### Why PostgreSQL?

The application contains strongly related structured data such as records, documents, proposed updates, approvals, and audit events. A relational database is appropriate for preserving those relationships and maintaining data integrity.

### Why Redis?

Redis will support temporary/background processing where appropriate. It is not a replacement for PostgreSQL.