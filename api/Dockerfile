FROM python:3.12-slim

RUN apt-get update && apt-get install -y libmagic1
WORKDIR /app

# Instala uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copia dependencias primero (cacheo de capas)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copia el código
COPY app/ ./app/

# Rutas de datos persistentes — separadas del código
ENV DATA_PATH=/data
RUN mkdir -p /data/storage /data/db

EXPOSE 7780
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7780"]
