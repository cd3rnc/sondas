FROM arm64v8/python:3.9

RUN apt-get update && apt-get install -y \
    unzip \
    wget \
    vim \ 
    curl \
    xvfb \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ./test3.py /app/
COPY ./.env /app/
COPY ./sitios.txt /app/
RUN pip install --no-cache-dir \
    selenium \
    pymongo \
    python-dotenv \
    pyvirtualdisplay \
    requests

RUN chmod +x test3.py

CMD while true; do python3 /app/main3.py; sleep 1000; done