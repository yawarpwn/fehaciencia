<!-- src/lib/components/single-doc-status.svelte -->
<script lang="ts">
	import type { InvoiceDocument } from '$lib/types';
	import type { Component } from 'svelte';

	let {
		document,
		icon: Icon,
		label
	}: {
		document: InvoiceDocument | null;
		icon: Component;
		label: string;
	} = $props();
</script>

<button
	type="button"
	disabled={!document}
	title={document ? `${label} — ${document.fileName}` : `${label} — falta`}
	onclick={() => document && window.open(document.fileUrl, '_blank')}
	class="flex size-8 items-center justify-center rounded-md transition-colors
		{document
		? 'bg-green-50 text-green-600 hover:bg-green-100 dark:bg-green-950 dark:text-green-400'
		: 'bg-muted text-muted-foreground/40 cursor-default'}"
>
	<Icon size={16} strokeWidth={2} />
</button>
