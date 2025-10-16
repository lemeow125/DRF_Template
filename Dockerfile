
# Stage 1: Builder
FROM python:3.13.7-slim AS builder

# UV Caching
ENV UV_LINK_MODE=copy
ENV UV_PYTHON_CACHE_DIR=/.cache/uv

# Install uv binary from it’s official docker repository
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install OS-level dependencies(needed for compiling python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
curl build-essential && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency management files
# (Only pyproject.toml and uv.lock file is needed to replicate the environment))
COPY pyproject.toml uv.lock /app/

# Use uv to install all project dependenies in a virtual environment
RUN --mount=type=cache,target=/tmp/.uv \ 
    uv sync --frozen --compile-bytecode


# Stage 2: Runtime
FROM python:3.13.7-slim AS runtime

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /app /app

# Add the virtual environment’s binary directory to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Copy project files
COPY . /app/
RUN chmod +x /app/.docker/start.sh

# Expose Django's default port
EXPOSE 8000

ENTRYPOINT [ "/app/.docker/start.sh" ]