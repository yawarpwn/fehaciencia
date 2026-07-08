<script lang="ts">
	import { enhance } from '$app/forms';
	import { Button } from '@/components/ui/button';

	let { form } = $props();
	let loading = $state(false);
	let errorMsg = $derived(form?.error);
</script>

<svelte:head>
	<title>Iniciar Sesión - FehacienciaDocs</title>
	<!-- <link rel="preconnect" href="https://fonts.googleapis.com" /> -->
	<!-- <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous" /> -->
	<!-- <link -->
	<!-- 	href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap" -->
	<!-- 	rel="stylesheet" -->
	<!-- /> -->
</svelte:head>

<div class="login-container">
	<!-- Elementos de fondo decorativos animados -->
	<div class="glow-sphere sphere-1"></div>
	<div class="glow-sphere sphere-2"></div>

	<div class="glass-card">
		<div class="card-header">
			<h1>Fehaciencia<span class="text-yellow-300 uppercase">TELL</span></h1>
			<p class="subtitle">Ingresa tus credenciales para acceder al sistema</p>
		</div>

		<form
			method="POST"
			use:enhance={() => {
				loading = true;
				return async ({ update }) => {
					await update();
					loading = false;
				};
			}}
			class="login-form"
		>
			{#if errorMsg}
				<div class="error-banner">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						viewBox="0 0 24 24"
						fill="currentColor"
						class="w-5 h-5 flex-shrink-0"
					>
						<path
							fill-rule="evenodd"
							d="M9.401 3.003c1.155-2 4.043-2 5.197 0l7.355 12.748c1.154 2-.29 4.5-2.599 4.5H4.645c-2.309 0-3.752-2.5-2.598-4.5L9.401 3.003ZM12 8.25a.75.75 0 0 1 .75.75v3.75a.75.75 0 0 1-1.5 0V9a.75.75 0 0 1 .75-.75Zm0 8.25a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Z"
							clip-rule="evenodd"
						/>
					</svg>
					<span>{errorMsg}</span>
				</div>
			{/if}

			<div class="input-group">
				<label for="username">Usuario</label>
				<div class="input-wrapper">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						fill="none"
						viewBox="0 0 24 24"
						stroke-width="1.5"
						stroke="currentColor"
						class="input-icon"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z"
						/>
					</svg>
					<input
						type="text"
						id="username"
						name="username"
						required
						autocomplete="username"
						placeholder="ej. admin"
						disabled={loading}
					/>
				</div>
			</div>

			<div class="input-group">
				<label for="password">Contraseña</label>
				<div class="input-wrapper">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						fill="none"
						viewBox="0 0 24 24"
						stroke-width="1.5"
						stroke="currentColor"
						class="input-icon"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							d="M16.5 10.5V6.75a4.5 4.5 0 1 0-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 0 0 2.25-2.25v-6.75a2.25 2.25 0 0 0-2.25-2.25H6.75a2.25 2.25 0 0 0-2.25 2.25v6.75a2.25 2.25 0 0 0 2.25 2.25Z"
						/>
					</svg>
					<input
						type="password"
						id="password"
						name="password"
						required
						autocomplete="current-password"
						placeholder="••••••••"
						disabled={loading}
					/>
				</div>
			</div>

			<Button type="submit" class="submit-btn" disabled={loading}>
				{#if loading}
					<span class="spinner"></span>
					Iniciando sesión...
				{:else}
					Ingresar al Sistema
				{/if}
			</Button>
		</form>
	</div>
</div>

<style>
	.login-container {
		position: fixed;
		inset: 0;
		width: 100vw;
		height: 100vh;
		display: flex;
		justify-content: center;
		align-items: center;
		background: radial-gradient(circle at 50% 50%, #1a1e35 0%, #0d0f19 100%);
		z-index: 999;
	}

	/* Esferas decorativas resplandecientes en el fondo */
	.glow-sphere {
		position: absolute;
		border-radius: 50%;
		filter: blur(80px);
		opacity: 0.15;
		z-index: 1;
		pointer-events: none;
	}

	.sphere-1 {
		width: 350px;
		height: 350px;
		background: #eab308;
		top: 15%;
		left: 20%;
		animation: float-slow 12s ease-in-out infinite alternate;
	}

	.sphere-2 {
		width: 400px;
		height: 400px;
		background: #3b82f6;
		bottom: 10%;
		right: 15%;
		animation: float-slow 16s ease-in-out infinite alternate-reverse;
	}

	@keyframes float-slow {
		0% {
			transform: translate(0, 0) scale(1);
		}
		100% {
			transform: translate(40px, -40px) scale(1.1);
		}
	}

	/* Tarjeta Glassmorphic */
	.glass-card {
		position: relative;
		width: 100%;
		max-width: 440px;
		padding: 2.5rem;
		background: rgba(30, 41, 59, 0.45);
		backdrop-filter: blur(16px);
		-webkit-backdrop-filter: blur(16px);
		border: 1px solid rgba(255, 255, 255, 0.08);
		border-radius: 24px;
		box-shadow: 0 20px 50px rgba(0, 0, 0, 0.35);
		z-index: 2;
		overflow: hidden;
		animation: card-appear 0.6s cubic-bezier(0.16, 1, 0.3, 1) both;
	}

	@keyframes card-appear {
		0% {
			opacity: 0;
			transform: translateY(20px) scale(0.98);
		}
		100% {
			opacity: 1;
			transform: translateY(0) scale(1);
		}
	}

	.card-header {
		text-align: center;
		margin-bottom: 2rem;
	}

	@keyframes pulse-ring {
		0%,
		100% {
			box-shadow: 0 0 0 0 rgba(234, 179, 8, 0.1);
		}
		50% {
			box-shadow: 0 0 15px 4px rgba(234, 179, 8, 0.2);
		}
	}

	h1 {
		font-size: 2rem;
		font-weight: 800;
		color: #ffffff;
		margin: 0 0 0.5rem 0;
		letter-spacing: -0.025em;
	}

	.subtitle {
		font-size: 0.875rem;
		color: #94a3b8;
		margin: 0;
		font-weight: 300;
	}

	.login-form {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
	}

	.error-banner {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		background: rgba(239, 68, 68, 0.15);
		border: 1px solid rgba(239, 68, 68, 0.3);
		color: #fca5a5;
		padding: 0.875rem 1rem;
		border-radius: 12px;
		font-size: 0.85rem;
		line-height: 1.4;
		animation: shake 0.4s ease-in-out;
	}

	@keyframes shake {
		0%,
		100% {
			transform: translateX(0);
		}
		25% {
			transform: translateX(-4px);
		}
		75% {
			transform: translateX(4px);
		}
	}

	.input-group {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	label {
		font-size: 0.875rem;
		font-weight: 600;
		color: #cbd5e1;
		margin-left: 0.25rem;
	}

	.input-wrapper {
		position: relative;
		display: flex;
		align-items: center;
	}

	.input-icon {
		position: absolute;
		left: 1rem;
		width: 1.25rem;
		height: 1.25rem;
		color: #64748b;
		pointer-events: none;
		transition: color 0.2s ease;
	}

	input {
		width: 100%;
		padding: 0.875rem 1rem 0.875rem 2.75rem;
		background: rgba(15, 23, 42, 0.6);
		border: 1px solid rgba(255, 255, 255, 0.08);
		border-radius: 12px;
		color: #ffffff;
		font-size: 0.95rem;
		transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
	}

	input::placeholder {
		color: #475569;
	}

	input:focus {
		outline: none;
		border-color: rgba(234, 179, 8, 0.5);
		background: rgba(15, 23, 42, 0.8);
		box-shadow: 0 0 0 4px rgba(234, 179, 8, 0.12);
	}

	input:focus + :global(.input-icon) {
		color: #eab308;
	}

	/* Sobrescribir estilos de Button de shadcn para hacerlo premium */
	:global(.submit-btn) {
		width: 100%;
		padding: 1.4rem !important;
		font-size: 1rem !important;
		font-weight: 700 !important;
		border-radius: 12px !important;
		background: linear-gradient(135deg, #eab308 0%, #ca8a04 100%) !important;
		color: #0f172a !important;
		border: none !important;
		cursor: pointer;
		box-shadow: 0 4px 15px rgba(234, 179, 8, 0.3) !important;
		transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
		position: relative;
		overflow: hidden;
		display: flex;
		justify-content: center;
		align-items: center;
		gap: 0.5rem;
	}

	:global(.submit-btn:hover:not(:disabled)) {
		transform: translateY(-2px);
		box-shadow: 0 8px 25px rgba(234, 179, 8, 0.45) !important;
		opacity: 0.95;
	}

	:global(.submit-btn:active:not(:disabled)) {
		transform: translateY(0);
	}

	:global(.submit-btn:disabled) {
		opacity: 0.6;
		cursor: not-allowed;
	}

	/* Spinner */
	.spinner {
		width: 18px;
		height: 18px;
		border: 2px solid rgba(15, 23, 42, 0.25);
		border-top-color: #0f172a;
		border-radius: 50%;
		animation: spin 0.8s linear infinite;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}

	/* Responsivo */
	@media (max-width: 480px) {
		.glass-card {
			padding: 2rem 1.5rem;
			border-radius: 16px;
			max-width: calc(100vw - 2rem);
		}
	}
</style>
