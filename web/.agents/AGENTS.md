# Reglas y Contexto del Proyecto TellDocs - Web

Este archivo contiene el contexto del proyecto y directrices específicas para el desarrollo del frontend de TellDocs.

## 📋 Descripción del Proyecto

Es un dashboard web para visualizar y gestionar facturas de venta (`SalesInvoice`) y verificar la completitud de sus documentos adjuntos (PDFs de facturas, órdenes de compra, guías de remisión, fotos, vouchers de pago, etc.).

## 🛠️ Tecnologías y Estructura

- **Framework Web**: [SvelteKit 2](https://kit.svelte.dev/) con [Svelte 5](https://svelte.dev/) (usando Runes como `$state`, `$derived`, `$props`, `$effect`).
- **Styling/CSS**: [Tailwind CSS v4](https://tailwindcss.com/) (integrado mediante `@tailwindcss/vite`).
- **Tablas**: [@tanstack/table-core](https://tanstack.com/table) usando un wrapper reactivo adaptado para Svelte 5 en `src/lib/components/ui/data-table/data-table.svelte.ts`.
- **Componentes**: [shadcn-svelte](https://shadcn-svelte.com/) y [bits-ui](https://bits-ui.com/).
- **Iconos**: [@lucide/svelte](https://lucide.dev/) (se importan directamente desde `@lucide/svelte/icons/{nombre-icono}`).

### Estructura de Directorios

- `src/routes/invoices/`: Módulo principal de visualización de facturas.
  - `+page.svelte`: Consume `data` y renderiza el componente `DataTable`.
  - `+page.server.ts`: Carga las facturas desde la API backend de manera paginada.
  - `data-table.svelte`: Implementación de la tabla TanStack y los controles de paginación server-side.
  - `columns.ts`: Definición de columnas de la tabla (monto, fecha, estado, visualizadores de documentos).
- `src/lib/components/ui/`: Componentes básicos reutilizables (botones, tablas, dropdowns, etc.).

---

## ⚙️ Reglas de Codificación y Paginación

1. **Paginación Server-Side**:
   - Se realiza mediante parámetros de consulta en la URL (`page`, `limit`).
   - La tabla en `data-table.svelte` recibe un prop `pagination` y renderiza los controles de navegación.
   - Para cambiar de página se usa la función helper `getPageUrl(pageNum)` que preserva otros query parameters usando `$page.url` y navega vía enlaces standard o mediante `goto` al cambiar de límite.
   - El backend FastAPI retorna los registros en el body de la respuesta y el total de registros en la cabecera `X-Total-Count`.

2. **Reactividad en Svelte 5 (Runes)**:
   - Al destrechar propiedades o crear instancias de componentes reactivos (como `createSvelteTable`), usa getters en las propiedades reactivas (por ejemplo, `get data() { return data; }` y `get columns() { return columns; }`) para que los cambios se propaguen correctamente.

3. **Consumo de APIs**:
   - El endpoint principal para facturas es `http://localhost:8000/sales-invoices`.
