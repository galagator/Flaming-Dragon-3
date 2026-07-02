<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import { TAGGER_CHARS } from '$lib/characters';
	import { toast } from '$lib/toast';
	import Lightbox from '$lib/Lightbox.svelte';

	const PHOTO_COUNT = 40;
	const photoKey = (i: number) => `photo_${String(i).padStart(2, '0')}`;

	type Marker = { id?: string; x: number; y: number; char: string };
	type StoredMarker = { id: string; x: number; y: number; char: string };
	type Mapping = Record<string, StoredMarker[]>;

	let state = $state({} as Mapping);
	let lightboxSrc = $state('');
	let saving = $state(false);
	let loading = $state(true);

	let pendingCtx = $state<{ photoIdx: number; x: number; y: number; left: number; top: number } | null>(null);

	function addIds(mapping: Mapping | null | undefined): Mapping {
		const out: Mapping = {};
		for (const [k, v] of Object.entries(mapping ?? {})) {
			if (!k.startsWith('photo_')) continue;
			out[k] = (v ?? []).map((m) => ({ ...m, id: m.id ?? Math.random().toString(36).slice(2, 6) }));
		}
		return out;
	}

	function getMarkers(i: number): Marker[] {
		const k = photoKey(i);
		if (!state[k]) state[k] = [];
		return state[k];
	}

	function addMarker(i: number, x: number, y: number, char: string) {
		getMarkers(i).push({ id: Math.random().toString(36).slice(2, 6), x, y, char });
		saveLocal();
	}
	function removeMarker(i: number, id: string) {
		const k = photoKey(i);
		state[k] = (state[k] ?? []).filter((m: StoredMarker) => m.id !== id);
		if (!state[k].length) delete state[k];
		saveLocal();
	}
	function updateChar(i: number, id: string, val: string) {
		const m = getMarkers(i).find((m) => m.id === id);
		if (m) m.char = val;
		saveLocal();
	}
	function taggedCount(): number {
		let t = 0;
		for (let i = 1; i <= PHOTO_COUNT; i++) if ((state[photoKey(i)] ?? []).some((m: StoredMarker) => m.char.trim())) t++;
		return t;
	}

	function buildMappingJson(): Mapping {
		const out: Mapping = {};
		for (let i = 1; i <= PHOTO_COUNT; i++) {
			const valid = getMarkers(i).filter((m: StoredMarker) => m.char.trim());
			if (valid.length) out[photoKey(i)] = valid.map((m: StoredMarker) => ({ id: m.id, x: m.x, y: m.y, char: m.char }));
		}
		return out;
	}

	async function saveToServer(force = false) {
		const out = buildMappingJson();
		saving = true;
		try {
			const d = await api.saveMapping(out, force);
			state = addIds(d.mapping as Record<string, Marker[]>);
			saveLocal();
			toast(`✅ Saved ${d.savedMarkers} markers across ${d.savedPhotos} photos`);
		} catch (e: any) {
			if (e.status === 409) {
				toast(`❌ ${e.serverMessage || e.message} (use force to override)`, 'err');
			} else {
				toast(`❌ ${e.message}`, 'err');
			}
		} finally {
			saving = false;
		}
	}

	function saveLocal() {
		try { localStorage.setItem('fd3-v3', JSON.stringify(state)); } catch {}
	}

	function loadFromFile() {
		const inp = document.createElement('input');
		inp.type = 'file';
		inp.accept = '.json';
		inp.onchange = (e) => {
			const f = (e.target as HTMLInputElement).files?.[0];
			if (!f) return;
			const reader = new FileReader();
			reader.onload = (ev) => {
				try {
					const data = JSON.parse(String(ev.target?.result));
					for (const [k, v] of Object.entries(data)) {
						if (!k.startsWith('photo_')) continue;
						state[k] = (v as Marker[]).map((m: Marker) => ({ x: m.x, y: m.y, char: m.char, id: Math.random().toString(36).slice(2, 6) }));
					}
					saveLocal();
					toast(`Loaded ${Object.keys(data).length} photos`);
				} catch (err: any) { toast(`Error: ${err.message}`, 'err'); }
			};
			reader.readAsText(f);
		};
		inp.click();
	}

	function downloadJson() {
		const out = buildMappingJson();
		const blob = new Blob([JSON.stringify(out, null, 2)], { type: 'application/json' });
		const a = document.createElement('a');
		a.href = URL.createObjectURL(blob);
		a.download = 'fd3-actor-mapping.json';
		a.click();
		URL.revokeObjectURL(a.href);
		toast(`Downloaded ${Object.keys(out).length} photos`);
	}

	function clearAll() {
		if (confirm('Clear all?')) {
			state = {};
			saveLocal();
		}
	}

	function onPhotoClick(e: MouseEvent, i: number) {
		const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
		const xPct = parseFloat((((e.clientX - rect.left) / rect.width) * 100).toFixed(1));
		const yPct = parseFloat((((e.clientY - rect.top) / rect.height) * 100).toFixed(1));
		pendingCtx = { photoIdx: i, x: xPct, y: yPct, left: Math.min(e.clientX, window.innerWidth - 160), top: Math.min(e.clientY, window.innerHeight - 350) };
		e.stopPropagation();
	}
	function closeCtx() { pendingCtx = null; }
	function pickChar(c: string) {
		if (pendingCtx) addMarker(pendingCtx.photoIdx, pendingCtx.x, pendingCtx.y, c);
		closeCtx();
	}

	onMount(async () => {
		try {
			const d = await api.getMapping();
			state = addIds(d.mapping);
			toast(`Loaded disk mapping: ${d.markers} markers`);
		} catch (e) {
			try { const s = localStorage.getItem('fd3-v3'); if (s) state = addIds(JSON.parse(s)); } catch {}
			toast('⚠️ Server unavailable — using browser cache only', 'err');
		} finally {
			loading = false;
		}
		const onClick = (e: MouseEvent) => { if (!(e.target as HTMLElement).closest('.ctx-menu')) closeCtx(); };
		document.addEventListener('click', onClick);
		document.addEventListener('click', onClick);
	});
