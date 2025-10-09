FROM python:3.13-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

RUN apk add --no-cache \
    build-base \
    curl \
    git \
    bash \
    libffi-dev \
    openssl-dev \
    python3-dev \
    musl-dev

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="$POETRY_HOME/bin:$PATH"

WORKDIR /app
COPY pyproject.toml poetry.lock* /app/
RUN poetry install
COPY . /app

EXPOSE 8000

CMD ["poetry", "run", "ohmyapi", "serve", "--host", "0.0.0.0"]
