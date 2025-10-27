FROM python:3.11-slim
RUN apt-get update && apt-get install -y imagemagick && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . .
RUN pip install flask
CMD ["python", "app.py"]
