# Speed Radar Mobile App - Setup Checklist

Use this checklist to ensure everything is properly configured before running the app.

## Initial Setup

### 1. System Requirements

- [ ] Node.js 16+ installed
  ```bash
  node --version  # Should be 16.x or higher
  ```

- [ ] npm or yarn package manager
  ```bash
  npm --version
  ```

- [ ] Git installed (optional)
  ```bash
  git --version
  ```

### 2. Backend Setup

- [ ] Backend server code available
- [ ] Python 3.8+ installed
- [ ] Backend dependencies installed
  ```bash
  cd C:\SpeedRadar\backend
  pip install -r requirements.txt
  ```

- [ ] Sample video exists
  ```bash
  # Check for sample_videos/test_video.mp4
  dir C:\SpeedRadar\sample_videos
  ```

- [ ] Backend runs successfully
  ```bash
  python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
  ```

- [ ] Backend API docs accessible
  - Open: http://localhost:8000/docs

### 3. Mobile App Installation

- [ ] Navigate to mobile directory
  ```bash
  cd C:\SpeedRadar\mobile
  ```

- [ ] Install dependencies
  ```bash
  npm install
  ```

- [ ] Verify all packages installed
  ```bash
  npm list --depth=0
  ```
  Expected:
  - expo
  - expo-camera
  - expo-av
  - axios
  - react
  - react-native

### 4. Development Environment

Choose ONE option:

#### Option A: Android Emulator
- [ ] Android Studio installed
- [ ] Android SDK installed
- [ ] AVD (emulator) created
- [ ] Emulator runs successfully
  ```bash
  # Start emulator from Android Studio
  # Or: emulator -avd YOUR_AVD_NAME
  ```

#### Option B: iOS Simulator (macOS only)
- [ ] Xcode installed
- [ ] iOS Simulator available
- [ ] Can launch simulator
  ```bash
  open -a Simulator
  ```

