# Testing Guide - Speed Radar Mobile App

This guide covers testing strategies and procedures for the Speed Radar mobile application.

## Pre-Testing Checklist

Before running tests, ensure:

- [ ] Backend server is running (`http://localhost:8000`)
- [ ] Backend has sample video available
- [ ] Mobile app builds without errors
- [ ] Camera permissions are granted
- [ ] Device/emulator has good network connection

## Manual Testing Procedures

### 1. Sample Video Analysis Test

**Purpose**: Verify backend connectivity and result display

**Steps**:
1. Launch the app
2. Tap "Use Sample Video" button
3. Observe loading spinner appears
4. Wait for processing to complete
5. Verify results are displayed

**Expected Results**:
- Loading spinner shows "Analyzing sample video..."
- Results appear within 10-60 seconds
- Each vehicle shows: Track ID, Speed (km/h), Confidence
- Processing time is displayed
- Vehicle count is accurate

**Failure Scenarios**:
- Error: "Cannot reach backend server"
  - Solution: Check backend is running
- Timeout error
  - Solution: Check backend logs, video might be too large
- No results displayed
  - Solution: Check backend sample video exists

### 2. Video Recording Test

**Purpose**: Verify camera functionality and video upload

**Steps**:
1. Tap "Record Video" button
2. Grant camera permission if prompted
3. Point camera at moving objects
4. Tap record button (red circle)
5. Record for 5-10 seconds
6. Tap stop button (red square)
7. Wait for upload and processing
8. Verify results

**Expected Results**:
- Camera preview appears
- Recording indicator shows timer
- Video stops when requested
- Upload begins immediately
- Results appear after processing
- Video quality is acceptable

**Failure Scenarios**:
- Black screen
  - Solution: Check camera permissions
- Recording doesn't start
  - Solution: Restart app, check device camera
- Upload fails
  - Solution: Check network connection, API URL

### 3. Permission Handling Test

**Purpose**: Verify proper permission requests

**Steps**:
1. Fresh install or clear app data
2. Launch app
3. Tap "Record Video"
4. Observe permission dialog
5. Deny permission
6. Observe error handling
7. Tap "Grant Permission"
8. Observe permission re-request

**Expected Results**:
- Permission dialog shows custom message
- App handles denial gracefully
- Retry option works correctly
- Permission persists after granted

### 4. Error Recovery Test

**Purpose**: Verify error handling and recovery

**Test 4a - Backend Offline**:
1. Stop backend server
2. Tap "Use Sample Video"
3. Observe error message
4. Start backend server
5. Tap "Retry" button
6. Verify success

**Test 4b - Network Timeout**:
1. Use slow network or large video
2. Observe timeout handling
3. Verify error message is clear
4. Verify retry works

**Test 4c - Invalid Response**:
1. Modify backend to return invalid JSON
2. Submit request
3. Verify error handling
4. Restore backend
5. Verify recovery

### 5. UI/UX Test

**Purpose**: Verify user interface quality

**Checklist**:
- [ ] All buttons are easily tappable
- [ ] Text is readable on all screen sizes
- [ ] Colors are consistent with theme
- [ ] Loading indicators are visible
- [ ] Cards display data correctly
- [ ] Navigation is intuitive
- [ ] No UI elements overlap
- [ ] Scrolling works smoothly

### 6. Cross-Platform Test

**Purpose**: Verify functionality on different platforms

**Platforms to Test**:
- [ ] Android Emulator
- [ ] Physical Android device
- [ ] iOS Simulator (macOS only)
- [ ] Physical iOS device (macOS only)

**Platform-Specific Issues**:
- Android: Check permission handling
- iOS: Verify camera orientation
- Both: Test network connectivity

### 7. Performance Test

**Purpose**: Verify app performance under various conditions

**Test Cases**:

**7a - Large Video**:
- Record 30+ second video
- Verify upload completes
- Check memory usage
- Verify no crashes

**7b - Multiple Vehicles**:
- Use video with 10+ vehicles
- Verify all results display
- Check scrolling performance
- Verify no UI lag

**7c - Slow Network**:
- Enable network throttling
- Submit request
- Verify timeout handling
- Check user feedback

### 8. Edge Cases Test

**Purpose**: Test unusual scenarios

**Test Cases**:

**8a - No Vehicles Detected**:
- Record video with no vehicles
- Verify "No vehicles detected" message
- Verify no crash

**8b - Low Confidence Results**:
- Use difficult video (poor lighting)
- Verify low confidence scores display correctly
- Check confidence color coding

**8c - App Backgrounding**:
- Start video upload
- Background the app
- Return to app
- Verify upload continues or handles gracefully

**8d - Multiple Rapid Requests**:
- Tap "Use Sample" multiple times quickly
- Verify requests are handled properly
- No duplicate results

## Automated Testing Setup

### Unit Tests (Future Implementation)

```bash
npm install --save-dev @testing-library/react-native jest
```

**Example test structure**:
```javascript
// __tests__/components/ResultCard.test.js
import { render } from '@testing-library/react-native';
import { ResultCard } from '../src/components/ResultCard';

test('ResultCard displays correct speed', () => {
  const { getByText } = render(
    <ResultCard trackId={1} speedKmh={45.3} confidence={0.89} />
  );
  expect(getByText('45.3')).toBeTruthy();
});
```

### Integration Tests (Future Implementation)

