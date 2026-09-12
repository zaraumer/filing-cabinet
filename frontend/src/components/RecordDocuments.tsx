"use client";

import { useEffect, useRef, useState } from "react";

import {
  fetchRecordDocuments,
  recordDocumentUrl,
  type SourceDocument,
  uploadRecordDocument,
} from "@/lib/records";

type RecordDocumentsProps = {
  recordId: number;
};

// Mirrors ALLOWED_CONTENT_TYPES in backend/app/storage.py. The backend is
// still the check that matters; this only filters the file picker.
const ACCEPTED_FILE_TYPES = "application/pdf,image/png,image/jpeg";

const CONTENT_TYPE_LABELS: Record<string, string> = {
  "application/pdf": "PDF",
  "image/png": "PNG",
  "image/jpeg": "JPEG",
};

function formatFileSize(bytes: number): string {
  if (bytes < 1024) {
    return `${bytes} B`;
  }

  if (bytes < 1024 * 1024) {
    return `${Math.round(bytes / 1024)} KB`;
  }

  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

/** uploaded_at is an ISO timestamp; this component only renders on the client. */
function formatUploadedAt(value: string): string {
  const uploadedAt = new Date(value);

  if (Number.isNaN(uploadedAt.getTime())) {
    return value;
  }

  return uploadedAt.toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function documentTypeLabel(contentType: string): string {
  return CONTENT_TYPE_LABELS[contentType] ?? contentType;
}

export default function RecordDocuments({ recordId }: RecordDocumentsProps) {
  const [documents, setDocuments] = useState<SourceDocument[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [listError, setListError] = useState<string | null>(null);

  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadedName, setUploadedName] = useState<string | null>(null);

  // Incremented after an upload so the list below reloads from the backend.
  const [reloadCount, setReloadCount] = useState(0);

  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const controller = new AbortController();

    async function loadDocuments() {
      setIsLoading(true);

      try {
        const results = await fetchRecordDocuments(recordId, controller.signal);

        setDocuments(results);
        setListError(null);
      } catch (caughtError) {
        if (controller.signal.aborted) {
          return;
        }

        setDocuments([]);
        setListError(
          caughtError instanceof Error ? caughtError.message : "Unknown error",
        );
      } finally {
        if (!controller.signal.aborted) {
          setIsLoading(false);
        }
      }
    }

    loadDocuments();

    return () => {
      controller.abort();
    };
  }, [recordId, reloadCount]);

  async function handleUpload(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const file = fileInputRef.current?.files?.[0];

    if (!file) {
      setUploadedName(null);
      setUploadError("Choose a file to upload.");

      return;
    }

    setIsUploading(true);
    setUploadError(null);
    setUploadedName(null);

    try {
      const document = await uploadRecordDocument(recordId, file);

      setUploadedName(document.original_filename);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }

      setReloadCount((count) => count + 1);
    } catch (caughtError) {
      setUploadError(
        caughtError instanceof Error ? caughtError.message : "Upload failed",
      );
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <section className="rounded-md border border-line bg-surface p-6">
      <h2 className="text-sm font-medium text-ink">Source Documents</h2>
      <p className="mt-1 text-sm text-muted">
        Scanned files this record came from. PDF, PNG, and JPEG up to 10 MB.
      </p>

      <form onSubmit={handleUpload} className="mt-5">
        <label
          htmlFor="source-document"
          className="block text-xs font-medium uppercase tracking-wide text-muted"
        >
          Upload a source document
        </label>

        <div className="mt-2 flex flex-wrap items-center gap-3">
          <input
            id="source-document"
            ref={fileInputRef}
            type="file"
            name="file"
            accept={ACCEPTED_FILE_TYPES}
            disabled={isUploading}
            onChange={() => {
              setUploadError(null);
              setUploadedName(null);
            }}
            className="max-w-full text-sm text-muted file:mr-3 file:cursor-pointer file:rounded-md file:border file:border-line file:bg-page file:px-3 file:py-2 file:text-sm file:font-medium file:text-ink hover:file:bg-accent-soft focus:outline-none focus-visible:ring-2 focus-visible:ring-accent/40"
          />

          <button
            type="submit"
            disabled={isUploading}
            className="rounded-md border border-accent px-3.5 py-2 text-sm font-medium text-accent transition-colors hover:bg-accent-soft focus:outline-none focus-visible:ring-2 focus-visible:ring-accent/40 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isUploading ? "Uploading…" : "Upload"}
          </button>
        </div>

        {uploadError ? (
          <p role="alert" className="mt-3 text-sm text-ink">
            Upload failed: {uploadError}
          </p>
        ) : null}

        {uploadedName ? (
          <p role="status" className="mt-3 text-sm text-accent-strong">
            Uploaded {uploadedName}.
          </p>
        ) : null}
      </form>

      <div className="mt-6 border-t border-line pt-5">
        {isLoading ? (
          <p className="text-sm text-muted">Loading documents…</p>
        ) : listError ? (
          <p className="text-sm text-muted">
            Could not load documents ({listError}).
          </p>
        ) : documents.length === 0 ? (
          <p className="text-sm text-muted">
            No source documents have been uploaded for this record yet.
          </p>
        ) : (
          <ul className="grid gap-3">
            {documents.map((document) => (
              <li
                key={document.id}
                className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1 rounded-md border border-line px-4 py-3"
              >
                <div>
                  <a
                    href={recordDocumentUrl(recordId, document.id)}
                    target="_blank"
                    rel="noreferrer"
                    className="rounded-sm text-sm font-medium text-ink underline decoration-line underline-offset-4 transition-colors hover:decoration-accent focus:outline-none focus-visible:ring-2 focus-visible:ring-accent/40"
                  >
                    {document.original_filename}
                  </a>
                  <p className="mt-1 text-xs text-muted">
                    {documentTypeLabel(document.content_type)} ·{" "}
                    {formatFileSize(document.file_size)}
                  </p>
                </div>

                <span className="text-xs text-muted">
                  Uploaded {formatUploadedAt(document.uploaded_at)}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  );
}
