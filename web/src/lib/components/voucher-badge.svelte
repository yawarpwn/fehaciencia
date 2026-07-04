<!-- src/lib/components/voucher-badge.svelte -->
<script lang="ts">
	import ReceiptOffIcon from '@lucide/svelte/icons/receipt-text';
	import type { InvoiceDocument } from '$lib/types';

	let { vouchers }: { vouchers: InvoiceDocument[] } = $props();

	const total = $derived(vouchers.reduce((sum, v) => sum + (v.amount ?? 0), 0));
	const formatter = new Intl.NumberFormat('es-PE', { style: 'currency', currency: 'PEN' });
</script>

{#if vouchers.length === 0}
	<div class="flex size-8 items-center justify-center rounded-md bg-muted text-muted-foreground/40">
		<ReceiptOffIcon size={16} strokeWidth={2} />
	</div>
{:else}
	<button
		type="button"
		onclick={() => window.open(vouchers[0].fileUrl, '_blank')}
		title={vouchers.map((v) => v.fileName).join(', ')}
		class="flex items-center gap-1.5 rounded-md bg-green-50 px-2 py-1 text-xs font-medium text-green-700 hover:bg-green-100 dark:bg-green-950 dark:text-green-400"
	>
		<span>{vouchers.length}× </span>
		<span>{formatter.format(total)}</span>
	</button>
{/if}
