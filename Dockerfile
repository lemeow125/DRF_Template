
# Stage 1: Builder
FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim AS builder

# UV Caching
ENV UV_LINK_MODE=copy

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