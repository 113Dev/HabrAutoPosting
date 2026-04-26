FROM python:3.14.2-alpine

WORKDIR /app

COPY requirements.txt .

RUN apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev \
    libffi-dev \
    libxml2-dev \
    libxslt-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del gcc musl-dev libffi-dev libxml2-dev libxslt-dev && \
    apk add --no-cache postgresql-libs

COPY src/ ./src/

CMD ["python", "src/main.py"]