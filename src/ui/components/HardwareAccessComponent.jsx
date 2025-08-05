import React, { useState, useEffect, useRef } from 'react';

/**
 * Hardware Access Component for TalkBridge
 * React component that handles microphone and webcam access
 */
const HardwareAccessComponent = ({ 
    onAudioAccess, 
    onVideoAccess, 
    onError, 
    autoRequest = true,
    showControls = true,
    children 
}) => {
    const [permissions, setPermissions] = useState({
        microphone: false,
        camera: false
    });
    const [streams, setStreams] = useState({
        audio: null,
        video: null,
        combined: null
    });
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [devices, setDevices] = useState({
        audioInputs: [],
        videoInputs: [],
        audioOutputs: []
    });

    const videoRef = useRef(null);
    const audioRef = useRef(null);

    useEffect(() => {
        // Initialize hardware access manager
        if (window.hardwareAccessManager) {
            window.hardwareAccessManager.setCallbacks({
                onAudioAccess: handleAudioAccess,
                onVideoAccess: handleVideoAccess,
                onError: handleError
            });

            // Auto-request permissions if enabled
            if (autoRequest) {
                requestAllAccess();
            }

            // Check available devices
            checkAvailableDevices();
        }

        return () => {
            // Cleanup on unmount
            if (window.hardwareAccessManager) {
                window.hardwareAccessManager.stopAllStreams();
            }
        };
    }, [autoRequest]);

    const handleAudioAccess = (stream) => {
        setStreams(prev => ({ ...prev, audio: stream }));
        setPermissions(prev => ({ ...prev, microphone: true }));
        setError(null);
        
        if (onAudioAccess) {
            onAudioAccess(stream);
        }
    };

    const handleVideoAccess = (stream) => {
        setStreams(prev => ({ ...prev, video: stream }));
        setPermissions(prev => ({ ...prev, camera: true }));
        setError(null);
        
        if (onVideoAccess) {
            onVideoAccess(stream);
        }
    };

    const handleError = (type, error) => {
        setError({ type, message: error.message });
        setPermissions(prev => ({ ...prev, [type === 'microphone' ? 'microphone' : 'camera']: false }));
        
        if (onError) {
            onError(type, error);
        }
    };

    const requestMicrophoneAccess = async () => {
        setIsLoading(true);
        setError(null);
        
        try {
            await window.hardwareAccessManager.requestMicrophoneAccess();
        } catch (error) {
            handleError('microphone', error);
        } finally {
            setIsLoading(false);
        }
    };

    const requestWebcamAccess = async () => {
        setIsLoading(true);
        setError(null);
        
        try {
            await window.hardwareAccessManager.requestWebcamAccess();
        } catch (error) {
            handleError('camera', error);
        } finally {
            setIsLoading(false);
        }
    };

    const requestAllAccess = async () => {
        setIsLoading(true);
        setError(null);
        
        try {
            await window.hardwareAccessManager.requestBothAccess();
        } catch (error) {
            handleError('media', error);
        } finally {
            setIsLoading(false);
        }
    };

    const stopAllStreams = () => {
        window.hardwareAccessManager.stopAllStreams();
        setStreams({ audio: null, video: null, combined: null });
        setPermissions({ microphone: false, camera: false });
    };

    const checkAvailableDevices = async () => {
        try {
            const availableDevices = await window.hardwareAccessManager.getAvailableDevices();
            setDevices(availableDevices);
        } catch (error) {
            console.error('Error checking devices:', error);
        }
    };

    const checkPermissions = async () => {
        try {
            const permissionStatus = await window.hardwareAccessManager.checkPermissions();
            setPermissions({
                microphone: permissionStatus.microphone === 'granted',
                camera: permissionStatus.camera === 'granted'
            });
        } catch (error) {
            console.error('Error checking permissions:', error);
        }
    };

    // Update video element when stream changes
    useEffect(() => {
        if (videoRef.current && streams.video) {
            videoRef.current.srcObject = streams.video;
        }
    }, [streams.video]);

    // Update audio element when stream changes
    useEffect(() => {
        if (audioRef.current && streams.audio) {
            audioRef.current.srcObject = streams.audio;
        }
    }, [streams.audio]);

    return (
        <div className="hardware-access-component">
            {/* Error Display */}
            {error && (
                <div className="error-message" style={{
                    backgroundColor: '#ffebee',
                    color: '#c62828',
                    padding: '10px',
                    borderRadius: '4px',
                    marginBottom: '10px'
                }}>
                    <strong>Error accessing {error.type}:</strong> {error.message}
                </div>
            )}

            {/* Permission Status */}
            <div className="permission-status" style={{
                display: 'flex',
                gap: '10px',
                marginBottom: '10px'
            }}>
                <span style={{
                    padding: '4px 8px',
                    borderRadius: '4px',
                    fontSize: '12px',
                    backgroundColor: permissions.microphone ? '#4caf50' : '#f44336',
                    color: 'white'
                }}>
                    🎤 Microphone: {permissions.microphone ? 'Granted' : 'Denied'}
                </span>
                <span style={{
                    padding: '4px 8px',
                    borderRadius: '4px',
                    fontSize: '12px',
                    backgroundColor: permissions.camera ? '#4caf50' : '#f44336',
                    color: 'white'
                }}>
                    📹 Camera: {permissions.camera ? 'Granted' : 'Denied'}
                </span>
            </div>

            {/* Controls */}
            {showControls && (
                <div className="hardware-controls" style={{
                    display: 'flex',
                    gap: '10px',
                    marginBottom: '15px',
                    flexWrap: 'wrap'
                }}>
                    <button
                        onClick={requestMicrophoneAccess}
                        disabled={isLoading}
                        style={{
                            padding: '8px 16px',
                            backgroundColor: '#2196f3',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            cursor: isLoading ? 'not-allowed' : 'pointer',
                            opacity: isLoading ? 0.6 : 1
                        }}
                    >
                        {isLoading ? 'Requesting...' : '🎤 Request Microphone'}
                    </button>

                    <button
                        onClick={requestWebcamAccess}
                        disabled={isLoading}
                        style={{
                            padding: '8px 16px',
                            backgroundColor: '#ff9800',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            cursor: isLoading ? 'not-allowed' : 'pointer',
                            opacity: isLoading ? 0.6 : 1
                        }}
                    >
                        {isLoading ? 'Requesting...' : '📹 Request Camera'}
                    </button>

                    <button
                        onClick={requestAllAccess}
                        disabled={isLoading}
                        style={{
                            padding: '8px 16px',
                            backgroundColor: '#4caf50',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            cursor: isLoading ? 'not-allowed' : 'pointer',
                            opacity: isLoading ? 0.6 : 1
                        }}
                    >
                        {isLoading ? 'Requesting...' : '🎥 Request Both'}
                    </button>

                    <button
                        onClick={stopAllStreams}
                        style={{
                            padding: '8px 16px',
                            backgroundColor: '#f44336',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            cursor: 'pointer'
                        }}
                    >
                        🛑 Stop All
                    </button>

                    <button
                        onClick={checkPermissions}
                        style={{
                            padding: '8px 16px',
                            backgroundColor: '#9c27b0',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            cursor: 'pointer'
                        }}
                    >
                        🔍 Check Permissions
                    </button>
                </div>
            )}

            {/* Video Display */}
            {streams.video && (
                <div className="video-container" style={{
                    marginBottom: '15px'
                }}>
                    <video
                        ref={videoRef}
                        autoPlay
                        playsInline
                        muted
                        style={{
                            width: '100%',
                            maxWidth: '400px',
                            borderRadius: '8px',
                            border: '2px solid #ddd'
                        }}
                    />
                    <p style={{ fontSize: '12px', color: '#666', marginTop: '5px' }}>
                        📹 Live Camera Feed
                    </p>
                </div>
            )}

            {/* Audio Display */}
            {streams.audio && (
                <div className="audio-container" style={{
                    marginBottom: '15px'
                }}>
                    <audio
                        ref={audioRef}
                        autoPlay
                        muted
                        style={{ display: 'none' }}
                    />
                    <div style={{
                        padding: '10px',
                        backgroundColor: '#e3f2fd',
                        borderRadius: '4px',
                        border: '1px solid #2196f3'
                    }}>
                        <p style={{ margin: 0, fontSize: '14px', color: '#1976d2' }}>
                            🎤 Audio stream active
                        </p>
                    </div>
                </div>
            )}

            {/* Device Information */}
            {(devices.audioInputs.length > 0 || devices.videoInputs.length > 0) && (
                <div className="device-info" style={{
                    marginTop: '15px',
                    padding: '10px',
                    backgroundColor: '#f5f5f5',
                    borderRadius: '4px'
                }}>
                    <h4 style={{ margin: '0 0 10px 0', fontSize: '14px' }}>Available Devices:</h4>
                    {devices.audioInputs.length > 0 && (
                        <div>
                            <strong>🎤 Audio Inputs:</strong>
                            <ul style={{ margin: '5px 0', paddingLeft: '20px' }}>
                                {devices.audioInputs.map((device, index) => (
                                    <li key={index} style={{ fontSize: '12px' }}>
                                        {device.label || `Audio Input ${index + 1}`}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}
                    {devices.videoInputs.length > 0 && (
                        <div>
                            <strong>📹 Video Inputs:</strong>
                            <ul style={{ margin: '5px 0', paddingLeft: '20px' }}>
                                {devices.videoInputs.map((device, index) => (
                                    <li key={index} style={{ fontSize: '12px' }}>
                                        {device.label || `Camera ${index + 1}`}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
            )}

            {/* Children Components */}
            {children}
        </div>
    );
};

export default HardwareAccessComponent; 