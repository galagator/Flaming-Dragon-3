<script lang="ts">
	import { onMount, tick } from 'svelte';
	import { api } from '$lib/api';
	import { toast } from '$lib/toast';

	type Panel = { panel: number; file: string; src: string; captureSec: number | null };
	type Scene = { id: string; title: string; shot: boolean; duration: number; video: string | null; panels: Panel[] };
	type VoiceLine = { index: number; text: string; file: string; url: string; status: string };
	type VoiceChar = { name: string; voice_id: string | null; lineCount: number; lines: VoiceLine[] };

	type ScriptLine = {
		id: number;
		kind: 'scene' | 'speaker' | 'line' | 'stage' | 'blank' | 'heading' | 'comment';
		raw: string;
		speaker?: string;
		text?: string;
		sceneId?: string;
		voiceLine?: VoiceLine;
	};

	let scenes = $state<Scene[]>([]);
	let voiceByChar = $state<Record<string, VoiceChar>>({});
	let scriptLines = $state<ScriptLine[]>([]);
	let loaded = $state(false);

	// Layout state
	let activePanelIdx = $state(0); // global panel index across all scenes
	let activeSceneIdx = $state(0);
	let stripEl: HTMLElement | undefined = $state();
	let lightboxSrc = $state<string | null>(null);

	// Notes state
	type NoteEntry = { text: string; updatedAt: string };
	let notes = $state<Record<string, NoteEntry>>({});
	let noteModal = $state<{ sceneId: string; file: string; text: string; saving: boolean; dirty: boolean } | null>(null);

	// Audio state
	let audio: HTMLAudioElement | null = $state(null);
	let playingId = $state<number | null>(null);

	// ---- derived: flat panel list with scene + cumulative timing ----
	type Flat = {
		panel: Panel;
		scene: Scene;
		sceneIdx: number;
		globalIdx: number;
		startSec: number; // within scene
		sceneStartSec: number; // cumulative across all scenes
		midSec: number; // midpoint within scene (for playhead alignment)
	};
	const flat = $derived.by<Flat[]>(() => {
		const out: Flat[] = [];
		let global = 0;
		let cumulative = 0;
		for (let s = 0; s < scenes.length; s++) {
			const sc = scenes[s];
			const count = Math.max(1, sc.panels.length || 1);
			const per = sc.duration / count;
			const labels = sc.panels.length;
			if (labels === 0) {
				// Empty scene still gets a slot in the timeline
				out.push({
					panel: { panel: 0, file: '', src: '', captureSec: null },
					scene: sc,
					sceneIdx: s,
					globalIdx: global++,
					startSec: 0,
					sceneStartSec: cumulative,
					midSec: cumulative + sc.duration / 2
				});
				cumulative += sc.duration;
				continue;
			}
			for (let p = 0; p < labels; p++) {
				const startSec = p * per;
				out.push({
					panel: sc.panels[p],
					scene: sc,
					sceneIdx: s,
					globalIdx: global++,
					startSec,
					sceneStartSec: cumulative,
					midSec: cumulative + startSec + per / 2
				});
			}
			cumulative += sc.duration;
		}
		return out;
	});

	const totalDuration = $derived(flat.length ? flat[flat.length - 1].sceneStartSec + (scenes[scenes.length - 1]?.duration || 0) : 0);
	const playheadSec = $derived(flat[activePanelIdx]?.midSec ?? 0);
	const activeScene = $derived(scenes[activeSceneIdx]);
	const activeFlat = $derived(flat[activePanelIdx]);

	function fmtTime(sec: number): string {
		sec = Math.max(0, Math.floor(sec));
		const m = Math.floor(sec / 60);
		const s = sec % 60;
		return `${m}:${String(s).padStart(2, '0')}`;
	}

	function setActivePanel(globalIdx: number) {
		activePanelIdx = globalIdx;
		const f = flat[globalIdx];
		if (f) activeSceneIdx = f.sceneIdx;
	}

	function panelLabel(p: Panel, scene: Scene): string {
		if (p.file === '') return `${scene.id} (no panels yet)`;
		const sec = p.captureSec != null ? `${fmtTime(p.captureSec)}` : `#${p.panel}`;
		return `${scene.id} · ${sec}`;
	}

	// ---- script parsing ----
	function parseScript(md: string): ScriptLine[] {
		const lines = md.split(/\r?\n/);
		const out: ScriptLine[] = [];
		let id = 0;
		let currentSceneId: string | undefined;
		const normChar = (s: string) => s.trim().replace(/\s+/g, ' ');
		const canonical = (s: string): string => {
			// Map script speaker tags to canonical character names.
			// Handled case-insensitively: script often uses ALL CAPS speaker tags.
			const norm = s.toUpperCase();
			const map: Record<string, string> = {
				'TONY': 'Tony',
				'YAKE-OH': 'Yake-oh',
				'YAKEOH': 'Yake-oh',
				'ERB DEAN': 'Erb Dean',
				'ERB DEAN (SIC)': 'Erb Dean',
				'MAMA': 'MAMA',
				'TRUBBLE': 'Trubble',
				'SLARTH': 'Slarth',
				'JI-LAN': 'Ji-lan',
				'JI-LAN (OFF CAMERA)': 'Ji-lan',
				'JI-LAN (ON PHONE)': 'Ji-lan',
				'JI-LAN (TO TONY)': 'Ji-lan',
				'JI-LAN (TO MAMA)': 'Ji-lan',
				'ZOH-BAGGO': 'Zoh-baggo',
				'TK-MAXX': 'TK-Maxx',
				'JASMINE': 'Jasmine',
				'WOMAN 1': 'WOMAN 1',
				'WOMAN 2': 'WOMAN 2',
				'ANNOUNCER': 'ANNOUNCER',
				'BRUCE LEE': 'Bruce Lee',
				'JACKIE CHAN': 'Jackie Chan',
				'STEVEN SEAGAL': 'Steven Seagal',
				'YAKE-OH & ERB DEAN': 'Yake-oh & Erb Dean'
			};
			return map[norm] ?? s;
		};
		const sceneRe = /^##\s+(?:SCENE\s+)?(.+?)\s*$/i;
		const charLineRe = /^\*\*([^*]+?):\*\*\s*(.*)$/;
		const stageRe = /^\*([^*].*[^*])\*\s*$/;

		for (const raw of lines) {
			const trimmed = raw.trim();
			if (trimmed.startsWith('# FLAMING DRAGON 3') || trimmed.startsWith('**Written by') || trimmed.startsWith('**Contact') || /^---+$/.test(trimmed)) {
				out.push({ id: id++, kind: 'heading', raw });
				continue;
			}
			const sm = trimmed.match(sceneRe);
			if (sm && !trimmed.startsWith('# ')) {
				const title = sm[1].trim();
				// Pull a short id like "SCENE 1 — ..." → "1"
				const idm = title.match(/^SCENE\s+(\d+[A-Z]?)\b/i);
				currentSceneId = idm ? idm[1] : undefined;
				out.push({ id: id++, kind: 'scene', raw, sceneId: currentSceneId, text: title });
				continue;
			}
			if (trimmed.startsWith('**Characters:')) {
				out.push({ id: id++, kind: 'heading', raw });
				continue;
			}
			if (trimmed.startsWith('>')) {
				out.push({ id: id++, kind: 'comment', raw, sceneId: currentSceneId });
				continue;
			}
			if (trimmed === '') {
				out.push({ id: id++, kind: 'blank', raw });
				continue;
			}
			const cl = trimmed.match(charLineRe);
			if (cl) {
				const speakerRaw = normChar(cl[1]);
				const speaker = canonical(speakerRaw);
				const text = cl[2].trim();
				out.push({
					id: id++,
					kind: 'speaker',
					raw,
					speaker,
					text,
					sceneId: currentSceneId
				});
				continue;
			}
			const stg = trimmed.match(stageRe);
			if (stg) {
				out.push({ id: id++, kind: 'stage', raw, text: stg[1].trim(), sceneId: currentSceneId });
				continue;
			}
			// Plain descriptive line (e.g. "Tony's lounge room. The air...")
			out.push({ id: id++, kind: 'line', raw, text: trimmed, sceneId: currentSceneId });
		}
		return out;
	}

	function attachVoice(lines: ScriptLine[]) {
		// For each speaker line, try to match a voice line by character + text
		for (const ln of lines) {
			if (ln.kind !== 'speaker' || !ln.speaker || !ln.text) continue;
			const char = voiceByChar[ln.speaker];
			if (!char) continue;
			// Try normalized text match first
			const norm = (s: string) => s.toLowerCase().replace(/[^a-z0-9 ]+/g, '').replace(/\s+/g, ' ').trim();
			const target = norm(ln.text);
			let best: VoiceLine | null = null;
			let bestScore = 0;
			for (const vl of char.lines) {
				const cand = norm(vl.text);
				if (!cand) continue;
				if (cand === target) { best = vl; bestScore = 1; break; }
				// Substring/prefix match scoring
				if (cand.startsWith(target) || target.startsWith(cand)) {
					const score = Math.min(cand.length, target.length) / Math.max(cand.length, target.length);
					if (score > bestScore) { best = vl; bestScore = score; }
				}
			}
			ln.voiceLine = best ?? undefined;
		}
	}

	function playLine(ln: ScriptLine) {
		if (!ln.voiceLine) {
			toast('No voice line for that one', 'err');
			return;
		}
		// Stop any currently playing
		if (audio) {
			audio.pause();
			audio.currentTime = 0;
		}
		playingId = ln.id;
		audio = new Audio(ln.voiceLine.url);
		audio.onended = () => { playingId = null; };
		audio.onerror = () => { playingId = null; toast('Audio failed to load', 'err'); };
		audio.play().catch(() => { playingId = null; });
	}

	function stopAudio() {
		if (audio) { audio.pause(); audio.currentTime = 0; }
		playingId = null;
	}

	function jumpToScene(sceneId: string | undefined) {
		if (!sceneId) return;
		const idx = scenes.findIndex(s => s.id === sceneId);
		if (idx >= 0) {
			// Find the first flat panel for that scene
			const f = flat.find(p => p.sceneIdx === idx);
			if (f) {
				setActivePanel(f.globalIdx);
				scrollStripToActive();
			}
		}
	}

	async function scrollStripToActive() {
 	await tick();
 	const el = stripEl?.querySelector<HTMLElement>(`[data-global="${activePanelIdx}"]`);
 	if (el && stripEl) {
 		const left = el.offsetLeft - stripEl.clientWidth / 2 + el.clientWidth / 2;
 		stripEl.scrollTo({ left, behavior: 'smooth' });
 	}
 }

 // === Notes ===
 function noteKey(sceneId: string, file: string): string {
 	return `${sceneId}::${file}`;
 }
 function getNote(sceneId: string, file: string): NoteEntry | undefined {
 	return notes[noteKey(sceneId, file)];
 }
 function openNoteModal(sceneId: string, file: string) {
 	const existing = getNote(sceneId, file);
 	noteModal = { sceneId, file, text: existing?.text ?? '', saving: false, dirty: false };
 }
 function closeNoteModal() {
 	noteModal = null;
 }
 async function saveNoteModal() {
 	if (!noteModal) return;
 	const k = noteKey(noteModal.sceneId, noteModal.file);
 	const text = noteModal.text.trim();
 	noteModal.saving = true;
 	try {
 		const r = await api.saveStoryboardNotes({ [k]: text });
 		notes = r.notes;
 		noteModal.dirty = false;
 		toast(text ? `📝 Note saved for ${noteModal.sceneId} #${noteModal.file}` : `🗑️ Note cleared`);
 	} catch (e) {
 		console.error('save note failed', e);
 		toast('Failed to save note', 'err');
 	} finally {
 		if (noteModal) noteModal.saving = false;
 	}
 }
 function deleteNoteFromModal() {
 	if (!noteModal) return;
 	// Setting text to '' + saving will delete the note (server removes empty)
 	noteModal.text = '';
 	saveNoteModal().then(() => { if (noteModal) noteModal.dirty = false; });
 }

	function onStripWheel(e: WheelEvent) {
		// Translate vertical wheel into horizontal scroll (Premiere-style)
		if (Math.abs(e.deltaY) > Math.abs(e.deltaX) && stripEl) {
			stripEl.scrollLeft += e.deltaY;
			e.preventDefault();
		}
	}

	function onKey(e: KeyboardEvent) {
		if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
			// Inside an input/textarea, only handle Escape (to close modal)
			if (e.key === 'Escape') {
				if (noteModal) closeNoteModal();
				else if (lightboxSrc) lightboxSrc = null;
			}
			return;
		}
		if (e.key === 'ArrowLeft' && activePanelIdx > 0) setActivePanel(activePanelIdx - 1);
		else if (e.key === 'ArrowRight' && activePanelIdx < flat.length - 1) setActivePanel(activePanelIdx + 1);
		else if (e.key === ' ') { e.preventDefault(); stopAudio(); }
		else if (e.key === 'Escape') {
			if (noteModal) closeNoteModal();
			else if (lightboxSrc) lightboxSrc = null;
		}
	}

	onMount(async () => {
		try {
			const [sb, vc, md, ns] = await Promise.all([
				api.getStoryboard(),
				api.getVoice(),
				api.getScript(),
				api.getStoryboardNotes().catch(() => ({ ok: true, notes: {} }))
			]);
			scenes = sb.scenes ?? [];
			const byName: Record<string, VoiceChar> = {};
			for (const c of vc.characters ?? []) byName[c.name] = c;
			voiceByChar = byName;
			scriptLines = parseScript(md);
			attachVoice(scriptLines);
			notes = ns.notes ?? {};
			loaded = true;
			// Auto-scroll to first panel
			setTimeout(() => scrollStripToActive(), 50);
		} catch (e) {
			console.error('storyboard load failed', e);
			toast('Failed to load storyboard data', 'err');
		}
	});

	$effect(() => {
		// keep active scene in sync
		if (flat[activePanelIdx]) activeSceneIdx = flat[activePanelIdx].sceneIdx;
	});
