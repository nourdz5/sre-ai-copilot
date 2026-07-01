# Stage 1: install dependencies (includes compilers, build tools)
FROM python:3.12-slim AS builder

WORKDIR /app

RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"
COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt


# Stage 2: final image — only the venv + app code
FROM python:3.12-slim

ENV PATH="/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copy only the installed packages from the builder
COPY --from=builder /venv /venv

# Copy only the source code (respects .dockerignore)
COPY . .

# Non-root user
RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]