# Stage 1 — install Python dependencies (needs gcc + libpq-dev to compile)
FROM python:3.12-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq-dev \
        gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# Stage 2 — lean runtime image (no build tools, non-root user)
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --no-create-home --shell /bin/false appuser

WORKDIR /app

# Copy only installed packages from the builder
COPY --from=builder /install /usr/local

# Copy application code — explicit paths avoid baking in secrets or venvs
COPY --chown=appuser:appuser alembic.ini        ./alembic.ini
COPY --chown=appuser:appuser models.json        ./models.json
COPY --chown=appuser:appuser src/               ./src/
COPY --chown=appuser:appuser migrations/        ./migrations/
COPY --chown=appuser:appuser templates/         ./templates/
COPY --chown=appuser:appuser static/            ./static/

USER appuser

EXPOSE 5000

CMD ["gunicorn", "src.app:create_app()", "--bind", "0.0.0.0:5000", "--workers", "2", "--log-file", "-"]
