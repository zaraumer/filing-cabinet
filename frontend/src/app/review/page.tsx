"use client";

import { useEffect, useMemo, useState } from "react";

import {
  approveProposedUpdate,
  fetchProposedUpdates,
  fetchRecord,
  rejectProposedUpdate,
  type ProposedUpdate,
  type RecordItem,
} from "@/lib/records";

type ReviewItem = {
  update: ProposedUpdate;
  record: RecordItem;
};

const FIELD_LABELS: Record<string, string> = {
  first_name: "First name",
  last_name: "Last name",
  email: "Email",
  phone: "Phone",
  address: "Address",
  city: "City",
  province_state: "Province / State",
  postal_zip: "Postal / ZIP code",
  organization: "Organization",
};

export default function ReviewPage() {
  const [items, setItems] = useState<ReviewItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reviewNotes, setReviewNotes] = useState<Record<number, string>>({});
  const [activeAction, setActiveAction] = useState<number | null>(null);

  async function loadUpdates() {
    setIsLoading(true);

    try {
      const updates = await fetchProposedUpdates("pending");

      const loadedItems = await Promise.all(
        updates.map(async (update) => {
          const record = await fetchRecord(update.record_id);

          return {
            update,
            record,
          };
        })
      );

      setItems(loadedItems);
      setError(null);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "Could not load review queue."
      );
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadUpdates();
  }, []);

  const pendingCount = useMemo(
    () => items.length,
    [items]
  );

  function updateReviewNote(
    updateId: number,
    value: string
  ) {
    setReviewNotes((current) => ({
      ...current,
      [updateId]: value,
    }));
  }

  async function handleApprove(updateId: number) {
    setActiveAction(updateId);
    setError(null);

    try {
      await approveProposedUpdate(
        updateId,
        reviewNotes[updateId]
      );

      setItems((current) =>
        current.filter(
          (item) => item.update.id !== updateId
        )
      );
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "Could not approve proposed update."
      );
    } finally {
      setActiveAction(null);
    }
  }

  async function handleReject(updateId: number) {
    setActiveAction(updateId);
    setError(null);

    try {
      await rejectProposedUpdate(
        updateId,
        reviewNotes[updateId]
      );

      setItems((current) =>
        current.filter(
          (item) => item.update.id !== updateId
        )
      );
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "Could not reject proposed update."
      );
    } finally {
      setActiveAction(null);
    }
  }

  return (
    <main className="mx-auto w-full max-w-5xl px-6 py-10">
      <div className="max-w-2xl">
        <p className="text-xs font-medium uppercase tracking-wide text-accent">
          Staff review
        </p>

        <h1 className="mt-2 font-serif text-4xl leading-tight tracking-tight text-ink">
          Review queue
        </h1>

        <p className="mt-3 text-sm leading-6 text-muted">
          Review corrections submitted by record owners before
          they are applied to the official record.
        </p>
      </div>

      <div className="mt-8 flex items-baseline gap-3">
        <h2 className="text-sm font-medium text-ink">
          Pending updates
        </h2>

        {!isLoading && !error ? (
          <span className="text-sm text-muted">
            {pendingCount}{" "}
            {pendingCount === 1 ? "request" : "requests"}
          </span>
        ) : null}
      </div>

      {error ? (
        <div className="mt-4 rounded-md border border-line bg-surface p-5">
          <p className="text-sm text-red-700">
            {error}
          </p>

          <button
            type="button"
            onClick={loadUpdates}
            className="mt-3 rounded-md border border-accent px-3.5 py-2 text-sm font-medium text-accent"
          >
            Retry
          </button>
        </div>
      ) : null}

      {isLoading ? (
        <p className="mt-6 text-sm text-muted">
          Loading review queue…
        </p>
      ) : items.length === 0 ? (
        <div className="mt-4 rounded-md border border-line bg-surface p-8">
          <h3 className="text-sm font-semibold text-ink">
            No pending updates
          </h3>

          <p className="mt-1 text-sm text-muted">
            Submitted record corrections will appear here.
          </p>
        </div>
      ) : (
        <div className="mt-4 space-y-5">
          {items.map(({ update, record }) => (
            <section
              key={update.id}
              className="rounded-md border border-line bg-surface"
            >
              <div className="border-b border-line px-6 py-5">
                <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <h3 className="font-serif text-2xl text-ink">
                      {record.first_name} {record.last_name}
                    </h3>

                    <p className="mt-1 text-sm text-muted">
                      Record #{record.id}
                      {record.reference_number
                        ? ` · ${record.reference_number}`
                        : ""}
                    </p>
                  </div>

                  <span className="text-xs text-muted">
                    Submitted{" "}
                    {new Date(
                      update.submitted_at
                    ).toLocaleDateString()}
                  </span>
                </div>
              </div>

              <div className="px-6 py-5">
                <h4 className="text-sm font-semibold text-ink">
                  Proposed changes
                </h4>

                <div className="mt-4 overflow-hidden rounded-md border border-line">
                  {Object.entries(update.proposed_fields).map(
                    ([fieldName, proposedValue]) => {
                      const currentValue =
                        record[
                          fieldName as keyof RecordItem
                        ];

                      return (
                        <div
                          key={fieldName}
                          className="grid gap-2 border-b border-line px-4 py-3 last:border-b-0 sm:grid-cols-[160px_1fr_1fr]"
                        >
                          <div className="text-xs font-medium uppercase tracking-wide text-muted">
                            {FIELD_LABELS[fieldName] ??
                              fieldName}
                          </div>

                          <div>
                            <p className="text-xs text-muted">
                              Current
                            </p>

                            <p className="mt-1 text-sm text-ink">
                              {currentValue
                                ? String(currentValue)
                                : "—"}
                            </p>
                          </div>

                          <div>
                            <p className="text-xs text-muted">
                              Proposed
                            </p>

                            <p className="mt-1 text-sm font-medium text-ink">
                              {proposedValue
                                ? String(proposedValue)
                                : "—"}
                            </p>
                          </div>
                        </div>
                      );
                    }
                  )}
                </div>

                <label className="mt-5 block">
                  <span className="text-xs font-medium uppercase tracking-wide text-muted">
                    Review note
                  </span>

                  <textarea
                    value={reviewNotes[update.id] ?? ""}
                    onChange={(event) =>
                      updateReviewNote(
                        update.id,
                        event.target.value
                      )
                    }
                    rows={3}
                    placeholder="Optional note about this decision"
                    className="mt-2 w-full resize-none rounded-md border border-line bg-background px-3 py-2.5 text-sm text-ink placeholder:text-muted focus:border-accent focus:outline-none focus-visible:ring-2 focus-visible:ring-accent/30"
                  />
                </label>

                <div className="mt-5 flex flex-wrap justify-end gap-3">
                  <button
                    type="button"
                    disabled={activeAction === update.id}
                    onClick={() =>
                      handleReject(update.id)
                    }
                    className="rounded-md border border-line px-4 py-2.5 text-sm font-medium text-ink disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    Reject
                  </button>

                  <button
                    type="button"
                    disabled={activeAction === update.id}
                    onClick={() =>
                      handleApprove(update.id)
                    }
                    className="rounded-md bg-accent px-4 py-2.5 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {activeAction === update.id
                      ? "Saving…"
                      : "Approve"}
                  </button>
                </div>
              </div>
            </section>
          ))}
        </div>
      )}
    </main>
  );
}