# Imagen compartida por los 3 mocks (ms1/ms2/ms3). Diferencia solo el CMD.
FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir fastapi==0.115.4 uvicorn[standard]==0.32.0
COPY mocks ./mocks
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
# El CMD real se define por servicio en docker-compose.mocks.yml.
