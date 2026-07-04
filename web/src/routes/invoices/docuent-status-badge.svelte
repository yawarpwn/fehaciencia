<!-- document-status-badge.svelte -->
<script lang="ts">
	import { Badge } from '$lib/components/ui/badge/index.js';
	import CheckIcon from '@lucide/svelte/icons/check';
	import AlertTriangleIcon from '@lucide/svelte/icons/alert-triangle';
	import type { InvoiceDocument, DocumentType } from '$lib/types';

	let {
		documents,
		missingDocuments,
		isComplete
	}: {
		documents: InvoiceDocument[];
		missingDocuments: DocumentType[];
		isComplete: boolean;
	} = $props();
</script>

{#if isComplete}
	<Badge variant="outline" class="gap-1 border-green-600 text-green-700">
		<CheckIcon class="size-3" />
		Completo ({documents.length})
	</Badge>
{:else}
	<Badge variant="destructive" class="gap-1">
		<AlertTriangleIcon class="size-3" />
		Falta {missingDocuments.length}
	</Badge>
{/if}
