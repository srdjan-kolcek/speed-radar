# Speed Radar Mobile App

A React Native mobile application for detecting vehicle speeds from video footage using computer vision and machine learning. This app captures or uses sample traffic videos and sends them to a FastAPI backend for real-time speed analysis.

## Features

- **Video Recording**: Record traffic videos directly from your device camera
- **Sample Analysis**: Test the system with pre-loaded sample videos
- **Real-time Results**: View detected vehicle speeds with confidence scores
- **Clean UI**: Modern, user-friendly interface with card-based results display
- **Error Handling**: Comprehensive error handling with retry options
- **Cross-Platform**: Works on both iOS and Android devices

## Tech Stack

- **React Native** with Expo
- **expo-camera** for video recording
- **axios** for API communication
- FastAPI backend integration

## Prerequisites

Before running the mobile app, ensure you have:

1. **Node.js** (version 16 or higher)
   - Download from [nodejs.org](https://nodejs.org/)

2. **Expo CLI** (optional but recommended)
   ```bash
   npm install -g expo-cli
   ```

3. **Backend Server Running**
   - The FastAPI backend must be running at `http://localhost:8000`
   - See the backend README for setup instructions

4. **Mobile Development Environment**:
   - **For Android**: Android Studio with Android SDK
   - **For iOS**: Xcode (macOS only)
   - **Alternative**: Expo Go app on your physical device

## Installation

1. Navigate to the mobile directory:
   ```bash
   cd C:\SpeedRadar\mobile
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Configure API URL (if needed):
   - Edit `src/utils/config.js`
   - For physical devices, replace `localhost` with your computer's IP address
   - Find your IP:
     - Windows: `ipconfig` (look for IPv4 Address)
     - macOS/Linux: `ifconfig` or `ip addr`

## Running the App

### Option 1: Expo Go (Easiest)

1. Install Expo Go on your phone:
   - [iOS App Store](https://apps.apple.com/app/expo-go/id982107779)
   - [Google Play Store](https://play.google.com/store/apps/details?id=host.exp.exponent)

2. Start the development server:
   ```bash
   npm start
   ```

3. Scan the QR code with:
   - **iOS**: Camera app
   - **Android**: Expo Go app

4. **Important**: Your phone and computer must be on the same WiFi network

5. Update API URL for physical devices:
   - Edit `src/utils/config.js`
   - Replace `localhost` with your computer's IP address:
   ```javascript
   export const API_BASE_URL = 'http://192.168.1.XXX:8000'; // Your IP
   ```

### Option 2: Android Emulator

1. Install Android Studio and set up an emulator

2. Start the emulator

3. Run the app:
   ```bash
   npm run android
   ```

4. The default config uses `10.0.2.2` which maps to localhost on the host machine

### Option 3: iOS Simulator (macOS only)

1. Install Xcode from the Mac App Store

2. Run the app:
   ```bash
   npm run ios
   ```

## Configuration

### API Endpoint Configuration

Edit `src/utils/config.js` to configure the backend URL:

```javascript
export const API_BASE_URL = __DEV__
  ? Platform.select({
      android: 'http://10.0.2.2:8000',        // Android emulator
      ios: 'http://localhost:8000',            // iOS simulator
      default: 'http://localhost:8000',
    })
  : 'http://YOUR_SERVER_IP:8000';            // Production
```

For physical devices during development, use your computer's local IP:

```javascript
export const API_BASE_URL = 'http://192.168.1.100:8000'; // Example
```

### Backend Endpoints

The app communicates with these backend endpoints:

- `POST /analyze/upload` - Upload and analyze custom video
- `POST /analyze/sample` - Analyze pre-loaded sample video

## Project Structure

```
mobile/
├── App.js                      # Main app entry point
├── app.json                    # Expo configuration
├── package.json                # Dependencies
├── src/
│   ├── components/             # Reusable UI components
│   │   ├── ActionButton.js     # Styled button component
│   │   ├── ErrorMessage.js     # Error display component
│   │   ├── LoadingSpinner.js   # Loading indicator
│   │   └── ResultCard.js       # Vehicle result card
│   ├── screens/                # App screens
│   │   ├── CameraScreen.js     # Video recording screen
│   │   └── HomeScreen.js       # Main application screen
│   ├── services/               # API and external services
│   │   └── api.js              # Backend API communication
│   ├── utils/                  # Utility functions and config
│   │   └── config.js           # App configuration
│   └── styles/                 # Styling
│       └── theme.js            # Theme constants (colors, fonts)
└── assets/                     # Images and static assets
```

## Usage

### Recording a Video

1. Tap the **"Record Video"** button on the home screen
2. Grant camera permissions if prompted
3. Point your camera at traffic
4. Tap the red button to start recording
5. Tap the square button to stop recording
6. Wait for the video to upload and process
7. View the results showing detected vehicle speeds

### Using a Sample Video

1. Tap the **"Use Sample Video"** button
2. Wait for the backend to process the sample
3. View the detection results

### Understanding Results

Each detected vehicle shows:
- **Track ID**: Unique identifier for the vehicle
- **Speed**: Detected speed in km/h
- **Confidence**: Detection confidence (0-100%)
  - Green (80%+): High confidence
  - Orange (60-79%): Medium confidence
  - Red (<60%): Low confidence

## Troubleshooting

### Camera Not Working

- **Permission Denied**: Go to device Settings > Apps > Speed Radar > Permissions and enable Camera
- **Black Screen**: Restart the app or check if another app is using the camera

### Cannot Connect to Backend

**Error**: "Cannot reach backend server"

**Solutions**:
1. Verify backend is running: Open `http://localhost:8000/docs` in browser
2. Check API URL in `src/utils/config.js`
3. For physical devices:
   - Use your computer's IP instead of `localhost`
   - Ensure phone and computer are on the same WiFi
   - Check firewall settings allow port 8000
4. Test connection in app logs

### Android Emulator Network Issues

- The emulator uses `10.0.2.2` to access host `localhost`
- This is configured by default in `config.js`
- If issues persist, check AVD network settings

### Upload Timeout

**Error**: "Request timed out"

**Solutions**:
- Video processing can take 30-60 seconds
- Ensure backend has GPU access for faster processing
- Check backend logs for errors
- Try with a shorter video (10-15 seconds)

### Build Errors

**Clear cache and rebuild**:
```bash
# Clear Expo cache
expo start -c

# Or clear npm cache
npm cache clean --force
rm -rf node_modules
npm install
```

## Development

### Running in Development Mode

```bash
npm start
```

This starts the Expo development server with:
- Hot reloading enabled
- Debug mode active
- Development API URLs

### Debugging

1. **Enable Remote Debugging**:
   - Shake device or press `Cmd+D` (iOS) / `Cmd+M` (Android)
   - Select "Debug Remote JS"
   - Open Chrome DevTools at `http://localhost:19000/debugger-ui`

2. **View Logs**:
   ```bash
   # In the terminal where npm start is running
   # Logs will appear automatically
   ```

3. **React DevTools**:
   ```bash
   npm install -g react-devtools
   react-devtools
   ```

### Code Structure

**Adding New Components**:
1. Create component in `src/components/`
2. Import theme constants from `src/styles/theme.js`
3. Export as named export

**Adding New API Endpoints**:
1. Add endpoint to `src/utils/config.js`
2. Create function in `src/services/api.js`
3. Handle errors with `handleApiError()`

## Building for Production

### Android APK

```bash
expo build:android
```

Or with EAS Build (recommended):
```bash
npm install -g eas-cli
eas build -p android
```

### iOS App

```bash
expo build:ios
```

Or with EAS Build:
```bash
eas build -p ios
```

## Environment Variables

For production deployments, consider using environment variables:

1. Install `expo-constants`:
   ```bash
   npm install expo-constants
   ```

2. Create `app.config.js`:
   ```javascript
   export default {
     expo: {
       extra: {
         apiUrl: process.env.API_URL || 'http://localhost:8000',
       },
     },
   };
   ```

3. Access in code:
   ```javascript
   import Constants from 'expo-constants';
   const API_URL = Constants.expoConfig.extra.apiUrl;
   ```

## Performance Optimization

- Videos are uploaded directly without conversion (keep recordings under 30 seconds)
- Results are displayed immediately upon receiving from backend
- Camera preview uses native hardware acceleration
- Images and icons are optimized for mobile

## Security Considerations

- Camera permissions are requested only when needed
- Videos are transmitted over HTTP (use HTTPS in production)
- No video data is stored locally after upload
- API endpoints should implement authentication in production

## Future Enhancements

Potential features to add:

- [ ] Video preview before upload
- [ ] Results history with local storage
- [ ] Export results as PDF or image
- [ ] Dark mode support
- [ ] Settings screen for API configuration
- [ ] Multiple language support
- [ ] Speed limit warnings
- [ ] Share results via social media

## Contributing

To contribute to this project:

1. Follow the existing code structure
2. Use the theme constants for styling
3. Add comments for complex logic
4. Test on both iOS and Android
5. Handle errors gracefully

## License

This project is part of the Speed Radar system.

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review backend logs for server-side errors
3. Check Expo documentation: [docs.expo.dev](https://docs.expo.dev)
4. Review React Native docs: [reactnative.dev](https://reactnative.dev)

## API Response Format

The backend returns JSON in this format:

```json
{
  "status": "success",
  "processing_time": 12.5,
  "results": [
    {
      "track_id": 1,
      "speed_kmh": 45.3,
      "confidence": 0.89
    },
    {
      "track_id": 2,
      "speed_kmh": 52.1,
      "confidence": 0.92
    }
  ]
}
```

## Version History

- **1.0.0** (2024-03-15)
  - Initial release
  - Video recording functionality
  - Sample video analysis
  - Results display with confidence scores
  - Error handling and loading states
