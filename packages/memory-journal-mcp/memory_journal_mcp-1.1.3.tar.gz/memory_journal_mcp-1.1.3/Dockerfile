# Memory Journal MCP Server - Full Version
# A containerized Model Context Protocol server for personal journaling with semantic search
# Alpine-based for enhanced security while maintaining all features
FROM python:3.13-alpine

# Set working directory
WORKDIR /app

# Upgrade OpenSSL, curl, and expat to latest patched versions FIRST (CVE fixes)
RUN apk add --no-cache --upgrade openssl=3.5.4-r0 curl=8.14.1-r2 expat=2.7.3-r0

# Install system dependencies for git and ML libraries
RUN apk add --no-cache \
    git \
    ca-certificates \
    build-base \
    linux-headers \
    gfortran \
    openblas-dev \
    musl-dev \
    libffi-dev \
    openssl-dev \
    python3-dev \
    && apk upgrade

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Upgrade pip and setuptools to fix security vulnerabilities
# CVE-2025-8869: Upgrade pip to latest version (Python 3.13 implements PEP 706)
RUN pip install --no-cache-dir --upgrade pip>=25.0 setuptools>=78.1.1

# Install core dependencies first
RUN pip install --no-cache-dir mcp aiohttp aiohttp-cors numpy

# Install ML dependencies with Alpine-compatible approach
RUN pip install --no-cache-dir \
    torch --index-url https://download.pytorch.org/whl/cpu \
    sentence-transformers \
    faiss-cpu \
    || echo "ML dependencies failed to install - continuing without semantic search"

# Copy source code and license
COPY src/ ./src/
COPY LICENSE ./LICENSE

# Create data directory for SQLite database with proper permissions
RUN mkdir -p /app/data && chmod 700 /app/data

# Create non-root user for security
RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup && \
    chown -R appuser:appgroup /app

# Set environment variables
ENV PYTHONPATH=/app
ENV DB_PATH=/app/data/memory_journal.db

# Expose the port (though MCP uses stdio, this is for potential future web interface)
EXPOSE 8000

# Switch to non-root user
USER appuser

# Health check to ensure the server can start
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.path.append('/app'); from src.server import *; print('Server healthy')" || exit 1

# Run the MCP server
CMD ["python", "src/server.py"]

# Labels for Docker Hub
LABEL maintainer="Memory Journal MCP"
LABEL description="A Model Context Protocol server for personal journaling with relationships and visualization"
LABEL version="1.1.3"
LABEL org.opencontainers.image.source="https://github.com/neverinfamous/memory-journal-mcp"