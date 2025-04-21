# Use Python 3.8 slim image as base
FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY src/requirements.txt .

# Install specific version of gotrue before other dependencies
RUN pip install --no-cache-dir gotrue==2.8.0

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ .

# Create directory for generated images
RUN mkdir -p images

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "marvin_art.py"]
