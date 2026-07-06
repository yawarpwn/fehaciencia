import { json, error } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
//import { EXTERNAL_API_URL, EXTERNAL_API_KEY } from '$env/static/private';

const EXTERNAL_API_URL = 'http://localhost:8000/sales-invoices/upload';
const EXTERNAL_API_KEY = '';

export const POST: RequestHandler = async ({ request }) => {
	const formData = await request.formData();

	const file = formData.get('file');
	const documentType = formData.get('documentType');
	const invoiceId = formData.get('invoiceId');

	if (!(file instanceof File)) {
		throw error(400, 'Archivo inválido');
	}
	if (!documentType || !invoiceId) {
		throw error(400, 'Faltan campos requeridos');
	}

	// Reenviamos a la API externa
	const externalForm = new FormData();
	externalForm.append('file', file, file.name);
	externalForm.append('document_type', documentType);
	externalForm.append('invoice_id', invoiceId);

	const res = await fetch(EXTERNAL_API_URL, {
		method: 'POST',
		// headers: {
		// 	Authorization: `Bearer ${EXTERNAL_API_KEY}`
		// },
		body: externalForm
	});

	if (!res.ok) {
		const text = await res.text().catch(() => '');
		throw error(res.status, `Error de la API externa: ${text || res.statusText}`);
	}

	const data = await res.json();
	return json(data);
};
