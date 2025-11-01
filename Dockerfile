# Multi-stage Docker build for Hypernode Node Client
FROM nvidia/cuda:12.0.0-base-ubuntu22.04 as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY jobs/ ./jobs/

# Create directories for job data
RUN mkdir -p /app/data /app/logs /app/models

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV HN_NODE_TOKEN=""
ENV WALLET_PUBKEY=""
ENV BACKEND_URL="https://api.hypernode.sol"
ENV HEARTBEAT_INTERVAL=60
ENV MAX_JOBS_CONCURRENT=1
ENV LOG_LEVEL="INFO"

# Health check
HEALTHCHECK --interval=60s --timeout=10s --start-period=10s --retries=3 \
  CMD python3 src/health_check.py || exit 1

# Run the worker
CMD ["python3", "src/main.py"]
