FROM python:3.13.11-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

WORKDIR /project

COPY uv.lock pyproject.toml /project/
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --frozen --no-dev

ENV PYTHONPATH=/project

COPY . /project

WORKDIR /project/src

CMD ["uv", "run", "run_main.py"]
