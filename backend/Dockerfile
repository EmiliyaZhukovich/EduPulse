FROM python:3.13-slim

WORKDIR /app
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libssl-dev \
    libffi-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:${PATH}"

COPY pyproject.toml poetry.lock /app/
RUN poetry config virtualenvs.create false \
    && poetry lock --no-update || poetry lock \
    && poetry install --no-root --only main --no-interaction --no-ansi

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
