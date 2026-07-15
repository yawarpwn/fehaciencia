<script lang="ts">
	import type { DeliveryNote } from '@/types';
	import Button from './ui/button/button.svelte';
	const { deliveryNotes }: { deliveryNotes: DeliveryNote[] } = $props();
</script>

<div class="flex flex-col gap-1">
	{#each deliveryNotes as deliveryNote (deliveryNote.id)}
		<Button
			disabled={!deliveryNote.pdf_file_url}
			size="xs"
			variant="outline"
			class="inline-block"
			type="button"
			onclick={() => window.open(deliveryNote.pdf_file_url, '_blank')}
		>
			{deliveryNote.document_id}
		</Button>
	{/each}
</div>
