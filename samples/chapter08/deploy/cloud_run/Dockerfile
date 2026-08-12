# samples/chapter08/deploy/cloud_run/Dockerfile
# Cloud Run用コンテナイメージ（8-2-5節の完全版）
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
