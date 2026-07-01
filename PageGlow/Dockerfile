# ===========================================
# Stage 1: Build dependencies
# ===========================================
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (Docker cache layer)
COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt

# ===========================================
# Stage 2: Production image
# ===========================================
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r django && useradd -r -g django django

WORKDIR /app

# Copy installed dependencies from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY --chown=django:django . .

# Create directories with proper permissions
RUN mkdir -p /app/staticfiles /app/static /app/media /app/logs && \
    chown -R django:django /app

# Switch to non-root user
USER django

EXPOSE 8000

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "PageGlow.asgi:application"]
