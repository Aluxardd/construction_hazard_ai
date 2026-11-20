import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export const RiskMatrix = ({ assessment }) => {
  if (!assessment) return null;

  const matrixData = assessment.matrix_counts
    ? Object.entries(assessment.matrix_counts).map(([key, value]) => ({
        name: key,
        count: value,
      }))
    : [];

  const riskTiers = assessment.tier_counts || {};

  return (
    <div style={styles.container}>
      <h2 style={styles.header}>📊 5×5 Construction Risk Matrix Distribution</h2>

      <div style={styles.content}>
        <div style={styles.chartContainer}>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={matrixData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="count" fill="#0066cc" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div style={styles.infoBox}>
          <h3 style={styles.rubricTitle}>Risk Evaluation Rubric</h3>
          <p style={styles.rubricText}>
            Risk Score = <strong>Likelihood (1–5) × Severity (1–5)</strong>:
          </p>

          <div style={{ ...styles.riskLevel, ...styles.critical }}>
            <strong>🔴 Critical (15 – 25):</strong> Immediate Work Stoppage. Major hazard likely to result in fatal or permanent injury.
          </div>

          <div style={{ ...styles.riskLevel, ...styles.high }}>
            <strong>🟠 High (10 – 14):</strong> Urgent Rectification within 1 hour. Significant regulatory non-compliance.
          </div>

          <div style={{ ...styles.riskLevel, ...styles.medium }}>
            <strong>🟡 Medium (5 – 9):</strong> Remedial Action required within current shift.
          </div>

          <div style={{ ...styles.riskLevel, ...styles.low }}>
            <strong>🟢 Low (1 – 4):</strong> Routine monitoring & toolbox talks.
          </div>

          <div style={styles.tierSummary}>
            <p><strong>Tier Summary:</strong></p>
            <ul>
              <li>🔴 Critical: {riskTiers.Critical || 0}</li>
              <li>🟠 High: {riskTiers.High || 0}</li>
              <li>🟡 Medium: {riskTiers.Medium || 0}</li>
              <li>🟢 Low: {riskTiers.Low || 0}</li>
            </ul>
          </div>

          {assessment.summary_statement && (
            <div style={styles.summary}>
              <strong>Audit Finding:</strong> {assessment.summary_statement}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const styles = {
  container: {
    marginBottom: '30px',
  },
  header: {
    fontSize: '18px',
    fontWeight: '600',
    marginBottom: '15px',
    color: '#1E293B',
  },
  content: {
    display: 'grid',
    gridTemplateColumns: '2fr 1fr',
    gap: '20px',
  },
  chartContainer: {
    backgroundColor: '#fff',
    padding: '15px',
    borderRadius: '8px',
    border: '1px solid #E2E8F0',
  },
  infoBox: {
    backgroundColor: '#F8FAFC',
    padding: '15px',
    borderRadius: '8px',
    border: '1px solid #E2E8F0',
  },
  rubricTitle: {
    fontSize: '14px',
    fontWeight: '600',
    marginBottom: '10px',
    color: '#1E293B',
  },
  rubricText: {
    fontSize: '12px',
    color: '#475569',
    marginBottom: '12px',
  },
  riskLevel: {
    padding: '8px 12px',
    marginBottom: '8px',
    borderRadius: '4px',
    fontSize: '12px',
    color: '#fff',
  },
  critical: {
    backgroundColor: '#dc3545',
  },
  high: {
    backgroundColor: '#fd7e14',
  },
  medium: {
    backgroundColor: '#ffc107',
    color: '#212529',
  },
  low: {
    backgroundColor: '#28a745',
  },
  tierSummary: {
    marginTop: '12px',
    padding: '8px 12px',
    backgroundColor: '#fff',
    borderRadius: '4px',
    fontSize: '12px',
  },
  summary: {
    marginTop: '12px',
    padding: '10px',
    backgroundColor: '#e3f2fd',
    borderRadius: '4px',
    fontSize: '12px',
    color: '#0066cc',
  },
};
