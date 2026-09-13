"use client";

import Link from "next/link";
import { useEffect, useState, type ReactNode } from "react";

import RecordDocuments from "@/components/RecordDocuments";
import StatusBadge from "@/components/StatusBadge";

import {
  ApiError,
  createVerificationRequest,
  fetchAuditEvents,
  fetchRecord,
  formatRecordName,
  type AuditEvent,
  type RecordItem,
} from "@/lib/records";

type RecordDetailProps = {
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

const AUDIT_EVENT_LABELS: Record<string, string> = {
  verification_requested: "Verification requested",
  proposed_update_submitted: "Corrections submitted",
  proposed_update_approved: "Corrections approved",
  proposed_update_rejected: "Corrections rejected",
  record_updated: "Record updated",
  verification_confirmed: "Record verified",
};

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

function formatDateTime(value: string): string {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
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
        } ${
          isMonospace && value
            ? "font-mono text-[0.8125rem]"
            : ""
        }`}
      >
        {value || "—"}
      </dd>
    </div>
  );
}

function DetailSection({
  title,
  children,
}: {
  title: string;
  children: ReactNode;
}) {
  return (
    <section className="rounded-md border border-line bg-surface p-6">
      <h2 className="text-sm font-medium text-ink">
        {title}
      </h2>

      <dl className="mt-5 grid gap-x-8 gap-y-5 sm:grid-cols-2">
        {children}
      </dl>
    </section>
  );
}

function DetailMessage({
  title,
  children,
}: {
  title: string;
  children: ReactNode;
}) {
  return (
    <div className="rounded-md border border-line bg-surface p-6">
      <h1 className="text-sm font-semibold text-ink">
        {title}
      </h1>

      <div className="mt-1.5 max-w-prose text-sm text-muted">
        {children}
      </div>
    </div>
  );
}

function AuditHistory({
  events,
  isLoading,
  error,
}: {
  events: AuditEvent[];
  isLoading: boolean;
  error: string | null;
}) {
  return (
    <section className="rounded-md border border-line bg-surface">
      <div className="border-b border-line px-6 py-5">
        <h2 className="text-sm font-medium text-ink">
          Audit History
        </h2>

        <p className="mt-1 text-sm text-muted">
          Verification and record changes are recorded here.
        </p>
      </div>

      <div className="px-6 py-5">
        {isLoading ? (
          <p className="text-sm text-muted">
            Loading history…
          </p>
        ) : error ? (
          <p className="text-sm text-red-700">
            {error}
          </p>
        ) : events.length === 0 ? (
          <p className="text-sm text-muted">
            No activity has been recorded yet.
          </p>
        ) : (
          <div className="divide-y divide-line">
            {events.map((event) => (
              <div
                key={event.id}
                className="flex flex-col gap-1 py-4 first:pt-0 last:pb-0 sm:flex-row sm:items-start sm:justify-between sm:gap-6"
              >
                <div>
                  <p className="text-sm font-medium text-ink">
                    {AUDIT_EVENT_LABELS[event.event_type] ??
                      event.event_type}
                  </p>

                  <p className="mt-1 text-xs text-muted">
                    By{" "}
                    {event.actor_type === "record_owner"
                      ? "record owner"
                      : event.actor_type}
                  </p>
                </div>

                <time className="text-xs text-muted">
                  {formatDateTime(event.created_at)}
                </time>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}

export default function RecordDetail({
  recordId,
}: RecordDetailProps) {
  const [record, setRecord] =
    useState<RecordItem | null>(null);

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] =
    useState<string | null>(null);

  const [isNotFound, setIsNotFound] =
    useState(false);

  const [reloadCount, setReloadCount] =
    useState(0);

  const [auditEvents, setAuditEvents] =
    useState<AuditEvent[]>([]);

  const [isAuditLoading, setIsAuditLoading] =
    useState(false);

  const [auditError, setAuditError] =
    useState<string | null>(null);

  const [
    verificationLink,
    setVerificationLink,
  ] = useState<string | null>(null);

  const [
    isCreatingVerification,
    setIsCreatingVerification,
  ] = useState(false);

  const [
    verificationError,
    setVerificationError,
  ] = useState<string | null>(null);

  const [copied, setCopied] = useState(false);

  const numericRecordId =
    /^\d+$/.test(recordId)
      ? Number(recordId)
      : null;

  async function loadAuditEvents(
    id: number,
    signal?: AbortSignal
  ) {
    setIsAuditLoading(true);

    try {
      const result = await fetchAuditEvents(
        id,
        signal
      );

      setAuditEvents(result);
      setAuditError(null);
    } catch (caughtError) {
      if (signal?.aborted) {
        return;
      }

      setAuditEvents([]);

      setAuditError(
        caughtError instanceof Error
          ? caughtError.message
          : "Could not load audit history."
      );
    } finally {
      if (!signal?.aborted) {
        setIsAuditLoading(false);
      }
    }
  }

  useEffect(() => {
    if (numericRecordId === null) {
      return;
    }

    const controller =
      new AbortController();

    async function loadRecord(id: number) {
      setIsLoading(true);

      try {
        const result = await fetchRecord(
          id,
          controller.signal
        );

        setRecord(result);
        setError(null);
        setIsNotFound(false);

        await loadAuditEvents(
          id,
          controller.signal
        );
      } catch (caughtError) {
        if (controller.signal.aborted) {
          return;
        }

        setRecord(null);

        if (
          caughtError instanceof ApiError &&
          caughtError.status === 404
        ) {
          setIsNotFound(true);
          setError(null);
        } else {
          setIsNotFound(false);

          setError(
            caughtError instanceof Error
              ? caughtError.message
              : "Unknown error"
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

  async function handleCreateVerification() {
    if (!record) {
      return;
    }

    setIsCreatingVerification(true);
    setVerificationError(null);
    setCopied(false);

    try {
      const request =
        await createVerificationRequest(
          record.id
        );

      const link =
        `${window.location.origin}/verify/` +
        encodeURIComponent(request.token);

      setVerificationLink(link);

      await loadAuditEvents(record.id);
    } catch (caughtError) {
      setVerificationError(
        caughtError instanceof Error
          ? caughtError.message
          : "Could not create verification request."
      );
    } finally {
      setIsCreatingVerification(false);
    }
  }

  async function handleCopyLink() {
    if (!verificationLink) {
      return;
    }

    try {
      await navigator.clipboard.writeText(
        verificationLink
      );

      setCopied(true);
    } catch {
      setCopied(false);
    }
  }

  return (
    <main className="mx-auto w-full max-w-5xl px-6 py-10">
      <BackToRecordsLink />

      <div className="mt-6">
        {numericRecordId === null ||
        isNotFound ? (
          <DetailMessage title="Record not found">
            <p>
              No record exists for this address. It may
              have been removed, or the link may be
              incorrect.
            </p>
          </DetailMessage>
        ) : isLoading ? (
          <DetailMessage title="Loading record…">
            <p>
              Fetching this record from the backend.
            </p>
          </DetailMessage>
        ) : error ? (
          <DetailMessage title="Could not load record">
            <p>
              The request to the backend failed (
              {error}). Confirm the API is running and
              try again.
            </p>

            <button
              type="button"
              onClick={() =>
                setReloadCount(
                  (count) => count + 1
                )
              }
              className="mt-4 rounded-md border border-accent px-3.5 py-2 text-sm font-medium text-accent transition-colors hover:bg-accent-soft focus:outline-none focus-visible:ring-2 focus-visible:ring-accent/40"
            >
              Retry
            </button>
          </DetailMessage>
        ) : record ? (
          <>
            <div className="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <div className="flex flex-wrap items-center gap-x-4 gap-y-2">
                  <h1 className="font-serif text-4xl leading-tight tracking-tight text-ink">
                    {formatRecordName(record)}
                  </h1>

                  <StatusBadge
                    status={
                      record.record_status
                    }
                  />
                </div>

                <p className="mt-2 text-sm text-muted">
                  {record.organization
                    ? record.organization
                    : "No organization on file"}
                </p>
              </div>

              <Link
                href="/review"
                className="text-sm font-medium text-accent hover:underline"
              >
                Review queue
              </Link>
            </div>

            <div className="mt-8 grid gap-5">
              <section className="rounded-md border border-line bg-surface p-6">
                <div className="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
                  <div className="max-w-xl">
                    <h2 className="text-sm font-medium text-ink">
                      Verification
                    </h2>

                    <p className="mt-2 text-sm leading-6 text-muted">
                      Create a secure link for the record
                      owner to review their information and
                      submit corrections.
                    </p>

                    {record.email ? (
                      <p className="mt-2 text-xs text-muted">
                        Recipient: {record.email}
                      </p>
                    ) : (
                      <p className="mt-2 text-xs text-red-700">
                        This record does not have an email
                        address.
                      </p>
                    )}
                  </div>

                  <button
                    type="button"
                    disabled={
                      isCreatingVerification ||
                      !record.email
                    }
                    onClick={
                      handleCreateVerification
                    }
                    className="shrink-0 rounded-md bg-accent px-4 py-2.5 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-40"
                  >
                    {isCreatingVerification
                      ? "Creating…"
                      : "Create verification request"}
                  </button>
                </div>

                {verificationError ? (
                  <p className="mt-4 text-sm text-red-700">
                    {verificationError}
                  </p>
                ) : null}

                {verificationLink ? (
                  <div className="mt-5 border-t border-line pt-5">
                    <p className="text-xs font-medium uppercase tracking-wide text-muted">
                      Verification link
                    </p>

                    <div className="mt-2 flex flex-col gap-2 sm:flex-row">
                      <input
                        readOnly
                        value={verificationLink}
                        className="min-w-0 flex-1 rounded-md border border-line bg-background px-3 py-2.5 font-mono text-xs text-ink"
                      />

                      <button
                        type="button"
                        onClick={handleCopyLink}
                        className="rounded-md border border-line px-4 py-2.5 text-sm font-medium text-ink transition-colors hover:border-accent"
                      >
                        {copied
                          ? "Copied"
                          : "Copy link"}
                      </button>
                    </div>

                    <p className="mt-2 text-xs text-muted">
                      Demo mode: this creates the
                      verification request and link but does
                      not send an email automatically.
                    </p>
                  </div>
                ) : null}
              </section>

              <DetailSection title="Contact Information">
                <DetailField
                  label="Email"
                  value={record.email}
                />

                <DetailField
                  label="Phone"
                  value={record.phone}
                />

                <DetailField
                  label="Address"
                  value={record.address}
                />

                <DetailField
                  label="City"
                  value={record.city}
                />

                <DetailField
                  label="Province/State"
                  value={
                    record.province_state
                  }
                />

                <DetailField
                  label="Postal/ZIP"
                  value={record.postal_zip}
                />
              </DetailSection>

              <DetailSection title="Record Information">
                <DetailField
                  label="Organization"
                  value={record.organization}
                />

                <DetailField
                  label="Reference Number"
                  value={
                    record.reference_number
                  }
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
                      ? formatDate(
                          record.last_verified_date
                        )
                      : null
                  }
                />
              </DetailSection>

              <RecordDocuments
                recordId={record.id}
              />

              <AuditHistory
                events={auditEvents}
                isLoading={isAuditLoading}
                error={auditError}
              />
            </div>
          </>
        ) : null}
      </div>
    </main>
  );
}