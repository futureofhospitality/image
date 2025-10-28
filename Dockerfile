FROM python:3.11-slim

# Install FFmpeg with HTTPS (libssl + gnutls)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libssl-dev \
    libgnutls30 \
    imagemagick && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

RUN pip install flask requests

ENV PORT=10000
CMD ["python", "app.py"]
