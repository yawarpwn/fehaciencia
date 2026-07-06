<!-- src/lib/components/multi-doc-thumbnails.svelte -->
<script lang="ts">
	import type { InvoiceDocument } from '$lib/types';
	import type { Component } from 'svelte';

	let {
		documents,
		icon: Icon
	}: {
		documents: InvoiceDocument[];
		icon: Component;
	} = $props();

	const maxVisible = 2;
	const visible = $derived(documents.slice(0, maxVisible));
	const extra = $derived(documents.length - maxVisible);
</script>

{#if documents.length === 0}
	<div class="flex size-8 items-center justify-center rounded-md bg-muted text-muted-foreground/40">
		<Icon size={16} strokeWidth={2} />
	</div>
{:else}
	<div class="flex items-center -space-x-3">
		{#each visible as doc (doc.id)}
			<button
				type="button"
				onclick={() => window.open(doc.fileUrl, '_blank')}
				title={doc.fileName}
				class="size-8 overflow-hidden rounded-md border-2 border-background bg-green-50 text-green-600 hover:bg-green-100 dark:bg-green-950 dark:text-green-400
					hover:z-10 hover:scale-110 transition-transform"
			>
				{#if doc.thumbnailUrl}
					<img src={doc.thumbnailUrl} alt={doc.fileName} class="size-full object-cover" />
				{:else}
					<!-- PDF u otro archivo sin miniatura visual -->
					<div class="size-full flex items-center justify-center">
						<Icon size={14} strokeWidth={2} class="text-green-600 dark:text-green-400" />
					</div>
				{/if}
			</button>
		{/each}
		{#if extra > 0}
			<div
				class="flex size-8 items-center justify-center rounded-md border-2
				border-background bg-muted text-[11px] font-medium text-muted-foreground z-10"
			>
				+{extra}
			</div>
		{/if}
	</div>
{/if}
