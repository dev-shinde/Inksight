FROM python:3.8-slim

WORKDIR /app
RUN apt-get update && apt-get install -y curl
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files including static and templates
COPY . .
COPY static/ /app/static/
COPY templates/ /app/templates/

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5001/health || exit 1

EXPOSE 5001
ENV FLASK_APP=app.py
ENV FLASK_ENV=development

CMD ["python", "app.py"]