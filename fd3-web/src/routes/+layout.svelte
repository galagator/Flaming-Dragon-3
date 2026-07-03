<script lang="ts">
	import '../app.css';
	import Toast from '$lib/Toast.svelte';
	import { page } from '$app/state';

	let { children } = $props();
</script>

<svelte:head>
	<title>FD3 — Flaming Dragon 3</title>
	<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 16 16%22><text y=%2214%22 font-size=%2214%22>🔥</text></svg>" />
</svelte:head>

{#if !page.url.pathname.startsWith('/studio') && !page.url.pathname.startsWith('/tagger') && !page.url.pathname.startsWith('/voice-tagger')}
	<nav class="topnav">
		<a href="/" class:active={page.url.pathname === '/'}>Dashboard</a>
		<a href="/studio" class:active={page.url.pathname === '/studio'}>Character Studio</a>
		<a href="/tagger" class:active={page.url.pathname === '/tagger'}>Face Tagger</a>
		<a href="/voice-tagger" class:active={page.url.pathname === '/voice-tagger'}>Voice Tagger</a>
		<a href="/storyboard" class:active={page.url.pathname === '/storyboard'}>Storyboard</a>
	</nav>
{/if}

{@render children()}

<Toast />

<style>
	.topnav {
		display: flex;
		gap: 16px;
		padding: 12px 24px;
		background: var(--card);
		border-bottom: 1px solid var(--border);
	}
	.topnav a {
		color: var(--muted);
		text-decoration: none;
		font-size: 0.85rem;
		font-weight: 600;
	}
	.topnav a.active,
	.topnav a:hover { color: var(--accent); }
</style>
