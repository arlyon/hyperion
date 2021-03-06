FROM python:3.7.6-alpine as base

ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1

WORKDIR /app

# build the app and package into a venv
FROM base as builder

ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.0.2

RUN apk add --no-cache gcc g++ libffi-dev musl-dev postgresql-dev make libxml2-dev libxslt-dev
RUN pip install "poetry==$POETRY_VERSION"
RUN python -m venv /venv

COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt | /venv/bin/pip install -r /dev/stdin

#COPY . .
#RUN poetry build && /venv/bin/pip install dist/*.whl

# copy the venv and the run scripts
FROM base as final

RUN apk add --no-cache libffi libpq libxslt
COPY --from=builder /venv /venv
COPY run.py entry.sh ./
COPY hyperion_cli hyperion_cli
RUN ls
CMD ["./entry.sh"]