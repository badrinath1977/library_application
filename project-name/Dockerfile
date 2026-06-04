FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

COPY project-name/requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY project-name/app ./app
COPY project-name/run_server.py .
COPY project-name/config.json .

EXPOSE 8000

CMD ["python", "run_server.py"]
