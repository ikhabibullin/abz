FROM python:3.9

WORKDIR /code

RUN apt update \
  && apt install netcat -y  \
  && pip install --upgrade pip \
  && pip install poetry==1.1.6

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-ansi

COPY src .
COPY entrypoint.sh .

RUN chmod 777 /code/entrypoint.sh

ENTRYPOINT ["/code/entrypoint.sh"]