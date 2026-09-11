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

export function formatRecordName(record: RecordItem): string {
  return `${record.first_name} ${record.last_name}`.trim();
}
