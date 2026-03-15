'use client';

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const isStaleDeployment =
    error.message?.includes('Failed to find Server Action') ||
    error.digest === 'NEXT_NOT_FOUND';

  if (isStaleDeployment) {
    // Force a full page reload to fetch the latest client bundle
    if (typeof window !== 'undefined') {
      window.location.reload();
    }
    return null;
  }

  return (
    <html lang="en" className="dark">
      <body className="flex min-h-screen items-center justify-center bg-background text-foreground">
        <div className="text-center space-y-4">
          <h2 className="text-2xl font-bold">Something went wrong</h2>
          <button
            onClick={() => reset()}
            className="px-4 py-2 rounded bg-primary text-primary-foreground hover:opacity-90"
          >
            Try again
          </button>
        </div>
      </body>
    </html>
  );
}
