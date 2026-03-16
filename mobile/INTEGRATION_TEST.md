# Backend Integration Test Instructions

This guide walks through testing the mobile app with the backend API.

## Prerequisites

1. Backend server running at `http://localhost:8000`
2. Mobile app installed on emulator or device
3. Sample video available in backend

## Setup Backend for Testing

### 1. Start Backend Server

```bash
cd C:\SpeedRadar\backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### 2. Verify Backend is Running

Open browser and navigate to: `http://localhost:8000/docs`

You should see the FastAPI Swagger documentation.

### 3. Test Backend Endpoints Manually

**Test Sample Endpoint**:
```bash
curl -X POST http://localhost:8000/analyze/sample \
  -H "Content-Type: application/json" \
  -d '{"sample_name": "test_video"}'
```

**Expected response**:
```json
{
  "status": "success",
  "processing_time": 12.5,
  "results": [
    {"track_id": 1, "speed_kmh": 45.3, "confidence": 0.89}
  ]
}
```

## Setup Mobile App for Testing

### 1. Configure API URL

Edit `mobile/src/utils/config.js`:

**For Android Emulator**:
```javascript
export const API_BASE_URL = 'http://10.0.2.2:8000';
```

**For Physical Device**:
```javascript
export const API_BASE_URL = 'http://192.168.1.XXX:8000';  // Your IP
```

### 2. Start Mobile App

```bash
cd mobile
npm start
```

Then:
- **Android Emulator**: Press 'a'
- **iOS Simulator**: Press 'i'
- **Physical Device**: Scan QR code with Expo Go

## Integration Test Scenarios

### Test 1: Sample Video Analysis

**Purpose**: Verify basic backend connectivity

**Steps**:
1. Launch mobile app
2. Tap "Use Sample Video" button
3. Wait for processing

**Expected Result**:
- Loading spinner appears
- After 10-60 seconds, results display
- Shows vehicle count, speeds, and confidence scores
- Processing time is displayed

**If it fails**:
- Check backend logs for errors
- Verify sample video exists in `backend/sample_videos/`
- Check API URL configuration
- Test backend endpoint with curl (see above)

### Test 2: Video Upload

**Purpose**: Verify video upload and processing

**Steps**:
1. Tap "Record Video" button
2. Grant camera permission if prompted
3. Record 5-10 seconds of traffic (or any movement)
4. Tap stop button
5. Wait for upload and processing

**Expected Result**:
- Video uploads successfully
- Processing completes
- Results display with detected vehicles
- If no vehicles detected, shows "No vehicles detected" message

**If it fails**:
- Check file size (should be < 50MB)
- Verify backend accepts multipart/form-data
- Check backend logs for upload errors
- Ensure network connectivity

### Test 3: Error Handling

**Purpose**: Verify error messages display correctly

**Test 3a - Backend Offline**:
1. Stop backend server
2. Tap "Use Sample Video"
3. Verify error message appears
4. Tap "Retry" button
5. Verify retry attempt

**Expected Result**:
- Clear error message: "Cannot reach backend server..."
- Retry button works

**Test 3b - Invalid Sample**:
1. Modify config to use non-existent sample
2. Tap "Use Sample Video"
3. Verify error handling

**Expected Result**:
- Backend returns 404 or error
- App shows user-friendly error message

### Test 4: Network Conditions

**Purpose**: Test under various network speeds

**Test with throttled network**:
1. Enable network throttling in emulator
2. Upload a video
3. Verify timeout handling

**Expected Result**:
- Upload may take longer
- App should handle gracefully
- Timeout after 60 seconds with clear message

## Verification Checklist

After running all tests:

- [ ] Sample video analysis works
- [ ] Video recording works
- [ ] Video upload succeeds
- [ ] Results display correctly
- [ ] Error messages are clear
- [ ] Retry functionality works
- [ ] Camera permissions handled correctly
- [ ] Loading states display properly
- [ ] Processing time is reasonable (< 60s)
- [ ] No console errors
- [ ] No app crashes

## Common Integration Issues

### Issue 1: "Cannot reach backend server"

**Cause**: Backend not running or wrong URL

**Solution**:
1. Verify backend is running: `curl http://localhost:8000`
2. Check API_BASE_URL in config.js
3. For physical devices, use computer's IP
4. Ensure firewall allows port 8000

