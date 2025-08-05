# TalkBridge UI Documentation

## Overview

This directory contains the TalkBridge web interface components with hardware access capabilities. The solution provides reliable microphone and webcam access for the TalkBridge web application using modern browser APIs. The implementation includes:

- **JavaScript Hardware Access Manager** (`hardware_access.js`)
- **React Component** (`HardwareAccessComponent.jsx`)
- **HTML Template** (`templates/index.html`)
- **Web Server** (`web_server.py`)

## Features

### ✅ Guaranteed Hardware Access
- **Automatic Permission Requests**: Requests microphone and webcam access on application load
- **Graceful Error Handling**: Comprehensive error handling for permission denials
- **Real-time Status Monitoring**: Live updates of permission and stream status
- **Device Enumeration**: Lists all available audio and video devices

### 🎤 Microphone Access
- Echo cancellation enabled
- Noise suppression
- Auto gain control
- Configurable sample rate (16kHz default)
- Mono channel support

### 📹 Webcam Access
- HD video support (640x480 ideal, up to 1280x720)
- Configurable frame rate (30fps ideal)
- Front-facing camera preference
- Real-time video display

## Quick Start

### 1. Start the Web Server

```bash
cd src/ui
python web_server.py
```

The server will start on `http://localhost:8080` and automatically open your browser.

### 2. Grant Permissions

When the page loads, the browser will prompt for microphone and camera permissions:

```
Allow TalkBridge to access your camera and microphone?
[Allow] [Block]
```

Click **Allow** to grant access.

### 3. Verify Hardware Access

The interface will show:
- ✅ **Green badges** for granted permissions
- 📹 **Live camera feed** when webcam access is granted
- 🎤 **Audio status indicator** when microphone access is granted

## Implementation Details

### JavaScript Hardware Access Manager

```javascript
// Initialize the hardware manager
const hardwareManager = new HardwareAccessManager();

// Request microphone access
await hardwareManager.requestMicrophoneAccess({
    audio: {
        echoCancellation: true,
        noiseSuppression: true,
        sampleRate: 16000
    }
});

// Request webcam access
await hardwareManager.requestWebcamAccess({
    video: {
        width: { ideal: 640, min: 320, max: 1280 },
        height: { ideal: 480, min: 240, max: 720 },
        frameRate: { ideal: 30, min: 15, max: 60 }
    }
});

// Request both simultaneously
await hardwareManager.requestBothAccess();
```

### React Component Usage

```jsx
import HardwareAccessComponent from './HardwareAccessComponent';

function App() {
    const handleAudioAccess = (stream) => {
        console.log('Microphone access granted:', stream);
    };

    const handleVideoAccess = (stream) => {
        console.log('Camera access granted:', stream);
    };

    const handleError = (type, error) => {
        console.error(`${type} access error:`, error);
    };

    return (
        <HardwareAccessComponent
            onAudioAccess={handleAudioAccess}
            onVideoAccess={handleVideoAccess}
            onError={handleError}
            autoRequest={true}
            showControls={true}
        >
            {/* Your application content */}
        </HardwareAccessComponent>
    );
}
```

## Browser Compatibility

### ✅ Supported Browsers
- **Chrome** 53+ (Full support)
- **Firefox** 36+ (Full support)
- **Safari** 11+ (Full support)
- **Edge** 79+ (Full support)

### 🔧 Required Features
- `navigator.mediaDevices.getUserMedia()`
- `navigator.permissions.query()`
- `navigator.mediaDevices.enumerateDevices()`

## Error Handling

### Common Permission Errors

```javascript
// Handle permission denied
try {
    await hardwareManager.requestMicrophoneAccess();
} catch (error) {
    if (error.name === 'NotAllowedError') {
        console.log('User denied microphone permission');
        // Show instructions to enable in browser settings
    } else if (error.name === 'NotFoundError') {
        console.log('No microphone found');
        // Show device connection instructions
    }
}
```

### Graceful Fallbacks

```javascript
// Check if hardware is available
const devices = await hardwareManager.getAvailableDevices();
if (devices.audioInputs.length === 0) {
    console.log('No audio input devices found');
    // Show alternative input methods
}

if (devices.videoInputs.length === 0) {
    console.log('No video input devices found');
    // Show static avatar or placeholder
}
```

## Security Considerations

### HTTPS Requirement
- **Production**: Must use HTTPS for hardware access
- **Development**: Localhost is allowed without HTTPS
- **Testing**: Use `http://localhost:8080` for development

