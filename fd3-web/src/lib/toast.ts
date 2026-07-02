// Minimal toast store. Was a per-file helper in character-studio.html and
// face-tagger.html. Now a single Svelte 5 rune store + <Toast /> component.
import { writable } from 'svelte/store';

export interface Toast { id: number; msg: string; kind: 'ok' | 'err' }
export const toasts = writable<Toast[]>([]);

let nextId = 1;
export function toast(msg: string, kind: 'ok' | 'err' = 'ok') {
	const id = nextId++;
	toasts.update(list => [...list, { id, msg, kind }]);
	setTimeout(() => {
		toasts.update(list => list.filter(t => t.id !== id));
	}, 2500);
}

export function fileToDataUrl(file: File): Promise<string> {
	return new Promise((resolve, reject) => {
		const r = new FileReader();
		r.onload = () => resolve(String(r.result));
		r.onerror = () => reject(r.error ?? new Error('File read failed'));
		r.readAsDataURL(file);
	});
}
