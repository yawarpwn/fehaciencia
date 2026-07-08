<script lang="ts">
	import { page } from '$app/stores';
	import { Button } from '@/components/ui/button';
</script>

<header class="bg-background border-b border-border/20 sticky top-0 z-50 w-full px-4">
	<div class="flex justify-between h-16 items-center">
		<div>
			<!-- <h1>Fehaciencia<span class="text-yellow-300 uppercase">TELL</span></h1> -->
			<a href="/" class="text-2xl font-bold">
				Fehaciencia<span class="uppercase font-extrabold text-yellow-300">TELL</span>
			</a>
		</div>
		<div>
			{#if $page.data.isAuthenticated}
				<form action="/logout" method="POST" class="inline-block">
					<Button
						type="submit"
						variant="ghost"
						class="text-slate-300 hover:text-white hover:bg-slate-800 text-sm font-semibold px-3 py-1.5 rounded-lg transition-all duration-200"
					>
						Cerrar Sesión
					</Button>
				</form>
			{/if}
		</div>
	</div>
</header>
