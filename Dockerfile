# ---- Stage 1: build the frontend bundle ----
FROM node:20-slim AS frontend

WORKDIR /build
COPY package.json package-lock.json ./
RUN npm ci
COPY webpack.config.js ./
COPY src/ ./src/
RUN npm run build

# ---- Stage 2: the application ----
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY --from=frontend /build/static/dist ./static/dist

ENV DJANGO_SECRET_KEY=build-only-not-a-real-secret \
    DATABASE_URL=postgres://build:build@localhost:5432/build \
    DJANGO_DEBUG=False
RUN python manage.py collectstatic --noinput

CMD exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:${PORT:-8080} \
    --workers 2 \
    --threads 4 \
    --timeout 60