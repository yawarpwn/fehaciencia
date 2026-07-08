import { redirect } from '@sveltejs/kit';
import type { Actions } from './$types';

export const actions: Actions = {
	default: async ({ cookies }) => {
		cookies.delete('session_token', { path: '/' });
		throw redirect(303, '/');
	}
};
export const load = () => {
	// Redirección de seguridad si acceden por GET
	throw redirect(303, '/');
};
