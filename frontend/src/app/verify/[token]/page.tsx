import VerificationForm from "@/components/VerificationForm";

type VerificationPageProps = {
  params: Promise<{
    token: string;
  }>;
};

export default async function VerificationPage({
  params,
}: VerificationPageProps) {
  const { token } = await params;

  return <VerificationForm token={token} />;
}