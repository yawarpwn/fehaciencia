import { json, error } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { SERVER_CONFIG } from '@/server/config';

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

	if (!SERVER_CONFIG.apiUrl) {
		throw error(500, 'La variabla API_URL no esta configurada en el servidor');
	}

	// Reenviamos a la API externa
	const externalForm = new FormData();
	externalForm.append('file', file, file.name);
	externalForm.append('document_type', documentType);
	externalForm.append('invoice_id', invoiceId);

	const url = `${SERVER_CONFIG.apiUrl}/sales-invoices/upload`;
	console.log(`Upload url ${url}`);
	const res = await fetch(`${SERVER_CONFIG.apiUrl}/sales-invoices/upload`, {
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
