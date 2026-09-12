export const API_BASE_URL = "http://127.0.0.1:8000";

/**
 * Mirrors RecordResponse in backend/app/schemas.py.
 * Named RecordItem so it does not collide with the built-in TypeScript
 * `Record` utility type.
 */
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

/** Mirrors SourceDocumentResponse in backend/app/schemas.py. */
export type SourceDocument = {
  id: number;
  record_id: number;
  original_filename: string;
  content_type: string;
  file_size: number;
  uploaded_at: string;
};

/** Carries the HTTP status so callers can tell "not found" from "API down". */
export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

/** FastAPI reports problems as {"detail": "..."}, so use that when present. */
async function readErrorDetail(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as { detail?: unknown };

    if (typeof body.detail === "string") {
      return body.detail;
    }
  } catch {
    // Body was not JSON; fall through to the generic message.
  }

  return `Request failed with status ${response.status}`;
}

async function requestJson<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const response = await fetch(new URL(path, API_BASE_URL), {
    cache: "no-store",
    ...init,
  });

  if (!response.ok) {
    throw new ApiError(await readErrorDetail(response), response.status);
  }

  return (await response.json()) as T;
}

/**
 * Fetches records from the backend, optionally filtered by a search term.
 * The signal lets the caller cancel a request that is no longer needed.
 */
export async function fetchRecords(
  search: string,
  signal?: AbortSignal,
): Promise<RecordItem[]> {
  const url = new URL("/records", API_BASE_URL);

  if (search.trim()) {
    url.searchParams.set("search", search.trim());
  }

  const response = await fetch(url, { signal, cache: "no-store" });

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  return (await response.json()) as RecordItem[];
}

export function fetchRecord(
  recordId: number,
  signal?: AbortSignal,
): Promise<RecordItem> {
  return requestJson<RecordItem>(`/records/${recordId}`, { signal });
}

export function fetchRecordDocuments(
  recordId: number,
  signal?: AbortSignal,
): Promise<SourceDocument[]> {
  return requestJson<SourceDocument[]>(`/records/${recordId}/documents`, {
    signal,
  });
}

export function uploadRecordDocument(
  recordId: number,
  file: File,
): Promise<SourceDocument> {
  const formData = new FormData();
  formData.append("file", file);

  return requestJson<SourceDocument>(`/records/${recordId}/documents`, {
    method: "POST",
    body: formData,
  });
}

/** Documents are always reached through the record that owns them. */
export function recordDocumentUrl(
  recordId: number,
  documentId: number,
): string {
  return `${API_BASE_URL}/records/${recordId}/documents/${documentId}`;
}

export function formatRecordName(record: RecordItem): string {
  return `${record.first_name} ${record.last_name}`.trim();
}
