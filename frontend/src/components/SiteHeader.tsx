const SECTIONS = [{ label: "Records", isCurrent: true }];

export default function SiteHeader() {
  return (
    <header className="border-b border-line bg-surface">
      <div className="mx-auto flex w-full max-w-5xl flex-wrap items-center gap-x-8 gap-y-2 px-6 py-6">
        <span className="font-serif text-2xl leading-none tracking-tight text-ink">
          Filing Cabinet
        </span>

        <nav aria-label="Sections">
          <ul className="flex items-center gap-6 text-sm">
            {SECTIONS.map((section) => (
              <li key={section.label}>
                <span
                  aria-current={section.isCurrent ? "page" : undefined}
                  className="border-b-2 border-accent pb-0.5 font-medium text-ink"
                >
                  {section.label}
                </span>
              </li>
            ))}
          </ul>
        </nav>
      </div>
    </header>
  );
}
