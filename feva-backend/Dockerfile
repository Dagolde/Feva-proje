# ── Stage 1: builder ──────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# GDAL + build deps — required to compile fiona/geopandas/geoalchemy2
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libgdal-dev \
    gdal-bin \
    libgeos-dev \
    libproj-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY app/__init__.py ./app/__init__.py

# Pin GDAL Python binding to match the system GDAL version exactly,
# then install the rest of the project.
RUN pip install --upgrade pip \
    && GDAL_VER=$(gdal-config --version) \
    && echo "Building with system GDAL $GDAL_VER" \
    && pip install --prefix=/install --no-cache-dir "GDAL==$GDAL_VER" \
    && pip install --prefix=/install --no-cache-dir .

# ── Stage 2: runtime ──────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

# Runtime GDAL shared libraries (no -dev headers needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libgdal32 \
    libgeos-c1v5 \
    libproj25 \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --gid 1001 feva \
    && useradd --uid 1001 --gid feva --shell /bin/bash --create-home feva

WORKDIR /app

COPY --from=builder /install /usr/local
COPY --chown=feva:feva . .

USER feva

EXPOSE 8000

CMD ["gunicorn", "app.main:app", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--workers", "4", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
