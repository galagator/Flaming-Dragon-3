<script lang="ts">
	import { onMount } from 'svelte';
	import { toast } from '$lib/toast';

	type Chunk = {
		file: string;
		scene: string;
		start: number;
		end: number;
		chunk_duration: number;
		speaker: string | null;
		overlap_seconds?: number;
		url: string;
		exists: boolean;
		assigned: string | null;
	};

	let chunks = $state<Chunk[]>([]);
	let characters = $state<string[]>([]);
	let summary = $state<Record<string, number>>({});
	let loading = $state(true);
	let dirty = $state(false);
	let saving = $state(false);

	// Filters
	let filterSpeaker = $state<string>('all');
	let filterAssigned = $state<'all' | 'unassigned' | 'assigned'>('all');
	let searchTerm = $state('');

	// Currently playing audio (so we can stop it when another starts)
	let currentAudio: HTMLAudioElement | null = null;

	// Local edit buffer — { file: character | null }
	// Track what the user has changed locally (not yet saved)
	let localEdits = $state<Record<string, string | null>>({});

	function effectiveAssigned(c: Chunk): string | null {
		// Local edit overrides server assignment
		if (Object.prototype.hasOwnProperty.call(localEdits, c.file)) {
			return localEdits[c.file];
		}
		return c.assigned;
	}

	function playChunk(c: Chunk) {
		if (currentAudio) {
			currentAudio.pause();
			currentAudio = null;
		}
		const audio = new Audio(c.url);
		audio.play().catch((e) => toast(`❌ Audio failed: ${e.message}`, 'err'));
		currentAudio = audio;
		audio.onended = () => {
			if (currentAudio === audio) currentAudio = null;
		};
	}

	function assignChunk(c: Chunk, character: string | null) {
		localEdits = { ...localEdits, [c.file]: character };
		dirty = true;
		// Recompute summary in real time
		summary = { ...summary };
		// Subtract old duration from old character's total
		const oldAssigned = c.assigned;
		if (oldAssigned && summary[oldAssigned] !== undefined) {
			summary[oldAssigned] = Math.max(0, (summary[oldAssigned] || 0) - (c.chunk_duration || 0));
		}
		// Add new duration to new character's total
		if (character && summary[character] !== undefined) {
			summary[character] = (summary[character] || 0) + (c.chunk_duration || 0);
		}
	}

	async function saveAll() {
		if (!dirty || saving) return;
		saving = true;
		try {
			const r = await fetch('/api/voice-assign', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ assignments: localEdits }),
			});
			if (!r.ok) throw new Error(`HTTP ${r.status}`);
			const d = await r.json();
			toast(`✅ Saved ${d.saved} assignments`);
			// Apply local edits to the chunks array so server state matches
			chunks = chunks.map((c) => {
				if (Object.prototype.hasOwnProperty.call(localEdits, c.file)) {
					return { ...c, assigned: localEdits[c.file] };
				}
				return c;
			});
			localEdits = {};
			dirty = false;
		} catch (e: any) {
			toast(`❌ Save failed: ${e.message}`, 'err');
		} finally {
			saving = false;
		}
	}

	async function loadChunks() {
		loading = true;
		try {
			const r = await fetch('/api/voice-chunks');
			if (!r.ok) throw new Error(`HTTP ${r.status}`);
			const d = await r.json();
			chunks = d.chunks;
			characters = d.characters;
			summary = d.summary;
			if (d.error) toast(`⚠️ ${d.error}`, 'err');
		} catch (e: any) {
			toast(`❌ Load failed: ${e.message}`, 'err');
		} finally {
			loading = false;
		}
	}

	function onKey(e: KeyboardEvent) {
		// Number keys 1-9: assign currently-playing chunk to Nth character
		// But this would require tracking "currently playing" — skip for now
		// Ctrl/Cmd+S to save
		if ((e.ctrlKey || e.metaKey) && e.key === 's') {
			e.preventDefault();
			saveAll();
		}
	}

	function filteredChunks(): Chunk[] {
		return chunks.filter((c) => {
			if (filterSpeaker !== 'all' && c.speaker !== filterSpeaker) return false;
			if (filterAssigned === 'unassigned' && effectiveAssigned(c) !== null) return false;
			if (filterAssigned === 'assigned' && effectiveAssigned(c) === null) return false;
			if (searchTerm && !c.file.toLowerCase().includes(searchTerm.toLowerCase()) && !c.scene.toLowerCase().includes(searchTerm.toLowerCase())) return false;
			return true;
		});
	}

	function speakerOptions(): string[] {
		const set = new Set<string>();
		for (const c of chunks) if (c.speaker) set.add(c.speaker);
		return Array.from(set).sort();
	}

	function fmtSec(s: number): string {
		if (s >= 60) return `${Math.floor(s / 60)}m ${(s % 60).toFixed(0)}s`;
		return `${s.toFixed(1)}s`;
	}

	function sortCharacters(a: string, b: string): number {
		// Sort by total seconds desc, then alphabetical
		const sa = summary[a] || 0;
		const sb = summary[b] || 0;
		if (sb !== sa) return sb - sa;
		return a.localeCompare(b);
	}

	onMount(() => {
		loadChunks();
		window.addEventListener('keydown', onKey);
		return () => {
			window.removeEventListener('keydown', onKey);
			if (currentAudio) currentAudio.pause();
		};
	});

	// Derived: count unassigned in current filter
	let unassignedInFilter = $derived(filteredChunks().filter((c) => effectiveAssigned(c) === null).length);
	let totalInFilter = $derived(filteredChunks().length);
