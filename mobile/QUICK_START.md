# Quick Start Guide - Speed Radar Mobile App

Get up and running with the Speed Radar mobile app in 5 minutes.

## Prerequisites Checklist

- [ ] Node.js 16+ installed
- [ ] Backend server running at `http://localhost:8000`
- [ ] Android emulator or physical device ready

## Step 1: Install Dependencies (2 minutes)

```bash
cd C:\SpeedRadar\mobile
npm install
```

## Step 2: Start the App (1 minute)

### For Android Emulator

```bash
npm run android
```

The app will open in your Android emulator automatically.

### For Physical Device (Expo Go)

```bash
npm start
```

Then:
1. Install "Expo Go" from Play Store or App Store
2. Scan the QR code displayed in terminal
3. Wait for app to load

## Step 3: Configure for Physical Device (Optional)

If using a physical device, update the API URL:

1. Find your computer's IP address:
   ```bash
   ipconfig  # Windows
   ```
   Look for "IPv4 Address" (e.g., 192.168.1.100)

2. Edit `src/utils/config.js`:
   ```javascript
   export const API_BASE_URL = 'http://192.168.1.100:8000';  // Your IP
   ```

3. Ensure phone and computer are on same WiFi network

## Step 4: Test the App

### Option A: Use Sample Video (Fastest)

1. Tap **"Use Sample Video"** button
2. Wait 10-30 seconds for processing
3. View results

### Option B: Record Your Own Video

1. Tap **"Record Video"** button
2. Grant camera permission when prompted
3. Record traffic for 5-10 seconds
4. Tap stop button
5. Wait for upload and processing
6. View results

## Common Quick Fixes

### "Cannot reach backend server"

```bash
# Check if backend is running
curl http://localhost:8000
# or open in browser: http://localhost:8000/docs
```

If not running, start the backend:
```bash
cd C:\SpeedRadar\backend
python -m uvicorn main:app --reload
```

### Camera permission denied

Go to: Device Settings > Apps > Speed Radar > Permissions > Enable Camera

### Build errors

```bash
# Clear cache and reinstall
npm start -- --clear
```

## Verify Everything Works

1. Backend running: Open `http://localhost:8000/docs` in browser
2. Mobile app running: See "Speed Radar" home screen
3. Sample test works: Tap "Use Sample Video" and see results
4. Camera works: Tap "Record Video" and see camera view

## Next Steps

- Read full README.md for detailed documentation
- Try recording traffic videos in different lighting
- Check backend logs to understand processing time
- Experiment with different video angles

## Getting Help

1. Check `README.md` troubleshooting section
2. Review backend logs in terminal
3. Check app logs in Expo DevTools
4. Ensure all prerequisites are installed correctly

## Development Workflow

```bash
# Start backend
cd C:\SpeedRadar\backend
python -m uvicorn main:app --reload

# In new terminal, start mobile app
cd C:\SpeedRadar\mobile
npm start

# Make changes to code
# App will hot-reload automatically
```

## Production Checklist

Before deploying to production:

- [ ] Update API_BASE_URL in config.js to production server
- [ ] Test on both iOS and Android devices
- [ ] Test with various network conditions
- [ ] Configure proper authentication
- [ ] Enable HTTPS for API communication
- [ ] Optimize video compression settings
- [ ] Add analytics and crash reporting
- [ ] Create app store listings and screenshots

## Useful Commands

```bash
# Start development server
npm start

# Start on Android
npm run android

# Start on iOS (macOS only)
npm run ios

# Clear cache
npm start -- --clear

# View logs
# Logs appear in terminal automatically

# Build production APK
expo build:android
```

## App Features at a Glance

1. **Record Video**: Capture traffic footage with your camera
2. **Use Sample**: Test with pre-loaded video
3. **View Results**: See detected speeds with confidence scores
4. **Error Handling**: Clear error messages with retry options
5. **Clean UI**: Modern interface with smooth animations

Enjoy using Speed Radar!
