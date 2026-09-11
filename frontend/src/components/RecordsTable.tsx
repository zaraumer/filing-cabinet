import { formatRecordName, type RecordItem } from "@/lib/records";

type RecordsTableProps = {
  records: RecordItem[];
};

const COLUMN_HEADINGS = [
  "Name",
  "Email",
  "Phone",
  "Organization",
  "Reference Number",
  "Status",
];

/** Empty fields come back as null from the API, so show a placeholder instead. */
function cellValue(value: string | null) {
  if (!value) {
    return <span className="text-line">—</span>;
  }

  return value;
}

/**
 * record_status is a free-form string on the backend, so only the known
 * "active" value gets the green treatment. Anything else stays neutral.
 */
function StatusBadge({ status }: { status: string }) {
  const isActive = status.trim().toLowerCase() === "active";

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium capitalize ${
        isActive
          ? "bg-accent-soft text-accent-strong"
          : "bg-page text-muted"
      }`}
    >
      <span
        aria-hidden="true"
        className={`h-1.5 w-1.5 rounded-full ${
          isActive ? "bg-accent" : "bg-muted"
        }`}
      />
      {status}
    </span>
  );
}

export default function RecordsTable({ records }: RecordsTableProps) {
  return (
    <div className="overflow-x-auto rounded-md border border-line bg-surface">
      <table className="w-full min-w-[900px] border-collapse text-sm">
        <thead>
          <tr className="border-b border-line text-left">
            {COLUMN_HEADINGS.map((heading) => (
              <th
                key={heading}
                scope="col"
                className="px-5 py-3 text-xs font-medium uppercase tracking-wide text-muted"
              >
                {heading}
              </th>
            ))}
          </tr>
        </thead>

        <tbody>
          {records.map((record) => (
            <tr
              key={record.id}
              className="border-b border-line/70 transition-colors last:border-b-0 hover:bg-page"
            >
              <td className="px-5 py-4 font-medium text-ink">
                {formatRecordName(record)}
              </td>
              <td className="px-5 py-4 text-muted">{cellValue(record.email)}</td>
              <td className="px-5 py-4 text-muted">{cellValue(record.phone)}</td>
              <td className="px-5 py-4 text-muted">
                {cellValue(record.organization)}
              </td>
              <td className="px-5 py-4 font-mono text-[0.8125rem] text-muted">
                {cellValue(record.reference_number)}
              </td>
              <td className="px-5 py-4">
                <StatusBadge status={record.record_status} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
