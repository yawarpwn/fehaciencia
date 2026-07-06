<script lang="ts">
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import * as Select from '$lib/components/ui/select/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import type { SaleInvoice } from '@/types';
	import { invalidateAll } from '$app/navigation';

	let {
		invoice,
		open = $bindable(false),
		onClose
	}: { invoice: SaleInvoice; open: boolean; onClose: () => void } = $props();

	// --- Config ---
	const ACCEPTED_TYPES = ['image/png', 'image/jpeg', 'image/webp', 'application/pdf'];
	const MAX_SIZE_MB = 10;

	export const DOCUMENT_TYPES = {
		PURCHASE_ORDER: 'Orden de compra',
		PHOTO: 'Fotos de entrega',
		PAYMENT_VOUCHER: 'Comprobante Deposito',
		DELIVERY_GUIDE_SIGNED: 'Guia Firmada',
		AGENCY_GUIDE: 'Guia de Agencia'
	};

	const documentTypes = Object.entries(DOCUMENT_TYPES).map(([value, label]) => ({
		value,
		label
	}));

	// --- State ---
	let isDragging = $state(false);
	let selectedFile = $state<File | null>(null);
	let previewUrl = $state<string | null>(null);
	let docType = $state<string>('');
	let uploading = $state(false);
	let error = $state<string | null>(null);
	let fileInput: HTMLInputElement;

	const docTypeLabel = $derived(
		documentTypes.find((d) => d.value === docType)?.label ?? 'Selecciona un tipo'
	);

	const isPdf = $derived(selectedFile?.type === 'application/pdf');

	// --- Helpers ---
	function validateAndSetFile(file: File) {
		error = null;

		if (!ACCEPTED_TYPES.includes(file.type)) {
			error = 'Formato no permitido. Solo se aceptan imágenes (PNG, JPG, WEBP) o PDF.';
			return;
		}

		if (file.size > MAX_SIZE_MB * 1024 * 1024) {
			error = `El archivo supera el límite de ${MAX_SIZE_MB}MB.`;
			return;
		}

		selectedFile = file;

		if (previewUrl) URL.revokeObjectURL(previewUrl);
		previewUrl = file.type.startsWith('image/') ? URL.createObjectURL(file) : null;
	}

	function handleDrop(e: DragEvent) {
		e.preventDefault();
		isDragging = false;
		const file = e.dataTransfer?.files?.[0];
		if (file) validateAndSetFile(file);
	}

	function handlePaste(e: ClipboardEvent) {
		if (!open) return;

		const items = e.clipboardData?.items;
		if (!items) return;

		for (const item of items) {
			if (item.type.startsWith('image/')) {
				const file = item.getAsFile();
				if (file) {
					// Le damos un nombre, ya que las imágenes del portapapeles
					// suelen venir como "image.png" sin extensión útil
					const ext = item.type.split('/')[1] ?? 'png';
					const namedFile = new File([file], `pegado-${Date.now()}.${ext}`, {
						type: item.type
					});
					validateAndSetFile(namedFile);
					e.preventDefault();
				}
				break;
			}
		}
	}

	function handleDragOver(e: DragEvent) {
		e.preventDefault();
		isDragging = true;
	}

	function handleDragLeave() {
		isDragging = false;
	}

	function handleFileInputChange(e: Event) {
		const file = (e.target as HTMLInputElement).files?.[0];
		if (file) validateAndSetFile(file);
	}

	function removeFile() {
		selectedFile = null;
		if (previewUrl) URL.revokeObjectURL(previewUrl);
		previewUrl = null;
		if (fileInput) fileInput.value = '';
	}

	function resetForm() {
		removeFile();
		docType = '';
		error = null;
		uploading = false;
	}

	async function handleSubmit() {
		error = null;

		if (!selectedFile) {
			error = 'Debes seleccionar un archivo.';
			return;
		}
		if (!docType) {
			error = 'Debes seleccionar el tipo de documento.';
			return;
		}

		uploading = true;

		try {
			const formData = new FormData();
			formData.append('file', selectedFile);
			formData.append('documentType', docType);
			formData.append('invoiceId', invoice.id);

			const res = await fetch('/api/invoices', {
				method: 'POST',
				body: formData
			});

			if (!res.ok) {
				throw new Error(`Error del servidor: ${res.status}`);
			}

			//  Forzar a SvelteKit a recargar los datos del load()
			await invalidateAll();

			open = false;
			resetForm();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Ocurrió un error al subir el documento.';
		} finally {
			uploading = false;
		}
	}

	$effect(() => {
		if (!open) return;

		window.addEventListener('paste', handlePaste);
		return () => window.removeEventListener('paste', handlePaste);
	});

	$effect(() => {
		if (!open) resetForm();
	});
</script>

<Dialog.Root bind:open onOpenChange={onClose}>
	<Dialog.Content>
		<Dialog.Header>
			<Dialog.Title>Cargar documento</Dialog.Title>
		</Dialog.Header>

		<div class="flex flex-col gap-4">
			<!-- Select de tipo de documento -->
			<div class="flex flex-col gap-1.5">
				<label for="doc-type" class="text-sm font-medium">Tipo de documento</label>
				<Select.Root type="single" bind:value={docType}>
					<Select.Trigger id="doc-type" class="w-full">
						{docTypeLabel}
					</Select.Trigger>
					<Select.Content>
						{#each documentTypes as type (type.value)}
							<Select.Item value={type.value} label={type.label}>
								{type.label}
							</Select.Item>
						{/each}
					</Select.Content>
				</Select.Root>
			</div>

			<!-- Zona de drag & drop -->
			<div
				role="button"
				tabindex="0"
				ondrop={handleDrop}
				ondragover={handleDragOver}
				ondragleave={handleDragLeave}
				onclick={() => fileInput.click()}
				onkeydown={(e) => e.key === 'Enter' && fileInput.click()}
				class="flex flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed p-6 text-center transition-colors
					{isDragging ? 'border-primary bg-primary/5' : 'border-muted-foreground/25'}
					{selectedFile ? 'py-4' : 'py-10'}"
			>
				<input
					bind:this={fileInput}
					type="file"
					accept="image/png,image/jpeg,image/webp,application/pdf"
					class="hidden"
					onchange={handleFileInputChange}
				/>

				{#if !selectedFile}
					<p class="text-sm text-muted-foreground">
						Arrastra tu archivo aquí o <span class="text-primary underline"
							>haz clic para elegir</span
						>
					</p>
					<p class="text-xs text-muted-foreground/70">
						PNG, JPG, WEBP o PDF · máx {MAX_SIZE_MB}MB
					</p>
				{:else if isPdf}
					<div class="flex items-center gap-2">
						<span class="text-sm font-medium">📄 {selectedFile.name}</span>
					</div>
				{:else if previewUrl}
					<img src={previewUrl} alt="Vista previa" class="max-h-32 rounded object-contain" />
					<span class="text-xs text-muted-foreground">{selectedFile.name}</span>
				{/if}

				{#if selectedFile}
					<button
						type="button"
						class="text-xs text-destructive underline"
						onclick={(e) => {
							e.stopPropagation();
							removeFile();
						}}
					>
						Quitar archivo
					</button>
				{/if}
			</div>

			{#if error}
				<p class="text-sm text-destructive">{error}</p>
			{/if}
		</div>

		<Dialog.Footer>
			<Button variant="outline" onclick={() => (open = false)} disabled={uploading}>
				Cancelar
			</Button>
			<Button onclick={handleSubmit} disabled={uploading}>
				{uploading ? 'Subiendo...' : 'Subir documento'}
			</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>
