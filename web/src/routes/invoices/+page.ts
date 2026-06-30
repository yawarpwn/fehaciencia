import type { PageLoad } from './$types';

async function fetchInvoices() {
	const res = await fetch('http://localhost:8000/sales-invoices');
	return res.json();
}

export const load: PageLoad = async () => {
	try {
		const invoices = await fetchInvoices();
		return { invoices };
	} catch (error) {
		console.log(error);
		return {
			invoices: []
		};
	}
};
