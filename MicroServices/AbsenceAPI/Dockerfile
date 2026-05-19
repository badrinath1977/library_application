FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /workspace/MicroServices/AbsenceAPI

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl gnupg unixodbc unixodbc-dev \
    && curl -sSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && curl -sSL https://packages.microsoft.com/config/debian/12/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql17 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY MicroServices/AbsenceAPI/requirements.txt ./requirements.txt
COPY libraries-dist /workspace/libraries-dist
RUN pip install --no-cache-dir -r requirements.txt

COPY MicroServices/AbsenceAPI .

EXPOSE 8020
CMD ["python", "run_server.py"]

