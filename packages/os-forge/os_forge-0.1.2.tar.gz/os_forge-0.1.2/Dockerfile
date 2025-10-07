# Multi-stage build for production-ready OS Forge Backend
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim as production

# Create non-root user
RUN groupadd -r osforge && useradd -r -g osforge -d /app -s /bin/bash osforge

# Install system dependencies for hardening rules
RUN apt-get update && apt-get install -y \
    # System utilities
    procps \
    util-linux \
    coreutils \
    grep \
    sed \
    awk \
    findutils \
    # Network tools
    net-tools \
    iputils-ping \
    curl \
    wget \
    # Security tools
    ufw \
    iptables \
    # SSH tools for Linux hardening
    openssh-client \
    # System control
    systemd \
    # Additional utilities
    sudo \
    less \
    vim-tiny \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Create necessary directories with proper permissions
RUN mkdir -p /app/data /app/reports /app/backups /app/logs /app/tmp && \
    chown -R policyguard:policyguard /app

# Copy application code
COPY --chown=policyguard:policyguard main.py .
COPY --chown=policyguard:policyguard requirements.txt .

# Create health check script
RUN echo '#!/bin/bash\n\
curl -f http://localhost:8000/health || exit 1' > /app/healthcheck.sh && \
    chmod +x /app/healthcheck.sh && \
    chown osforge:osforge /app/healthcheck.sh

# Switch to non-root user
USER osforge

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    DATABASE_URL=sqlite:///./data/policy_guard.db \
    LOG_LEVEL=INFO \
    LOG_FORMAT=json \
    ENABLE_METRICS=true \
    METRICS_PORT=9090

# Expose ports
EXPOSE 8000 9090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD /app/healthcheck.sh

# Add labels for metadata
LABEL maintainer="OS Forge Team" \
      version="1.0.0" \
      description="OS Forge - Multi-Platform System Hardening Tool" \
      org.opencontainers.image.title="OS Forge Backend" \
      org.opencontainers.image.description="FastAPI backend for system hardening" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.source="https://github.com/your-org/policy-guard"

# Use exec form for proper signal handling
CMD ["python", "main.py", "server", "--host", "0.0.0.0", "--port", "8000"]