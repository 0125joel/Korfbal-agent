const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? (typeof window !== 'undefined' ? `${window.location.origin}/api` : '/api');

export async function fetcher(path: string) {
  const url = path.startsWith('http') ? path : `${baseUrl}${path}`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`API fout (${response.status})`);
  }
  return response.json();
}
