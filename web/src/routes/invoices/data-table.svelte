<script lang="ts" generics="TData, TValue">
	import { type ColumnDef, getCoreRowModel } from '@tanstack/table-core';
	import { createSvelteTable, FlexRender } from '$lib/components/ui/data-table/index.js';
	import * as Table from '$lib/components/ui/table/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import ChevronLeftIcon from '@lucide/svelte/icons/chevron-left';
	import ChevronRightIcon from '@lucide/svelte/icons/chevron-right';
	import ChevronsLeftIcon from '@lucide/svelte/icons/chevrons-left';
	import ChevronsRightIcon from '@lucide/svelte/icons/chevrons-right';
	import SearchIcon from '@lucide/svelte/icons/search';
	import XIcon from '@lucide/svelte/icons/x';

	type DataTableProps<TData, TValue> = {
		columns: ColumnDef<TData, TValue>[];
		data: TData[];
		pagination?: {
			page: number;
			limit: number;
			total: number;
			totalPages: number;
		};
		q?: string;
	};

	let { data, columns, pagination, q = '' }: DataTableProps<TData, TValue> = $props();

	const table = createSvelteTable({
		get data() {
			return data;
		},
		get columns() {
			return columns;
		},
		getCoreRowModel: getCoreRowModel()
	});

	let searchVal = $state('');

	$effect(() => {
		searchVal = q;
	});

	let debounceTimeout: ReturnType<typeof setTimeout>;

	function handleSearch() {
		clearTimeout(debounceTimeout);
		debounceTimeout = setTimeout(() => {
			const url = new URL($page.url);
			url.searchParams.set('page', '1');
			if (searchVal.trim()) {
				url.searchParams.set('q', searchVal);
			} else {
				url.searchParams.delete('q');
			}
			goto(url.pathname + url.search, { keepFocus: true });
		}, 300);
	}

	function clearSearch() {
		searchVal = '';
		const url = new URL($page.url);
		url.searchParams.set('page', '1');
		url.searchParams.delete('q');
		goto(url.pathname + url.search);
	}

	function getPageUrl(pageNum: number) {
		const url = new URL($page.url);
		url.searchParams.set('page', pageNum.toString());
		return url.pathname + url.search;
	}
</script>

<div class="flex items-center py-4">
	<div class="relative w-full max-w-sm">
		<SearchIcon class="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
		<input
			type="text"
			placeholder="Buscar por ID, RUC o cliente..."
			class="h-9 w-full rounded-md border border-input bg-transparent pl-8 pr-8 text-sm outline-none focus:ring-2 focus:ring-ring focus:border-ring transition-shadow"
			value={searchVal}
			oninput={(e) => {
				searchVal = e.currentTarget.value;
				handleSearch();
			}}
		/>
		{#if searchVal}
			<button
				type="button"
				class="absolute right-2.5 top-2.5 h-4 w-4 text-muted-foreground hover:text-foreground cursor-pointer flex items-center justify-center rounded-sm hover:bg-muted"
				onclick={clearSearch}
			>
				<XIcon class="size-4" />
			</button>
		{/if}
	</div>
</div>

<div class="rounded-md border">
	<Table.Root>
		<Table.Header>
			{#each table.getHeaderGroups() as headerGroup (headerGroup.id)}
				<Table.Row>
					{#each headerGroup.headers as header (header.id)}
						<Table.Head colspan={header.colSpan}>
							{#if !header.isPlaceholder}
								<FlexRender
									content={header.column.columnDef.header}
									context={header.getContext()}
								/>
							{/if}
						</Table.Head>
					{/each}
				</Table.Row>
			{/each}
		</Table.Header>
		<Table.Body>
			{#each table.getRowModel().rows as row (row.id)}
				<Table.Row data-state={row.getIsSelected() && 'selected'}>
					{#each row.getVisibleCells() as cell (cell.id)}
						<Table.Cell>
							<FlexRender content={cell.column.columnDef.cell} context={cell.getContext()} />
						</Table.Cell>
					{/each}
				</Table.Row>
			{:else}
				<Table.Row>
					<Table.Cell colspan={columns.length} class="h-24 text-center">No results.</Table.Cell>
				</Table.Row>
			{/each}
		</Table.Body>
	</Table.Root>
</div>

{#if pagination}
	<div class="flex flex-col sm:flex-row items-center justify-between gap-4 px-2 py-4">
		<div
			class="flex flex-wrap items-center gap-4 sm:gap-6 w-full sm:w-auto justify-between sm:justify-start"
		>
			<div class="text-sm text-muted-foreground">
				Mostrando
				<span class="font-medium"
					>{Math.min((pagination.page - 1) * pagination.limit + 1, pagination.total)}</span
				>
				al
				<span class="font-medium"
					>{Math.min(pagination.page * pagination.limit, pagination.total)}</span
				>
				de
				<span class="font-medium">{pagination.total}</span>
				facturas
			</div>

			<div class="flex items-center space-x-2">
				<p class="text-sm font-medium text-muted-foreground">Filas por página</p>
				<select
					class="h-8 w-[70px] rounded-md border border-input bg-transparent px-1 py-0.5 text-sm outline-none focus:ring-2 focus:ring-ring focus:border-ring transition-shadow cursor-pointer"
					value={pagination.limit}
					onchange={(e) => {
						const select = e.currentTarget;
						const limit = select.value;
						const url = new URL($page.url);
						url.searchParams.set('page', '1');
						url.searchParams.set('limit', limit);
						goto(url.pathname + url.search);
					}}
				>
					{#each [10, 15, 20, 50, 100] as size}
						<option value={size} class="bg-background">{size}</option>
					{/each}
				</select>
			</div>
		</div>

		<div class="flex items-center space-x-2">
			<Button
				variant="outline"
				size="icon-sm"
				href={pagination.page > 1 ? getPageUrl(1) : undefined}
				disabled={pagination.page <= 1}
				title="Primera página"
			>
				<ChevronsLeftIcon class="size-4" />
			</Button>
			<Button
				variant="outline"
				size="icon-sm"
				href={pagination.page > 1 ? getPageUrl(pagination.page - 1) : undefined}
				disabled={pagination.page <= 1}
				title="Página anterior"
			>
				<ChevronLeftIcon class="size-4" />
			</Button>

			<div class="text-sm font-medium px-2 select-none">
				Página {pagination.page} de {pagination.totalPages}
			</div>

			<Button
				variant="outline"
				size="icon-sm"
				href={pagination.page < pagination.totalPages ? getPageUrl(pagination.page + 1) : undefined}
				disabled={pagination.page >= pagination.totalPages}
				title="Página siguiente"
			>
				<ChevronRightIcon class="size-4" />
			</Button>
			<Button
				variant="outline"
				size="icon-sm"
				href={pagination.page < pagination.totalPages
					? getPageUrl(pagination.totalPages)
					: undefined}
				disabled={pagination.page >= pagination.totalPages}
				title="Última página"
			>
				<ChevronsRightIcon class="size-4" />
			</Button>
		</div>
	</div>
{/if}
