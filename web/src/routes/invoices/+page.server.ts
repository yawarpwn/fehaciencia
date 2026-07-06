import type { PageServerLoad } from './$types';
import type { SaleInvoice } from '$lib/types';

async function fetchInvoices(page: number, limit: number): Promise<{ invoices: SaleInvoice[]; total: number }> {
	const res = await fetch(`http://localhost:8000/sales-invoices?page=${page}&limit=${limit}`);
	const invoices = await res.json();
	const totalHeader = res.headers.get('X-Total-Count');
	const total = totalHeader ? parseInt(totalHeader, 10) : invoices.length;
	return { invoices, total };
}

export const load: PageServerLoad = async ({ url }) => {
	const page = Number(url.searchParams.get('page') ?? '1');
	const limit = Number(url.searchParams.get('limit') ?? '10');

	try {
		const { invoices, total } = await fetchInvoices(page, limit);
		return {
			invoices,
			pagination: {
				page,
				limit,
				total,
				totalPages: Math.ceil(total / limit)
			}
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
			}
		};
	}
};
