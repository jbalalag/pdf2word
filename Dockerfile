FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    ocrmypdf tesseract-ocr tesseract-ocr-ara tesseract-ocr-eng ghostscript \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT=8000
CMD gunicorn -b 0.0.0.0:$PORT -w 1 --timeout 300 app:app
