FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install poetry
COPY combinario/pyproject.toml combinario/poetry.lock .
RUN poetry config virtualenvs.create false \
    && poetry install --without dev --no-interaction --no-ansi

ENV PYTHONUNBUFFERED=1

RUN groupadd -r app && useradd -r -g app app

RUN chown -R app:app /app

COPY --chown=app:app combinario .

USER app