# ---- Stage 1 : build des dépendances ----
FROM python:3.11-slim AS builder
WORKDIR /build

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --target=/packages -r requirements.txt

# ---- Stage 2 : image de production (légère) ----
FROM python:3.11-slim AS production

# Sécurité : utilisateur non-root
RUN groupadd -r appgroup && \
    useradd -r -g appgroup -m -d /home/appuser appuser

WORKDIR /app

# Copier les dépendances déjà compilées, pas les outils de build
COPY --from=builder /packages /usr/local/lib/python3.11/site-packages

# Copier le code, en donnant la propriété à l'utilisateur non-root
COPY --chown=appuser:appgroup app/ ./app/
COPY --chown=appuser:appgroup alembic/ ./alembic/
COPY --chown=appuser:appgroup alembic.ini .

USER appuser

# Variables d'environnement par défaut
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    PATH="/usr/local/lib/python3.11/site-packages/bin:$PATH"

EXPOSE $PORT

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:$PORT/health')" || exit 1

CMD ["sh", "-c", \
    "gunicorn app.main:app \
    -k uvicorn_worker.UvicornWorker \
    --workers 4 \
    --bind 0.0.0.0:$PORT \
    --timeout 60 \
    --access-logfile - \
    --error-logfile -"]