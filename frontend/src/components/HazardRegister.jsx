import React from 'react';

const isFlaggedItem = (item) =>
  item.normalized_key?.startsWith('no_') || item.normalized_key === 'forklift';

const getStatusLabel = (item) => {
  if (item.normalized_key?.startsWith('no_')) return 'Review model flag';
  if (item.normalized_key === 'forklift') return 'Review plant hazard';
  return 'Detected';
};

export const HazardRegister = ({ assessment, results = null, showHazardsOnly = true }) => {
  if (!assessment && (!results || results.length === 0)) return null;

  const rawRows = results && results.length > 0
    ? results.flatMap((result) =>
        (result.evaluation?.all_items || []).map((item) => ({
          ...item,
          _filename: result.filename || 'Image',
        })),
      )
    : (assessment?.all_items || []).map((item) => ({ ...item, _filename: null }));

  const items = showHazardsOnly ? rawRows.filter(isFlaggedItem) : rawRows;
  const showImageColumn = Boolean(results && results.length > 0);

  if (items.length === 0) {
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
              {showImageColumn && <th style={styles.headerCell}>Image</th>}
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
                {showImageColumn && <td style={styles.cell}><code>{item._filename}</code></td>}
                <td style={styles.cell}>{getStatusLabel(item)}</td>
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
