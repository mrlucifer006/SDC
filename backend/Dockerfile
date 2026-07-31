FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN apt-get update && apt-get install -y nodejs g++ default-jdk && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt
WORKDIR /app/backend
COPY . .
WORKDIR /app
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
