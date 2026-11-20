import React from 'react';

export const HazardRegister = ({ assessment, showHazardsOnly = true }) => {
  if (!assessment) return null;

  const items = showHazardsOnly
    ? assessment.all_items?.filter((item) => item.normalized_key?.startsWith('no_'))
    : assessment.all_items;

  if (!items || items.length === 0) {
    return (
      <div style={styles.container}>
        <p style={styles.empty}>No items match the selected filter.</p>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.tableWrapper}>
        <table style={styles.table}>
          <thead>
            <tr style={styles.headerRow}>
              <th style={styles.headerCell}>Status</th>
              <th style={styles.headerCell}>Finding / Item</th>
              <th style={styles.headerCell}>Confidence</th>
              <th style={styles.headerCell}>Model label</th>
              <th style={styles.headerCell}>Bounding box (xyxy)</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item, idx) => (
              <tr key={idx} style={styles.bodyRow}>
                <td style={styles.cell}>
                  {item.normalized_key?.startsWith('no_') ? 'Review model flag' : 'Detected'}
                </td>
                <td style={styles.cell}>{item.title}</td>
                <td style={styles.cell}>{Math.round(item.confidence * 100)}%</td>
                <td style={styles.cell}>{item.raw_label}</td>
                <td style={styles.cell}>{item.bbox?.join(', ')}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const getRiskTierStyle = (tier) => {
  const colors = {
    Critical: { backgroundColor: '#dc3545', color: '#fff' },
    High: { backgroundColor: '#fd7e14', color: '#fff' },
    Medium: { backgroundColor: '#ffc107', color: '#212529' },
    Low: { backgroundColor: '#28a745', color: '#fff' },
  };
  return colors[tier] || {};
};

const styles = {
  container: {
    marginBottom: '30px',
  },
  tableWrapper: {
    overflowX: 'auto',
    backgroundColor: '#fff',
    borderRadius: '8px',
    border: '1px solid #E2E8F0',
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
    fontSize: '12px',
  },
  headerRow: {
    backgroundColor: '#F1F5F9',
    borderBottom: '2px solid #E2E8F0',
  },
  headerCell: {
    padding: '12px 8px',
    textAlign: 'left',
    fontWeight: '600',
    color: '#475569',
  },
  bodyRow: {
    borderBottom: '1px solid #E2E8F0',
  },
  cell: {
    padding: '12px 8px',
    color: '#475569',
  },
  empty: {
    padding: '20px',
    textAlign: 'center',
    color: '#64748B',
  },
};
