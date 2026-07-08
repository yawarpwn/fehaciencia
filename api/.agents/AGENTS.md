# Reglas y Contexto del Proyecto TellDocs

Este archivo contiene el contexto del proyecto y las directrices específicas para el desarrollo de la API TellDocs.

## 📋 Descripción del Proyecto

TellDocs es una API desarrollada en Python para la recepción, almacenamiento y gestión de documentos de soporte (facturas XML/PDF, guías de remisión, vouchers de banco, fotos, etc.) asociados a facturas de venta (`SalesInvoice`).

## 🛠️ Tecnologías y Estructura

- **Framework Web**: [FastAPI](https://fastapi.tiangolo.com/)
- **ORM/Base de Datos**: [SQLModel](https://sqlmodel.tiangolo.com/) sobre SQLite (`data.db`) en modo **WAL** para mejor concurrencia.
- **Gestor de Paquetes**: `uv` (`pyproject.toml`, `uv.lock`).
- **Almacenamiento**: Local en disco bajo la ruta configurada en `STORAGE_PATH` (por defecto `app/storage`).

### Estructura de Directorios

- `/app/main.py`: Punto de entrada de la aplicación y configuración de FastAPI.
- `/app/config.py`: Configuraciones globales (límites de tamaño, extensiones permitidas, rutas de almacenamiento).
- `/app/core/database.py`: Configuración de la base de datos local SQLite y sesión de base de datos.
- `/app/modules/sales_invoices/`: Módulo para la gestión de facturas de venta y sus documentos adjuntos.
- `/app/modules/upload/`: Módulo encargado de recibir y validar la subida de archivos físicos.

---

## ⚙️ Reglas de Codificación e Instrucciones

1. **Modelos y Schemas**:
   - Al agregar campos a los modelos en `app/modules/sales_invoices/model.py`, asegúrate de actualizar también los esquemas de Pydantic correspondientes en `app/modules/sales_invoices/schema.py`.
2. **Control de Archivos**:
   - Las extensiones permitidas y el tamaño máximo de los archivos cargados se centralizan en `app/config.py`.
   - Todo documento físico guardado debe registrarse con un nombre único utilizando una marca de tiempo y un UUID (`{timestamp}_{uuid4()[:8]}.{ext}`).
3. **Servicio Estático**:
   - Los documentos guardados se sirven estáticamente bajo el prefijo `/documents` mediante `StaticFiles` montado sobre la ruta configurada por `STORAGE_PATH`.
4. **Sistema de Autenticación**:
   - Se implementa autenticación basada en tokens JWT usando `pyjwt` y contraseñas cifradas con `bcrypt`.
   - El enrutador `app/modules/auth/route.py` maneja los endpoints de `/auth/login` y `/auth/me`.
   - Al inicializar la base de datos (`app/core/database.py`), si no existe ningún usuario, se siembra automáticamente un usuario `admin` con la contraseña definida por la variable de entorno `DEFAULT_ADMIN_PASSWORD` (por defecto `admin123`).
   - Las rutas de los endpoints en `/sales-invoices` y `/upload` están protegidas de forma global en sus respectivos enrutadores agregando la dependencia `get_current_user` (`dependencies=[Depends(get_current_user)]`).

