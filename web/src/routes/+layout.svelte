<script lang="ts">
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg';
	import { ModeWatcher } from 'mode-watcher';
	import SiteHeader from '@/components/site-header.svelte';
	import SiteFooter from '@/components/site-footer.svelte';

	let { children } = $props();
</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>
<ModeWatcher />
<div class="bg-background relative z-10 min-h-svh flex flex-col max-w-7xl w-full mx-auto">
	<SiteHeader />
	<main class="flex flex-1 flex-col">
		{@render children()}
	</main>
	<SiteFooter />
</div>
