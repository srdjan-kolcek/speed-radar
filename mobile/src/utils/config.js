/**
 * Application Configuration
 *
 * API_BASE_URL:
 * - For Android Emulator: use 10.0.2.2 (maps to localhost on host machine)
 * - For iOS Simulator: use localhost
 * - For Physical Device: use your computer's IP address on local network
 */

import { Platform } from 'react-native';

// Determine the API base URL based on environment and platform
export const API_BASE_URL = __DEV__
  ? Platform.select({
      android: 'http://10.0.2.2:8000',
      ios: 'http://localhost:8000',
      default: 'http://localhost:8000',
    })
  : 'http://YOUR_SERVER_IP:8000'; // Replace with production server IP

export const ENDPOINTS = {
  UPLOAD: '/analyze/upload',
  SAMPLE: '/analyze/sample',
};

// Request timeout in milliseconds
export const REQUEST_TIMEOUT = 60000; // 60 seconds

// Sample video name (must exist in backend sample_videos folder)
export const DEFAULT_SAMPLE_NAME = 'test_video';
