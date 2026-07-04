<!-- src/lib/components/document-status-icons.svelte -->
<script lang="ts">
	import { REQUIRED_DOCUMENT_TYPES, DOCUMENT_TYPE_META } from '$lib/types';
	import type { DocumentType, InvoiceDocument } from '$lib/types';

	let {
		documents,
		missingDocuments
	}: {
		documents: InvoiceDocument[];
		missingDocuments: DocumentType[];
	} = $props();

	const isPresent = (type: DocumentType) => !missingDocuments.includes(type);

	const findDoc = (type: DocumentType) => documents.find((d) => d.documentType === type);
</script>

<div class="flex items-center gap-1.5">
	{#each REQUIRED_DOCUMENT_TYPES as type (type)}
		{@const present = isPresent(type)}
		{@const meta = DOCUMENT_TYPE_META[type]}
		{@const doc = findDoc(type)}
		{@const Icon = meta.icon}
		<span
			title={present ? `${meta.label} — subido` : `${meta.label} — falta`}
			class="flex size-7 items-center justify-center rounded-md
				{present
				? 'bg-green-50 text-green-600 dark:bg-green-950 dark:text-green-400'
				: 'bg-muted text-muted-foreground/40'}"
		>
			<Icon size={16} strokeWidth={2} />
		</span>
	{/each}
</div>
