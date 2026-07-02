<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import { CHARACTERS, refPrefix, fallbackRefUrls, type Character } from '$lib/characters';
	import { toast, fileToDataUrl } from '$lib/toast';
	import Lightbox from '$lib/Lightbox.svelte';
	import { page } from '$app/state';

	let refsByChar = $state<Record<string, string[]>>({});
	let refsLoaded = $state(false);
	let activeIdx = $state(0);
	let lightboxSrc = $state('');
	let recropping = $state(false);
	let uploading = $state<string | null>(null);

	const active = $derived(CHARACTERS[activeIdx] as Character | undefined);

	function refUrlsFor(c: Character): string[] {
		return refsByChar[c.name] ?? fallbackRefUrls(c.name, 24);
	}

	function firstRef(c: Character): string {
		return refsByChar[c.name]?.[0] ?? `character-references/${refPrefix(c.name)}01.jpg`;
	}

	function fallbackThumb(): string {
		return `data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect fill='#333' width='32' height='32'/><text x='16' y='20' font-size='12' text-anchor='middle' fill='#888'>?</text></svg>`;
	}

	function fallbackBig(): string {
		return `data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 400'><rect fill='#222' width='400' height='400'/><text x='200' y='210' font-size='24' text-anchor='middle' fill='#888'>no refs</text></svg>`;
	}

	function statusClass(c: Character): string { return c.status === 'shot' ? '' : 'ai'; }
	function statusText(c: Character): string { return c.status === 'shot' ? '✅ Shot footage exists' : '🤖 AI generation needed'; }
	function sceneIcon(s: 'shot' | 'missing' | 'ai'): string { return s === 'shot' ? '✅' : '🆕'; }

	async function loadRefs() {
		try {
			const d = await api.getReferences();
			refsByChar = d.references ?? {};
		} catch (e) {
			console.warn('refs load failed', e);
			toast('⚠️ Could not load reference list — using fallback names', 'err');
			refsByChar = {};
		} finally {
			refsLoaded = true;
		}
	}

	async function recrop() {
		recropping = true;
		try {
			const d = await api.recrop();
			toast(`✅ Recropped: ${d.count} faces`);
			await loadRefs();
		} catch (e: any) {
			toast(`❌ Recrop failed: ${e.message}`, 'err');
		} finally {
			recropping = false;
		}
	}

	function pickUpload(name: string) {
		uploading = name;
		queueMicrotask(() => {
			const inp = document.getElementById('upload-input') as HTMLInputElement | null;
			inp?.click();
		});
	}

	async function uploadReference(evt: Event) {
		const inp = evt.currentTarget as HTMLInputElement;
		const file = inp.files?.[0];
		inp.value = '';
		const charName = uploading;
		uploading = null;
		if (!file || !charName) return;
		try {
			const dataUrl = await fileToDataUrl(file);
			const d = await api.uploadReference(charName, dataUrl, file.name);
			refsByChar = d.references ?? refsByChar;
			toast(`✅ Added face reference: ${d.file}`);
		} catch (e: any) {
			toast(`❌ ${e.message}`, 'err');
		}
	}

	onMount(async () => {
		await loadRefs();
		// Honor ?char=… from dashboard links
		const wanted = page.url.searchParams.get('char');
		if (wanted) {
			const idx = CHARACTERS.findIndex(c => c.name === wanted);
			if (idx >= 0) activeIdx = idx;
		}
	});
</script>

