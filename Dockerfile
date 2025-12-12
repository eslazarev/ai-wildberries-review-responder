FROM python:3.12.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates tzdata && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

COPY src ./src
COPY settings.yaml ./settings.yaml

ENTRYPOINT ["python", "-m"]
CMD ["src.entrypoints.docker_once"]
