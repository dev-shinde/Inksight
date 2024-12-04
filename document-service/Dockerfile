FROM python:3.9-slim

WORKDIR /app

# Install system dependencies including poppler-utils
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5003
CMD ["python", "app.py"]