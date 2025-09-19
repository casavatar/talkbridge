# TalkBridge Desktop - Configuration & Setup Scripts

This directory contains all the scripts and configuration files needed to run TalkBridge Desktop.

## 📁 Included Files

### Installation and Execution Scripts

- **`setup_conda_desktop.py`** - Automated script to create the Conda environment
- **`run_desktop_conda.bat`** - Startup script for Windows
- **`run_desktop_conda.sh`** - Startup script for Linux/macOS
- **`cleanup_conda_env.py`** - Script to forcefully remove problematic environments
- **`post_install_fix.py`** - Post-installation verification and fix script
- **`diagnostic.py`** - Diagnostic script to identify and fix common issues

### Configuration Files

- **`environment-desktop.yaml`** - Main Conda environment configuration
- **`environment-desktop-simple.yml.backup`** - Simplified configuration (backup)
- **`config.yaml`** - Application configuration

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

```bash
cd config
python setup_conda_desktop.py
```

### Option 2: Direct Startup Scripts

**Windows:**
```cmd
cd config
run_desktop_conda.bat
```

**Linux/macOS:**
```bash
cd config
./run_desktop_conda.sh
```

## 🔧 How It Works

1. **Conda Verification** - Checks if Conda is installed
2. **Environment Creation** - If it doesn't exist, creates the `talkbridge-desktop-env` environment
3. **Activation** - Automatically activates the environment
4. **Information** - Shows available commands to run the application

## 📋 Available Commands (once the environment is activated)

```bash
# Start desktop application
python src/desktop/main.py

# Run all tests
pytest src/desktop/

# Deactivate environment
conda deactivate
```

## ⚙️ Configuration

Edit `config.yaml` to customize:

- Ollama server URL
- AI model to use
- Audio configuration
- UI configuration
- Logging level

## 🔍 Troubleshooting

### If Environment Creation Fails

1. Verify that Conda is installed: `conda --version`
2. Clean up any partial installation: `python cleanup_conda_env.py talkbridge-desktop-env --force`
3. Run the setup script again: `python setup_conda_desktop.py`

### If Dependencies Are Missing

1. Run diagnostic: `python diagnostic.py`
2. Run post-installation fix: `python post_install_fix.py`
3. Or install manually: `conda run -n talkbridge-desktop-env pip install <package>`

### Common Issues and Solutions

#### Missing Module Errors
```bash
# Fix missing Python packages
python post_install_fix.py

# Or install specific packages
conda run -n talkbridge-desktop-env pip install sounddevice mediapipe TTS argos-translate
```

#### Qt Wayland Plugin Error
```bash
# Fix Qt environment issues
python post_install_fix.py --fix-qt

# Or manually set environment
export QT_QPA_PLATFORM=xcb
```

#### Audio System Issues
```bash
# Check audio system
python diagnostic.py

# Install audio dependencies
sudo apt-get install libasound2-dev portaudio19-dev  # Ubuntu/Debian
# or
sudo dnf install alsa-lib-devel portaudio-devel      # Fedora
```

## 🛠️ Advanced Usage

### Custom Environment Name
```bash
python setup_conda_desktop.py --env-name my-custom-env
```

### Verify Installation Only
```bash
python setup_conda_desktop.py --verify-only
```

### Create Launcher Scripts Only
```bash
python setup_conda_desktop.py --create-scripts-only
```

### Force Environment Cleanup
```bash
python cleanup_conda_env.py talkbridge-desktop-env --force
```

### Comprehensive Diagnostic
```bash
python diagnostic.py --fix
```

## 📝 Notes

- Scripts automatically detect the operating system
- `environment-desktop.yaml` is used preferentially over the simple version
- All paths are relative to the project root directory
- Post-installation fixes handle common Linux/Wayland compatibility issues
- Created launcher scripts include environment fixes automatically

## 🐛 Error Resolution Guide

| Error | Solution |
|-------|----------|
| `No module named 'sounddevice'` | `python post_install_fix.py` |
| `No module named 'mediapipe'` | `python post_install_fix.py` |
| `TTS module not available` | `conda run -n talkbridge-desktop-env pip install TTS` |
| `Qt platform plugin "wayland"` | `python post_install_fix.py --fix-qt` |
| `Audio Capture not available` | Install system audio dev packages + `pip install sounddevice` |
| Environment creation fails | `python cleanup_conda_env.py <env> --force` then retry |

## 🚀 Final Setup Verification

After installation, verify everything works:

```bash
# Run full diagnostic
python diagnostic.py

# Test the environment
conda activate talkbridge-desktop-env
python -c "import PySide6, TTS, mediapipe, sounddevice; print('All modules OK!')"

# Start the application
./launch_talkbridge_desktop.sh
```
