// columns.ts
import type { ColumnDef } from '@tanstack/table-core';
import { createRawSnippet } from 'svelte';
import { renderComponent, renderSnippet } from '$lib/components/ui/data-table/index.js';
import DataTableAction from './data-table-action.svelte';
import SingleDocStatus from '$lib/components/single-doc-status.svelte';
import MultiDocThumbnails from '@/components/multi-doc-thumbnails.svelte';
import { MULTI_DOC_META, MULTI_DOC_ORDER } from '$lib/constants';
import type { InvoiceStatus, SaleInvoice } from '$lib/types';
import ShoppingCartIcon from '@lucide/svelte/icons/shopping-cart';
import FileText from '@lucide/svelte/icons/file';

const formatter = new Intl.NumberFormat('es-PE', { style: 'currency', currency: 'PEN' });
const dateFormater = new Intl.DateTimeFormat('es-PE', {
	day: '2-digit',
	month: '2-digit'
});

export const columns: ColumnDef<SaleInvoice>[] = [
	{
		header: 'Factura',
		accessorKey: 'invoiceId'
	},
	{
		accessorKey: 'period',
		header: 'Periodo'

		// cell: ({ row }) => {
		// 	const snippet = createRawSnippet<[string]>((getPeriod) => ({
		// 		render: () => `<span class="capitalize">${formatPeriod(getPeriod())}</span>`
		// 	}));
		// 	return renderSnippet(snippet, row.original.period);
		// }
	},
	{
		id: 'Fecha',
		header: 'Fecha',
		cell: ({ row }) => {
			const issueDate = row.original.issueDate;

			const dateCellSnippet = createRawSnippet<[{ issueDate: string }]>((getIsuue) => {
				const { issueDate } = getIsuue();

				return {
					render: () =>
						`<div class="text-end font-medium">${dateFormater.format(new Date(issueDate))}</div>`
				};
			});

			return renderSnippet(dateCellSnippet, { issueDate });
		}
	},
	{
		accessorKey: 'customerRuc',
		header: 'Ruc'
	},
	{
		accessorKey: 'customerShortName',
		header: 'Cliente'
	},
	{
		id: 'total',
		header: 'Monto',
		cell: ({ row }) => {
			const amountCellSnippet = createRawSnippet<[{ amount: number }]>((getAmount) => {
				const { amount } = getAmount();
				return {
					render: () => `<div class="text-end font-medium">${formatter.format(amount)}</div>`
				};
			});
			return renderSnippet(amountCellSnippet, { amount: row.original.totalAmount });
		}
	},
	{
		id: 'Factura',
		header: 'FA',
		cell: ({ row }) => {
			return renderComponent(SingleDocStatus, {
				document: row.original.pdfFile,
				label: 'mee',
				icon: FileText
			});
		}
	},
	{
		id: 'purchaseOrder',
		header: 'OC',
		cell: ({ row }) => {
			return renderComponent(SingleDocStatus, {
				document: row.original.purchaseOrder,
				label: 'mee',
				icon: ShoppingCartIcon
			});
		}
	},
	// Columnas de documentos únicos — generadas dinámicamente desde SINGLE_DOC_ORDER
	...MULTI_DOC_ORDER.map((docType): ColumnDef<SaleInvoice> => ({
		id: docType,
		header: MULTI_DOC_META[docType].shortLabel,
		meta: { tooltip: MULTI_DOC_META[docType].label }, // para tooltip en el header si lo quieres
		cell: ({ row }) => {
			const key = {
				PHOTO: 'photos',
				DELIVERY_GUIDE: 'deliveryGuides',
				AGENCY_GUIDE: 'agencyGuides',
				DELIVERY_GUIDE_SIGNED: 'signedDeliveryGuides',
				PAYMENT_VOUCHER: 'vouchers'
			}[docType] as keyof SaleInvoice;

			const documents = row.original[key] as any;

			return renderComponent(MultiDocThumbnails, {
				documents: documents,
				icon: MULTI_DOC_META[docType].icon,
				invoice: row.original,
				docType: docType
			});
		}
	})),
	{
		id: 'status',
		header: 'Estado',
		cell: ({ row }) => {
			const { missing, status } = row.original;

			const snippet = createRawSnippet<
				[
					{
						missing: string[];
						status: InvoiceStatus;
					}
				]
			>((getData) => {
				const { missing, status } = getData();

				if (status === 'VOIDED') {
					return {
						render: () =>
							`<span class="inline-flex items-center rounded-md bg-purple-50 px-2 py-1 text-xs font-medium text-purple-700 dark:bg-purple-950 dark:text-purple-400">ANULADO</span>`
					};
				}

				if (status === 'ADVANCE') {
					return {
						render: () =>
							`<span class="inline-flex items-center rounded-md bg-orange-50 px-2 py-1 text-xs font-medium text-orange-700 dark:bg-orange-950 dark:text-orange-400">ANTICIPO</span>`
					};
				}

				if (status === 'COMPLETE') {
					return {
						render: () =>
							`<span class="inline-flex items-center rounded-md bg-green-50 px-2 py-1 text-xs font-medium text-green-700 dark:bg-green-950 dark:text-green-400">Completo</span>`
					};
				}
				const tooltip = missing.join(', ');
				return {
					render: () =>
						`<span title="Falta: ${tooltip}" class="inline-flex items-center rounded-md bg-red-50 px-2 py-1 text-xs font-medium text-red-700 dark:bg-red-950 dark:text-red-400 cursor-help">${missing[0]}</span>`
				};
			});
			return renderSnippet(snippet, { missing, status });
		}
	},
	{
		id: 'action',
		cell: ({ row }) => renderComponent(DataTableAction, { invoice: row.original })
	}
];
