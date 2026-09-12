"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import RecordDocuments from "@/components/RecordDocuments";
import StatusBadge from "@/components/StatusBadge";
import {
  ApiError,
  fetchRecord,
  formatRecordName,
  type RecordItem,
} from "@/lib/records";

type RecordDetailProps = {
  /** Straight from the URL, so it still has to be checked. */
  recordId: string;
};

const MONTH_NAMES = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December",
];

/**
 * last_verified_date arrives as YYYY-MM-DD. It is formatted from the string
 * parts rather than through Date so a timezone never shifts the day.
 */
function formatDate(value: string): string {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value);

  if (!match) {
    return value;
  }

  const [, year, month, day] = match;
  const monthName = MONTH_NAMES[Number(month) - 1];

  if (!monthName) {
    return value;
  }

  return `${monthName} ${Number(day)}, ${year}`;
}

function BackToRecordsLink() {
  return (
    <Link
      href="/"
      className="inline-flex items-center gap-1.5 rounded-sm text-sm text-muted transition-colors hover:text-accent focus:outline-none focus-visible:ring-2 focus-visible:ring-accent/40"
    >
      <span aria-hidden="true">←</span>
      Back to Records
    </Link>
  );
}

/** One label/value pair. Missing values show a dash rather than a blank gap. */
function DetailField({
  label,
  value,
  isMonospace = false,
}: {
  label: string;
  value: string | null;
  isMonospace?: boolean;
}) {
  return (
    <div>
      <dt className="text-xs font-medium uppercase tracking-wide text-muted">
        {label}
      </dt>
      <dd
        className={`mt-1 text-sm ${
          value ? "text-ink" : "text-line"
        } ${isMonospace && value ? "font-mono text-[0.8125rem]" : ""}`}
      >
        {value ? value : "—"}
      </dd>
    </div>
  );
}

function DetailSection({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section className="rounded-md border border-line bg-surface p-6">
      <h2 className="text-sm font-medium text-ink">{title}</h2>
      <dl className="mt-5 grid gap-x-8 gap-y-5 sm:grid-cols-2">{children}</dl>
    </section>
  );
}

/** Shared frame so every state keeps the page layout and the way back. */
function DetailMessage({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-md border border-line bg-surface p-6">
      <h1 className="text-sm font-semibold text-ink">{title}</h1>
      <div className="mt-1.5 max-w-prose text-sm text-muted">{children}</div>
    </div>
  );
}

export default function RecordDetail({ recordId }: RecordDetailProps) {
  const [record, setRecord] = useState<RecordItem | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isNotFound, setIsNotFound] = useState(false);
  // Incremented by the retry button so the effect below runs again.
  const [reloadCount, setReloadCount] = useState(0);

  // A URL such as /records/abc is treated as not found without a request.
  const numericRecordId = /^\d+$/.test(recordId) ? Number(recordId) : null;

  useEffect(() => {
    if (numericRecordId === null) {
      return;
    }

    const controller = new AbortController();

    async function loadRecord(id: number) {
      setIsLoading(true);

      try {
        const result = await fetchRecord(id, controller.signal);

        setRecord(result);
        setError(null);
        setIsNotFound(false);
      } catch (caughtError) {
        if (controller.signal.aborted) {
          return;
        }

        setRecord(null);

        if (caughtError instanceof ApiError && caughtError.status === 404) {
          setIsNotFound(true);
          setError(null);
        } else {
          setIsNotFound(false);
          setError(
            caughtError instanceof Error ? caughtError.message : "Unknown error",
          );
        }
      } finally {
        if (!controller.signal.aborted) {
          setIsLoading(false);
        }
      }
    }

    loadRecord(numericRecordId);

    return () => {
      controller.abort();
    };
  }, [numericRecordId, reloadCount]);

  return (
    <main className="mx-auto w-full max-w-5xl px-6 py-10">
      <BackToRecordsLink />

      <div className="mt-6">
        {numericRecordId === null || isNotFound ? (
          <DetailMessage title="Record not found">
            <p>
              No record exists for this address. It may have been removed, or
              the link may be incorrect.
            </p>
          </DetailMessage>
        ) : isLoading ? (
          <DetailMessage title="Loading record…">
            <p>Fetching this record from the backend.</p>
          </DetailMessage>
        ) : error ? (
          <DetailMessage title="Could not load record">
            <p>
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
          </DetailMessage>
        ) : record ? (
          <>
            <div className="flex flex-wrap items-center gap-x-4 gap-y-2">
              <h1 className="font-serif text-4xl leading-tight tracking-tight text-ink">
                {formatRecordName(record)}
              </h1>
              <StatusBadge status={record.record_status} />
            </div>

            <p className="mt-2 text-sm text-muted">
              {record.organization
                ? record.organization
                : "No organization on file"}
            </p>

            <div className="mt-8 grid gap-5">
              <DetailSection title="Contact Information">
                <DetailField label="Email" value={record.email} />
                <DetailField label="Phone" value={record.phone} />
                <DetailField label="Address" value={record.address} />
                <DetailField label="City" value={record.city} />
                <DetailField
                  label="Province/State"
                  value={record.province_state}
                />
                <DetailField label="Postal/ZIP" value={record.postal_zip} />
              </DetailSection>

              <DetailSection title="Record Information">
                <DetailField
                  label="Organization"
                  value={record.organization}
                />
                <DetailField
                  label="Reference Number"
                  value={record.reference_number}
                  isMonospace
                />
                <DetailField
                  label="Record Status"
                  value={record.record_status}
                />
                <DetailField
                  label="Last Verified Date"
                  value={
                    record.last_verified_date
                      ? formatDate(record.last_verified_date)
                      : null
                  }
                />
              </DetailSection>

              <RecordDocuments recordId={record.id} />
            </div>
          </>
        ) : null}
      </div>
    </main>
  );
}
