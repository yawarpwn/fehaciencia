import uuid
from fastapi import APIRouter, File, HTTPException, UploadFile, Depends
from fastapi.responses import JSONResponse
from app.config import (
    ALLOWED_EXTENSIONS,
    STORAGE_PATH,
    MAX_FILE_SIZE,
)
from app.core.auth import get_current_user

from datetime import datetime, timezone

router = APIRouter(
    prefix="/upload",
    tags=["upload"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/")
async def upload_file(file: UploadFile = File(...)):

    # 1. Validar Extension
    original_name = file.filename or "archivo_sin_nombre"
    print("original name", original_name)
    extension = (
        "." + original_name.rsplit(".", 1)[-1].lower() if "." in original_name else ""
    )
    print("extension", extension)

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, detail=f"Extensión '{extension} no permitida'"
        )

    # 2. Leer contenido y validar tamaño
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"Archivo demasiado grande: Máximo permitido: {MAX_FILE_SIZE // (1024 * 1024)}",
        )
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="El archivo esta vacío")

    # 3. Generar nombre único pero trazable: fhecha + uuid + extension original
    timesamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    safe_filename = f"{timesamp}_{unique_id}{extension}"

    destination = STORAGE_PATH / safe_filename

    # 4. Guardar en disco
    try:
        with open(destination, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar el archivo: {e}")

    return JSONResponse(
        status_code=201,
        content={
            "message": "Archivo guardado correctamente",
            "filename_original": original_name,
            "filename_guardado": safe_filename,
            "size_bytes": len(contents),
            "path": str(destination),
        },
    )
