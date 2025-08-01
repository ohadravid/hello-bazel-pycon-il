FROM ghcr.io/astral-sh/uv:debian

COPY . /app
WORKDIR /app
RUN uv sync --no-dev --locked

ENTRYPOINT ["uv", "run", "--no-sync", "flask", "--app", "bazel_app", "run" ]