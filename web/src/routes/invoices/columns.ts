// columns.ts
import type { ColumnDef } from '@tanstack/table-core';
import { createRawSnippet } from 'svelte';
import { renderComponent, renderSnippet } from '$lib/components/ui/data-table/index.js';
import DataTableAction from './data-table-action.svelte';
import SingleDocStatus from '$lib/components/single-doc-status.svelte';
import MultiDocThumbnails from '@/components/multi-doc-thumbnails.svelte';
import TruckIcon from '@lucide/svelte/icons/truck';
import FileSignatureIcon from '@lucide/svelte/icons/file-signature';
import LandMarkIcon from '@lucide/svelte/icons/landmark';
import ImageOffIcon from '@lucide/svelte/icons/image-off';
import type { InvoiceStatus, SaleInvoice } from '$lib/types';
import ShoppingCartIcon from '@lucide/svelte/icons/shopping-cart';
import InvoiceLink from '$lib/components/invoice-link.svelte';
import DeliveryNoteLink from '@/components/delivery_note-link.svelte';

const formatter = (currency: string | undefined) =>
	new Intl.NumberFormat('es-PE', { style: 'currency', currency: currency });
const dateFormater = new Intl.DateTimeFormat('es-PE', {
	day: '2-digit',
	month: '2-digit'
});

export const columns: ColumnDef<SaleInvoice>[] = [
	{
		id: 'DOCUMENT_ID',
		header: 'Factura',
		cell: ({ row }) => {
			return renderComponent(InvoiceLink, { invoice: row.original });
		}
	},
	{
		accessorKey: 'period',
		header: 'Periodo'
	},
	{
		id: 'Fecha',
		header: 'Fecha',
		cell: ({ row }) => {
			const issueDate = row.original.issue_date;

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
		accessorKey: 'customer_ruc',
		header: 'Ruc'
	},
	{
		accessorKey: 'customer_short_name',
		header: 'Cliente'
	},
	{
		id: 'total',
		header: 'Monto',
		cell: ({ row }) => {
			const amountCellSnippet = createRawSnippet<[{ amount: number }]>((getAmount) => {
				const { amount } = getAmount();
				const fm = formatter(row.original.currency);
				return {
					render: () => `<div class="text-end  text-sm">${fm.format(amount)}</div>`
				};
			});
			return renderSnippet(amountCellSnippet, { amount: row.original.total_amount });
		}
	},
	{
		id: 'DELIVERY_GUIDE',
		header: 'GR',
		cell: ({ row }) => {
			return renderComponent(DeliveryNoteLink, {
				deliveryNotes: row.original.delivery_notes
			});
		}
	},
	{
		id: 'PURCHASE_ORDER',
		header: 'OC',
		cell: ({ row }) => {
			return renderComponent(SingleDocStatus, {
				fileUrl: row.original.purchase_order?.file_url,
				label: 'mee',
				icon: ShoppingCartIcon
			});
		}
	},
	{
		id: 'PHOTO',
		header: 'FT',
		cell: ({ row }) => {
			return renderComponent(MultiDocThumbnails, {
				documents: row.original.photos,
				label: 'mee',
				icon: ImageOffIcon
			});
		}
	},
	{
		id: 'DELIVERY_GUIDE_SIGNED',
		header: 'GF',
		cell: ({ row }) => {
			return renderComponent(MultiDocThumbnails, {
				documents: row.original.signed_delivery_guides,
				label: 'mee',
				icon: FileSignatureIcon
			});
		}
	},
	{
		id: 'PAYMENT_VOUCHER',
		header: 'DP',
		cell: ({ row }) => {
			return renderComponent(MultiDocThumbnails, {
				documents: row.original.payment_vouchers,
				label: 'mee',
				icon: LandMarkIcon
			});
		}
	},
	{
		id: 'AGENCY_GUIDE',
		header: 'AG',
		cell: ({ row }) => {
			return renderComponent(MultiDocThumbnails, {
				documents: row.original.agency_guides,
				label: 'mee',
				icon: TruckIcon
			});
		}
	},
	{
		id: 'status',
		header: 'Estado',
		cell: ({ row }) => {
			const { missing, status, payment_method } = row.original;

			const snippet = createRawSnippet<
				[
					{
						missing: string[];
						status: InvoiceStatus;
						paymentMethod: string;
					}
				]
			>((getData) => {
				const { missing, status, paymentMethod } = getData();

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
							`<span class="inline-flex items-center rounded-md bg-green-50 px-2 py-1 text-xs font-medium text-green-700 dark:bg-green-950 dark:text-green-400">Completo`
					};
				}
				const tooltip = missing.join(', ');
				return {
					render: () =>
						`<span title="Falta: ${tooltip}" class="inline-flex items-center rounded-md bg-red-50 px-2 py-1 text-xs font-medium text-red-700 dark:bg-red-950 dark:text-red-400 cursor-help">${missing[0]}</span>`
				};
			});
			return renderSnippet(snippet, {
				missing: missing,
				status: status,
				paymentMethod: payment_method
			});
		}
	},
	{
		id: 'paymentMethod',
		cell: ({ row }) => {
			const amountCellSnippet = createRawSnippet<[{ paymentMethod: string }]>((getAmount) => {
				const { paymentMethod } = getAmount();
				const color = paymentMethod === 'Credito' ? 'bg-orange-500' : 'bg-green-500';
				return {
					render: () => `<span class='size-1 rounded-full inline-block ${color}'></span>`
				};
			});
			return renderSnippet(amountCellSnippet, { paymentMethod: row.original.payment_method });
		}
	},
	{
		id: 'action',
		cell: ({ row }) => renderComponent(DataTableAction, { invoice: row.original })
	}
];
