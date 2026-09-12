import RecordDetail from "@/components/RecordDetail";

export default async function RecordDetailPage({
  params,
}: PageProps<"/records/[id]">) {
  const { id } = await params;

  return <RecordDetail recordId={id} />;
}
