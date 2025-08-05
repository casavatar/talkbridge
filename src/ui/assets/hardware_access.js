/**
 * Hardware Access Manager for TalkBridge
 * Handles microphone and webcam access using browser MediaDevices API
 */

class HardwareAccessManager {
    constructor() {
        this.streams = {
            audio: null,
            video: null,
            combined: null
        };
        this.permissions = {
            microphone: false,
            camera: false
        };
        this.callbacks = {
            onAudioAccess: null,
            onVideoAccess: null,
            onError: null
        };
    }

    /**
     * Request microphone access
     * @param {Object} constraints - Audio constraints
     * @param {Function} onSuccess - Success callback
     * @param {Function} onError - Error callback
     */
    async requestMicrophoneAccess(constraints = {}, onSuccess = null, onError = null) {
        const defaultConstraints = {
            audio: {
                echoCancellation: true,
                noiseSuppression: true,
                autoGainControl: true,
                sampleRate: 16000,
                channelCount: 1
            }
        };

        const audioConstraints = { ...defaultConstraints.audio, ...constraints.audio };

        try {
            console.log('Requesting microphone access...');
            const stream = await navigator.mediaDevices.getUserMedia({ audio: audioConstraints });
            
            this.streams.audio = stream;
            this.permissions.microphone = true;
            
            console.log('Microphone access granted');
            
            if (onSuccess) onSuccess(stream);
            if (this.callbacks.onAudioAccess) this.callbacks.onAudioAccess(stream);
            
            return stream;
        } catch (error) {
            console.error('Microphone access denied:', error);
            this.permissions.microphone = false;
            
            if (onError) onError(error);
            if (this.callbacks.onError) this.callbacks.onError('microphone', error);
            
            throw error;
        }
    }

    /**
     * Request webcam access
     * @param {Object} constraints - Video constraints
     * @param {Function} onSuccess - Success callback
     * @param {Function} onError - Error callback
     */
    async requestWebcamAccess(constraints = {}, onSuccess = null, onError = null) {
        const defaultConstraints = {
            video: {
                width: { ideal: 640, min: 320, max: 1280 },
                height: { ideal: 480, min: 240, max: 720 },
                frameRate: { ideal: 30, min: 15, max: 60 },
                facingMode: 'user'
            }
        };

        const videoConstraints = { ...defaultConstraints.video, ...constraints.video };

        try {
            console.log('Requesting webcam access...');
            const stream = await navigator.mediaDevices.getUserMedia({ video: videoConstraints });
            
            this.streams.video = stream;
            this.permissions.camera = true;
            
            console.log('Webcam access granted');
            
            if (onSuccess) onSuccess(stream);
            if (this.callbacks.onVideoAccess) this.callbacks.onVideoAccess(stream);
            
            return stream;
        } catch (error) {
            console.error('Webcam access denied:', error);
            this.permissions.camera = false;
            
            if (onError) onError(error);
            if (this.callbacks.onError) this.callbacks.onError('camera', error);
            
            throw error;
        }
    }

    /**
     * Request both microphone and webcam access
     * @param {Object} constraints - Media constraints
     * @param {Function} onSuccess - Success callback
     * @param {Function} onError - Error callback
     */
    async requestBothAccess(constraints = {}, onSuccess = null, onError = null) {
        const defaultConstraints = {
            audio: {
                echoCancellation: true,
                noiseSuppression: true,
                autoGainControl: true,
                sampleRate: 16000,
                channelCount: 1
            },
            video: {
                width: { ideal: 640, min: 320, max: 1280 },
                height: { ideal: 480, min: 240, max: 720 },
                frameRate: { ideal: 30, min: 15, max: 60 },
                facingMode: 'user'
            }
        };

        const mediaConstraints = {
            audio: { ...defaultConstraints.audio, ...constraints.audio },
            video: { ...defaultConstraints.video, ...constraints.video }
        };

        try {
            console.log('Requesting microphone and webcam access...');
            const stream = await navigator.mediaDevices.getUserMedia(mediaConstraints);
            
            this.streams.combined = stream;
            this.streams.audio = stream;
            this.streams.video = stream;
            this.permissions.microphone = true;
            this.permissions.camera = true;
            
            console.log('Microphone and webcam access granted');
            
            if (onSuccess) onSuccess(stream);
            
            return stream;
        } catch (error) {
            console.error('Media access denied:', error);
            this.permissions.microphone = false;
            this.permissions.camera = false;
            
            if (onError) onError(error);
            if (this.callbacks.onError) this.callbacks.onError('media', error);
            
            throw error;
        }
    }

    /**
     * Check current permissions
     * @returns {Object} Permission status
     */
    async checkPermissions() {
        try {
            const permissions = await navigator.permissions.query({ name: 'camera' });
            const audioPermissions = await navigator.permissions.query({ name: 'microphone' });
            
            return {
                camera: permissions.state,
                microphone: audioPermissions.state
            };
        } catch (error) {
            console.warn('Could not check permissions:', error);
            return {
                camera: 'unknown',
                microphone: 'unknown'
            };
        }
    }

    /**
     * Stop all media streams
     */
    stopAllStreams() {
        Object.values(this.streams).forEach(stream => {
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
            }
        });
        
        this.streams = {
            audio: null,
            video: null,
            combined: null
        };
        
        console.log('All media streams stopped');
    }

    /**
     * Stop specific stream
     * @param {string} type - Stream type ('audio', 'video', 'combined')
     */
    stopStream(type) {
        if (this.streams[type]) {
            this.streams[type].getTracks().forEach(track => track.stop());
            this.streams[type] = null;
            console.log(`${type} stream stopped`);
        }
    }

    /**
     * Get available devices
     * @returns {Promise<Object>} Available devices
     */
    async getAvailableDevices() {
        try {
            const devices = await navigator.mediaDevices.enumerateDevices();
            
            return {
                audioInputs: devices.filter(device => device.kind === 'audioinput'),
                videoInputs: devices.filter(device => device.kind === 'videoinput'),
                audioOutputs: devices.filter(device => device.kind === 'audiooutput')
            };
        } catch (error) {
            console.error('Error getting devices:', error);
            return { audioInputs: [], videoInputs: [], audioOutputs: [] };
        }
    }

    /**
     * Set callbacks for hardware access events
     * @param {Object} callbacks - Callback functions
     */
    setCallbacks(callbacks) {
        this.callbacks = { ...this.callbacks, ...callbacks };
    }

    /**
     * Get current status
     * @returns {Object} Current status
     */
    getStatus() {
        return {
            permissions: this.permissions,
            streams: {
                audio: !!this.streams.audio,
                video: !!this.streams.video,
                combined: !!this.streams.combined
            }
        };
    }
}

// Create global instance
window.hardwareAccessManager = new HardwareAccessManager();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = HardwareAccessManager;
} 