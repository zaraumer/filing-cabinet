"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

import {
  fetchVerification,
  submitProposedUpdate,
  type ProposedRecordFields,
  type VerificationView,
} from "@/lib/records";

type VerificationFormProps = {
  token: string;
};

const EDITABLE_FIELDS: {
  key: keyof ProposedRecordFields;
  label: string;
  type?: string;
}[] = [
  { key: "first_name", label: "First name" },
  { key: "last_name", label: "Last name" },
  { key: "email", label: "Email", type: "email" },
  { key: "phone", label: "Phone" },
  { key: "address", label: "Address" },
  { key: "city", label: "City" },
  { key: "province_state", label: "Province / State" },
  { key: "postal_zip", label: "Postal / ZIP code" },
  { key: "organization", label: "Organization" },
];

export default function VerificationForm({
  token,
}: VerificationFormProps) {
  const [verification, setVerification] =
    useState<VerificationView | null>(null);

  const [form, setForm] =
    useState<ProposedRecordFields>({});

  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [error, setError] =
    useState<string | null>(null);

  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function loadVerification() {
      try {
        const data = await fetchVerification(token);

        if (cancelled) {
          return;
        }

        setVerification(data);

        setForm({
          first_name: data.record.first_name,
          last_name: data.record.last_name,
          email: data.record.email,
          phone: data.record.phone,
          address: data.record.address,
          city: data.record.city,
          province_state: data.record.province_state,
          postal_zip: data.record.postal_zip,
          organization: data.record.organization,
        });

        setError(null);
      } catch (caughtError) {
        if (cancelled) {
          return;
        }

        setError(
          caughtError instanceof Error
            ? caughtError.message
            : "Could not load verification request."
        );
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    loadVerification();

    return () => {
      cancelled = true;
    };
  }, [token]);

  const changedFields = useMemo(() => {
    if (!verification) {
      return {};
    }

    const changes: ProposedRecordFields = {};

    for (const field of EDITABLE_FIELDS) {
      const currentValue =
        verification.record[field.key] ?? "";

      const formValue =
        form[field.key] ?? "";

      if (formValue !== currentValue) {
        if (
          field.key === "first_name" ||
          field.key === "last_name"
        ) {
          changes[field.key] = formValue;
        } else {
          changes[field.key] =
            formValue === "" ? null : formValue;
        }
      }
    }

    return changes;
  }, [form, verification]);

  const changedFieldCount =
    Object.keys(changedFields).length;

  function updateField(
    field: keyof ProposedRecordFields,
    value: string
  ) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  }

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    if (changedFieldCount === 0) {
      setError(
        "Make at least one change before submitting."
      );
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      await submitProposedUpdate(
        token,
        changedFields
      );

      setSubmitted(true);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "Could not submit your changes."
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  if (isLoading) {
    return (
      <main className="mx-auto w-full max-w-3xl px-6 py-12">
        <p className="text-sm text-muted">
          Loading verification request…
        </p>
      </main>
    );
  }

  if (error && !verification) {
    return (
      <main className="mx-auto w-full max-w-3xl px-6 py-12">
        <div className="rounded-md border border-line bg-surface p-6">
          <h1 className="font-serif text-3xl text-ink">
            Verification unavailable
          </h1>

          <p className="mt-3 text-sm text-muted">
            {error}
          </p>
        </div>
      </main>
    );
  }

  if (!verification) {
    return null;
  }

  if (submitted) {
    return (
      <main className="mx-auto w-full max-w-3xl px-6 py-12">
        <div className="rounded-md border border-line bg-surface p-8">
          <p className="text-xs font-medium uppercase tracking-wide text-accent">
            Submitted
          </p>

          <h1 className="mt-2 font-serif text-3xl text-ink">
            Your changes were sent for review
          </h1>

          <p className="mt-3 max-w-xl text-sm leading-6 text-muted">
            Your record has not been changed yet. A staff member
            will review the corrections before they become part of
            the official record.
          </p>
        </div>
      </main>
    );
  }

  const expiresAt = new Date(
    verification.verification_request.expires_at
  );

  return (
    <main className="mx-auto w-full max-w-3xl px-6 py-12">
      <div className="max-w-2xl">
        <p className="text-xs font-medium uppercase tracking-wide text-accent">
          Record verification
        </p>

        <h1 className="mt-2 font-serif text-4xl leading-tight tracking-tight text-ink">
          Review your information
        </h1>

        <p className="mt-3 text-sm leading-6 text-muted">
          Review the information currently on file. If something
          is incorrect, update it below and submit your changes for
          staff review.
        </p>

        <p className="mt-2 text-xs text-muted">
          This request expires{" "}
          {expiresAt.toLocaleDateString()}.
        </p>
      </div>

      <form
        onSubmit={handleSubmit}
        className="mt-8"
      >
        <section className="rounded-md border border-line bg-surface">
          <div className="border-b border-line px-6 py-5">
            <h2 className="text-sm font-semibold text-ink">
              Information on file
            </h2>

            <p className="mt-1 text-sm text-muted">
              Only changed fields will be sent for review.
            </p>
          </div>

          <div className="grid gap-5 p-6 sm:grid-cols-2">
            {EDITABLE_FIELDS.map((field) => (
              <label
                key={field.key}
                className={
                  field.key === "address"
                    ? "sm:col-span-2"
                    : ""
                }
              >
                <span className="block text-xs font-medium uppercase tracking-wide text-muted">
                  {field.label}
                </span>

                <input
                  type={field.type ?? "text"}
                  required={
                    field.key === "first_name" ||
                    field.key === "last_name"
                  }
                  value={form[field.key] ?? ""}
                  onChange={(event) =>
                    updateField(
                      field.key,
                      event.target.value
                    )
                  }
                  className="mt-2 w-full rounded-md border border-line bg-background px-3 py-2.5 text-sm text-ink focus:border-accent focus:outline-none focus-visible:ring-2 focus-visible:ring-accent/30"
                />
              </label>
            ))}
          </div>
        </section>

        <section className="mt-6 rounded-md border border-line bg-surface p-6">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="text-sm font-semibold text-ink">
                Submit corrections
              </h2>

              <p className="mt-1 text-sm text-muted">
                {changedFieldCount === 0
                  ? "No changes made."
                  : `${changedFieldCount} ${
                      changedFieldCount === 1
                        ? "field"
                        : "fields"
                    } changed.`}
              </p>
            </div>

            <button
              type="submit"
              disabled={
                isSubmitting ||
                changedFieldCount === 0
              }
              className="rounded-md bg-accent px-4 py-2.5 text-sm font-medium text-white transition-opacity disabled:cursor-not-allowed disabled:opacity-40"
            >
              {isSubmitting
                ? "Submitting…"
                : "Submit changes"}
            </button>
          </div>

          {error ? (
            <p className="mt-4 text-sm text-red-700">
              {error}
            </p>
          ) : null}
        </section>
      </form>
    </main>
  );
}