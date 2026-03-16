/**
 * Error Message Component
 * Displays error messages with retry option
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { ActionButton } from './ActionButton';
import { colors, typography, spacing, borderRadius } from '../styles/theme';

export const ErrorMessage = ({ message, onRetry }) => {
  return (
    <View style={styles.container}>
      <View style={styles.errorBox}>
        <Text style={styles.errorIcon}>⚠️</Text>
        <Text style={styles.errorTitle}>Error</Text>
        <Text style={styles.errorMessage}>{message}</Text>
        {onRetry && (
          <ActionButton
            title="Retry"
            onPress={onRetry}
            variant="primary"
            style={styles.retryButton}
          />
        )}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: spacing.md,
  },
  errorBox: {
    backgroundColor: '#FFEBEE',
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#FFCDD2',
  },
  errorIcon: {
    fontSize: 48,
    marginBottom: spacing.sm,
  },
  errorTitle: {
    ...typography.h3,
    color: colors.error,
    marginBottom: spacing.sm,
  },
  errorMessage: {
    ...typography.body,
    color: colors.text,
    textAlign: 'center',
    marginBottom: spacing.md,
  },
  retryButton: {
    marginTop: spacing.sm,
    minWidth: 120,
  },
});
