import React from 'react';

export const DetectionResults = ({ results }) => {
  if (!results || results.length === 0) return null;

  return (
    <div style={styles.container}>
      <h2 style={styles.header}>Visual Inspection & Bounding Box Annotations</h2>

      {results.map((result, idx) => (
        <div key={idx} style={styles.resultCard}>
          <div style={styles.resultHeader}>
            <span>
              <strong>Image:</strong> <code>{result.filename}</code>
            </span>
            <span>
              Detected Hazards: <strong>{result.evaluation.total_hazards}</strong> |{' '}
              Compliant PPE: <strong>{result.evaluation.compliant_count}</strong>
            </span>
          </div>

          <div style={styles.imageGrid}>
            <div style={styles.imageColumn}>
              <p style={styles.imageCaption}>Original Site Photo</p>
              {/* Original image would need to be stored in results */}
              <div style={styles.imagePlaceholder}>Original Image</div>
            </div>
            <div style={styles.imageColumn}>
              <p style={styles.imageCaption}>YOLOv8 Detection (Green = Compliant, Red/Orange = Hazard)</p>
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
  imageGrid: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
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
