# Configuration Guide - Speed Radar Mobile App

This guide explains how to configure the app for different development and deployment scenarios.

## API Configuration

### Understanding the Configuration File

Location: `src/utils/config.js`

```javascript
export const API_BASE_URL = __DEV__
  ? Platform.select({
      android: 'http://10.0.2.2:8000',
      ios: 'http://localhost:8000',
      default: 'http://localhost:8000',
    })
  : 'http://YOUR_SERVER_IP:8000';
```

### Configuration Scenarios

#### 1. Android Emulator (Default)

No changes needed. The default configuration works:

```javascript
android: 'http://10.0.2.2:8000'
```

- `10.0.2.2` is a special IP that maps to `localhost` on the host machine
- Backend should run on `http://localhost:8000`

#### 2. iOS Simulator

No changes needed. The default configuration works:

```javascript
ios: 'http://localhost:8000'
```

- iOS simulator can access `localhost` directly
- Backend should run on `http://localhost:8000`

#### 3. Physical Android/iOS Device (Development)

**Step 1**: Find your computer's IP address

**Windows**:
```bash
ipconfig
```
Look for "IPv4 Address" under your active network adapter (e.g., `192.168.1.100`)

**macOS/Linux**:
```bash
ifconfig
# or
ip addr
```
Look for `inet` address (e.g., `192.168.1.100`)

**Step 2**: Update `src/utils/config.js`:

```javascript
export const API_BASE_URL = __DEV__
  ? 'http://192.168.1.100:8000'  // Your computer's IP
  : 'http://YOUR_SERVER_IP:8000';
```

**Step 3**: Ensure:
- Phone and computer are on the same WiFi network
- Backend is running on `http://0.0.0.0:8000` (not `127.0.0.1`)
- Firewall allows connections to port 8000

**Backend command**:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### 4. Production Deployment

Update for production server:

```javascript
export const API_BASE_URL = __DEV__
  ? Platform.select({...})
  : 'https://api.speedradar.com';  // Your production domain
```

**Important for Production**:
- Use HTTPS, not HTTP
- Include full domain with protocol
- Configure CORS on backend
- Implement authentication

## Network Configuration

### Testing Backend Connectivity

Add this test to verify backend is reachable:

```javascript
import { testConnection } from './src/services/api';

// In your component
const checkBackend = async () => {
  const isConnected = await testConnection();
  console.log('Backend connected:', isConnected);
};
```

### Backend CORS Configuration

For development with physical devices, update backend CORS:

```python
# backend/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Production CORS**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific domains
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)
```

## Firewall Configuration

### Windows Firewall

Allow port 8000 for development:

1. Open "Windows Defender Firewall"
2. Click "Advanced settings"
3. Click "Inbound Rules" > "New Rule"
4. Select "Port" > Next
5. Select "TCP" and enter "8000"
6. Allow the connection
7. Apply to all profiles

### macOS Firewall

```bash
# Allow port 8000
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/local/bin/python3
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp /usr/local/bin/python3
```

### Linux (ufw)

```bash
sudo ufw allow 8000/tcp
sudo ufw reload
```

## Environment-Specific Configuration

### Using Environment Variables

For more flexible configuration, use environment variables:

**Step 1**: Install dependencies
```bash
npm install react-native-dotenv
```

**Step 2**: Create `.env` file:
```env
API_BASE_URL=http://192.168.1.100:8000
REQUEST_TIMEOUT=60000
```

**Step 3**: Update `src/utils/config.js`:
```javascript
import { API_BASE_URL as ENV_API_URL } from '@env';

export const API_BASE_URL = ENV_API_URL || 'http://localhost:8000';
```

**Step 4**: Add to `.gitignore`:
```
.env
.env.local
```

### Multiple Environments

Create separate config files:

```
src/utils/
├── config.js           # Main config
├── config.dev.js       # Development
├── config.staging.js   # Staging
└── config.prod.js      # Production
```

**config.dev.js**:
```javascript
export const API_BASE_URL = 'http://192.168.1.100:8000';
export const REQUEST_TIMEOUT = 60000;
export const ENABLE_LOGGING = true;
```

**config.prod.js**:
```javascript
export const API_BASE_URL = 'https://api.speedradar.com';
export const REQUEST_TIMEOUT = 30000;
export const ENABLE_LOGGING = false;
```

**config.js**:
```javascript
const ENV = process.env.NODE_ENV || 'development';

let config;
if (ENV === 'production') {
  config = require('./config.prod');
} else if (ENV === 'staging') {
  config = require('./config.staging');
} else {
  config = require('./config.dev');
}

export default config;
```

