FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /workspace/MicroServices/ChatAPI

COPY MicroServices/ChatAPI/requirements.txt ./requirements.txt
COPY libraries-dist /workspace/libraries-dist
RUN pip install --no-cache-dir -r requirements.txt

COPY MicroServices/ChatAPI .

EXPOSE 8010
CMD ["python", "run_server.py"]

