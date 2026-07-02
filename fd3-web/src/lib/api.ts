// Tiny fetch wrapper that throws on !ok and surfaces server message.
export interface ApiError extends Error {
	status: number;
	serverMessage?: string;
}

async function call<T>(path: string, init?: RequestInit): Promise<T> {
	const r = await fetch(path, { cache: 'no-store', ...init });
	let body: any = null;
	try { body = await r.json(); } catch { /* not JSON */ }
	if (!r.ok || (body && body.ok === false)) {
		const err: ApiError = Object.assign(
			new Error(body?.message || body?.error || `HTTP ${r.status}`),
			{ status: r.status, serverMessage: body?.message }
		);
		throw err;
	}
	return body as T;
}

export const api = {
	getMapping: () => call<{
		ok: true;
		mapping: Record<string, Array<{ x: number; y: number; char: string; id?: string }>>;
		markers: number;
		perCharacter: Record<string, number>;
	}>('/api/mapping'),
	getReferences: () => call<{
		ok: true;
		references: Record<string, string[]>;
		markers: number;
	}>('/api/references'),
	saveMapping: (mapping: unknown, force = false) =>
		call<{
			ok: true;
			forced: boolean;
			savedPhotos: number;
			savedMarkers: number;
			backupPath: string;
			mapping: unknown;
		}>('/save' + (force ? '?force=1' : ''), {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(mapping)
		}),
	uploadReference: (char: string, dataUrl: string, filename: string) =>
		call<{ ok: true; file: string; url: string; references: Record<string, string[]> }>(
			'/api/references',
			{
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ char, dataUrl, filename })
			}
		),
	recrop: () =>
		call<{ ok: true; count: number; output: string }>('/recrop', { method: 'POST' })
};
