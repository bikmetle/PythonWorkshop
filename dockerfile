FROM python:3.12-slim-trixie

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["/bin/bash", "-c", "alembic upgrade head && python main.py"]
