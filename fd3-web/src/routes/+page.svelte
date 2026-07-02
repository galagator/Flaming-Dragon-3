<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import { CHARACTERS, refPrefix } from '$lib/characters';

	let markers = $state(0);
	let perChar = $state<Record<string, number>>({});
	let refsByChar = $state<Record<string, string[]>>({});
	let loaded = $state(false);

	const scenes: Array<[string, 'shot' | 'missing']> = [
		['GKD Commercial', 'shot'],
		['Intro + Sitcom', 'missing'],
		['Scene 1 — Lounge Room', 'shot'],
		['Scene 2 — Fruity Groovin', 'shot'],
		['Scene 3 — Goons Descend', 'shot'],
		['Scene 4 — Chinatown Mall', 'shot'],
		['Scene 5 — Bridge Moonlight', 'shot'],
		['Scene 6 — Tony\'s House', 'shot'],
		['Scene 7 — Dream Sequence', 'missing'],
		['Scene 8A — Park Training', 'missing'],
		['Scene 8B — GKD HQ', 'missing'],
		['Scene 8C — Park Fight', 'missing'],
		['Scene 8D — Office', 'missing'],
		['Scene 8E — Escape', 'missing'],
		['Scene 9 — Dirt Bowl', 'missing'],
		['Scene 10 — Spirit Path', 'missing'],
		['Scene 11 — Dirt Bowl Fight', 'missing'],
		['Scene 12 — Morning After', 'missing'],
		['Scene 13 — Deaths Dam', 'missing'],
		['Scene 16 — Post-Credits', 'missing']
	];

	const scenesShot = scenes.filter(([, s]) => s === 'shot').length;
	const scenesMissing = scenes.length - scenesShot;

	function firstRef(name: string): string {
		return refsByChar[name]?.[0] ?? `character-references/${refPrefix(name)}01.jpg`;
	}

	function fallbackThumb(name: string): string {
		const svg = `<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 48 48'><rect fill='#333' width='48' height='48'/><text x='24' y='30' font-size='18' text-anchor='middle' fill='#888'>?</text></svg>`;
		return `data:image/svg+xml,${svg}`;
	}

	onMount(async () => {
		try {
			const [m, r] = await Promise.all([api.getMapping(), api.getReferences()]);
			markers = m.markers;
			perChar = m.perCharacter;
			refsByChar = r.references;
		} catch (e) {
			console.warn('dashboard data load failed', e);
		} finally {
			loaded = true;
		}
	});
</script>

<h1>🔥 Flaming Dragon 3</h1>
<div class="subtitle">Production Dashboard — Gold Coast, Australia</div>

<div class="cards">
	<a class="card" href="/studio">
		<div class="icon">🎭</div>
		<h2>Character Studio</h2>
		<p>Browse every character with face refs, costume notes, dialogue lines, and scene breakdowns.</p>
		<span class="tag">{CHARACTERS.length} characters</span>
	</a>
	<a class="card" href="/tagger">
		<div class="icon">🏷️</div>
		<h2>Face Tagger</h2>
		<p>Click faces on photos and assign character names. Save to disk writes straight to the project.</p>
		<span class="tag">40 photos loaded</span>
	</a>
	<a class="card" href="https://github.com/galagator/Flaming-Dragon-3" target="_blank" rel="noopener">
		<div class="icon">📂</div>
		<h2>GitHub Repo</h2>
		<p>Source code, script, production guide, and all assets.</p>
		<span class="tag">galagator/Flaming-Dragon-3</span>
	</a>
</div>

<div class="section">
	<h3>📊 Project Stats</h3>
	<div class="stats">
		<div class="stat"><div class="num">{scenesShot}</div><div class="label">Scenes Shot</div></div>
		<div class="stat"><div class="num">{scenesMissing}</div><div class="label">Scenes to Generate</div></div>
		<div class="stat"><div class="num">{CHARACTERS.length}</div><div class="label">Characters</div></div>
		<div class="stat"><div class="num">{loaded ? markers : '…'}</div><div class="label">Face References</div></div>
		<div class="stat"><div class="num">~10m</div><div class="label">Shot Footage</div></div>
		<div class="stat"><div class="num">~15-20m</div><div class="label">Needs AI</div></div>
	</div>
</div>

