FROM python:3.11-slim

# Install ImageMagick only (no curl needed)
RUN apt-get update && apt-get install -y imagemagick && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

# Install Flask + Requests
RUN pip install flask requests

ENV PORT=10000
CMD ["python", "app.py"]
