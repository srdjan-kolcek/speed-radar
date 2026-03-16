/**
 * API Service
 * Handles all communication with the backend FastAPI server
 */

import axios from 'axios';
import { API_BASE_URL, ENDPOINTS, REQUEST_TIMEOUT, DEFAULT_SAMPLE_NAME } from '../utils/config';

/**
 * Upload a video file to the backend for analysis
 *
 * @param {string} videoUri - Local URI of the video file
 * @returns {Promise<Object>} - Analysis results
 */
export const uploadVideo = async (videoUri) => {
  try {
    const formData = new FormData();

    // Extract filename from URI
    const filename = videoUri.split('/').pop() || 'recording.mp4';

    formData.append('video', {
      uri: videoUri,
      type: 'video/mp4',
      name: filename,
    });

    console.log(`Uploading video to: ${API_BASE_URL}${ENDPOINTS.UPLOAD}`);

    const response = await axios.post(
      `${API_BASE_URL}${ENDPOINTS.UPLOAD}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: REQUEST_TIMEOUT,
      }
    );

    console.log('Upload successful:', response.data);
    return response.data;
  } catch (error) {
    console.error('Upload error:', error);
    throw handleApiError(error);
  }
};

/**
 * Request analysis of a sample video stored on the backend
 *
 * @param {string} sampleName - Name of the sample video (without extension)
 * @returns {Promise<Object>} - Analysis results
 */
export const analyzeSample = async (sampleName = DEFAULT_SAMPLE_NAME) => {
  try {
    console.log(`Analyzing sample video: ${sampleName}`);
    console.log(`Request URL: ${API_BASE_URL}${ENDPOINTS.SAMPLE}`);

    const response = await axios.post(
      `${API_BASE_URL}${ENDPOINTS.SAMPLE}`,
      { sample_name: sampleName },
      {
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: REQUEST_TIMEOUT,
      }
    );

    console.log('Sample analysis successful:', response.data);
    return response.data;
  } catch (error) {
    console.error('Sample analysis error:', error);
    throw handleApiError(error);
  }
};

/**
 * Handle API errors and format them into user-friendly messages
 *
 * @param {Error} error - The error object from axios
 * @returns {Error} - Formatted error with user-friendly message
 */
const handleApiError = (error) => {
  if (error.response) {
    // Server responded with error status
    const status = error.response.status;
    const message = error.response.data?.detail || error.response.data?.message || 'Server error occurred';

    if (status === 404) {
      return new Error('Backend server not found. Please check if the server is running.');
    } else if (status === 500) {
      return new Error(`Server error: ${message}`);
    } else if (status === 422) {
      return new Error(`Invalid request: ${message}`);
    } else {
      return new Error(`Error ${status}: ${message}`);
    }
  } else if (error.request) {
    // Request was made but no response received
    return new Error(
      'Cannot reach backend server. Please check:\n' +
      '1. Backend server is running\n' +
      '2. API URL is correct in config\n' +
      '3. Network connection is active'
    );
  } else if (error.code === 'ECONNABORTED') {
    // Request timeout
    return new Error('Request timed out. Video processing is taking too long.');
  } else {
    // Something else happened
    return new Error(`Network error: ${error.message}`);
  }
};

/**
 * Test connection to the backend server
 *
 * @returns {Promise<boolean>} - True if server is reachable
 */
export const testConnection = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/`, { timeout: 5000 });
    return response.status === 200;
  } catch (error) {
    return false;
  }
};