<div class="section">
	<h3>🎬 Scene Progress</h3>
	<div class="scene-progress">
		{#each scenes as [name, status]}
			<span class="scene-chip {status}">
				{status === 'shot' ? '✅' : '🆕'} {name}
			</span>
		{/each}
	</div>
</div>

<div class="section">
	<h3>👥 Cast & Characters</h3>
	<div class="char-grid">
		{#each CHARACTERS as c}
			<a class="char-item" href="/studio?char={encodeURIComponent(c.name)}">
				<img src={firstRef(c.name)} alt={c.name} onerror={(e) => ((e.currentTarget as HTMLImageElement).src = fallbackThumb(c.name))} />
				<div class="name">{c.name}</div>
				<div class="badge"><span class="dot {c.status}"></span>{c.dialogue.length} lines</div>
			</a>
		{/each}
	</div>
</div>

<div class="section">
	<h3>📄 Project Files</h3>
	<div class="cards">
		<a class="card" href="/FD3-Script.md">
			<div class="icon">📜</div>
			<h2>Script</h2>
			<p>Full reformatted script — 19 scenes, 532 lines.</p>
		</a>
		<a class="card" href="/AI-PRODUCTION-GUIDE.md">
			<div class="icon">📖</div>
			<h2>Production Guide</h2>
			<p>AI workflow guide, character refs, pipeline recommendations.</p>
		</a>
	</div>
</div>

<div class="footer">FD3 — Flaming Dragon 3 · Gold Coast · node server.js on port 6060</div>

<style>
	h1 { font-size: 1.6rem; display: flex; align-items: center; gap: 8px; }
	.subtitle { color: var(--muted); font-size: 0.85rem; margin: 4px 0 20px; }
	.cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; margin-bottom: 24px; }
	.card {
		background: var(--card);
		border: 1px solid var(--border);
		border-radius: 10px;
		padding: 20px;
		transition: 0.15s;
		text-decoration: none;
		color: var(--text);
		display: block;
	}
	.card:hover { border-color: var(--accent); transform: translateY(-2px); }
	.card .icon { font-size: 1.6rem; margin-bottom: 8px; }
	.card h2 { font-size: 1rem; margin-bottom: 4px; }
	.card p { font-size: 0.82rem; color: var(--muted); line-height: 1.4; }
	.card .tag {
		display: inline-block;
		font-size: 0.68rem;
		padding: 2px 6px;
		border-radius: 4px;
		margin-top: 8px;
		background: rgba(255,255,255,0.06);
		color: var(--muted);
	}
	.section { margin-top: 24px; }
	.section h3 {
		font-size: 0.85rem;
		text-transform: uppercase;
		letter-spacing: 0.5px;
		color: var(--muted);
		margin-bottom: 12px;
		padding-bottom: 6px;
		border-bottom: 1px solid var(--border);
	}
	.stats { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 12px; margin-bottom: 24px; }
	.stat { background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 14px; text-align: center; }
	.stat .num { font-size: 1.4rem; font-weight: 700; color: var(--accent); }
	.stat .label { font-size: 0.72rem; color: var(--muted); margin-top: 2px; }
	.char-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(100px, 1fr)); gap: 10px; }
	.char-item {
		background: var(--card);
		border: 1px solid var(--border);
		border-radius: 8px;
		padding: 10px;
		text-align: center;
		text-decoration: none;
		color: var(--text);
		transition: 0.1s;
	}
	.char-item:hover { border-color: var(--accent); }
	.char-item img {
		width: 48px; height: 48px;
		border-radius: 50%;
		object-fit: cover;
		background: #222;
		margin-bottom: 4px;
	}
	.char-item .name { font-size: 0.72rem; line-height: 1.2; }
	.char-item .badge { font-size: 0.6rem; color: var(--muted); }
	.dot { display: inline-block; width: 6px; height: 6px; border-radius: 50%; margin-right: 4px; }
	.dot.shot { background: var(--green); }
	.dot.ai { background: var(--accent); }
	.scene-progress { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 24px; }
	.scene-chip {
		padding: 4px 10px;
		border-radius: 6px;
		font-size: 0.78rem;
		border: 1px solid var(--border);
		display: flex;
		align-items: center;
		gap: 4px;
	}
	.scene-chip.shot { border-color: rgba(46,204,113,0.3); color: var(--green); }
	.scene-chip.missing { border-color: rgba(233,69,96,0.3); color: var(--accent); }
	.footer { margin-top: 32px; padding-top: 16px; border-top: 1px solid var(--border); font-size: 0.78rem; color: var(--muted); text-align: center; }
	@media (max-width: 700px) { .char-grid { grid-template-columns: repeat(auto-fill, minmax(80px, 1fr)); } }
</style>