## Camera Configuration

### Camera Permissions

Configured in `app.json`:

```json
{
  "expo": {
    "plugins": [
      [
        "expo-camera",
        {
          "cameraPermission": "Allow Speed Radar to access your camera to record traffic videos.",
          "microphonePermission": "Allow Speed Radar to access your microphone to record video with audio.",
          "recordAudioAndroid": true
        }
      ]
    ]
  }
}
```

### Recording Settings

Modify camera settings in `src/screens/CameraScreen.js`:

```javascript
const video = await cameraRef.current.recordAsync({
  maxDuration: 60,        // Max 60 seconds
  quality: '720p',        // Video quality
  mute: false,            // Include audio
});
```

**Quality Options**:
- `'2160p'` - 4K (very large files)
- `'1080p'` - Full HD (large files)
- `'720p'` - HD (recommended)
- `'480p'` - SD (smaller files)

## Performance Configuration

### Request Timeout

Adjust timeout based on network speed:

```javascript
// src/utils/config.js
export const REQUEST_TIMEOUT = 60000;  // 60 seconds

// For faster networks
export const REQUEST_TIMEOUT = 30000;  // 30 seconds

// For slower networks
export const REQUEST_TIMEOUT = 120000; // 120 seconds
```

### Video Upload Optimization

For large videos, consider compression:

```bash
npm install expo-video-thumbnails
```

```javascript
import * as VideoThumbnails from 'expo-video-thumbnails';

// Compress before upload
const compressedVideo = await compressVideo(videoUri);
```

## Debugging Configuration

### Enable Detailed Logging

```javascript
// src/services/api.js
const DEBUG = __DEV__ && true;

if (DEBUG) {
  console.log('Request URL:', url);
  console.log('Request data:', data);
  console.log('Response:', response);
}
```

### Network Inspector

Enable in development:

```javascript
// App.js
if (__DEV__) {
  const originalFetch = global.fetch;
  global.fetch = (...args) => {
    console.log('Fetch:', args);
    return originalFetch(...args);
  };
}
```

## Platform-Specific Configuration

### Android-Specific

```javascript
// android/app/src/main/AndroidManifest.xml
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.RECORD_AUDIO" />
<uses-permission android:name="android.permission.INTERNET" />

// For HTTP (not HTTPS) in development
<application
  android:usesCleartextTraffic="true"
  ...
>
```

### iOS-Specific

```javascript
// ios/SpeedRadar/Info.plist
<key>NSCameraUsageDescription</key>
<string>This app needs camera access to record traffic videos for speed detection.</string>
<key>NSMicrophoneUsageDescription</key>
<string>This app needs microphone access to record video with audio.</string>
<key>NSAppTransportSecurity</key>
<dict>
  <key>NSAllowsArbitraryLoads</key>
  <true/>  <!-- For HTTP in development only -->
</dict>
```

## Troubleshooting Network Issues

### Test Backend from Device

Use a network testing app or browser:
1. Open browser on device
2. Navigate to `http://YOUR_IP:8000/docs`
3. Should see FastAPI documentation

### Test Network Connectivity

```javascript
import NetInfo from '@react-native-community/netinfo';

NetInfo.fetch().then(state => {
  console.log('Connection type:', state.type);
  console.log('Is connected:', state.isConnected);
});
```

### Check Firewall Blocks

```bash
# Windows - Test if port is open
Test-NetConnection -ComputerName YOUR_IP -Port 8000

# macOS/Linux
nc -zv YOUR_IP 8000
```

## Configuration Checklist

Before testing:

- [ ] Backend running on correct host (0.0.0.0 for physical devices)
- [ ] Backend port accessible (8000)
- [ ] Firewall allows port 8000
- [ ] Phone and computer on same network (for physical devices)
- [ ] API_BASE_URL configured correctly
- [ ] CORS enabled on backend
- [ ] Camera permissions granted
- [ ] Network connection active

## Summary

| Scenario | API URL | Backend Host |
|----------|---------|--------------|
| Android Emulator | `http://10.0.2.2:8000` | `localhost:8000` |
| iOS Simulator | `http://localhost:8000` | `localhost:8000` |
| Physical Device | `http://192.168.1.X:8000` | `0.0.0.0:8000` |
| Production | `https://api.domain.com` | Production server |

For most development scenarios, the default configuration works out of the box. Physical device testing requires finding your IP and updating the config file.
