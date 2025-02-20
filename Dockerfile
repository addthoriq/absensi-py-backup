FROM python:3.12

LABEL version="1.0.0"
LABEL maintainer="thoriq@qti.co.id"

ENV DEBIAN_FRONTEND='noninteractive'

WORKDIR /usr/src/app

# RUN apt-get update && apt install -y curl
# RUN curl -sSL https://install.python-poetry.org | python3 -
# ENV PATH="$PATH:/root/.local/bin"
RUN pip install poetry
RUN poetry config virtualenvs.create false

COPY pyproject.toml ./
COPY poetry.lock ./
COPY . .

RUN poetry install

# COPY entrypoint.sh ./

RUN chmod +x entrypoint.sh
# CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


ENTRYPOINT [ "./entrypoint.sh" ]

EXPOSE 8000