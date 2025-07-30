# TalkBridge Setup Instructions

Complete guide to install and run the TalkBridge offline AI voice assistant system.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Python Installation](#python-installation)
3. [Offline Installation](#offline-installation)
4. [Docker Installation](#docker-installation)
5. [Demo Mode Setup](#demo-mode-setup)
6. [Running the System](#running-the-system)
7. [Troubleshooting](#troubleshooting)

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10/11 or macOS 10.15+
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **Audio**: Microphone and speakers/headphones
- **Camera**: Webcam (optional, for avatar animation)

### Recommended Requirements
- **RAM**: 16GB or higher
- **Storage**: 5GB free space (for models and audio files)
- **GPU**: NVIDIA GPU with CUDA support (optional, for faster processing)
- **Internet**: Initial download only (system runs fully offline after setup)

## Python Installation

### Windows Installation

1. **Download Python 3.8+**
   ```bash
   # Download from python.org or use winget
   winget install Python.Python.3.8
   ```

2. **Verify Installation**
   ```bash
   python --version
   pip --version
   ```

3. **Add Python to PATH** (if not done automatically)
   - Open System Properties → Environment Variables
   - Add Python and Scripts directories to PATH

### macOS Installation

1. **Using Homebrew** (recommended)
   ```bash
   brew install python@3.8
   ```

2. **Using Official Installer**
   - Download from python.org
   - Run the installer package
   - Python is automatically added to PATH

3. **Verify Installation**
   ```bash
   python3 --version
   pip3 --version
   ```

## Offline Installation

### Step 1: Download Dependencies

If you have internet access initially:

```bash
# Clone the repository
git clone https://github.com/your-org/talkbridge.git
cd talkbridge

# Download all dependencies to a local directory
pip download -r requirements.txt -d ./offline_packages/
```

### Step 2: Install Dependencies Offline

```bash
# Install from local packages
pip install --no-index --find-links ./offline_packages/ -r requirements.txt
```

### Step 3: Verify Installation

```bash
# Test core modules
python -c "import streamlit; print('Streamlit OK')"
python -c "import numpy; print('NumPy OK')"
python -c "import cv2; print('OpenCV OK')"
```

## Docker Installation

### Option 1: Using Pre-built Image

```bash
# Pull the image
docker pull talkbridge/talkbridge:latest

# Run the container
docker run -p 8501:8501 -v $(pwd)/data:/app/data talkbridge/talkbridge:latest
```

### Option 2: Build from Source

```bash
# Build the image
docker build -t talkbridge .

# Run the container
docker run -p 8501:8501 -v $(pwd)/data:/app/data talkbridge
```

### Docker Compose (Recommended)

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  talkbridge:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - DEMO_MODE=true
      - DEBUG=false
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

## Demo Mode Setup

### Enable Demo Mode

1. **Edit Configuration**
   ```bash
   # Edit demo config
   nano src/demo/demo_config.py
   ```

2. **Set Demo Mode**
   ```python
   DEMO_MODE = True
   ```

3. **Verify Demo Files**
   ```bash
   # Run demo setup
   python src/demo/run_demo.py --test
   ```

### Demo Mode Features

- **No Hardware Required**: Works without microphone or camera
- **Predefined Responses**: Uses sample files for consistent demo
- **Realistic Delays**: Simulates processing times
- **Web Interface**: Full UI integration

## Running the System

### Method 1: Direct Python Execution

```bash
# Run the main web interface
python src/ui/web_interface.py

# Or run the demo interface
python src/demo/demo_ui.py
```

### Method 2: Using Streamlit

```bash
# Run with Streamlit
streamlit run src/ui/web_interface.py --server.port 8501

# Run demo mode
streamlit run src/demo/demo_ui.py --server.port 8501
```

### Method 3: Using the Runner Script

```bash
# Run main system
python src/ui/run_web_interface.py

# Run demo tests
python src/demo/run_demo.py --test
```

### Method 4: Docker

```bash
# Using docker-compose
docker-compose up

# Or direct docker
docker run -p 8501:8501 talkbridge
```

## Accessing the System

### Web Interface
- **URL**: http://localhost:8501
- **Default Credentials**: 
  - Username: `admin`
  - Password: `admin123`

### Demo Mode Access
- **URL**: http://localhost:8501
- **No Login Required**: Demo mode bypasses authentication

## Configuration

### Environment Variables

```bash
# Set environment variables
export DEMO_MODE=true
export DEBUG=false
export LOG_LEVEL=INFO
export DATA_DIR=./data
export LOGS_DIR=./logs
```

### Configuration File

Edit `src/config.py`:

```python
# System settings
DEMO_MODE = True
DEBUG = False
LOG_LEVEL = "INFO"

# Paths
DATA_DIR = "./data"
LOGS_DIR = "./logs"
MODELS_DIR = "./data/models"

# Audio settings
SAMPLE_RATE = 22050
CHUNK_DURATION = 5.0
```

## Troubleshooting

### Common Issues

#### 1. Python Not Found
```bash
# Windows
python --version

# macOS/Linux
python3 --version

# If not found, reinstall Python and add to PATH
```

#### 2. Missing Dependencies
```bash
# Reinstall requirements
pip install -r requirements.txt

# Or install offline
pip install --no-index --find-links ./offline_packages/ -r requirements.txt
```

#### 3. Port Already in Use
```bash
# Check what's using port 8501
lsof -i :8501

# Kill the process
kill -9 <PID>

# Or use a different port
streamlit run src/ui/web_interface.py --server.port 8502
```

#### 4. Audio Issues
```bash
# Check audio devices
python -c "import pyaudio; p = pyaudio.PyAudio(); print(p.get_device_count())"

# Test microphone
python src/audio/capture.py --test
```

#### 5. Demo Mode Not Working
```bash
# Check demo configuration
python src/demo/run_demo.py --config

# Recreate demo files
python src/demo/demo_config.py
```

#### 6. Docker Issues
```bash
# Check Docker logs
docker logs <container_id>

# Rebuild image
docker build --no-cache -t talkbridge .

# Clean up containers
docker system prune -a
```

### Debug Mode

Enable debug logging:

```bash
# Set debug environment variable
export DEBUG=true

# Or edit config
echo "DEBUG = True" >> src/config.py

# Run with debug output
python -u src/ui/web_interface.py
```

### Log Files

Check log files for errors:

```bash
# View error logs
tail -f logs/errors.log

# View application logs
tail -f logs/app.log

# View demo logs
tail -f logs/demo.log
```

### Performance Issues

#### Memory Usage
```bash
# Monitor memory usage
htop  # Linux/macOS
taskmgr  # Windows

# Reduce memory usage
export PYTHONOPTIMIZE=1
```

#### CPU Usage
```bash
# Monitor CPU usage
top

# Use demo mode for testing
export DEMO_MODE=true
```

## Security Considerations

### Offline Security
- **No Internet Access**: System runs completely offline
- **Local Data**: All data stays on your machine
- **No External APIs**: No data sent to third parties

### File Permissions
```bash
# Set proper permissions
chmod 755 src/
chmod 644 src/*.py
chmod 600 logs/*.log
```

### User Authentication
- **Default Admin**: Change default credentials
- **Session Management**: Sessions expire automatically
- **Access Control**: Role-based permissions

## Support

### Getting Help

1. **Check Logs**: Review error logs in `logs/` directory
2. **Run Tests**: Execute test suite with `python -m unittest discover test/`
3. **Demo Mode**: Use demo mode for testing without hardware
4. **Documentation**: Review module documentation in `doc/`

### Reporting Issues

When reporting issues, include:
- Operating system and version
- Python version (`python --version`)
- Error messages from logs
- Steps to reproduce the issue
- Demo mode vs live mode behavior

### Community Support

- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: Check `doc/` folder for detailed guides
- **Examples**: Review example scripts in `examples/`

## Next Steps

After successful installation:

1. **Test the System**: Run demo mode to verify functionality
2. **Configure Settings**: Adjust audio, language, and performance settings
3. **Add Models**: Download additional TTS and STT models
4. **Customize UI**: Modify web interface appearance and behavior
5. **Deploy**: Set up for production use with proper security

---

**Note**: This system is designed to run completely offline. Ensure all dependencies and models are downloaded before disconnecting from the internet. 