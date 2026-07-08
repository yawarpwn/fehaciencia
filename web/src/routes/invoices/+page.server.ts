import type { PageServerLoad } from './$types';
import type { SaleInvoice } from '$lib/types';
import { SERVER_CONFIG } from '@/server/config';

async function fetchInvoices(
	page: number,
	limit: number,
	q: string
): Promise<{ invoices: SaleInvoice[]; total: number }> {
	const url = new URL(`${SERVER_CONFIG.apiUrl}/sales-invoices`);
	url.searchParams.set('page', page.toString());
	url.searchParams.set('limit', limit.toString());
	if (q) {
		url.searchParams.set('q', q);
	}
	const res = await fetch(url.toString());
	const invoices = await res.json();
	const totalHeader = res.headers.get('X-Total-Count');
	const total = totalHeader ? parseInt(totalHeader, 10) : invoices.length;
	return { invoices, total };
}

export const load: PageServerLoad = async ({ url }) => {
	const page = Number(url.searchParams.get('page') ?? '1');
	const limit = Number(url.searchParams.get('limit') ?? '10');
	const q = url.searchParams.get('q') ?? '';

	try {
		const { invoices, total } = await fetchInvoices(page, limit, q);
		return {
			invoices,
			pagination: {
				page,
				limit,
				total,
				totalPages: Math.ceil(total / limit)
			},
			q
		};
	} catch (error) {
		console.error('Error fetching invoices:', error);
		return {
			invoices: [],
			pagination: {
				page,
				limit,
				total: 0,
				totalPages: 0
			},
			q
		};
	}
};
