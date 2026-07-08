# TellDocs - Sistema de Gestión de Fehaciencia de Documentos

TellDocs es una aplicación web y API diseñada para recibir, organizar y verificar fotos y documentos relacionados con facturas de ventas, guías de remisión, depósitos bancarios, órdenes de compra y más.

El proyecto está estructurado como una aplicación monorepo con un backend en **FastAPI** y un frontend en **SvelteKit**.

---

## 🏛️ Arquitectura del Sistema

El sistema se divide en tres componentes principales:

1. **Frontend (SvelteKit)**: Servido en el puerto `7730` por defecto. Es el encargado de renderizar la interfaz de usuario, validar sesiones mediante cookies y realizar peticiones proxies hacia la API.
2. **Backend (FastAPI)**: Servido en el puerto `7780` por defecto. Maneja la lógica de negocio, procesamiento de imágenes (generación de miniaturas), y base de datos.
3. **Base de Datos (SQLite + SQLModel)**: Almacén local ligero configurado en modo WAL para optimizar lecturas/escrituras.

---

## 🔐 Sistema de Autenticación (Implementado)

Se ha integrado un sistema de autenticación simple y seguro basado en **Tokens JWT sin estado (stateless)** y **Cookies HttpOnly**.

### Flujo de Autenticación
1. El usuario inicia sesión en la raíz `/` de la aplicación web.
2. SvelteKit realiza una solicitud `POST` interna al endpoint del backend `/auth/login`.
3. El backend verifica la existencia del usuario y compara las contraseñas usando `bcrypt`.
4. Si las credenciales son válidas, el backend responde con un token JWT firmado.
5. El servidor SvelteKit almacena este token en una cookie cifrada llamada `session_token` configurada como `HttpOnly` y `SameSite: Lax`.
6. Al navegar, el hook global de servidor `web/src/hooks.server.ts` verifica la existencia del token:
   * Si no hay token y la ruta es protegida (`/invoices` o `/api/*`), redirige a `/`.
   * Si hay token e intenta acceder a `/`, redirige automáticamente a `/invoices`.
7. En cada solicitud de carga de datos (`load` y endpoints API en SvelteKit), el token se recupera de la cookie y se envía al API de FastAPI en el header `Authorization: Bearer <token>`.

### Configuración del Entorno (`.env` o Variables de Sistema)
* `JWT_SECRET_KEY`: Llave utilizada para firmar tokens JWT (Backend).
* `JWT_ALGORITHM`: Algoritmo de cifrado del token (por defecto `HS256`).
* `ACCESS_TOKEN_EXPIRE_MINUTES`: Minutos de validez del token (por defecto `1440` (24 horas)).
* `DEFAULT_ADMIN_PASSWORD`: Contraseña inicial del administrador por defecto (por defecto `admin123`).

---

## 📂 Estructura del Código

### Backend (`/api`)
* [app/config.py](file:///home/johneyder/dev/fehaciencia-tell/api/app/config.py): Variables de entorno, rutas de base de datos y llaves de cifrado.
* [app/core/auth.py](file:///home/johneyder/dev/fehaciencia-tell/api/app/core/auth.py): Lógica de hashing de contraseñas (`bcrypt`), creación de tokens JWT y dependencia de ruta `get_current_user`.
* [app/core/database.py](file:///home/johneyder/dev/fehaciencia-tell/api/app/core/database.py): Inicialización de tablas y sembrado automático del usuario `admin` por defecto.
* [app/modules/auth/model.py](file:///home/johneyder/dev/fehaciencia-tell/api/app/modules/auth/model.py): Definición de la entidad `User` en la base de datos SQLite.
* [app/modules/auth/route.py](file:///home/johneyder/dev/fehaciencia-tell/api/app/modules/auth/route.py): Endpoints de autenticación (`/auth/login`, `/auth/me`).
* [app/modules/sales_invoices/route.py](file:///home/johneyder/dev/fehaciencia-tell/api/app/modules/sales_invoices/route.py) y [app/modules/upload/route.py](file:///home/johneyder/dev/fehaciencia-tell/api/app/modules/upload/route.py): Rutas protegidas mediante la inyección de la dependencia de seguridad.

### Frontend (`/web`)
* [src/hooks.server.ts](file:///home/johneyder/dev/fehaciencia-tell/web/src/hooks.server.ts): Interceptor global de rutas y validación de cookies de sesión.
* [src/app.d.ts](file:///home/johneyder/dev/fehaciencia-tell/web/src/app.d.ts): Tipado global para la propiedad `locals.token`.
* [src/routes/+layout.server.ts](file:///home/johneyder/dev/fehaciencia-tell/web/src/routes/+layout.server.ts): Carga el estado de autenticación a todos los layouts del cliente.
* [src/lib/components/site-header.svelte](file:///home/johneyder/dev/fehaciencia-tell/web/src/lib/components/site-header.svelte): Barra de navegación global, adaptada para renderizar el botón de **Cerrar Sesión**.
* [src/routes/+page.svelte](file:///home/johneyder/dev/fehaciencia-tell/web/src/routes/+page.svelte) y [src/routes/+page.server.ts](file:///home/johneyder/dev/fehaciencia-tell/web/src/routes/+page.server.ts): Vista de Login premium (Glassmorphism) y controlador de inicio de sesión.
* [src/routes/logout/+page.server.ts](file:///home/johneyder/dev/fehaciencia-tell/web/src/routes/logout/+page.server.ts): Manejador POST que destruye la cookie de sesión y redirige al inicio.

---

## 🛠️ Ejecución Local

Para levantar ambos servidores en modo de desarrollo local de manera simultánea, utiliza el script proporcionado en la raíz:

```bash
chmod +x dev.sh
./dev.sh
```

Esto ejecutará:
1. **FastAPI**: `http://localhost:7780` (Documentación Swagger disponible en `/docs`).
2. **SvelteKit**: `http://localhost:7730`.

### Credenciales Iniciales por Defecto
* **Usuario**: `admin`
* **Contraseña**: `admin123`
