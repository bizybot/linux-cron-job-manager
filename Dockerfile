# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    cron \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

# Install curl
RUN apt-get update && apt-get install -y curl

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Create scripts directory
RUN mkdir -p scripts

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

# Add appuser to the crontab group and create crontab file
RUN usermod -a -G crontab appuser && \
    touch /var/spool/cron/crontabs/appuser && \
    chown appuser:crontab /var/spool/cron/crontabs/appuser && \
    chmod 0600 /var/spool/cron/crontabs/appuser

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/jobs || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 