</script>

<div class="layout">
	<aside class="sidebar">
		<h1><span>🎤</span> Voice Tagger</h1>
		<div class="meta">
			{chunks.length} chunks loaded
			{#if dirty}<span class="dirty">• unsaved</span>{/if}
		</div>

		<button class="btn save-btn" onclick={saveAll} disabled={!dirty || saving}>
			{saving ? 'Saving…' : dirty ? '💾 Save assignments (⌘S)' : '✓ All saved'}
		</button>

		<h2>Per character</h2>
		<div class="char-list">
			{#each [...characters].sort(sortCharacters) as ch}
				<div class="char-row" class:has-data={(summary[ch] || 0) > 0}>
					<span class="char-name">{ch}</span>
					<span class="char-secs">{fmtSec(summary[ch] || 0)}</span>
				</div>
			{/each}
		</div>

		<h2>Filters</h2>
		<label class="filter-label">
			Speaker cluster
			<select bind:value={filterSpeaker}>
				<option value="all">All</option>
				{#each speakerOptions() as sp}
					<option value={sp}>{sp}</option>
				{/each}
			</select>
		</label>
		<label class="filter-label">
			Assignment
			<select bind:value={filterAssigned}>
				<option value="all">All chunks</option>
				<option value="unassigned">Unassigned only</option>
				<option value="assigned">Assigned only</option>
			</select>
		</label>
		<label class="filter-label">
			Search
			<input type="text" placeholder="filename or scene…" bind:value={searchTerm} />
		</label>

		<div class="legend">
			{totalInFilter} shown • {unassignedInFilter} unassigned
		</div>
	</aside>

	<main class="main">
		{#if loading}
			<div class="empty"><p>Loading voice chunks…</p></div>
		{:else if chunks.length === 0}
			<div class="empty">
				<h2>No voice chunks</h2>
				<p>Run the voice extraction pipeline first:</p>
				<pre>bash voice/extract-raw.sh
python3 voice/extract-chunks.py
python3 voice/extract-gkd-chunks.py
python3 voice/diarize-chunks.py</pre>
			</div>
		{:else}
			<div class="chunk-list">
				{#each filteredChunks() as c (c.file)}
					{@const assigned = effectiveAssigned(c)}
					<div class="chunk-card" class:assigned={assigned !== null} data-speaker={c.speaker}>
						<div class="chunk-head">
							<button class="play-btn" onclick={() => playChunk(c)} title="Play">▶</button>
							<div class="chunk-info">
								<div class="chunk-file">{c.file}</div>
								<div class="chunk-meta">
									<span class="meta-tag">{c.scene}</span>
									<span class="meta-tag">{c.start.toFixed(1)}s → {c.end.toFixed(1)}s</span>
									<span class="meta-tag">{c.chunk_duration.toFixed(1)}s</span>
									{#if c.speaker}
										<span class="meta-tag speaker-tag">{c.speaker}</span>
									{:else}
										<span class="meta-tag muted">no speaker</span>
									{/if}
								</div>
							</div>
							<div class="chunk-picker">
								<select
									value={assigned ?? ''}
									onchange={(e) => {
										const v = (e.currentTarget as HTMLSelectElement).value;
										assignChunk(c, v === '' ? null : v);
									}}
								>
									<option value="">— unassigned —</option>
									{#each characters as ch}
										<option value={ch}>{ch}</option>
									{/each}
								</select>
							</div>
						</div>
					</div>
				{/each}
			</div>
		{/if}
	</main>
</div>

<style>
	.layout { display: flex; height: 100vh; overflow: hidden; }
	.sidebar {
		width: 260px;
		background: var(--card);
		border-right: 1px solid var(--border);
		padding: 16px;
		overflow-y: auto;
		flex-shrink: 0;
	}
	.sidebar h1 { font-size: 1rem; margin-bottom: 8px; display: flex; align-items: center; gap: 6px; }
	.sidebar h1 span { color: var(--accent); }
	.sidebar h2 {
		font-size: 0.7rem;
		text-transform: uppercase;
		letter-spacing: 0.5px;
		color: var(--muted);
		margin: 16px 0 8px;
	}
	.meta { color: var(--muted); font-size: 0.78rem; margin-bottom: 12px; }
	.dirty { color: var(--yellow); font-weight: 600; }

	.save-btn {
		width: 100%;
		justify-content: center;
		padding: 10px;
		font-size: 0.85rem;
	}
	.save-btn:disabled { opacity: 0.5; cursor: default; }

	.char-list { display: flex; flex-direction: column; gap: 2px; }
	.char-row {
		display: flex;
		justify-content: space-between;
		padding: 4px 8px;
		border-radius: 4px;
		font-size: 0.82rem;
	}
	.char-row.has-data { background: rgba(46,204,113,0.1); }
	.char-name { color: var(--text); }
	.char-secs { color: var(--muted); font-variant-numeric: tabular-nums; font-size: 0.78rem; }
	.char-row.has-data .char-secs { color: var(--green); font-weight: 600; }

	.filter-label {
		display: block;
		font-size: 0.75rem;
		color: var(--muted);
		margin-bottom: 8px;
	}
	.filter-label select, .filter-label input {
		display: block;
		width: 100%;
		margin-top: 4px;
		padding: 4px 6px;
		background: var(--bg);
		color: var(--text);
		border: 1px solid var(--border);
		border-radius: 4px;
		font-size: 0.85rem;
	}
	.legend { color: var(--muted); font-size: 0.72rem; margin-top: 8px; }

	.main { flex: 1; padding: 16px; overflow-y: auto; }
	.empty { text-align: center; padding: 60px 20px; color: var(--muted); }
	.empty h2 { font-size: 1.5rem; margin-bottom: 12px; color: var(--accent); }
	.empty pre {
		display: inline-block;
		text-align: left;
		background: var(--bg);
		padding: 12px 16px;
		border-radius: 6px;
		font-size: 0.85rem;
		color: var(--text);
		margin-top: 8px;
	}

	.chunk-list { display: flex; flex-direction: column; gap: 8px; }
	.chunk-card {
		background: var(--card);
		border: 1px solid var(--border);
		border-radius: 8px;
		padding: 10px 12px;
		transition: 0.15s;
	}
	.chunk-card.assigned { border-color: var(--green); background: rgba(46,204,113,0.04); }
	.chunk-head { display: flex; align-items: center; gap: 12px; }

	.play-btn {
		flex-shrink: 0;
		width: 36px;
		height: 36px;
		border-radius: 50%;
		background: var(--accent);
		color: #fff;
		border: none;
		cursor: pointer;
		font-size: 0.9rem;
		display: flex;
		align-items: center;
		justify-content: center;
	}
	.play-btn:hover { transform: scale(1.05); }

	.chunk-info { flex: 1; min-width: 0; }
	.chunk-file { font-family: ui-monospace, monospace; font-size: 0.82rem; color: var(--text); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
	.chunk-meta { display: flex; gap: 6px; margin-top: 4px; flex-wrap: wrap; }
	.meta-tag {
		font-size: 0.7rem;
		padding: 1px 6px;
		background: rgba(255,255,255,0.06);
		color: var(--muted);
		border-radius: 3px;
	}
	.meta-tag.speaker-tag { background: rgba(233,69,96,0.15); color: var(--accent); }
	.meta-tag.muted { opacity: 0.5; }

	.chunk-picker select {
		padding: 6px 8px;
		background: var(--bg);
		color: var(--text);
		border: 1px solid var(--border);
		border-radius: 4px;
		font-size: 0.85rem;
		min-width: 140px;
	}
</style>
