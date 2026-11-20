import React from 'react';

export const DetectionResults = ({ results }) => {
  if (!results || results.length === 0) return null;

  return (
    <div style={styles.container}>
      <h2 style={styles.header}>PPE Detection Results & Compliance Analysis</h2>

      {results.map((result, idx) => (
        <div key={idx} style={styles.resultCard}>
          <div style={styles.resultHeader}>
            <span>
              <strong>Image:</strong> <code>{result.filename}</code>
            </span>
            <span>
              PPE Items Detected: <strong>{result.ppe_compliance?.detected_items?.length || 0}</strong> |{' '}
              Compliance: <strong style={{ color: getComplianceColor(result.ppe_compliance?.compliance_rate) }}>
                {result.ppe_compliance?.compliance_rate || 0}%
              </strong>
            </span>
          </div>

          {/* Compliance Status */}
          {result.ppe_compliance && (
            <div style={styles.compliancePanel}>
              <div style={styles.complianceHeader}>
                <span style={{
                  color: '#fff',
                  backgroundColor: result.ppe_compliance.status.color,
                  padding: '6px 12px',
                  borderRadius: '4px',
                  fontWeight: '600',
                  fontSize: '12px'
                }}>
                  {result.ppe_compliance.status.level}
                </span>
                <span style={styles.complianceMessage}>{result.ppe_compliance.status.message}</span>
              </div>
              
              <div style={styles.ppeGrid}>
                <div style={styles.ppeColumn}>
                  <strong style={styles.ppeLabel}>✓ Detected PPE:</strong>
                  <ul style={styles.ppeList}>
                    {result.ppe_compliance.detected_items?.length > 0 ? (
                      result.ppe_compliance.detected_items.map((item) => (
                        <li key={item} style={styles.ppeItem}>
                          <span style={styles.checkmark}>✓</span> {item.charAt(0).toUpperCase() + item.slice(1)}
                        </li>
                      ))
                    ) : (
                      <li style={styles.ppeItem}>None detected</li>
                    )}
                  </ul>
                </div>
                
                {result.ppe_compliance.missing_items?.length > 0 && (
                  <div style={styles.ppeColumn}>
                    <strong style={styles.ppeLabel}>✗ Missing PPE:</strong>
                    <ul style={styles.ppeList}>
                      {result.ppe_compliance.missing_items.map((item) => (
                        <li key={item} style={{ ...styles.ppeItem, color: '#dc3545' }}>
                          <span style={{ color: '#dc3545', fontWeight: 'bold' }}>✗</span> {item.charAt(0).toUpperCase() + item.slice(1)}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}

          <div style={styles.imageGrid}>
            <div style={styles.imageColumn}>
              <p style={styles.imageCaption}>Annotated Detection</p>
              {result.annotated_image && (
                <img
                  src={result.annotated_image}
                  alt={result.filename}
                  style={styles.image}
                />
              )}
            </div>
          </div>

          <hr style={styles.divider} />
        </div>
      ))}
    </div>
  );
};

function getComplianceColor(rate) {
  if (rate >= 100) return '#28a745'; // Green
  if (rate >= 80) return '#ffc107'; // Yellow
  if (rate >= 50) return '#fd7e14'; // Orange
  return '#dc3545'; // Red
}

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
  resultCard: {
    backgroundColor: '#fff',
    padding: '15px',
    borderRadius: '8px',
    border: '1px solid #E2E8F0',
    marginBottom: '20px',
  },
  resultHeader: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '20px',
    marginBottom: '15px',
    fontSize: '14px',
    color: '#475569',
  },
  compliancePanel: {
    backgroundColor: '#F8F9FA',
    padding: '12px',
    borderRadius: '6px',
    marginBottom: '15px',
    border: '1px solid #E2E8F0',
  },
  complianceHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    marginBottom: '10px',
  },
  complianceMessage: {
    fontSize: '14px',
    color: '#475569',
    fontWeight: '500',
  },
  ppeGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '15px',
  },
  ppeColumn: {
    padding: '10px 0',
  },
  ppeLabel: {
    display: 'block',
    marginBottom: '8px',
    fontSize: '13px',
    color: '#1E293B',
  },
  ppeList: {
    listStyle: 'none',
    padding: 0,
    margin: 0,
  },
  ppeItem: {
    padding: '6px 0',
    fontSize: '13px',
    color: '#28a745',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  checkmark: {
    fontWeight: 'bold',
    color: '#28a745',
  },
  imageGrid: {
    display: 'grid',
    gridTemplateColumns: '1fr',
    gap: '15px',
  },
  imageColumn: {
    textAlign: 'center',
  },
  imageCaption: {
    fontSize: '12px',
    color: '#64748B',
    marginBottom: '10px',
    fontWeight: '500',
  },
  image: {
    maxWidth: '100%',
    height: 'auto',
    borderRadius: '4px',
    border: '1px solid #E2E8F0',
  },
  imagePlaceholder: {
    backgroundColor: '#F1F5F9',
    height: '400px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: '#94A3B8',
    borderRadius: '4px',
    border: '1px solid #E2E8F0',
  },
  divider: {
    marginTop: '15px',
    border: 'none',
    borderTop: '1px solid #E2E8F0',
  },
};
