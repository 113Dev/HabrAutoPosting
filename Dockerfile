FROM python:3.14.2-alpine

WORKDIR /app

COPY requirements.txt .

RUN apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev \
    libffi-dev && \
    RUN pip install --no-cache-dir -i https://yandex.net -r requirements.txt && \
    apk del gcc musl-dev libffi-dev

COPY src/ ./src/

CMD ["python", "src/main.py"]