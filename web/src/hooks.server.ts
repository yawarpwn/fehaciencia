import { redirect, type Handle } from '@sveltejs/kit';

export const handle: Handle = async ({ event, resolve }) => {
	const token = event.cookies.get('session_token');
	const pathname = event.url.pathname;

	// Rutas protegidas (panel de facturas y APIs internas de facturas)
	const isProtectedRoute = pathname.startsWith('/invoices') || pathname.startsWith('/api/');
	const isRootRoute = pathname === '/';

	if (isProtectedRoute && !token) {
		throw redirect(303, '/');
	}

	if (isRootRoute && token) {
		// Si ya está autenticado, redirigir directo a /invoices
		throw redirect(303, '/invoices');
	}

	// Almacenar el token en locals para usarlo en load o endpoints del servidor
	event.locals.token = token;

	const response = await resolve(event);
	return response;
};
