// src/lib/trpc/utils.ts

function getBaseUrl() {
  // Ensure consistent trailing slash
  const ensureTrailingSlash = (url: string) => (url.endsWith('/') ? url : `${url}/`);

  // Browser should use relative path
  if (typeof window !== 'undefined') return ensureTrailingSlash('');

  // Vercel deployment URL
  if (process.env.VERCEL_URL) return ensureTrailingSlash(`https://${process.env.VERCEL_URL}`);

  // Docker or other containerized environments (check for common env vars)
  const port = process.env.PORT || 3000;
  if (process.env.CONTAINER_HOST) {
    return ensureTrailingSlash(`http://${process.env.CONTAINER_HOST}:${port}`);
  }

  // Assume localhost for development or other environments
  return ensureTrailingSlash(`http://localhost:${port}`);
}

export function getUrl() {
  return getBaseUrl() + 'api/trpc'; // Append the API endpoint
}