</script>

<svelte:window on:keydown={onKey} />

<div class="page">
	<header class="topbar">
		<div class="title">🎬 Storyboard</div>
		<div class="meta">
			{#if loaded}
				<span class="chip">{scenes.length} scenes</span>
				<span class="chip">{flat.length} panels</span>
				<span class="chip">{fmtTime(totalDuration)} total</span>
				{#if activeScene}
					<span class="chip scene-name">Scene {activeScene.id} — {activeScene.title}</span>
					{#if activeScene.shot}<span class="chip green">shot</span>{:else}<span class="chip red">ai</span>{/if}
				{/if}
			{:else}
				<span class="chip muted">loading…</span>
			{/if}
		</div>
		<div class="legend">
			<span><kbd>←</kbd><kbd>→</kbd> step</span>
			<span><kbd>space</kbd> stop audio</span>
			<span><kbd>click</kbd> note · <kbd>dbl-click</kbd> zoom</span>
			<a href="/">← dashboard</a>
		</div>
	</header>

	<!-- TOP 2/3: horizontal storyboard strip -->
	<section class="panels" bind:this={stripEl} on:wheel={onStripWheel}>
		{#if !loaded}
			<div class="empty">Loading panels…</div>
		{:else}
			{#each scenes as sc, si (sc.id)}
				<div class="scene-block">
					<div class="scene-header">
						<span class="scene-id">{sc.id}</span>
						<span class="scene-title">{sc.title}</span>
						<span class="scene-meta">{sc.panels.length} panel{sc.panels.length === 1 ? '' : 's'} · {fmtTime(sc.duration)}</span>
					</div>
					<div class="scene-strip">
						{#if sc.video}
							{@const f = flat.find(fl => fl.sceneIdx === si)}
							{@const vidName = sc.video.split('/').pop() || 'video'}
							<button
								class="panel video-panel"
								class:active={f && f.globalIdx === activePanelIdx}
								data-global={f?.globalIdx ?? -1}
								on:click={() => { if (f) { setActivePanel(f.globalIdx); openNoteModal(sc.id, vidName); } }}
								title="Video: {sc.video}"
							>
								<video
									src={sc.video}
									muted
									playsinline
									preload="metadata"
									on:dblclick={() => (lightboxSrc = sc.video)}
								></video>
								<div class="panel-cap">
									<span class="pn">▶ video</span>
									<span class="ts">{vidName}</span>
								</div>
							</button>
						{/if}
						{#if sc.panels.length === 0 && !sc.video}
							<div class="panel-empty" data-global={flat.find(p => p.sceneIdx === si && p.panel.file === '')?.globalIdx ?? -1}>
								<div class="panel-img blank">🆕</div>
								<div class="panel-cap">no panels yet</div>
							</div>
						{:else}
							{#each sc.panels as p, pi (p.file)}
								{@const f = flat.find(fl => fl.sceneIdx === si && fl.panel.panel === p.panel)}
								{@const note = getNote(sc.id, p.file)}
								<button
									class="panel"
									class:active={f && f.globalIdx === activePanelIdx}
									class:has-note={!!note}
									data-global={f?.globalIdx ?? -1}
									on:click={() => { if (f) { setActivePanel(f.globalIdx); openNoteModal(sc.id, p.file); } }}
									title={panelLabel(p, sc)}
								>
									<img
										src={p.src}
										alt={panelLabel(p, sc)}
										loading="lazy"
										on:dblclick={() => (lightboxSrc = p.src)}
										on:error={(e) => { (e.currentTarget as HTMLImageElement).style.opacity = '0.2'; }}
									/>
									{#if note}
										<span class="note-badge" title={`Note: ${note.text.slice(0, 60)}${note.text.length > 60 ? '…' : ''}`}>📝</span>
									{/if}
									<div class="panel-cap">
										<span class="pn">#{p.panel}</span>
										{#if p.captureSec != null}
											<span class="ts">{fmtTime(p.captureSec)}</span>
										{/if}
									</div>
								</button>
							{/each}
						{/if}
					</div>
				</div>
			{/each}
		{/if}
	</section>

	<!-- MIDDLE: timer / ruler -->
	<section class="timer-bar">
		<div class="timer-readout">
			<span class="t-cur">{fmtTime(playheadSec)}</span>
			<span class="t-sep">/</span>
			<span class="t-tot">{fmtTime(totalDuration)}</span>
			{#if activeFlat}
				<span class="t-scene">· Scene {activeFlat.scene.id}</span>
			{/if}
		</div>
		<div class="ruler">
			{#if loaded}
				{#each flat as f, i (i)}
					<div
						class="ruler-tick"
						class:current={i === activePanelIdx}
						style:left={`${(f.midSec / Math.max(1, totalDuration)) * 100}%`}
						title={`${f.scene.id} · ${fmtTime(f.midSec)}`}
						on:click={() => setActivePanel(i)}
						role="button"
						tabindex="-1"
					></div>
				{/each}
				<div
					class="playhead"
					style:left={`${(playheadSec / Math.max(1, totalDuration)) * 100}%`}
				></div>
			{/if}
		</div>
		<div class="timer-actions">
			<button class="btn btn-sm btn-outline" on:click={() => activePanelIdx > 0 && setActivePanel(activePanelIdx - 1)}>◀ prev</button>
			<button class="btn btn-sm" on:click={scrollStripToActive}>center</button>
			<button class="btn btn-sm btn-outline" on:click={() => activePanelIdx < flat.length - 1 && setActivePanel(activePanelIdx + 1)}>next ▶</button>
		</div>
	</section>

	<!-- BOTTOM 1/3: script -->
	<section class="script">
		<div class="script-head">
			<div class="script-title">📜 FD3 Script</div>
			<div class="script-stats">
				{#if loaded}
					<span class="chip">{scriptLines.length} lines</span>
					<span class="chip">{scriptLines.filter(l => l.voiceLine).length} with voice</span>
				{/if}
			</div>
		</div>
		<div class="script-body">
			{#if !loaded}
				<div class="empty">Loading script…</div>
			{:else}
				{#each scriptLines as ln (ln.id)}
					{#if ln.kind === 'heading'}
						<div class="ln heading">{ln.raw}</div>
					{:else if ln.kind === 'scene'}
						<button
							class="ln scene"
							on:click={() => jumpToScene(ln.sceneId)}
							title="Jump to storyboard scene {ln.sceneId}"
						>
							{ln.raw}
						</button>
					{:else if ln.kind === 'comment'}
						<div class="ln comment">{ln.raw}</div>
					{:else if ln.kind === 'stage'}
						<div class="ln stage"><em>· {ln.text} ·</em></div>
					{:else if ln.kind === 'speaker'}
						<button
							class="ln speaker"
							class:playing={playingId === ln.id}
							class:has-voice={!!ln.voiceLine}
							on:click={() => playLine(ln)}
							disabled={!ln.voiceLine}
							title={ln.voiceLine ? `Play ${ln.speaker}: ${ln.voiceLine.file}` : `No voice line generated for ${ln.speaker}`}
						>
							<span class="spk">{ln.speaker}:</span>
							<span class="spk-text">{ln.text}</span>
							{#if ln.voiceLine}
								<span class="play-icon">{playingId === ln.id ? '■' : '▶'}</span>
							{:else}
								<span class="play-icon muted">∅</span>
							{/if}
						</button>
					{:else if ln.kind === 'blank'}
						<div class="ln blank">&nbsp;</div>
					{:else}
						<div class="ln line">{ln.raw}</div>
					{/if}
				{/each}
			{/if}
		</div>
	</section>

	{#if lightboxSrc}
		<button
			class="lightbox"
			on:click={() => (lightboxSrc = null)}
			aria-label="Close panel preview"
		>
			<img src={lightboxSrc} alt="panel preview" />
		</button>
	{/if}

	{#if noteModal}
		{@const nm = noteModal}
		{@const liveNote = notes[noteKey(nm.sceneId, nm.file)]}
		<div
			class="note-modal-bg"
			role="presentation"
			on:click={(e) => { if (e.target === e.currentTarget) closeNoteModal(); }}
		>
			<div class="note-modal" role="dialog" aria-modal="true" aria-label="Panel notes">
				<header class="note-head">
					<div class="note-title">
						<span class="note-scene">Scene {nm.sceneId}</span>
						<span class="note-file">{nm.file}</span>
						{#if liveNote}
							<span class="note-status">📝 saved {new Date(liveNote.updatedAt).toLocaleString()}</span>
						{:else}
							<span class="note-status muted">new note</span>
						{/if}
					</div>
					<button class="btn-icon" on:click={closeNoteModal} aria-label="Close">✕</button>
				</header>
				<div class="note-body">
					<textarea
						bind:value={noteModal.text}
						on:input={() => { if (noteModal) noteModal.dirty = true; }}
						on:keydown={(e) => {
							if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
								e.preventDefault();
								saveNoteModal();
							}
						}}
						placeholder="e.g. 'make the lighting warmer, Tony's pose more aggressive, regenerate with seed 42'&#10;&#10;Anything you want to remember for the next regen pass — prompt tweaks, fixes, continuity notes."
						autofocus
						spellcheck="true"
					></textarea>
				</div>
				<footer class="note-foot">
					<button class="btn btn-sm btn-outline" on:click={deleteNoteFromModal} disabled={!nm.text || nm.saving}>🗑 clear</button>
					<div class="note-foot-right">
						<span class="note-count">{nm.text.length} char{nm.text.length === 1 ? '' : 's'}</span>
						<button class="btn btn-sm" on:click={saveNoteModal} disabled={!nm.dirty || nm.saving}>
							{nm.saving ? 'saving…' : '💾 save'}
						</button>
					</div>
				</footer>
			</div>
		</div>
	{/if}
</div>

<style>
	.page {
		display: flex;
		flex-direction: column;
		height: 100vh;
		background: var(--bg);
		color: var(--text);
		overflow: hidden;
	}

	/* ---- Top bar ---- */
	.topbar {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 16px;
		padding: 8px 16px;
		background: var(--card);
		border-bottom: 1px solid var(--border);
		flex: 0 0 auto;
	}
	.topbar .title {
		font-weight: 700;
		font-size: 1rem;
		letter-spacing: 0.3px;
	}
	.topbar .meta {
		display: flex;
		gap: 6px;
		flex-wrap: wrap;
		align-items: center;
	}
	.chip {
		background: rgba(255, 255, 255, 0.06);
		color: var(--muted);
		font-size: 0.72rem;
		padding: 3px 8px;
		border-radius: 4px;
		border: 1px solid var(--border);
	}
	.chip.scene-name { color: var(--text); }
	.chip.green { color: var(--green); border-color: rgba(46, 204, 113, 0.4); }
	.chip.red { color: var(--accent); border-color: rgba(233, 69, 96, 0.4); }
	.chip.muted { color: var(--muted); }

	.topbar .legend {
		display: flex;
		gap: 10px;
		font-size: 0.7rem;
		color: var(--muted);
		align-items: center;
	}
	.topbar .legend a { color: var(--muted); text-decoration: none; }
	.topbar .legend a:hover { color: var(--accent); }
	.topbar .legend kbd {
		background: rgba(255, 255, 255, 0.08);
		border: 1px solid var(--border);
		border-radius: 3px;
		padding: 0 4px;
		font-size: 0.65rem;
		font-family: inherit;
	}

	/* ---- Top 2/3: horizontal panels ---- */
	.panels {
		flex: 2 1 0;
		min-height: 0;
		overflow-x: auto;
		overflow-y: hidden;
		padding: 16px 16px 12px;
		background: linear-gradient(180deg, #0f0f1f 0%, #0a0a16 100%);
		scroll-behavior: smooth;
		display: flex;
		flex-direction: row;
		align-items: stretch;
		gap: 0;
	}
	.panels::-webkit-scrollbar { height: 10px; }
	.panels::-webkit-scrollbar-track { background: rgba(255, 255, 255, 0.04); }
	.panels::-webkit-scrollbar-thumb { background: var(--border); border-radius: 5px; }
	.panels::-webkit-scrollbar-thumb:hover { background: var(--accent); }

	.empty {
		padding: 40px;
		text-align: center;
		color: var(--muted);
	}

	.scene-block {
		display: flex;
		flex: 0 0 auto;
		flex-direction: column;
		margin-right: 20px;
		padding-right: 16px;
		border-right: 1px dashed var(--border);
		height: 100%;
		min-height: 0;
		max-width: 100vw;
	}
	.scene-header {
		display: flex;
		gap: 8px;
		align-items: baseline;
		padding: 0 4px 6px;
		font-size: 0.78rem;
		white-space: nowrap;
	}
	.scene-id {
		background: var(--accent);
		color: #fff;
		font-weight: 700;
		padding: 1px 6px;
		border-radius: 3px;
		font-size: 0.7rem;
	}
	.scene-title { color: var(--text); font-weight: 600; }
	.scene-meta { color: var(--muted); font-size: 0.7rem; }

	.scene-strip {
		display: flex;
		align-items: stretch;
		gap: 8px;
		padding-bottom: 4px;
		flex: 1 1 auto;
		min-height: 0;
	}
	.panel {
		position: relative;
		flex: 0 0 auto;
		height: 100%;
		width: auto;
		min-width: 100px;
		max-width: 360px;
		background: var(--card);
		border: 2px solid var(--border);
		border-radius: 6px;
		padding: 0;
		cursor: pointer;
		overflow: hidden;
		display: flex;
		flex-direction: column;
		transition: border-color 0.12s, transform 0.12s;
		font: inherit;
		color: inherit;
	}
	.panel:hover { border-color: rgba(233, 69, 96, 0.6); transform: translateY(-2px); }
	.panel.active { border-color: var(--accent); box-shadow: 0 0 0 1px var(--accent), 0 4px 16px rgba(233, 69, 96, 0.3); }
	.panel.has-note { border-color: var(--yellow); }
	.panel.has-note.active { border-color: var(--accent); box-shadow: 0 0 0 1px var(--accent), 0 4px 16px rgba(233, 69, 96, 0.3); }
	.panel img {
		flex: 1 1 auto;
		min-height: 0;
		width: auto;
		max-width: 100%;
		aspect-ratio: 16 / 9;
		object-fit: cover;
		display: block;
		background: #000;
		margin: 0 auto;
	}
	.panel video {
		flex: 1 1 auto;
		min-height: 0;
		width: auto;
		max-width: 100%;
		aspect-ratio: 16 / 9;
		object-fit: cover;
		display: block;
		background: #000;
		margin: 0 auto;
	}
	.video-panel { border-color: rgba(46, 204, 113, 0.4); }
	.video-panel:hover { border-color: var(--green); }
	.note-badge {
		position: absolute;
		top: 6px;
		right: 6px;
		background: var(--yellow);
		color: #1a1a1a;
		font-size: 0.85rem;
		padding: 2px 6px;
		border-radius: 4px;
		line-height: 1;
		box-shadow: 0 2px 6px rgba(0, 0, 0, 0.5);
		pointer-events: auto;
		cursor: help;
		z-index: 1;
	}
	.panel-cap {
		display: flex;
		justify-content: space-between;
		padding: 4px 8px;
		font-size: 0.7rem;
		color: var(--muted);
		flex: 0 0 auto;
		background: rgba(0, 0, 0, 0.4);
	}
	.panel-cap .pn { color: var(--text); font-weight: 600; }
	.panel-cap .ts { font-variant-numeric: tabular-nums; }

	.panel-empty {
		flex: 0 0 auto;
		width: 180px;
		display: flex;
		flex-direction: column;
		gap: 4px;
	}
	.panel-img.blank {
		width: 100%;
		aspect-ratio: 16 / 9;
		background: rgba(255, 255, 255, 0.03);
		border: 2px dashed var(--border);
		border-radius: 6px;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 2rem;
	}
	.panel-empty .panel-cap { font-size: 0.7rem; color: var(--muted); padding: 0 4px; }

	/* ---- Middle: timer / ruler ---- */
	.timer-bar {
		flex: 0 0 auto;
		background: #0a0a14;
		border-top: 1px solid var(--border);
		border-bottom: 1px solid var(--border);
		padding: 8px 16px;
		display: flex;
		gap: 16px;
		align-items: center;
	}
	.timer-readout {
		display: flex;
		gap: 6px;
		align-items: baseline;
		font-family: ui-monospace, 'SF Mono', Menlo, monospace;
		min-width: 180px;
	}
	.t-cur { color: var(--accent); font-size: 1.4rem; font-weight: 700; font-variant-numeric: tabular-nums; }
	.t-sep { color: var(--muted); }
	.t-tot { color: var(--muted); font-size: 1rem; font-variant-numeric: tabular-nums; }
	.t-scene { color: var(--muted); font-size: 0.8rem; margin-left: 6px; }

	.ruler {
		flex: 1 1 auto;
		position: relative;
		height: 32px;
		background: linear-gradient(180deg, #11111e 0%, #0a0a14 100%);
		border: 1px solid var(--border);
		border-radius: 4px;
		overflow: hidden;
	}
	.ruler-tick {
		position: absolute;
		top: 0;
		bottom: 0;
		width: 2px;
		background: rgba(255, 255, 255, 0.12);
		cursor: pointer;
		transition: background 0.1s;
	}
	.ruler-tick:hover { background: rgba(255, 255, 255, 0.3); }
	.ruler-tick.current { background: var(--accent); width: 3px; }
	.playhead {
		position: absolute;
		top: -4px;
		bottom: -4px;
		width: 0;
		border-left: 2px solid var(--accent);
		pointer-events: none;
		transform: translateX(-1px);
		box-shadow: 0 0 6px rgba(233, 69, 96, 0.6);
	}
	.playhead::after {
		content: '';
		position: absolute;
		left: -5px;
		top: -2px;
		width: 0;
		height: 0;
		border-left: 6px solid transparent;
		border-right: 6px solid transparent;
		border-top: 8px solid var(--accent);
	}

	.timer-actions { display: flex; gap: 6px; }

	/* ---- Bottom 1/3: script ---- */
	.script {
		flex: 1 1 0;
		min-height: 0;
		display: flex;
		flex-direction: column;
		background: var(--bg);
		border-top: 1px solid var(--border);
	}
	.script-head {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 6px 16px;
		background: var(--card);
		border-bottom: 1px solid var(--border);
		flex: 0 0 auto;
	}
	.script-title { font-size: 0.85rem; font-weight: 600; }
	.script-stats { display: flex; gap: 6px; }

	.script-body {
		flex: 1 1 0;
		min-height: 0;
		overflow-y: auto;
		padding: 12px 24px 24px;
		font-family: ui-monospace, 'SF Mono', Menlo, monospace;
		font-size: 0.85rem;
		line-height: 1.55;
	}
	.script-body::-webkit-scrollbar { width: 10px; }
	.script-body::-webkit-scrollbar-track { background: rgba(255, 255, 255, 0.04); }
	.script-body::-webkit-scrollbar-thumb { background: var(--border); border-radius: 5px; }

	.ln {
		padding: 2px 0;
		white-space: pre-wrap;
	}
	.ln.heading { color: var(--muted); font-weight: 600; margin-top: 8px; }
	.ln.scene {
		display: block;
		width: 100%;
		text-align: left;
		background: linear-gradient(90deg, rgba(233, 69, 96, 0.18), transparent 80%);
		border-left: 3px solid var(--accent);
		color: var(--text);
		font-weight: 700;
		font-size: 0.95rem;
		padding: 8px 12px;
		margin: 14px 0 6px;
		cursor: pointer;
		font-family: inherit;
		border-radius: 0 4px 4px 0;
	}
	.ln.scene:hover { background: linear-gradient(90deg, rgba(233, 69, 96, 0.32), transparent 80%); }
	.ln.comment { color: var(--muted); font-style: italic; padding-left: 16px; }
	.ln.stage { color: var(--muted); padding-left: 16px; }
	.ln.blank { height: 0.5em; }
	.ln.line { color: var(--text); padding-left: 8px; }

	.ln.speaker {
		display: inline-flex;
		gap: 8px;
		align-items: baseline;
		padding: 4px 10px;
		margin: 2px 0;
		border-radius: 4px;
		background: transparent;
		border: 1px solid transparent;
		color: inherit;
		font: inherit;
		text-align: left;
		cursor: pointer;
		max-width: 100%;
	}
	.ln.speaker.has-voice { background: rgba(46, 204, 113, 0.06); border-color: rgba(46, 204, 113, 0.15); }
	.ln.speaker.has-voice:hover { background: rgba(46, 204, 113, 0.12); border-color: rgba(46, 204, 113, 0.4); }
	.ln.speaker.playing { background: rgba(46, 204, 113, 0.25); border-color: var(--green); animation: pulse 1.2s infinite; }
	.ln.speaker:disabled { cursor: not-allowed; opacity: 0.4; }
	.ln.speaker .spk { color: var(--accent); font-weight: 700; flex: 0 0 auto; }
	.ln.speaker .spk-text { color: var(--text); flex: 1 1 auto; }
	.ln.speaker .play-icon {
		flex: 0 0 auto;
		color: var(--green);
		font-size: 0.75rem;
		padding: 1px 6px;
		border-radius: 3px;
		background: rgba(46, 204, 113, 0.15);
	}
	.ln.speaker .play-icon.muted { color: var(--muted); background: transparent; }

	@keyframes pulse {
		0%, 100% { box-shadow: 0 0 0 0 rgba(46, 204, 113, 0.4); }
		50% { box-shadow: 0 0 0 4px rgba(46, 204, 113, 0); }
	}

	/* ---- Lightbox ---- */
	.lightbox {
		position: fixed;
		inset: 0;
		background: rgba(0, 0, 0, 0.85);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 1000;
		border: 0;
		cursor: zoom-out;
		padding: 0;
	}
	.lightbox img {
		max-width: 90vw;
		max-height: 90vh;
		object-fit: contain;
		box-shadow: 0 0 40px rgba(0, 0, 0, 0.6);
	}

	/* ---- Note modal ---- */
	.note-modal-bg {
		position: fixed;
		inset: 0;
		background: rgba(0, 0, 0, 0.7);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 1100;
		padding: 24px;
	}
	.note-modal {
		background: var(--card);
		border: 1px solid var(--border);
		border-radius: 10px;
		width: 100%;
		max-width: 640px;
		max-height: 80vh;
		display: flex;
		flex-direction: column;
		box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);
		overflow: hidden;
	}
	.note-head {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 12px 16px;
		border-bottom: 1px solid var(--border);
		gap: 12px;
	}
	.note-title {
		display: flex;
		gap: 10px;
		align-items: baseline;
		flex-wrap: wrap;
		flex: 1 1 auto;
		min-width: 0;
	}
	.note-scene {
		background: var(--accent);
		color: #fff;
		font-weight: 700;
		padding: 2px 8px;
		border-radius: 4px;
		font-size: 0.8rem;
	}
	.note-file {
		font-family: ui-monospace, 'SF Mono', Menlo, monospace;
		font-size: 0.8rem;
		color: var(--text);
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
		min-width: 0;
	}
	.note-status {
		font-size: 0.72rem;
		color: var(--yellow);
		white-space: nowrap;
	}
	.note-status.muted { color: var(--muted); }
	.btn-icon {
		background: transparent;
		border: 1px solid var(--border);
		color: var(--muted);
		width: 28px;
		height: 28px;
		border-radius: 4px;
		cursor: pointer;
		font-size: 0.9rem;
		padding: 0;
	}
	.btn-icon:hover { border-color: var(--accent); color: var(--accent); }
	.note-body {
		flex: 1 1 auto;
		min-height: 240px;
		display: flex;
		padding: 12px 16px;
	}
	.note-body textarea {
		flex: 1 1 auto;
		background: #0a0a14;
		border: 1px solid var(--border);
		border-radius: 6px;
		color: var(--text);
		font: inherit;
		font-family: ui-monospace, 'SF Mono', Menlo, monospace;
		font-size: 0.85rem;
		line-height: 1.55;
		padding: 10px 12px;
		resize: vertical;
		min-height: 220px;
	}
	.note-body textarea:focus {
		outline: none;
		border-color: var(--accent);
		box-shadow: 0 0 0 2px rgba(233, 69, 96, 0.2);
	}
	.note-foot {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 10px 16px;
		border-top: 1px solid var(--border);
		background: rgba(0, 0, 0, 0.3);
	}
	.note-foot-right {
		display: flex;
		gap: 12px;
		align-items: center;
	}
	.note-count {
		font-size: 0.72rem;
		color: var(--muted);
		font-variant-numeric: tabular-nums;
	}

	@media (max-width: 900px) {
		.topbar { flex-wrap: wrap; }
		.legend { display: none; }
		.timer-bar { flex-wrap: wrap; }
		.timer-readout { min-width: 0; }
		.panel { width: 140px; }
	}
</style>
