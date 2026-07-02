<script lang="ts">
	import { toasts } from './toast';
</script>

<div class="toasts">
	{#each $toasts as t (t.id)}
		<div class="toast" class:err={t.kind === 'err'}>{t.msg}</div>
	{/each}
</div>

<style>
	.toasts {
		position: fixed;
		bottom: 24px;
		left: 50%;
		transform: translateX(-50%);
		display: flex;
		flex-direction: column;
		gap: 8px;
		z-index: 2000;
	}
	.toast {
		background: #2ecc71;
		color: #fff;
		padding: 10px 20px;
		border-radius: 8px;
		font-size: 0.85rem;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
	}
	.toast.err { background: #e94560; }
</style>
