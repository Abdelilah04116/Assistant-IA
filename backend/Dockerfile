FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy simplified requirements first for better caching
COPY requirements-simple.txt ./requirements.txt

# Install Python dependencies with timeout and retry
RUN pip install --no-cache-dir --upgrade pip --timeout 60 || \
    pip install --no-cache-dir --upgrade pip --timeout 120 && \
    pip install --no-cache-dir -r requirements.txt --timeout 300

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p ./data/temp ./data/documents ./data/vector_store

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
