FROM python:3.12

WORKDIR /app

COPY main3.py insert_into_mongodb.py qos.py streamsh.py execute_streaming.sh test.sh ./
COPY streamlink-7.1.2-1-cp312-cp312-manylinux_2_28_aarch64.AppImage ./
COPY .env ./
COPY requirements.txt ./

RUN apt-get update && apt-get install -y \
    tcpdump \
    wget \
    ca-certificates \
    chromium-driver \
    chromium \
    libfuse2 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/squashfs-root && \
    ./streamlink-7.1.2-1-cp312-cp312-manylinux_2_28_aarch64.AppImage --appimage-extract && \
    chmod -R +x ./squashfs-root/AppRun execute_streaming.sh

RUN chmod +x execute_streaming.sh test.sh

EXPOSE 80 443

ENV PYTHONUNBUFFERED=1

CMD while true; do python3 /app/main3.py; sleep 1800; done
