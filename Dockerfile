FROM python:3.11-slim

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system deps cleanly
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    imagemagick \
    libjpeg62-turbo-dev \
    libpng-dev \
    libtiff-dev \
    libwebp-dev \
    libxml2-dev \
    libssl-dev \
    libgnutls30 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# ✅ Allow color + composite operations blocked by default
RUN sed -i 's/<policy domain="path" rights="none" pattern="@*" \/>/<!-- & -->/' /etc/ImageMagick-6/policy.xml || true

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir flask requests

ENV PORT=10000
CMD ["python", "app.py"]
