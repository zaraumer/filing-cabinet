export const API_BASE_URL = "http://127.0.0.1:8000";

export type RecordItem = {
  id: number;
  first_name: string;
  last_name: string;
  email: string | null;
  phone: string | null;
  address: string | null;
  city: string | null;
  province_state: string | null;
  postal_zip: string | null;
  organization: string | null;
  reference_number: string | null;
  record_status: string;
  last_verified_date: string | null;
};

export type SourceDocument = {
  id: number;
  record_id: number;
  original_filename: string;
  content_type: string;
  file_size: number;
  uploaded_at: string;
};

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function readErrorDetail(
  response: Response
): Promise<string> {
  try {
    const body = (await response.json()) as {
      detail?: unknown;
    };

    if (typeof body.detail === "string") {
      return body.detail;
    }
  } catch {
    // Use the generic status message below.
  }

  return `Request failed with status ${response.status}`;
}

async function requestJson<T>(
  path: string,
  init?: RequestInit
): Promise<T> {
  const response = await fetch(
    new URL(path, API_BASE_URL),
    {
      cache: "no-store",
      ...init,
    }
  );

  if (!response.ok) {
    throw new ApiError(
      await readErrorDetail(response),
      response.status
    );
  }

  return (await response.json()) as T;
}

export async function fetchRecords(
  search: string,
  signal?: AbortSignal
): Promise<RecordItem[]> {
  const url = new URL("/records", API_BASE_URL);

  if (search.trim()) {
    url.searchParams.set(
      "search",
      search.trim()
    );
  }

  const response = await fetch(url, {
    signal,
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(
      `Request failed with status ${response.status}`
    );
  }

  return (await response.json()) as RecordItem[];
}

export function fetchRecord(
  recordId: number,
  signal?: AbortSignal
): Promise<RecordItem> {
  return requestJson<RecordItem>(
    `/records/${recordId}`,
    { signal }
  );
}

export function fetchRecordDocuments(
  recordId: number,
  signal?: AbortSignal
): Promise<SourceDocument[]> {
  return requestJson<SourceDocument[]>(
    `/records/${recordId}/documents`,
    { signal }
  );
}

export function uploadRecordDocument(
  recordId: number,
  file: File
): Promise<SourceDocument> {
  const formData = new FormData();
  formData.append("file", file);

  return requestJson<SourceDocument>(
    `/records/${recordId}/documents`,
    {
      method: "POST",
      body: formData,
    }
  );
}

export function recordDocumentUrl(
  recordId: number,
  documentId: number
): string {
  return `${API_BASE_URL}/records/${recordId}/documents/${documentId}`;
}

export function formatRecordName(
  record: RecordItem
): string {
  return `${record.first_name} ${record.last_name}`.trim();
}

export type RecordFormData = {
  first_name: string;
  last_name: string;
  email: string | null;
  phone: string | null;
  address: string | null;
  city: string | null;
  province_state: string | null;
  postal_zip: string | null;
  organization: string | null;
  reference_number: string | null;
  record_status: string;
  last_verified_date: string | null;
};

export type IntakeDocument = {
  id: number;
  original_filename: string;
  content_type: string;
  file_size: number;
  uploaded_at: string;
  extraction_status: string;
  extracted_fields: RecordFormData | null;
  created_record_id: number | null;
};

export type DuplicateMatch = {
  record: RecordItem;
  score: number;
  reasons: string[];
};

export type DuplicateCheckResponse = {
  matches: DuplicateMatch[];
};

export async function uploadIntakeDocument(
  file: File
): Promise<IntakeDocument> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(
    `${API_BASE_URL}/intake/documents`,
    {
      method: "POST",
      body: formData,
    }
  );

  if (!response.ok) {
    throw new Error(
      "Could not upload document."
    );
  }

  return response.json();
}

export async function checkIntakeDuplicates(
  intakeId: number,
  record: RecordFormData
): Promise<DuplicateCheckResponse> {
  const response = await fetch(
    `${API_BASE_URL}/intake/documents/${intakeId}/duplicates`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(record),
    }
  );

  if (!response.ok) {
    throw new Error(
      "Could not check for duplicate records."
    );
  }

  return response.json();
}

