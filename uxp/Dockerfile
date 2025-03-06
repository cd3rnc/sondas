# Use the official multi-arch Python 3.9 Alpine image
FROM python:3.9-alpine

RUN apk add --no-cache \
    chromium \
    chromium-chromedriver \
    xvfb \
    tzdata

# Set timezone environment variable
ENV TZ=America/Santiago

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY main.py .
COPY config.yaml .
COPY plugins/ plugins/

# Copy the external cron file into the root crontab directory for BusyBox cron
COPY sonda.cron /etc/crontabs/root
RUN chmod 0644 /etc/crontabs/root

# Run the cron daemon in the foreground
CMD ["crond", "-f"]