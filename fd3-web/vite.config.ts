import { sveltekit } from '@sveltejs/kit/vite';
import adapter from '@sveltejs/adapter-static';
import { defineConfig } from 'vite';

const API_TARGET = process.env.FD3_API || 'http://localhost:6060';

export default defineConfig({
	plugins: [
		sveltekit({
			compilerOptions: {
				runes: ({ filename }) =>
					filename.split(/[/\\]/).includes('node_modules') ? undefined : true
			},
			adapter: adapter({ fallback: 'index.html' })
		})
	],
	server: {
		port: 5173,
		proxy: {
			'/api': { target: API_TARGET, changeOrigin: true },
			'/save': { target: API_TARGET, changeOrigin: true },
			'/recrop': { target: API_TARGET, changeOrigin: true },
			'/character-references': { target: API_TARGET, changeOrigin: true },
			'/character-sheets': { target: API_TARGET, changeOrigin: true },
			'/actor-photos-raw': { target: API_TARGET, changeOrigin: true }
		}
	}
});
