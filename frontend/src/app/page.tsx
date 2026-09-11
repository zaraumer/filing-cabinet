"use client";

import { useEffect, useState } from "react";

import RecordsTable from "@/components/RecordsTable";
import { fetchRecords, type RecordItem } from "@/lib/records";

const SEARCH_DEBOUNCE_MS = 300;

/** Small inline magnifier so the search field reads as a search field. */
function SearchIcon() {
  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 16 16"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      className="h-4 w-4"
    >
      <circle cx="7" cy="7" r="4.5" />
      <path d="M10.5 10.5 14 14" />
    </svg>
  );
}

export default function RecordsPage() {
  const [search, setSearch] = useState("");
  const [records, setRecords] = useState<RecordItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  // Incremented by the retry button so the effect below runs again.
  const [reloadCount, setReloadCount] = useState(0);

  useEffect(() => {
    const controller = new AbortController();

    // Wait a moment before querying so typing does not fire a request per key.
    const timer = setTimeout(async () => {
      setIsLoading(true);

      try {
        const results = await fetchRecords(search, controller.signal);

        setRecords(results);
        setError(null);
      } catch (caughtError) {
        if (controller.signal.aborted) {
          return;
        }

        setRecords([]);
        setError(
          caughtError instanceof Error
            ? caughtError.message
            : "Unknown error",
        );
      } finally {
        if (!controller.signal.aborted) {
          setIsLoading(false);
        }
      }
    }, SEARCH_DEBOUNCE_MS);

    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [search, reloadCount]);

  const recordCountLabel = isLoading
    ? "Loading records…"
    : `${records.length} ${records.length === 1 ? "record" : "records"}`;

  return (
    <main className="mx-auto w-full max-w-5xl px-6 py-10">
      <div className="max-w-2xl">
        <h1 className="font-serif text-4xl leading-tight tracking-tight text-ink">
          Records
        </h1>
        <p className="mt-2 text-sm text-muted">
          Search and review digitized records.
        </p>
      </div>

      <div className="mt-8 w-full sm:max-w-2xl">
        <label
          htmlFor="record-search"
          className="block text-xs font-medium uppercase tracking-wide text-muted"
        >
          Search records
        </label>

        <div className="relative mt-2">
          <span className="pointer-events-none absolute inset-y-0 left-3 flex items-center text-muted">
            <SearchIcon />
          </span>
          <input
            id="record-search"
            type="search"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Name, email, phone, organization, reference number"
            className="w-full rounded-md border border-line bg-surface py-2.5 pl-9 pr-3 text-sm text-ink placeholder:text-muted focus:border-accent focus:outline-none focus-visible:ring-2 focus-visible:ring-accent/30"
          />
        </div>
      </div>

      <section className="mt-8">
        <div className="mb-3 flex flex-wrap items-baseline gap-x-3 gap-y-1">
          <h2 className="text-sm font-medium text-ink">All records</h2>
          {/* Hidden on failure, where a count of zero would be misleading. */}
          {error ? null : (
            <span className="text-sm text-muted">{recordCountLabel}</span>
          )}
        </div>

        {error ? (
          <div className="rounded-md border border-line bg-surface p-6">
            <h3 className="text-sm font-semibold text-ink">
              Could not load records
            </h3>
            <p className="mt-1.5 max-w-prose text-sm text-muted">
              The request to the backend failed ({error}). Confirm the API is
              running and try again.
            </p>
            <button
              type="button"
              onClick={() => setReloadCount((count) => count + 1)}
              className="mt-4 rounded-md border border-accent px-3.5 py-2 text-sm font-medium text-accent transition-colors hover:bg-accent-soft focus:outline-none focus-visible:ring-2 focus-visible:ring-accent/40"
            >
              Retry
            </button>
          </div>
        ) : records.length === 0 && !isLoading ? (
          <div className="rounded-md border border-line bg-surface p-8 text-sm text-muted">
            {search.trim()
              ? `No records match “${search.trim()}”.`
              : "No records have been added yet."}
          </div>
        ) : (
          <RecordsTable records={records} />
        )}
      </section>
    </main>
  );
}
