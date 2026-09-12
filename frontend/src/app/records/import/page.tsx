"use client";

import { ChangeEvent, FormEvent, useState } from "react";
import { useRouter } from "next/navigation";


import {
  checkIntakeDuplicates,
  createRecordFromIntake,
  DuplicateMatch,
  RecordFormData,
  uploadIntakeDocument,
} from "@/lib/records";


const EMPTY_FORM: RecordFormData = {
  first_name: "",
  last_name: "",
  email: null,
  phone: null,
  address: null,
  city: null,
  province_state: null,
  postal_zip: null,
  organization: null,
  reference_number: null,
  record_status: "active",
  last_verified_date: null,
};


export default function ImportRecordPage() {
  const router = useRouter();

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [intakeId, setIntakeId] = useState<number | null>(null);
  const [form, setForm] = useState<RecordFormData>(EMPTY_FORM);
  const [duplicates, setDuplicates] = useState<DuplicateMatch[]>([]);
  const [duplicateCheckComplete, setDuplicateCheckComplete] = useState(false);

  const [uploading, setUploading] = useState(false);
  const [checkingDuplicates, setCheckingDuplicates] = useState(false);
  const [creating, setCreating] = useState(false);

  const [error, setError] = useState<string | null>(null);


  function handleFileChange(
    event: ChangeEvent<HTMLInputElement>
  ) {
    const file = event.target.files?.[0] ?? null;

    setSelectedFile(file);
    setError(null);
  }


  function updateField(
    field: keyof RecordFormData,
    value: string
  ) {
    setForm((current) => ({
      ...current,
      [field]: value === "" ? null : value,
    }));

    setDuplicateCheckComplete(false);
    setDuplicates([]);
  }


  async function handleUpload() {
    if (!selectedFile) {
      setError("Choose a document first.");
      return;
    }

    try {
      setUploading(true);
      setError(null);

      const intake = await uploadIntakeDocument(
        selectedFile
      );

      setIntakeId(intake.id);

      setForm({
        ...EMPTY_FORM,
        ...intake.extracted_fields,
        record_status:
          intake.extracted_fields?.record_status?.toLowerCase()
          || "active",
      });

      setDuplicates([]);
      setDuplicateCheckComplete(false);
    } catch (uploadError) {
      setError(
        uploadError instanceof Error
          ? uploadError.message
          : "Could not upload document."
      );
    } finally {
      setUploading(false);
    }
  }


  async function handleDuplicateCheck(
    event: FormEvent
  ) {
    event.preventDefault();

    if (intakeId === null) {
      return;
    }

    if (!form.first_name || !form.last_name) {
      setError("First and last name are required.");
      return;
    }

    try {
      setCheckingDuplicates(true);
      setError(null);

      const result = await checkIntakeDuplicates(
        intakeId,
        form
      );

      setDuplicates(result.matches);
      setDuplicateCheckComplete(true);
    } catch (duplicateError) {
      setError(
        duplicateError instanceof Error
          ? duplicateError.message
          : "Could not check for duplicates."
      );
    } finally {
      setCheckingDuplicates(false);
    }
  }


  async function handleCreateRecord() {
    if (intakeId === null) {
      return;
    }

    if (!duplicateCheckComplete) {
      setError(
        "Check for duplicate records before creating this record."
      );
      return;
    }

    try {
      setCreating(true);
      setError(null);

      const newRecord = await createRecordFromIntake(
        intakeId,
        form,
        duplicates.length > 0
      );

      router.push(
        `/records/${newRecord.id}`
      );
    } catch (createError) {
      setError(
        createError instanceof Error
          ? createError.message
          : "Could not create record."
      );
    } finally {
      setCreating(false);
    }
  }


  const formReady = intakeId !== null;


  return (
    <main className="min-h-screen bg-[#F7F6F2] text-[#20211F]">
      <div className="mx-auto w-full max-w-5xl px-6 py-12">
        <div className="mb-10">
          <button
            type="button"
            onClick={() => router.push("/records")}
            className="mb-6 text-sm text-[#686A65] transition hover:text-[#20211F]"
          >
            ← Back to records
          </button>

          <h1 className="font-serif text-4xl tracking-tight">
            Import a record
          </h1>

          <p className="mt-3 max-w-2xl text-sm leading-6 text-[#686A65]">
            Upload a source document, review the extracted information,
            then check for possible duplicate records before creating a new profile.
          </p>
        </div>


        <section className="rounded-xl border border-[#DEDCD5] bg-white p-6">
          <div className="mb-5">
            <p className="text-xs font-medium uppercase tracking-[0.15em] text-[#686A65]">
              Step 1
            </p>

            <h2 className="mt-2 text-xl font-medium">
              Upload source document
            </h2>
          </div>

          <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
            <input
              type="file"
              accept=".pdf,.png,.jpg,.jpeg"
              onChange={handleFileChange}
              className="block w-full text-sm text-[#686A65] file:mr-4 file:rounded-md file:border-0 file:bg-[#F0EFEA] file:px-4 file:py-2 file:text-sm file:font-medium file:text-[#20211F] hover:file:bg-[#E8E6DF]"
            />

            <button
              type="button"
              disabled={!selectedFile || uploading}
              onClick={handleUpload}
              className="shrink-0 rounded-md bg-[#355E4A] px-5 py-2.5 text-sm font-medium text-white transition hover:bg-[#2E5140] disabled:cursor-not-allowed disabled:opacity-50"
            >
              {uploading ? "Uploading..." : "Upload document"}
            </button>
          </div>

          {selectedFile && (
            <p className="mt-3 text-sm text-[#686A65]">
              Selected: {selectedFile.name}
            </p>
          )}
        </section>


        {formReady && (
          <form
            onSubmit={handleDuplicateCheck}
            className="mt-6 rounded-xl border border-[#DEDCD5] bg-white p-6"
          >
            <div className="mb-6">
              <p className="text-xs font-medium uppercase tracking-[0.15em] text-[#686A65]">
                Step 2
              </p>

              <h2 className="mt-2 text-xl font-medium">
                Review extracted information
              </h2>

              <p className="mt-2 text-sm leading-6 text-[#686A65]">
                Correct anything that was not extracted properly before continuing.
              </p>
            </div>

            <div className="grid gap-5 md:grid-cols-2">
              <Field
                label="First name"
                value={form.first_name}
                required
                onChange={(value) =>
                  updateField("first_name", value)
                }
              />

              <Field
                label="Last name"
                value={form.last_name}
                required
                onChange={(value) =>
                  updateField("last_name", value)
                }
              />

              <Field
                label="Email"
                value={form.email}
                type="email"
                onChange={(value) =>
                  updateField("email", value)
                }
              />

              <Field
                label="Phone"
                value={form.phone}
                onChange={(value) =>
                  updateField("phone", value)
                }
              />

              <Field
                label="Organization"
                value={form.organization}
                onChange={(value) =>
                  updateField("organization", value)
                }
              />

              <Field
                label="Reference number"
                value={form.reference_number}
                onChange={(value) =>
                  updateField("reference_number", value)
                }
              />

              <Field
                label="Address"
                value={form.address}
                onChange={(value) =>
                  updateField("address", value)
                }
              />

              <Field
                label="City"
                value={form.city}
                onChange={(value) =>
                  updateField("city", value)
                }
              />

              <Field
                label="Province / state"
                value={form.province_state}
                onChange={(value) =>
                  updateField("province_state", value)
                }
              />

              <Field
                label="Postal / ZIP code"
                value={form.postal_zip}
                onChange={(value) =>
                  updateField("postal_zip", value)
                }
              />

              <Field
                label="Record status"
                value={form.record_status}
                onChange={(value) =>
                  updateField("record_status", value)
                }
              />

              <Field
                label="Last verified date"
                value={form.last_verified_date}
                type="date"
                onChange={(value) =>
                  updateField("last_verified_date", value)
                }
              />
            </div>

            <div className="mt-7 border-t border-[#EEECE6] pt-5">
              <button
                type="submit"
                disabled={checkingDuplicates}
                className="rounded-md border border-[#355E4A] px-5 py-2.5 text-sm font-medium text-[#355E4A] transition hover:bg-[#F0F5F2] disabled:cursor-not-allowed disabled:opacity-50"
              >
                {checkingDuplicates
                  ? "Checking..."
                  : "Check for duplicates"}
              </button>
            </div>
          </form>
        )}


        {duplicateCheckComplete && (
          <section className="mt-6 rounded-xl border border-[#DEDCD5] bg-white p-6">
            <div>
              <p className="text-xs font-medium uppercase tracking-[0.15em] text-[#686A65]">
                Step 3
              </p>

              <h2 className="mt-2 text-xl font-medium">
                Duplicate review
              </h2>
            </div>

            {duplicates.length === 0 ? (
              <div className="mt-5 rounded-lg border border-[#C7D8CC] bg-[#F0F5F2] p-4">
                <p className="text-sm font-medium text-[#355E4A]">
                  No likely duplicates found.
                </p>

                <p className="mt-1 text-sm text-[#686A65]">
                  You can create the new record.
                </p>
              </div>
            ) : (
              <div className="mt-5">
                <div className="mb-4 rounded-lg border border-[#D8CDB4] bg-[#FAF7EF] p-4">
                  <p className="text-sm font-medium">
                    {duplicates.length} possible duplicate
                    {duplicates.length === 1 ? "" : "s"} found.
                  </p>

                  <p className="mt-1 text-sm text-[#686A65]">
                    Review these records before deciding whether to continue.
                  </p>
                </div>

                <div className="divide-y divide-[#EEECE6] border-y border-[#EEECE6]">
                  {duplicates.map((match) => (
                    <div
                      key={match.record.id}
                      className="flex flex-col gap-4 py-5 sm:flex-row sm:items-center sm:justify-between"
                    >
                      <div>
                        <p className="font-medium">
                          {match.record.first_name}{" "}
                          {match.record.last_name}
                        </p>

                        <p className="mt-1 text-sm text-[#686A65]">
                          {match.record.email || "No email"}
                          {match.record.reference_number
                            ? ` · ${match.record.reference_number}`
                            : ""}
                        </p>

                        <div className="mt-2 flex flex-wrap gap-2">
                          {match.reasons.map((reason) => (
                            <span
                              key={reason}
                              className="rounded-full bg-[#F0EFEA] px-2.5 py-1 text-xs text-[#686A65]"
                            >
                              {reason}
                            </span>
                          ))}
                        </div>
                      </div>

                      <button
                        type="button"
                        onClick={() =>
                          router.push(
                            `/records/${match.record.id}`
                          )
                        }
                        className="text-left text-sm font-medium text-[#355E4A] hover:underline"
                      >
                        View existing record
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="mt-6 flex justify-end">
              <button
                type="button"
                disabled={creating}
                onClick={handleCreateRecord}
                className="rounded-md bg-[#355E4A] px-5 py-2.5 text-sm font-medium text-white transition hover:bg-[#2E5140] disabled:cursor-not-allowed disabled:opacity-50"
              >
                {creating
                  ? "Creating..."
                  : duplicates.length > 0
                    ? "Create anyway"
                    : "Create record"}
              </button>
            </div>
          </section>
        )}


        {error && (
          <div className="mt-6 rounded-lg border border-[#D9BDB9] bg-[#FBF3F2] px-4 py-3 text-sm text-[#7A3430]">
            {error}
          </div>
        )}
      </div>
    </main>
  );
}


type FieldProps = {
  label: string;
  value: string | null;
  type?: string;
  required?: boolean;
  onChange: (value: string) => void;
};


function Field({
  label,
  value,
  type = "text",
  required = false,
  onChange,
}: FieldProps) {
  return (
    <label className="block">
      <span className="mb-2 block text-sm font-medium">
        {label}
        {required && (
          <span className="ml-1 text-[#686A65]">
            *
          </span>
        )}
      </span>

      <input
        type={type}
        required={required}
        value={value ?? ""}
        onChange={(event) =>
          onChange(event.target.value)
        }
        className="w-full rounded-md border border-[#DEDCD5] bg-white px-3.5 py-2.5 text-sm outline-none transition placeholder:text-[#A09F99] focus:border-[#355E4A] focus:ring-1 focus:ring-[#355E4A]"
      />
    </label>
  );
}