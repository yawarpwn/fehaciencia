import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { SERVER_CONFIG } from '@/server/config';

export const load: PageServerLoad = async ({ locals }) => {
	if (locals.token) {
		throw redirect(303, '/invoices');
	}
	return {};
};

export const actions: Actions = {
	default: async ({ request, cookies }) => {
		const data = await request.formData();
		const username = data.get('username')?.toString();
		const password = data.get('password')?.toString();

		if (!username || !password) {
			return fail(400, { error: 'El usuario y la contraseña son requeridos' });
		}

		try {
			const res = await fetch(`${SERVER_CONFIG.apiUrl}/auth/login`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ username, password })
			});

			if (!res.ok) {
				const errData = await res.json().catch(() => ({ detail: 'Credenciales inválidas' }));
				return fail(401, { error: errData.detail || 'Usuario o contraseña incorrectos' });
			}

			const loginData = await res.json();

			// Guardamos el token en la cookie
			cookies.set('session_token', loginData.access_token, {
				path: '/',
				httpOnly: true,
				sameSite: 'lax',
				secure: SERVER_CONFIG.isProd,
				maxAge: 60 * 60 * 24 // 24 horas
			});

			throw redirect(303, '/invoices');
		} catch (err: any) {
			if (err.status === 303) {
				throw err; // Relanzar redirección de SvelteKit
			}
			console.error('Error en el login action:', err);
			return fail(500, { error: 'Error de conexión con el servidor de autenticación' });
		}
	}
};
