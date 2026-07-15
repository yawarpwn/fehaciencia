<!-- src/lib/components/single-doc-status.svelte -->
<script lang="ts">
	import type { Component } from 'svelte';

	let {
		icon: Icon,
		fileUrl,
		label
	}: {
		fileUrl?: string | null;
		icon: Component;
		label: string;
	} = $props();
	// title={document ? `${label} — ${document.fileName}` : `${label} — falta`}
</script>

<button
	type="button"
	disabled={!fileUrl}
	onclick={() => document && window.open(fileUrl, '_blank')}
	class="flex size-8 items-center justify-center rounded-md transition-colors
		{fileUrl
		? 'bg-green-50 text-green-600 hover:bg-green-100 dark:bg-green-950 dark:text-green-400'
		: 'bg-muted text-muted-foreground/40 cursor-default'}"
>
	<Icon size={16} strokeWidth={2} />
</button>