<div class="layout">
	<aside class="sidebar">
		<h1><span>🔥</span> FD3 Cast</h1>
		{#each CHARACTERS as c, i}
			<button class="char-btn" class:active={i === activeIdx} onclick={() => (activeIdx = i)}>
				<img class="thumb" src={firstRef(c)} alt={c.name} onerror={(e) => ((e.currentTarget as HTMLImageElement).src = fallbackThumb())} />
				<span>{c.name}</span>
				<span class="badge">{c.dialogue.length}</span>
			</button>
		{/each}
	</aside>

	<main class="main">
		{#if !refsLoaded}
			<div class="empty-state"><p>Loading references…</p></div>
		{:else if !active}
			<div class="empty-state">
				<h2>🔥 Flaming Dragon 3</h2>
				<p>Select a character from the sidebar</p>
			</div>
		{:else}
			<h2>🔥 {active.name} <span class="status-tag {statusClass(active)}">{statusText(active)}</span></h2>
			<div class="role">{active.role}</div>

			<div class="panel-grid">
				<div class="panel full">
					<h3>👤 Face References
						<span class="actions">
							<button class="btn btn-sm" onclick={() => pickUpload(active.name)} disabled={uploading === active.name}>+ Upload Ref</button>
							<button class="btn btn-sm btn-recrop" onclick={recrop} disabled={recropping}>{recropping ? '↻ Cropping…' : '↻ Refresh Crops'}</button>
						</span>
					</h3>
					<div class="face-grid">
						{#each refUrlsFor(active) as ref}
							<img src={ref} alt="" onerror={(e) => ((e.currentTarget as HTMLImageElement).style.display = 'none')} onclick={() => (lightboxSrc = ref)} />
						{/each}
					</div>
				</div>

				<div class="panel">
					<h3>👕 Costume & Details</h3>
					<div class="detail-row"><span class="label">Costume:</span><span class="value">{active.costume}</span></div>
					<div class="detail-row"><span class="label">Status:</span><span class="value">{statusText(active)}</span></div>
				</div>

				<div class="panel">
					<h3>🎬 Appears In</h3>
					<div class="scene-tags">
						{#each active.scenes as [name, status]}
							<span class="scene-tag {status}">{sceneIcon(status)} {name}</span>
						{/each}
					</div>
				</div>

				<div class="panel full">
					<h3>💬 Dialogue ({active.dialogue.length} lines)</h3>
					{#each active.dialogue as line}
						<div class="dialogue-line"><span class="speaker">{active.name}</span><br />{line}</div>
					{/each}
				</div>
			</div>
		{/if}
	</main>
</div>

<input id="upload-input" class="ref-upload" type="file" accept="image/jpeg,image/png,image/webp" onchange={uploadReference} />

<Lightbox bind:src={lightboxSrc} />

<style>
	.layout { display: flex; height: 100vh; overflow: hidden; }
	.sidebar {
		width: 220px;
		background: var(--card);
		border-right: 1px solid var(--border);
		padding: 16px 0;
		overflow-y: auto;
		flex-shrink: 0;
	}
	.sidebar h1 {
		font-size: 1rem;
		padding: 0 14px 12px;
		border-bottom: 1px solid var(--border);
		margin-bottom: 8px;
		display: flex;
		align-items: center;
		gap: 6px;
	}
	.sidebar h1 span { color: var(--accent); }
	.char-btn {
		display: flex;
		align-items: center;
		gap: 10px;
		width: 100%;
		padding: 8px 14px;
		border: none;
		background: none;
		color: var(--text);
		cursor: pointer;
		font-size: 0.82rem;
		text-align: left;
		transition: 0.1s;
		border-left: 3px solid transparent;
	}
	.char-btn:hover { background: rgba(233,69,96,0.08); }
	.char-btn.active { background: rgba(233,69,96,0.15); border-left-color: var(--accent); color: #fff; }
	.char-btn .thumb { width: 32px; height: 32px; border-radius: 50%; object-fit: cover; background: #222; flex-shrink: 0; }
	.char-btn .badge { margin-left: auto; font-size: 0.65rem; color: var(--muted); background: rgba(255,255,255,0.05); padding: 1px 6px; border-radius: 8px; }

	.main { flex: 1; overflow-y: auto; padding: 24px 32px; }
	.main h2 { font-size: 1.6rem; margin-bottom: 2px; display: flex; align-items: center; gap: 10px; }
	.main .role { color: var(--muted); font-size: 0.85rem; margin-bottom: 16px; }
	.status-tag { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.72rem; background: rgba(46,204,113,0.15); color: var(--green); margin-left: 8px; }
	.status-tag.ai { background: rgba(233,69,96,0.15); color: var(--accent); }

	.panel-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 16px; }
	.panel { background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 16px; }
	.panel.full { grid-column: 1 / -1; }
	.panel h3 { font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.5px; color: var(--accent); margin-bottom: 10px; display: flex; align-items: center; gap: 6px; }
	.actions { margin-left: auto; display: flex; gap: 6px; }

	.face-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(90px, 1fr)); gap: 8px; }
	.face-grid img { width: 100%; aspect-ratio: 3/4; object-fit: cover; border-radius: 6px; border: 1px solid var(--border); cursor: pointer; transition: 0.15s; }
	.face-grid img:hover { border-color: var(--accent); transform: scale(1.05); }

	.detail-row { display: flex; gap: 8px; margin-bottom: 8px; font-size: 0.85rem; }
	.detail-row .label { color: var(--muted); min-width: 80px; flex-shrink: 0; font-size: 0.78rem; }
	.detail-row .value { color: var(--text); }

	.dialogue-line { padding: 6px 10px; margin-bottom: 4px; border-left: 2px solid var(--border); font-size: 0.85rem; line-height: 1.4; transition: 0.1s; }
	.dialogue-line:hover { border-left-color: var(--accent); background: rgba(233,69,96,0.04); }
	.dialogue-line .speaker { font-weight: 600; color: var(--accent); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.3px; }

	.scene-tags { display: flex; flex-wrap: wrap; gap: 4px; }
	.scene-tag { padding: 2px 8px; border-radius: 4px; font-size: 0.72rem; background: rgba(255,255,255,0.06); color: var(--muted); }
	.scene-tag.shot { background: rgba(46,204,113,0.1); color: var(--green); }
	.scene-tag.missing { background: rgba(233,69,96,0.1); color: var(--accent); }

	.empty-state { text-align: center; padding: 60px 20px; color: var(--muted); }
	.empty-state h2 { font-size: 2rem; margin-bottom: 8px; color: var(--accent); }
	.empty-state p { font-size: 0.9rem; }

	.ref-upload { display: none; }

	@media (max-width: 700px) {
		.layout { flex-direction: column; }
		.sidebar { width: 100%; height: auto; max-height: 150px; border-right: none; border-bottom: 1px solid var(--border); }
		.panel-grid { grid-template-columns: 1fr; }
	}
</style>
