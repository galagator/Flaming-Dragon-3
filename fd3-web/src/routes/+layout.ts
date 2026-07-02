// Disable SSR — the SvelteKit app talks to a separate Node API on :6060
// via Vite's dev proxy, and all pages are interactive tools.
export const ssr = false;
export const prerender = false;
