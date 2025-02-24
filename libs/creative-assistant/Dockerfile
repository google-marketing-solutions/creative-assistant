FROM python:3.11.8-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:0.5.18 /uv /uvx /bin/
ENV UV_SYSTEM_PYTHON=1
COPY requirements.txt requirements.txt
COPY creative_assistant creative_assistant
RUN uv pip install --require-hashes -r requirements.txt --no-deps
CMD ["uvicorn", "--port", "8080", "--host", "0.0.0.0", "creative_assistant.entrypoints.server:app"]
