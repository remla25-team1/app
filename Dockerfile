# Build stage
FROM python:3.12.9-slim AS builder

WORKDIR /app

# Install git  
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# Install dependencies 
COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
    pip install --user -r requirements.txt

# Runtime stage
FROM python:3.12.9-slim

WORKDIR /root

COPY src src

COPY --from=builder /root/.local /root/.local

ENV PATH=/root/.local/bin:$PATH \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MODEL_SERVICE_HOST=model-service \
	MODEL_SERVICE_PORT=8081 \
    MODEL_SERVICE_VERSION=0.0.0 \
    APP_VERSION=0.0.0 \
    PORT=8080

EXPOSE ${PORT}

ENTRYPOINT ["python"]
CMD ["src/app.py"]