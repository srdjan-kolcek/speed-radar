/**
 * Result Card Component
 * Displays speed detection results for a single vehicle
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { colors, typography, spacing, borderRadius, shadows } from '../styles/theme';

export const ResultCard = ({ trackId, speedKmh, confidence }) => {
  // Determine confidence color based on value
  const getConfidenceColor = (conf) => {
    if (conf >= 0.8) return colors.success;
    if (conf >= 0.6) return colors.warning;
    return colors.error;
  };

  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <View style={styles.vehicleInfo}>
          <Text style={styles.vehicleLabel}>Vehicle</Text>
          <Text style={styles.trackId}>#{trackId}</Text>
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

      <View style={styles.speedContainer}>
        <Text style={styles.speed}>{speedKmh.toFixed(1)}</Text>
        <Text style={styles.unit}>km/h</Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.cardBackground,
    borderRadius: borderRadius.lg,
    padding: spacing.md,
    marginVertical: spacing.sm,
    marginHorizontal: spacing.md,
    ...shadows.medium,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  vehicleInfo: {
    flexDirection: 'row',
    alignItems: 'baseline',
  },
  vehicleLabel: {
    ...typography.body,
    color: colors.textSecondary,
    marginRight: spacing.xs,
  },
  trackId: {
    ...typography.h3,
    color: colors.text,
  },
  confidenceContainer: {
    alignItems: 'flex-end',
  },
  confidence: {
    ...typography.h3,
    fontWeight: 'bold',
  },
  confidenceLabel: {
    ...typography.small,
    color: colors.textLight,
    marginTop: spacing.xs / 2,
  },
  speedContainer: {
    flexDirection: 'row',
    alignItems: 'baseline',
  },
  speed: {
    fontSize: 48,
    fontWeight: 'bold',
    color: colors.primary,
  },
  unit: {
    ...typography.h3,
    color: colors.textSecondary,
    marginLeft: spacing.sm,
  },
});
