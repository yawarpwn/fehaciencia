<script lang="ts">
	import EllipsisIcon from '@lucide/svelte/icons/ellipsis';
	import { Button } from '$lib/components/ui/button/index.js';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu/index.js';

	import DocumentDialog from '@/components/document-dialog.svelte';
	import type { SaleInvoice } from '@/types';

	let { invoice }: { invoice: SaleInvoice } = $props();

	let open = $state(false);

	function openModal() {
		open = true;
	}

	function closeModal() {
		open = false;
	}
</script>

<DocumentDialog {open} {invoice} onClose={closeModal} />
<DropdownMenu.Root>
	<DropdownMenu.Trigger>
		{#snippet child({ props })}
			<Button {...props} variant="ghost" size="icon" class="relative size-8 p-0">
				<span class="sr-only">Open menu</span>
				<EllipsisIcon />
			</Button>
		{/snippet}
	</DropdownMenu.Trigger>
	<DropdownMenu.Content>
		<DropdownMenu.Group>
			<DropdownMenu.Label>Actions</DropdownMenu.Label>
			<DropdownMenu.Item onclick={() => openModal()}>Subir</DropdownMenu.Item>
		</DropdownMenu.Group>
		<DropdownMenu.Separator />
	</DropdownMenu.Content>
</DropdownMenu.Root>
