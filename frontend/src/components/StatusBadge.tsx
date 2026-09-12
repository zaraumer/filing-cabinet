/**
 * record_status is a free-form string on the backend, so only the known
 * "active" value gets the green treatment. Anything else stays neutral.
 */
export default function StatusBadge({ status }: { status: string }) {
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
