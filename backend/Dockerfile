FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file content
COPY requirements.txt ./requirements.txt

# Set pip settings to avoid timeouts
ENV PIP_DEFAULT_TIMEOUT=1000 \
    PIP_NO_CACHE_DIR=1

# 1. Install PyTorch CPU version first (Big download, ~200MB instead of 900MB)
RUN pip install --no-cache-dir torch==2.1.2 --index-url https://download.pytorch.org/whl/cpu

# 2. Install heavy dependencies individually to prevent build timeouts/memory issues
# We add --extra-index-url to ensure dependencies that might trigger a torch check can see the CPU wheels
RUN pip install --no-cache-dir sentence-transformers==2.2.2 --extra-index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir chromadb==0.4.18
RUN pip install --no-cache-dir langchain==0.1.0

# 3. Install remaining dependencies form requirements.txt
# (pip will skip what's already installed and compatible)
RUN pip install --no-cache-dir -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu

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