### Issue 2: Upload timeout

**Cause**: Video processing taking too long

**Solution**:
1. Check backend logs for errors
2. Use shorter videos (5-10 seconds)
3. Verify backend has GPU access
4. Increase REQUEST_TIMEOUT if needed

### Issue 3: No results returned

**Cause**: Backend processed but no vehicles detected

**Solution**:
1. Check backend response in logs
2. Verify video has moving vehicles
3. Check backend detection thresholds
4. Try sample video first to verify pipeline

### Issue 4: Permission denied

**Cause**: Camera permissions not granted

**Solution**:
1. Go to device Settings > Apps > Speed Radar
2. Enable Camera permission
3. Restart app

## Backend Logs to Monitor

Watch backend terminal for:

```
INFO:     10.0.2.2:XXXXX - "POST /analyze/sample HTTP/1.1" 200 OK
INFO:     Processing video: test_video
INFO:     Detected 3 vehicles
INFO:     Processing complete in 15.3s
```

Or for errors:
```
ERROR:    Error processing video: ...
WARNING:  No vehicles detected
ERROR:    Sample video not found: ...
```

## Mobile Logs to Monitor

In Expo DevTools console, look for:

```
Analyzing sample video: test_video
Request URL: http://10.0.2.2:8000/analyze/sample
Sample analysis successful: {status: "success", ...}
```

Or for errors:
```
Sample analysis error: Error: Cannot reach backend server...
```

## Performance Benchmarks

Record actual performance:

| Test | Expected | Actual | Status |
|------|----------|--------|--------|
| Sample analysis | < 30s | ___ s | Pass/Fail |
| Video upload (10s) | < 5s | ___ s | Pass/Fail |
| Video processing | < 60s | ___ s | Pass/Fail |
| Results render | < 1s | ___ s | Pass/Fail |

## Network Debugging

### View actual API requests:

Add to `src/services/api.js`:
```javascript
console.log('Request:', {
  url: `${API_BASE_URL}${ENDPOINTS.SAMPLE}`,
  method: 'POST',
  data: { sample_name }
});
```

### Test endpoint from mobile device:

If using physical device, test if backend is reachable:
1. Open device browser
2. Navigate to `http://YOUR_IP:8000/docs`
3. Should see API documentation

If this fails, the mobile app won't be able to connect either.

## Integration Test Report Template

```markdown
# Integration Test Report

**Date**: 2024-03-15
**Tester**: [Your Name]
**Backend Version**: 1.0.0
**Mobile Version**: 1.0.0
**Platform**: Android Emulator / Physical Device

## Environment
- Backend: http://localhost:8000
- Mobile API URL: http://10.0.2.2:8000
- Network: WiFi / 4G / Emulator

## Test Results

### Sample Video Analysis
- Status: ✓ Pass / ✗ Fail
- Processing Time: 15.3s
- Results: 3 vehicles detected
- Notes: _____

### Video Upload
- Status: ✓ Pass / ✗ Fail
- Upload Time: 3.2s
- Processing Time: 18.5s
- Results: 2 vehicles detected
- Notes: _____

### Error Handling
- Backend offline: ✓ Pass / ✗ Fail
- Invalid sample: ✓ Pass / ✗ Fail
- Notes: _____

## Issues Found
1. _____
2. _____

## Recommendations
- _____
```

## Next Steps After Successful Integration

1. **Performance Tuning**
   - Optimize video quality vs file size
   - Reduce processing time
   - Improve error messages

2. **Feature Additions**
   - Add video preview
   - Implement results caching
   - Add progress indicators

3. **Production Preparation**
   - Add authentication
   - Enable HTTPS
   - Implement rate limiting
   - Add crash reporting

## Continuous Integration

For automated testing:

1. Set up test backend
2. Create automated API tests
3. Mock camera for automated testing
4. Run tests on each commit

## Support

If integration tests fail:

1. Check this guide's troubleshooting section
2. Review backend logs carefully
3. Test backend endpoints independently
4. Verify network connectivity
5. Check firewall and security settings
6. Try sample video first before custom uploads

The mobile app and backend should work seamlessly together. Follow these tests to verify the integration is successful.