```javascript
// __tests__/api/uploadVideo.test.js
import { uploadVideo } from '../src/services/api';

test('uploadVideo returns valid response', async () => {
  const mockUri = 'file:///path/to/video.mp4';
  const response = await uploadVideo(mockUri);
  expect(response.status).toBe('success');
  expect(response.results).toBeDefined();
});
```

## Testing Checklists

### Pre-Release Testing

Before releasing a new version:

- [ ] All manual tests pass
- [ ] Tested on Android emulator
- [ ] Tested on physical Android device
- [ ] Tested on iOS simulator (if available)
- [ ] Tested on physical iOS device (if available)
- [ ] Tested with sample video
- [ ] Tested with recorded video
- [ ] Tested error scenarios
- [ ] Tested permission flows
- [ ] Verified UI on different screen sizes
- [ ] Checked memory usage
- [ ] Verified no console errors
- [ ] Backend integration works
- [ ] Documentation is up to date

### Regression Testing

After making changes, verify:

- [ ] Existing features still work
- [ ] No new console errors
- [ ] Performance hasn't degraded
- [ ] UI still renders correctly
- [ ] API calls still succeed
- [ ] Error handling still works

## Test Data

### Sample Videos

The backend should have these sample videos:
- `test_video.mp4` - Standard traffic footage (default)
- Short videos (5-10 seconds) for quick testing
- Long videos (30+ seconds) for performance testing
- Videos with varying vehicle counts

### Test Accounts

For production testing with authentication:
- Test user account
- Admin account
- Account with limited permissions

## Performance Benchmarks

Target performance metrics:

| Metric | Target | Acceptable |
|--------|--------|------------|
| App launch time | < 2s | < 3s |
| Sample video processing | < 30s | < 60s |
| Video upload (10s video) | < 5s | < 10s |
| Results rendering | < 1s | < 2s |
| Camera launch | < 1s | < 2s |
| Recording start | < 0.5s | < 1s |

## Bug Reporting Template

When reporting bugs, include:

```markdown
**Environment**:
- Device: [Android Emulator / Physical Device]
- OS Version: [Android 13 / iOS 16]
- App Version: [1.0.0]
- Backend Version: [1.0.0]

**Steps to Reproduce**:
1. Launch app
2. Tap "Record Video"
3. ...

**Expected Behavior**:
Camera should open and show preview

**Actual Behavior**:
App crashes with error: ...

**Screenshots**:
[Attach screenshots]

**Logs**:
[Paste relevant console logs]

**Additional Context**:
This started happening after...
```

## Test Results Documentation

Keep a log of test results:

```markdown
## Test Session - 2024-03-15

**Tester**: [Your Name]
**Build**: v1.0.0
**Platform**: Android Emulator (API 33)

### Tests Performed:
- [x] Sample video analysis - PASS
- [x] Video recording - PASS
- [x] Permission handling - PASS
- [x] Error recovery - PASS
- [ ] Cross-platform - PENDING (iOS not available)

### Issues Found:
1. Loading spinner too small on tablet - LOW PRIORITY
2. Confidence color not visible on light backgrounds - MEDIUM

### Notes:
- Processing time average: 15 seconds
- No crashes observed
- Memory usage stable
```

## Debugging Tips

### Enable Debug Mode

Add to `src/utils/config.js`:
```javascript
export const DEBUG = __DEV__;
```

### View Network Requests

In `src/services/api.js`:
```javascript
if (DEBUG) {
  console.log('API Request:', url, data);
  console.log('API Response:', response.data);
}
```

### Check Component Render

```javascript
useEffect(() => {
  console.log('Component rendered with:', props);
}, [props]);
```

### Monitor Performance

```javascript
const startTime = Date.now();
// ... operation
console.log(`Operation took: ${Date.now() - startTime}ms`);
```

## Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Camera black screen | Permission denied | Check device settings |
| Upload fails | Wrong API URL | Verify config.js |
| No results shown | Backend error | Check backend logs |
| App crashes on record | Memory issue | Restart app/device |
| Slow processing | Large video | Use shorter videos |
| Network timeout | Slow connection | Increase timeout value |

## Testing Best Practices

1. **Test on Real Devices**: Emulators don't always match real device behavior
2. **Test Various Networks**: WiFi, 4G, 5G, slow connections
3. **Test Edge Cases**: No internet, low battery, low storage
4. **Document Issues**: Keep detailed notes of bugs found
5. **Regression Test**: Verify old bugs don't reappear
6. **User Testing**: Get feedback from real users
7. **Performance Monitor**: Watch memory and CPU usage
8. **Accessibility**: Test with screen readers and larger fonts

## Continuous Testing

Integrate testing into development workflow:

1. **Before Commit**: Run quick smoke tests
2. **Before PR**: Full manual test suite
3. **Before Release**: Complete checklist + cross-platform tests
4. **After Release**: Monitor crash reports and user feedback

## Tools for Testing

- **React Native Debugger**: UI inspection and network monitoring
- **Expo DevTools**: Logs and debugging
- **Android Studio Profiler**: Performance monitoring
- **Xcode Instruments**: iOS performance analysis
- **Charles Proxy**: Network request inspection
- **Postman**: API endpoint testing

## Next Steps

Future testing improvements:

- [ ] Set up automated unit tests
- [ ] Implement integration tests
- [ ] Add E2E testing with Detox
- [ ] Set up CI/CD pipeline
- [ ] Add crash reporting (Sentry)
- [ ] Implement analytics tracking
- [ ] Add performance monitoring
- [ ] Create automated test suite

Testing is crucial for maintaining quality. Follow this guide to ensure the app works reliably across all scenarios.