### Permission Persistence
- Permissions are remembered by the browser
- Users can revoke permissions in browser settings
- Application gracefully handles permission changes

## Troubleshooting

### Permission Issues

1. **Check Browser Settings**
   ```
   Chrome: Settings > Privacy and Security > Site Settings > Camera/Microphone
   Firefox: about:preferences#privacy > Permissions > Camera/Microphone
   Safari: Safari > Preferences > Websites > Camera/Microphone
   ```

2. **Clear Site Data**
   ```
   Chrome: Settings > Privacy and Security > Clear browsing data
   Firefox: about:preferences#privacy > Clear Data
   ```

3. **Check Device Connection**
   - Ensure microphone/camera is properly connected
   - Check if device is being used by another application
   - Try refreshing the page

### Browser Console Errors

```javascript
// Check if MediaDevices API is available
if (!navigator.mediaDevices) {
    console.error('MediaDevices API not supported');
}

// Check if getUserMedia is available
if (!navigator.mediaDevices.getUserMedia) {
    console.error('getUserMedia not supported');
}
```

## API Reference

### HardwareAccessManager Methods

```javascript
// Request access
await requestMicrophoneAccess(constraints, onSuccess, onError)
await requestWebcamAccess(constraints, onSuccess, onError)
await requestBothAccess(constraints, onSuccess, onError)

// Check status
const status = getStatus()
const permissions = await checkPermissions()
const devices = await getAvailableDevices()

// Control streams
stopAllStreams()
stopStream('audio' | 'video' | 'combined')

// Set callbacks
setCallbacks({
    onAudioAccess: (stream) => {},
    onVideoAccess: (stream) => {},
    onError: (type, error) => {}
})
```

### Constraints Examples

```javascript
// Audio constraints
const audioConstraints = {
    echoCancellation: true,
    noiseSuppression: true,
    autoGainControl: true,
    sampleRate: 16000,
    channelCount: 1
};

// Video constraints
const videoConstraints = {
    width: { ideal: 640, min: 320, max: 1280 },
    height: { ideal: 480, min: 240, max: 720 },
    frameRate: { ideal: 30, min: 15, max: 60 },
    facingMode: 'user' // or 'environment' for back camera
};
```

## Integration with Existing Code

### Replace Streamlit Components

Instead of using Streamlit's placeholder components:

```python
# Old Streamlit approach (doesn't work for hardware access)
st.button("Start Recording")  # Placeholder only
st.image("placeholder.jpg")   # Static image only
```

Use the web interface:

```html
<!-- New web approach (actual hardware access) -->
<video id="videoElement" autoplay playsInline></video>
<audio id="audioElement" autoplay></audio>
```

### Backend Integration

```python
# Web server can handle WebSocket connections for real-time communication
import asyncio
import websockets

async def handle_media_stream(websocket, path):
    # Handle real-time audio/video data
    async for message in websocket:
        # Process media data
        pass
```

## Performance Optimization

### Stream Management
```javascript
// Stop unused streams to save resources
hardwareManager.stopStream('video'); // Stop video when not needed
hardwareManager.stopStream('audio'); // Stop audio when not needed

// Resume streams when needed
await hardwareManager.requestWebcamAccess();
```

### Memory Management
```javascript
// Clean up on page unload
window.addEventListener('beforeunload', () => {
    hardwareManager.stopAllStreams();
});
```

## Testing

### Manual Testing
1. Start the web server: `python web_server.py`
2. Open browser to `http://localhost:8080/templates/index.html`
3. Grant permissions when prompted
4. Verify camera feed and audio status
5. Test permission revocation and re-granting

### Automated Testing
Run the test suite from the test directory:

```bash
cd test
python test_hardware_access.py
```



## Deployment

### Production Setup
1. **HTTPS Required**: Deploy with SSL certificate
2. **Domain Setup**: Configure proper domain name
3. **CORS Configuration**: Set appropriate CORS headers
4. **Error Monitoring**: Implement error tracking

### Environment Variables
```bash
# Production environment
export TALKBRIDGE_HOST=0.0.0.0
export TALKBRIDGE_PORT=443
export TALKBRIDGE_SSL_CERT=/path/to/cert.pem
export TALKBRIDGE_SSL_KEY=/path/to/key.pem
```

## Support

For issues with hardware access:

1. **Check Browser Console**: Look for JavaScript errors
2. **Verify Permissions**: Check browser permission settings
3. **Test Device**: Try with different microphone/camera
4. **Browser Update**: Ensure browser is up to date

## License

This hardware access solution is part of the TalkBridge project and follows the same licensing terms. 