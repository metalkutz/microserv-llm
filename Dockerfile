# multistage Dockerfile para aplicación Python
FROM python:3.12-slim AS build

# Instalar poetry
ENV POETRY_HOME="/opt/poetry"
ENV POETRY_PATH="$POETRY_HOME/bin"
ENV PATH="$POETRY_PATH:$PATH"
RUN apt-get update && apt-get install -y curl && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# configurar poetry
ENV POETRY_NO_INTERACTION=1
ENV POETRY_VIRTUALENVS_IN_PROJECT=1
ENV POETRY_CACHE_DIR="/opt/poetry/cache"

# Copiar archivos de configuración
WORKDIR /app
COPY pyproject.toml poetry.lock ./

# instalar dependencias
RUN poetry install --no-root --only main && \
    rm -rf $POETRY_CACHE_DIR/*

# instalar dependencias de producción
FROM python:3.12-slim AS production

# Instalar dependencias del sistema necesarias para PyTorch/Transformers
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# configurar directorio de trabajo
WORKDIR /app

# Copiar el entorno virtual de poetry desde el stage build
COPY --from=build /app/.venv /app/.venv

# Configurar PATH para usar el entorno virtual
ENV PATH="/app/.venv/bin:$PATH"

# Copiar archivos de la aplicación
COPY src/ /app/src/

# configurar variables de entorno
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Exponer el puerto de la aplicación
EXPOSE 8000

# healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3\
    CMD curl -f http://localhost:8000/health || exit 1

# Comando para ejecutar la aplicación
CMD ["/app/.venv/bin/python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]