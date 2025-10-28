FROM python:3.11-slim

# Install FFmpeg + full ImageMagick with delegates
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libssl-dev \
    libgnutls30 \
    libjpeg62-turbo-dev \
    libpng-dev \
    libtiff-dev \
    libmagickcore-6.q16-6-extra \
    imagemagick \
    && rm -rf /var/lib/apt/lists/*

# ✅ Allow color transformations & composite ops
# Disable security restrictions that block CLUT/FX/Compose
RUN sed -i 's/<policy domain="coder" rights="none" pattern="MVG" \/>/<!-- & -->/' /etc/ImageMagick-6/policy.xml || true \
 && sed -i 's/<policy domain="coder" rights="none" pattern="PDF" \/>/<!-- & -->/' /etc/ImageMagick-6/policy.xml || true \
 && sed -i 's/<policy domain="coder" rights="none" pattern="PS" \/>/<!-- & -->/' /etc/ImageMagick-6/policy.xml || true \
 && sed -i 's/<policy domain="path" rights="none" pattern="@*" \/>/<!-- & -->/' /etc/ImageMagick-6/policy.xml || true

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir flask requests

ENV PORT=10000
CMD ["python", "app.py"]
