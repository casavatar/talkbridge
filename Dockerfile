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

# Install Python dependencies in stages
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Stage 1: Install core dependencies
RUN pip install --no-cache-dir \
    numpy==1.21.6 \
    matplotlib==3.5.3 \
    scipy==1.7.3 \
    requests==2.28.2 \
    pandas==1.5.3

# Stage 2: Install audio processing
RUN pip install --no-cache-dir \
    sounddevice==0.4.6 \
    wave==0.0.2 \
    librosa==0.10.0 \
    soundfile==0.12.1 \
    pygame==2.5.2

# Stage 3: Install ML dependencies
RUN pip install --no-cache-dir torch==1.13.1 torchaudio==0.13.1 --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir transformers==4.21.3 sentencepiece==0.1.99

# Stage 4: Install web interface and other dependencies
RUN pip install --no-cache-dir \
    streamlit==1.28.1 \
    streamlit-webrtc==0.47.1 \
    plotly==5.15.0 \
    cryptography>=42.0.0 \
    bcrypt==4.0.1 \
    passlib==1.7.4 \
    pyyaml==6.0.1 \
    jsonschema==4.17.3 \
    structlog==22.3.0 \
    colorlog==6.7.0 \
    pytest==7.3.1 \
    pytest-cov==4.1.0 \
    black==23.3.0 \
    isort==5.12.0 \
    flake8==6.0.0 \
    mypy==1.3.0 \
    python-dotenv==1.0.0 \
    click==8.1.3 \
    rich==13.3.5 \
    tqdm==4.65.0

# Stage 5: Install translation alternatives
RUN pip install --no-cache-dir \
    googletrans==4.0.0rc1 \
    translate==3.6.1

# Stage 6: Install optional computer vision dependencies
RUN pip install --no-cache-dir \
    mediapipe==0.10.11 \
    opencv-python==4.8.0.76 \
    pillow==9.5.0

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