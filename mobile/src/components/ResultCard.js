/**
 * Result Card Component
 * Displays speed detection results for a single vehicle with image and detailed stats
 */

import React, { useState } from 'react';
import { View, Text, StyleSheet, Image, ActivityIndicator } from 'react-native';
import { API_BASE_URL } from '../utils/config';
import { colors, typography, spacing, borderRadius, shadows } from '../styles/theme';

export const ResultCard = ({ 
  trackId, 
  speedKmh, 
  maxSpeedKmh,
  confidence, 
  vehicleType,
  imageFilename 
}) => {
  const [imageLoading, setImageLoading] = useState(true);
  const [imageError, setImageError] = useState(false);

  // Determine confidence color based on value
  const getConfidenceColor = (conf) => {
    if (conf >= 0.8) return colors.success;
    if (conf >= 0.6) return colors.warning;
    return colors.error;
  };

  // Build image URL
  const imageUrl = imageFilename ? `${API_BASE_URL}/vehicle_crops/${imageFilename}` : null;

  const handleImageLoad = () => {
    setImageLoading(false);
  };

  const handleImageError = () => {
    setImageLoading(false);
    setImageError(true);
  };

  return (
    <View style={styles.card}>
      {/* Vehicle Image */}
      {imageUrl ? (
        <View style={styles.imageContainer}>
          {imageLoading && (
            <View style={styles.imageLoading}>
              <ActivityIndicator size="large" color={colors.primary} />
            </View>
          )}
          {!imageError ? (
            <Image
              source={{ uri: imageUrl }}
              style={styles.vehicleImage}
              onLoad={handleImageLoad}
              onError={handleImageError}
            />
          ) : (
            <View style={styles.imageError}>
              <Text style={styles.imageErrorText}>🚗</Text>
            </View>
          )}
        </View>
      ) : (
        <View style={styles.imagePlaceholder}>
          <Text style={styles.imagePlaceholderText}>🚗</Text>
        </View>
      )}

      {/* Header Info */}
      <View style={styles.header}>
        <View style={styles.vehicleInfo}>
          <Text style={styles.vehicleLabel}>Vehicle</Text>
          <Text style={styles.trackId}>#{trackId}</Text>
          {vehicleType && (
            <Text style={styles.vehicleType}>{vehicleType}</Text>
          )}
        </View>
        <View style={styles.confidenceContainer}>
          <Text
            style={[
              styles.confidence,
              { color: getConfidenceColor(confidence) },
            ]}
          >
            {(confidence * 100).toFixed(0)}%
          </Text>
          <Text style={styles.confidenceLabel}>Confidence</Text>
        </View>
      </View>

      {/* Speed Stats */}
      <View style={styles.speedStats}>
        <View style={styles.speedStat}>
          <Text style={styles.speedLabel}>Average Speed</Text>
          <View style={styles.speedValue}>
            <Text style={styles.speed}>{speedKmh.toFixed(1)}</Text>
            <Text style={styles.unit}>km/h</Text>
          </View>
        </View>
        {maxSpeedKmh !== null && maxSpeedKmh !== undefined && (
          <View style={styles.speedStat}>
            <Text style={styles.speedLabel}>Max Speed</Text>
            <View style={styles.speedValue}>
              <Text style={[styles.speed, styles.maxSpeed]}>{maxSpeedKmh.toFixed(1)}</Text>
              <Text style={styles.unit}>km/h</Text>
            </View>
          </View>
        )}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.cardBackground,
    borderRadius: borderRadius.lg,
    overflow: 'hidden',
    marginVertical: spacing.sm,
    marginHorizontal: spacing.md,
    ...shadows.medium,
  },
  imageContainer: {
    position: 'relative',
    width: '100%',
    height: 200,
    backgroundColor: colors.background,
  },
  imageLoading: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.background,
  },
  vehicleImage: {
    width: '100%',
    height: '100%',
    resizeMode: 'cover',
  },
  imageError: {
    width: '100%',
    height: '100%',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.background,
  },
  imageErrorText: {
    fontSize: 48,
  },
  imagePlaceholder: {
    width: '100%',
    height: '100%',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.background,
  },
  imagePlaceholderText: {
    fontSize: 48,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    padding: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  vehicleInfo: {
    flex: 1,
  },
  vehicleLabel: {
    ...typography.body,
    color: colors.textSecondary,
    marginBottom: spacing.xs / 2,
  },
  trackId: {
    ...typography.h3,
    color: colors.text,
    marginBottom: spacing.xs,
  },
  vehicleType: {
    ...typography.small,
    color: colors.primary,
    fontWeight: '600',
    textTransform: 'capitalize',
  },
  confidenceContainer: {
    alignItems: 'flex-end',
  },
  confidence: {
    ...typography.h3,
    fontWeight: 'bold',
    marginBottom: spacing.xs / 2,
  },
  confidenceLabel: {
    ...typography.small,
    color: colors.textLight,
  },
  speedStats: {
    flexDirection: 'row',
    padding: spacing.md,
    gap: spacing.md,
  },
  speedStat: {
    flex: 1,
    alignItems: 'center',
  },
  speedLabel: {
    ...typography.small,
    color: colors.textSecondary,
    marginBottom: spacing.sm,
    textAlign: 'center',
  },
  speedValue: {
    flexDirection: 'row',
    alignItems: 'baseline',
    justifyContent: 'center',
  },
  speed: {
    fontSize: 32,
    fontWeight: 'bold',
    color: colors.primary,
  },
  maxSpeed: {
    color: colors.warning,
  },
  unit: {
    ...typography.h3,
    color: colors.textSecondary,
    marginLeft: spacing.xs,
  },
});