</script>

<h1>🔥 Flaming Dragon 3 — Face Tagger</h1>
<div class="subtitle">Click a face → pick character → done. Click a marker to delete it.</div>

<div class="toolbar">
	<button class="btn" onclick={() => saveToServer(false)} disabled={saving}>💾 Save to Disk</button>
	<button class="btn btn-outline" onclick={() => saveToServer(true)} disabled={saving} title="Save even if fewer markers than on disk">⚠️ Force Save</button>
	<button class="btn btn-outline" onclick={downloadJson}>⬇️ Download JSON</button>
	<button class="btn btn-outline" onclick={loadFromFile}>📂 Load JSON</button>
	<button class="btn btn-outline" onclick={clearAll}>🗑️ Clear All</button>
	<span class="progress">{taggedCount()} / {PHOTO_COUNT}</span>
</div>

{#if loading}
	<div class="empty-state">Loading…</div>
{:else}
	<div class="photo-grid">
		{#each Array.from({ length: PHOTO_COUNT }, (_, idx) => idx + 1) as i}
			{@const markers = getMarkers(i)}
			{@const p = String(i).padStart(2, '0')}
			{@const hasTag = markers.some((m) => m.char.trim())}
			<div class="photo-card" class:filled={hasTag}>
				<div
					class="photo-wrap"
					role="button"
					tabindex="0"
					onclick={(e) => onPhotoClick(e, i)}
					ondblclick={() => (lightboxSrc = `photo_${p}.jpg`)}
				>
					<img src={`photo_${p}.jpg`} alt={`Photo ${p}`} loading="lazy" draggable="false" />
					{#each markers as m, idx}
						<div
							class="marker"
							class:done={m.char.trim()}
							style:left={`${m.x}%`}
							style:top={`${m.y}%`}
							title={m.char || '?'}
							role="button"
							tabindex="0"
							onclick={(e) => { e.stopPropagation(); removeMarker(i, m.id); }}
						>
							{idx + 1}
						</div>
					{/each}
				</div>
				<div class="photo-sidebar">
					{#each markers as m, idx (m.id)}
						<div class="marker-input">
							<span class="num" class:done={m.char.trim()}>{idx + 1}</span>
							<input
								type="text"
								value={m.char}
								placeholder="Name..."
								autocomplete="off"
								spellcheck="false"
								oninput={(e) => updateChar(i, m.id, (e.target as HTMLInputElement).value)}
							/>
							<button class="del" onclick={() => removeMarker(i, m.id)}>✕</button>
						</div>
					{/each}
				</div>
			</div>
		{/each}
	</div>
{/if}

{#if pendingCtx}
	<div class="ctx-menu show" style:left={`${pendingCtx.left}px`} style:top={`${pendingCtx.top}px`}>
		<span class="ctx-pos">photo_{String(pendingCtx.photoIdx).padStart(2,'0')} @ {pendingCtx.x.toFixed(1)}%, {pendingCtx.y.toFixed(1)}%</span>
		<div>
			{#if getMarkers(pendingCtx.photoIdx).filter((m) => m.char.trim()).length}
				<button class="ctx-item done-item" disabled>Already: {getMarkers(pendingCtx.photoIdx).filter((m) => m.char.trim()).map((m) => m.char.trim()).join(', ')}</button>
				<hr class="ctx-item divider" />
			{/if}
			{#each TAGGER_CHARS as c}
				{@const assigned = getMarkers(pendingCtx.photoIdx).some((m) => m.char.trim() === c)}
				<button class="ctx-item" disabled={assigned} style:opacity={assigned ? 0.3 : 1} onclick={() => pickChar(c)}>{c}</button>
			{/each}
			<hr class="ctx-item divider" />
			<button class="ctx-item" style:color="var(--muted)" onclick={closeCtx}>Cancel</button>
		</div>
	</div>
{/if}

<Lightbox bind:src={lightboxSrc} />

<style>
	h1 { font-size: 1.5rem; margin-bottom: 2px; padding: 20px 20px 0; }
	.subtitle { color: var(--muted); font-size: 0.82rem; margin-bottom: 14px; padding: 0 20px; }
	.toolbar { display: flex; gap: 8px; align-items: center; margin: 0 20px 12px; flex-wrap: wrap; }
	.progress { color: var(--muted); font-size: 0.82rem; margin-left: auto; }
	.photo-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
		gap: 16px;
		padding: 0 20px 20px;
	}
	.photo-card { background: var(--card); border: 1px solid var(--border); border-radius: 10px; overflow: hidden; transition: 0.15s; }
	.photo-card.filled { border-color: var(--green); }
	.photo-wrap { position: relative; cursor: crosshair; height: 270px; overflow: hidden; background: #111; }
	.photo-wrap img { width: 100%; height: 100%; object-fit: cover; display: block; pointer-events: none; }
	.marker {
		position: absolute; width: 28px; height: 28px; border-radius: 50%;
		background: rgba(233,69,96,0.8); border: 2px solid #fff;
		display: flex; justify-content: center; align-items: center;
		font-size: 0.7rem; font-weight: 700; color: #fff; cursor: pointer;
		transform: translate(-50%, -50%);
		box-shadow: 0 1px 6px rgba(0,0,0,0.4);
		transition: 0.12s; z-index: 10; user-select: none;
	}
	.marker.done { background: rgba(46,204,113,0.85); }
	.marker:hover { transform: translate(-50%, -50%) scale(1.3); z-index: 20; }
	.ctx-menu {
		position: fixed; background: #1e2a4a; border: 1px solid var(--border);
		border-radius: 8px; padding: 4px; box-shadow: 0 8px 24px rgba(0,0,0,0.5);
		z-index: 500; min-width: 160px; max-height: 320px; overflow-y: auto;
	}
	.ctx-item {
		display: block; width: 100%; padding: 6px 12px; border: none; background: none;
		color: var(--text); font-size: 0.82rem; text-align: left; cursor: pointer;
		border-radius: 4px; transition: 0.08s;
	}
	.ctx-item:hover:not(:disabled) { background: rgba(233,69,96,0.2); color: #fff; }
	.ctx-item.divider { border-top: 1px solid rgba(255,255,255,0.06); margin: 3px 0; padding: 0; height: 0; cursor: default; }
	.ctx-item.done-item { color: var(--green); font-size: 0.75rem; text-align: center; }
	.ctx-item.done-item:hover { background: none; cursor: default; color: var(--muted); }
	.ctx-pos { display: block; text-align: center; font-size: 0.65rem; color: var(--muted); padding: 2px 0 4px; border-bottom: 1px solid rgba(255,255,255,0.06); margin-bottom: 4px; }
	.photo-sidebar { padding: 6px 10px 8px; }
	.marker-input { display: flex; align-items: center; gap: 5px; margin-bottom: 2px; }
	.marker-input .num { width: 20px; height: 20px; border-radius: 50%; background: var(--accent); color: #fff; display: flex; justify-content: center; align-items: center; font-size: 0.65rem; font-weight: 700; flex-shrink: 0; }
	.marker-input .num.done { background: var(--green); }
	.marker-input input { flex: 1; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08); border-radius: 4px; color: var(--text); padding: 3px 6px; font-size: 0.76rem; outline: none; }
	.marker-input input:focus { border-color: var(--accent); }
	.marker-input .del { background: none; border: none; color: #555; cursor: pointer; font-size: 0.8rem; padding: 0 2px; line-height: 1; }
	.marker-input .del:hover { color: var(--accent); }
	.empty-state { padding: 60px 20px; color: var(--muted); text-align: center; }
	@media (max-width: 600px) { .photo-grid { grid-template-columns: 1fr; } .photo-wrap { height: 200px; } }
</style>
