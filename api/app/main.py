from app.core.database import init_db
from contextlib import asynccontextmanager
from app.config import STORAGE_PATH

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.modules.sales_invoices.route import router as sales_invoices
from app.modules.upload.route import router as upload
from app.modules.auth.route import router as auth



@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando Base de Datos local")
    init_db()
    print("Tablas creadas y modo Wal activado!")
    yield


app = FastAPI(
    title="TellDocs Api",
    description="Api para recibir y guardar fotos de guías, facturas, depósitos, etc.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir la carpeta de almacenamiento de manera estática en la URL "/documents"
app.mount("/documents", StaticFiles(directory=STORAGE_PATH), name="documents")

app.include_router(auth)
app.include_router(sales_invoices)
app.include_router(upload)


@app.get("/health")
def health_check():
    """Endpoint simple para verificar que la Api está corriendo utíl para dockerhealthcheck"""
    return {"status": "ok"}


def main():
    print("Hello from telldocs!")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
