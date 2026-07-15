import tailwindcss from '@tailwindcss/vite';
import adapter from '@sveltejs/adapter-node';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
const API_TARGET = process.env.API_URL || 'http://localhost:8000';
export default defineConfig({
	plugins: [
		tailwindcss(),
		sveltekit({
			compilerOptions: {
				// Force runes mode for the project, except for libraries. Can be removed in svelte 6.
				runes: ({ filename }) =>
					filename.split(/[/\\]/).includes('node_modules') ? undefined : true
			},
			adapter: adapter(),
			alias: {
				'@/*': './src/lib/*'
			},
			csrf: {
				trustedOrigins: [API_TARGET]
			}
		})
	],
	server: {
		port: 7730,
		proxy: {
			'/documents': {
				target: API_TARGET,
				changeOrigin: true,
				// Esto asegura que si la API se demora en responder imágenes grandes, no se caiga
				secure: false
			}
		}
	}
});
