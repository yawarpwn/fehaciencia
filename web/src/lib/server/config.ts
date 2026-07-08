import { dev } from '$app/environment';
import { env } from '$env/dynamic/private';

export const SERVER_CONFIG = {
	isDev: dev,
	isProd: !dev,

	apiUrl: env.API_URL || (dev ? 'http://localhost:7780' : '')
};
