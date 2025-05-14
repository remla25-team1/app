#multi-stage
FROM python:3.12.9-slim AS builder

RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
    pip install --user -r requirements.txt

COPY src src


FROM python:3.12.9-slim

WORKDIR /root/

COPY --from=builder /root/.local /root/.local
COPY --from=builder /app/src src


ARG APP_VERSION=0.0.0
ARG MODEL_SERVICE_VERSION=0.0.0

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MODEL_SERVICE_HOST=model-service \
	MODEL_SERVICE_PORT=8081\
    PORT=8080

ARG APP_VERSION=0.0.0
ARG MODEL_SERVICE_VERSION=0.0.0
ENV APP_VERSION=${APP_VERSION}
ENV MODEL_SERVICE_VERSION=${MODEL_SERVICE_VERSION}


COPY src src
EXPOSE ${PORT}

ENTRYPOINT ["python"]
CMD ["src/app.py"]