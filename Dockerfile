FROM python:3.12.9-slim

WORKDIR /app
COPY . /app

EXPOSE 3000
CMD ["python", "-m", "http.server", "3000"]
