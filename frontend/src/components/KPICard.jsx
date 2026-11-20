import React from 'react';

export const KPICard = ({ title, value, color = '#1E293B' }) => {
  return (
    <div style={styles.card}>
      <div style={styles.title}>{title}</div>
      <div style={{ ...styles.value, color }}>{value}</div>
    </div>
  );
};

const styles = {
  card: {
    backgroundColor: '#F8FAFC',
    border: '1px solid #E2E8F0',
    borderRadius: '8px',
    padding: '12px',
    textAlign: 'center',
  },
  title: {
    fontSize: '11px',
    color: '#64748B',
    fontWeight: '600',
    textTransform: 'uppercase',
  },
  value: {
    fontSize: '22px',
    fontWeight: '700',
    marginTop: '4px',
  },
};
