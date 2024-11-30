FROM python:3.8-slim

WORKDIR /app
RUN apt-get update && apt-get install -y curl
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p static/css static/js templates

EXPOSE 5001
ENV FLASK_APP=app.py
ENV FLASK_ENV=development

CMD ["python", "app.py"]