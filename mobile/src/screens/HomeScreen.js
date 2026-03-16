/**
 * Home Screen
 * Main application screen with record/sample buttons and results display
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  StatusBar,
  SafeAreaView,
  Alert,
} from 'react-native';
import { CameraScreen } from './CameraScreen';
import { ActionButton } from '../components/ActionButton';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ResultCard } from '../components/ResultCard';
import { ErrorMessage } from '../components/ErrorMessage';
import { uploadVideo, analyzeSample } from '../services/api';
import { colors, typography, spacing } from '../styles/theme';

// App states
const STATES = {
  IDLE: 'idle',
  CAMERA: 'camera',
  PROCESSING: 'processing',
  RESULTS: 'results',
  ERROR: 'error',
};

export const HomeScreen = () => {
  const [appState, setAppState] = useState(STATES.IDLE);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [processingMessage, setProcessingMessage] = useState('Processing...');

  // Handle record video button press
  const handleRecordPress = () => {
    setAppState(STATES.CAMERA);
  };

  // Handle sample video button press
  const handleSamplePress = async () => {
    setAppState(STATES.PROCESSING);
    setProcessingMessage('Analyzing sample video...');

    try {
      const response = await analyzeSample();

      if (response.status === 'success' && response.results) {
        setResults(response);
        setAppState(STATES.RESULTS);
      } else {
        throw new Error('No results returned from server');
      }
    } catch (err) {
      console.error('Sample analysis error:', err);
      setError(err.message);
      setAppState(STATES.ERROR);
    }
  };

  // Handle video recording completion
  const handleRecordingComplete = async (videoUri) => {
    setAppState(STATES.PROCESSING);
    setProcessingMessage('Uploading and analyzing video...');

    try {
      const response = await uploadVideo(videoUri);

      if (response.status === 'success' && response.results) {
        setResults(response);
        setAppState(STATES.RESULTS);
      } else {
        throw new Error('No results returned from server');
      }
    } catch (err) {
      console.error('Upload error:', err);
      setError(err.message);
      setAppState(STATES.ERROR);
    }
  };

  // Handle camera cancel
  const handleCameraCancel = () => {
    setAppState(STATES.IDLE);
  };

  // Handle retry after error
  const handleRetry = () => {
    setAppState(STATES.IDLE);
    setError(null);
  };

  // Handle new analysis
  const handleNewAnalysis = () => {
    setAppState(STATES.IDLE);
    setResults(null);
    setError(null);
  };

  // Render camera screen
  if (appState === STATES.CAMERA) {
    return (
      <CameraScreen
        onRecordingComplete={handleRecordingComplete}
        onCancel={handleCameraCancel}
      />
    );
  }

  // Render main screen
  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle="dark-content" backgroundColor={colors.background} />
      <ScrollView
        style={styles.container}
        contentContainerStyle={styles.contentContainer}
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>Speed Radar</Text>
          <Text style={styles.subtitle}>Vehicle Speed Detection</Text>
        </View>

        {/* Action Buttons - Show only in IDLE state */}
        {appState === STATES.IDLE && (
          <View style={styles.actionsContainer}>
            <ActionButton
              title="Record Video"
              onPress={handleRecordPress}
              variant="primary"
              icon={<Text style={styles.buttonIcon}>📹</Text>}
              style={styles.actionButton}
            />
            <ActionButton
              title="Use Sample Video"
              onPress={handleSamplePress}
              variant="secondary"
              icon={<Text style={styles.buttonIcon}>▶️</Text>}
              style={styles.actionButton}
            />
          </View>
        )}

        {/* Processing State */}
        {appState === STATES.PROCESSING && (
          <LoadingSpinner message={processingMessage} />
        )}

        {/* Error State */}
        {appState === STATES.ERROR && (
          <ErrorMessage message={error} onRetry={handleRetry} />
        )}

        {/* Results State */}
        {appState === STATES.RESULTS && results && (
          <View style={styles.resultsContainer}>
            <View style={styles.resultsHeader}>
              <Text style={styles.resultsTitle}>Detection Results</Text>
              <Text style={styles.processingTime}>
                Processed in {results.processing_time?.toFixed(2)}s
              </Text>
            </View>

            {results.results && results.results.length > 0 ? (
              <>
                <Text style={styles.vehicleCount}>
                  {results.results.length} vehicle{results.results.length !== 1 ? 's' : ''} detected
                </Text>
                {results.results.map((result, index) => (
                  <ResultCard
                    key={`${result.track_id}-${index}`}
                    trackId={result.track_id}
                    speedKmh={result.speed_kmh}
                    confidence={result.confidence}
                  />
                ))}
              </>
            ) : (
              <View style={styles.noResultsContainer}>
                <Text style={styles.noResultsIcon}>🚗</Text>
                <Text style={styles.noResultsText}>No vehicles detected in the video</Text>
              </View>
            )}

            <ActionButton
              title="Analyze Another Video"
              onPress={handleNewAnalysis}
              variant="primary"
              style={styles.newAnalysisButton}
            />
          </View>
        )}

        {/* Instructions - Show only in IDLE state */}
        {appState === STATES.IDLE && (
          <View style={styles.instructionsContainer}>
            <Text style={styles.instructionsTitle}>How to use:</Text>
            <Text style={styles.instructionText}>
              1. Tap "Record Video" to capture traffic footage
            </Text>
            <Text style={styles.instructionText}>
              2. Or tap "Use Sample Video" to test with pre-loaded footage
            </Text>
            <Text style={styles.instructionText}>
              3. Wait for the AI to analyze vehicle speeds
            </Text>
            <Text style={styles.instructionText}>
              4. View detected speeds and confidence levels
            </Text>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: colors.background,
  },
  container: {
    flex: 1,
  },
  contentContainer: {
    paddingBottom: spacing.xl,
  },
  header: {
    alignItems: 'center',
    paddingTop: spacing.xl,
    paddingBottom: spacing.lg,
    backgroundColor: colors.primary,
  },
  title: {
    ...typography.h1,
    color: '#FFFFFF',
    marginBottom: spacing.xs,
  },
  subtitle: {
    ...typography.body,
    color: '#FFFFFF',
    opacity: 0.9,
  },
  actionsContainer: {
    padding: spacing.md,
  },
  actionButton: {
    marginVertical: spacing.sm,
  },
  buttonIcon: {
    fontSize: 24,
  },
  resultsContainer: {
    paddingTop: spacing.md,
  },
  resultsHeader: {
    paddingHorizontal: spacing.md,
    marginBottom: spacing.md,
  },
  resultsTitle: {
    ...typography.h2,
    color: colors.text,
    marginBottom: spacing.xs,
  },
  processingTime: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  vehicleCount: {
    ...typography.body,
    color: colors.textSecondary,
    paddingHorizontal: spacing.md,
    marginBottom: spacing.sm,
  },
  noResultsContainer: {
    alignItems: 'center',
    padding: spacing.xl,
  },
  noResultsIcon: {
    fontSize: 64,
    marginBottom: spacing.md,
  },
  noResultsText: {
    ...typography.body,
    color: colors.textSecondary,
    textAlign: 'center',
  },
  newAnalysisButton: {
    marginHorizontal: spacing.md,
    marginTop: spacing.lg,
  },
  instructionsContainer: {
    margin: spacing.md,
    padding: spacing.md,
    backgroundColor: colors.cardBackground,
    borderRadius: 12,
  },
  instructionsTitle: {
    ...typography.h3,
    color: colors.text,
    marginBottom: spacing.sm,
  },
  instructionText: {
    ...typography.caption,
    color: colors.textSecondary,
    marginVertical: spacing.xs / 2,
    paddingLeft: spacing.sm,
  },
});
