# TalkBridge Dockerfile
# Lightweight, cross-platform Docker image for the TalkBridge offline AI voice assistant

# Use Python 3.8 slim image as base
FROM python:3.8-slim

# Set metadata
LABEL maintainer="TalkBridge Team <team@talkbridge.ai>"
LABEL version="1.0.0"
LABEL description="TalkBridge - Offline AI Voice Assistant"

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Audio dependencies
    portaudio19-dev \
    libasound2-dev \
    # Image processing dependencies
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    # Development tools
    build-essential \
    pkg-config \
    # Clean up
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with fallback for problematic packages
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt || \
    (pip install --no-cache-dir TTS==0.14.3 && \
     pip install --no-cache-dir -r requirements.txt)

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data/audio \
    /app/data/models \
    /app/data/avatars \
    /app/data/logs \
    /app/data/temp \
    /app/logs \
    /app/src/demo/samples

# Set proper permissions
RUN chmod -R 755 /app/src && \
    chmod -R 644 /app/src/*.py && \
    chmod -R 755 /app/data && \
    chmod -R 755 /app/logs

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash talkbridge && \
    chown -R talkbridge:talkbridge /app

# Switch to non-root user
USER talkbridge

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8501/_stcore/health')" || exit 1

# Set default command
CMD ["streamlit", "run", "src/ui/web_interface.py", "--server.port=8501", "--server.address=0.0.0.0"]

# Alternative commands for different modes
# For demo mode:
# CMD ["streamlit", "run", "src/demo/demo_ui.py", "--server.port=8501", "--server.address=0.0.0.0"]

# For direct Python execution:
# CMD ["python", "src/ui/web_interface.py"]

# For testing:
# CMD ["python", "-m", "unittest", "discover", "test"]

# Build instructions:
# docker build -t talkbridge .
# docker run -p 8501:8501 -v $(pwd)/data:/app/data talkbridge

# Run with demo mode:
# docker run -p 8501:8501 -v $(pwd)/data:/app/data -e DEMO_MODE=true talkbridge

# Run with custom configuration:
# docker run -p 8501:8501 \
#   -v $(pwd)/data:/app/data \
#   -v $(pwd)/logs:/app/logs \
#   -e DEMO_MODE=true \
#   -e DEBUG=false \
#   -e LOG_LEVEL=INFO \
#   talkbridge 