<script lang="ts">
	import type { SaleInvoice } from '@/types';
	import Button from './ui/button/button.svelte';
	const { invoice }: { invoice: SaleInvoice } = $props();
	console.log(invoice);
</script>

<Button
	disabled={!invoice.pdf_file_url}
	size="xs"
	variant="outline"
	type="button"
	onclick={() => window.open(invoice.pdf_file_url, '_blank')}
>
	{invoice.document_id}
</Button>
