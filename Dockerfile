FROM python:3.7-alpine3.9

RUN apk add --no-cache --virtual .build-deps g++ python3-dev build-base libffi-dev openssl-dev && \
    pip3 install --upgrade pip setuptools

WORKDIR /usr/src/app
EXPOSE 8000

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "--workers=1", "--bind=0.0.0.0:8000", "--log-level=debug", "--access-logfile=-", "--error-logfile=-", "app:app"]