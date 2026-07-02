<script lang="ts">
	let { src = $bindable('') } = $props<{ src: string }>();
	let open = $derived(Boolean(src));
</script>

{#if open}
	<button
		type="button"
		class="lightbox show"
		onclick={() => (src = '')}
		aria-label="Close lightbox"
	>
		<img {src} alt="Full size" />
	</button>
{/if}

<style>
	.lightbox {
		display: flex;
		position: fixed;
		inset: 0;
		background: rgba(0, 0, 0, 0.92);
		z-index: 1000;
		justify-content: center;
		align-items: center;
		border: none;
		padding: 0;
		cursor: pointer;
	}
	.lightbox img {
		max-width: 90vw;
		max-height: 90vh;
		object-fit: contain;
		border-radius: 4px;
	}
</style>
