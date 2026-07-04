<!-- src/lib/components/photo-thumbnails.svelte -->
<script lang="ts">
	import ImageOffIcon from '@lucide/svelte/icons/image-off';
	import type { InvoiceDocument } from '$lib/types';

	let { photos }: { photos: InvoiceDocument[] } = $props();

	const maxVisible = 3;
	const visible = $derived(photos.slice(0, maxVisible));
	const extra = $derived(photos.length - maxVisible);
</script>

{#if photos.length === 0}
	<div class="flex size-8 items-center justify-center rounded-md bg-muted text-muted-foreground/40">
		<ImageOffIcon size={16} strokeWidth={2} />
	</div>
{:else}
	<div class="flex items-center -space-x-2">
		{#each visible as photo (photo.id)}
			<button
				type="button"
				onclick={() => window.open(photo.fileUrl, '_blank')}
				class="size-8 overflow-hidden rounded-md border-2 border-background hover:z-10 hover:scale-110 transition-transform"
				title={photo.fileName}
			>
				<img src={photo.thumbnailUrl} alt={photo.fileName} class="size-full object-cover" />
			</button>
		{/each}
		{#if extra > 0}
			<div
				class="flex size-8 items-center justify-center rounded-md border-2 border-background bg-muted text-[11px] font-medium text-muted-foreground"
			>
				+{extra}
			</div>
		{/if}
	</div>
{/if}
