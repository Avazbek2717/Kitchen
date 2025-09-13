FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && \
    apt-get install -y docker.io && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install gunicorn

COPY . .

CMD ["gunicorn", "core.wsgi:application", "--workers", "4", "--bind", "0.0.0.0:8099"]

EXPOSE 8099

RUN chmod a+x /app/*
