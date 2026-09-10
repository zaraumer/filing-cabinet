export default async function Home() {
  let backendStatus = "offline";

  try {
    const response = await fetch("http://127.0.0.1:8000/health", {
      cache: "no-store",
    });

    if (response.ok) {
      const data = await response.json();
      backendStatus = data.status;
    }
  } catch {
    backendStatus = "offline";
  }

  return (
    <main className="min-h-screen p-10">
      <h1 className="text-3xl font-bold">Filing Cabinet</h1>

      <p className="mt-4">
        Backend status:{" "}
        <span className="font-semibold">{backendStatus}</span>
      </p>
    </main>
  );
}