FROM python:3.11-slim

WORKDIR /app

# Install curl for healthcheck / troubleshooting
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Pre-download NLTK stopwords
RUN python -m nltk.downloader stopwords

# Copy backend source code
COPY . .

# Ensure temp_data and models directories exist
RUN mkdir -p /app/temp_data /app/models

EXPOSE 8000

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