export async function createRecordFromIntake(
  intakeId: number,
  record: RecordFormData,
  duplicateReviewed: boolean
): Promise<RecordItem> {
  const response = await fetch(
    `${API_BASE_URL}/intake/documents/${intakeId}/create-record`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        ...record,
        duplicate_reviewed: duplicateReviewed,
      }),
    }
  );

  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => null);

    throw new Error(
      error?.detail ||
        "Could not create record."
    );
  }

  return response.json();
}

export type VerificationRequest = {
  id: number;
  record_id: number;
  recipient_email: string;
  token: string;
  status: string;
  created_at: string;
  expires_at: string;
  completed_at: string | null;
};

export type VerificationView = {
  verification_request: VerificationRequest;
  record: RecordItem;
};

export type ProposedRecordFields = {
  first_name?: string;
  last_name?: string;
  email?: string | null;
  phone?: string | null;
  address?: string | null;
  city?: string | null;
  province_state?: string | null;
  postal_zip?: string | null;
  organization?: string | null;
};

export type ProposedUpdate = {
  id: number;
  record_id: number;
  verification_request_id: number;
  proposed_fields: ProposedRecordFields;
  status: string;
  submitted_at: string;
  reviewed_at: string | null;
  review_note: string | null;
};

export type AuditEvent = {
  id: number;
  record_id: number;
  verification_request_id: number | null;
  proposed_update_id: number | null;
  event_type: string;
  actor_type: string;
  details: Record<string, unknown> | null;
  created_at: string;
};

export async function createVerificationRequest(
  recordId: number,
  recipientEmail?: string,
  expiresInDays = 7
): Promise<VerificationRequest> {
  return requestJson<VerificationRequest>(
    `/records/${recordId}/verification-requests`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        recipient_email:
          recipientEmail || null,
        expires_in_days: expiresInDays,
      }),
    }
  );
}

export async function fetchVerification(
  token: string
): Promise<VerificationView> {
  const response = await fetch(
    `${API_BASE_URL}/verification/${encodeURIComponent(token)}`
  );

  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => null);

    throw new Error(
      error?.detail ||
        "Could not load verification request."
    );
  }

  return response.json();
}

export async function submitProposedUpdate(
  token: string,
  proposedFields: ProposedRecordFields
): Promise<ProposedUpdate> {
  const response = await fetch(
    `${API_BASE_URL}/verification/${encodeURIComponent(token)}/proposed-updates`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        proposed_fields: proposedFields,
      }),
    }
  );

  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => null);

    throw new Error(
      error?.detail ||
        "Could not submit your changes."
    );
  }

  return response.json();
}

export async function fetchProposedUpdates(
  status?: string
): Promise<ProposedUpdate[]> {
  const url = new URL(
    "/proposed-updates",
    API_BASE_URL
  );

  if (status) {
    url.searchParams.set("status", status);
  }

  const response = await fetch(url, {
    cache: "no-store",
  });

  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => null);

    throw new Error(
      error?.detail ||
        "Could not load proposed updates."
    );
  }

  return response.json();
}

export async function approveProposedUpdate(
  proposedUpdateId: number,
  reviewNote?: string
): Promise<ProposedUpdate> {
  return requestJson<ProposedUpdate>(
    `/proposed-updates/${proposedUpdateId}/approve`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        review_note:
          reviewNote?.trim() || null,
      }),
    }
  );
}

export async function rejectProposedUpdate(
  proposedUpdateId: number,
  reviewNote?: string
): Promise<ProposedUpdate> {
  return requestJson<ProposedUpdate>(
    `/proposed-updates/${proposedUpdateId}/reject`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        review_note:
          reviewNote?.trim() || null,
      }),
    }
  );
}

export async function fetchAuditEvents(
  recordId: number,
  signal?: AbortSignal
): Promise<AuditEvent[]> {
  return requestJson<AuditEvent[]>(
    `/records/${recordId}/audit-events`,
    { signal }
  );
}