#### Option C: Physical Device (Recommended for testing)
- [ ] Expo Go app installed on device
  - [iOS App Store](https://apps.apple.com/app/expo-go/id982107779)
  - [Google Play Store](https://play.google.com/store/apps/details?id=host.exp.exponent)

- [ ] Device and computer on same WiFi network
- [ ] Found computer's IP address
  ```bash
  ipconfig  # Windows
  ifconfig  # macOS/Linux
  ```
  Note IP: ___.___.___.___

## Configuration

### 5. API Configuration

- [ ] Opened `src/utils/config.js`

For Android Emulator:
- [ ] Using `http://10.0.2.2:8000` (default)

For iOS Simulator:
- [ ] Using `http://localhost:8000` (default)

For Physical Device:
- [ ] Updated to `http://YOUR_IP:8000`
- [ ] Replaced YOUR_IP with actual IP address

### 6. Permissions Configuration

- [ ] Reviewed `app.json` permissions
- [ ] Camera permission message set
- [ ] Microphone permission message set

### 7. Firewall Configuration (for physical devices)

- [ ] Port 8000 allowed in firewall

  Windows:
  ```bash
  # Check Windows Firewall settings
  # Control Panel > System and Security > Windows Defender Firewall
  ```

- [ ] Backend accessible from network
  ```bash
  # Test from another device on same network
  curl http://YOUR_IP:8000
  ```

## Testing Setup

### 8. Backend Testing

- [ ] Backend server running
- [ ] Can access http://localhost:8000/docs
- [ ] Sample endpoint works
  ```bash
  curl -X POST http://localhost:8000/analyze/sample \
    -H "Content-Type: application/json" \
    -d '{"sample_name": "test_video"}'
  ```
- [ ] Returns valid JSON response

### 9. Mobile App Testing

- [ ] Start development server
  ```bash
  npm start
  ```

- [ ] QR code appears in terminal
- [ ] No error messages in terminal

For Emulator:
- [ ] App opens in emulator
- [ ] No build errors

For Physical Device:
- [ ] Scanned QR code with Expo Go
- [ ] App loads successfully
- [ ] No connection errors

### 10. Feature Testing

- [ ] App displays home screen
- [ ] "Record Video" button visible
- [ ] "Use Sample Video" button visible

**Test Sample Video**:
- [ ] Tap "Use Sample Video"
- [ ] Loading spinner appears
- [ ] Results display after processing
- [ ] No errors

**Test Camera**:
- [ ] Tap "Record Video"
- [ ] Permission dialog appears (first time)
- [ ] Grant permission
- [ ] Camera preview appears
- [ ] Can start/stop recording

**Test Upload** (optional, requires recording):
- [ ] Record short video
- [ ] Video uploads successfully
- [ ] Results display

## Troubleshooting Setup Issues

### Backend Issues

**Backend won't start**:
- [ ] Check Python version: `python --version`
- [ ] Reinstall dependencies: `pip install -r requirements.txt`
- [ ] Check port 8000 not in use: `netstat -an | find "8000"`

**Can't access backend docs**:
- [ ] Verify backend is running
- [ ] Try http://127.0.0.1:8000/docs
- [ ] Check firewall settings

### Mobile App Issues

**npm install fails**:
- [ ] Clear npm cache: `npm cache clean --force`
- [ ] Delete node_modules: `rm -rf node_modules`
- [ ] Reinstall: `npm install`

**App won't start**:
- [ ] Clear Expo cache: `npm start -- --clear`
- [ ] Restart Metro bundler
- [ ] Check for syntax errors in code

**Can't connect to backend from app**:
- [ ] Verify API_BASE_URL in config.js
- [ ] Test backend from browser on device
- [ ] Check both on same WiFi
- [ ] Verify firewall allows connections

**Camera won't work**:
- [ ] Check device permissions
- [ ] Restart app
- [ ] Try different emulator/device

### Network Issues

**Physical device can't reach backend**:
- [ ] Ping computer from device
- [ ] Check WiFi vs cellular (must be WiFi)
- [ ] Verify IP address is correct
- [ ] Test http://YOUR_IP:8000/docs in device browser

## Pre-Development Checklist

Before starting development:

- [ ] All setup steps completed
- [ ] Backend running and tested
- [ ] Mobile app runs successfully
- [ ] Sample video test passes
- [ ] Camera test passes (if needed)
- [ ] No console errors
- [ ] Documentation reviewed

## Quick Start Verification

Run these commands to verify everything:

```bash
# Terminal 1 - Backend
cd C:\SpeedRadar\backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 - Mobile
cd C:\SpeedRadar\mobile
npm start

# Then test in app:
# 1. Tap "Use Sample Video"
# 2. Verify results appear
```

If both work, setup is complete!

## Additional Tools (Optional)

For enhanced development:

- [ ] React DevTools
  ```bash
  npm install -g react-devtools
  ```

- [ ] Expo CLI
  ```bash
  npm install -g expo-cli
  ```

- [ ] EAS CLI (for builds)
  ```bash
  npm install -g eas-cli
  ```

- [ ] Android Debug Bridge (adb)
  - Comes with Android Studio

## Documentation Review

Before proceeding, review:

- [ ] README.md - Full documentation
- [ ] QUICK_START.md - Quick start guide
- [ ] CONFIGURATION_GUIDE.md - Configuration options
- [ ] TESTING_GUIDE.md - Testing procedures
- [ ] INTEGRATION_TEST.md - Backend integration

## Final Verification

Everything ready when:

- ✓ Backend returns results for sample video
- ✓ Mobile app connects to backend
- ✓ Sample video test completes successfully
- ✓ Camera permission flow works
- ✓ Results display correctly
- ✓ Error handling works

## Next Steps

After setup is complete:

1. Run integration tests (INTEGRATION_TEST.md)
2. Test with real traffic videos
3. Review configuration options
4. Start development or customization
5. Deploy to production (when ready)

## Common First-Time Issues

| Issue | Solution |
|-------|----------|
| "Cannot reach backend" | Check backend is running, verify API URL |
| Camera black screen | Grant camera permission in settings |
| App won't install | Clear cache, reinstall dependencies |
| Slow processing | Normal for first run, subsequent runs faster |
| Network timeout | Increase timeout or use shorter videos |

## Support

If stuck during setup:

1. Check troubleshooting section above
2. Review error messages carefully
3. Check both backend and mobile logs
4. Verify each checklist item
5. Try sample video test first
6. Ensure all prerequisites met

## Setup Complete!

When all checkboxes are marked, you're ready to use the Speed Radar mobile app!

To run the app daily:

```bash
# Terminal 1
cd C:\SpeedRadar\backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2
cd C:\SpeedRadar\mobile
npm start
```

Then scan QR code or run on emulator.

Happy developing!
