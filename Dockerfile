# Use official Python image
FROM python:3.11-slim

# Set environment variables early
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /usr/src/app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libxml2-dev \
    libxslt1-dev \
    libpq-dev \
    build-essential \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
# Try to upgrade pip with timeout, but don't fail if it times out
RUN pip install --upgrade pip --timeout 300 --retries 3 || echo "Pip upgrade failed, continuing with existing version"
RUN pip install --no-cache-dir -r requirements.txt --timeout 300 --retries 5

# Copy Django app code
COPY . .

CMD ["./entrypoint.sh"]