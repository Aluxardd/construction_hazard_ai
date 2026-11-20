import React from 'react';

export const ConfigPanel = ({ config, onConfigChange, isProcessing }) => {
  const handleChange = (key, value) => {
    onConfigChange({ ...config, [key]: value });
  };

  return (
    <div style={styles.sidebar}>
      <h2 style={styles.header}>⚙️ System Configuration</h2>

      <div style={styles.section}>
        <h3 style={styles.subheader}>Model Status</h3>
        {config.is_custom_model ? (
          <div style={styles.success}>
            ✅ Active Trained Model: <code>{config.model_name}</code>
          </div>
        ) : (
          <div style={styles.info}>
            ℹ️ Running in <strong>Demo / Simulation Mode</strong>
          </div>
        )}
        {config.class_names?.length > 0 && (
          <details style={styles.details}>
            <summary>Detected Model Classes ({config.class_names.length})</summary>
            <ul style={styles.classList}>
              {config.class_names.map((cls) => (
                <li key={cls} style={styles.classItem}>
                  <strong>{cls}</strong>
                </li>
              ))}
            </ul>
          </details>
        )}
      </div>

      <hr style={styles.divider} />

      <div style={styles.section}>
        <h3 style={styles.subheader}>Inference Settings</h3>

        <label style={styles.label}>
          <span>Confidence Threshold: {config.conf_threshold.toFixed(2)}</span>
          <input
            type="range"
            min="0.1"
            max="0.95"
            step="0.05"
            value={config.conf_threshold}
            onChange={(e) => handleChange('conf_threshold', parseFloat(e.target.value))}
            disabled={isProcessing}
            style={styles.slider}
          />
        </label>

        <label style={styles.label}>
          <span>IoU NMS Threshold: {config.iou_threshold.toFixed(2)}</span>
          <input
            type="range"
            min="0.1"
            max="0.9"
            step="0.05"
            value={config.iou_threshold}
            onChange={(e) => handleChange('iou_threshold', parseFloat(e.target.value))}
            disabled={isProcessing}
            style={styles.slider}
          />
        </label>

        <label style={styles.checkboxLabel}>
          <input
            type="checkbox"
            checked={config.show_compliant}
            onChange={(e) => handleChange('show_compliant', e.target.checked)}
            disabled={isProcessing}
          />
          <span>Show Compliant PPE in annotations</span>
        </label>
      </div>

      <hr style={styles.divider} />

      <div style={styles.section}>
        <h3 style={styles.subheader}>Audit Metadata</h3>

        <label style={styles.label}>
          <span>Site / Project Name</span>
          <input
            type="text"
            value={config.site_name}
            onChange={(e) => handleChange('site_name', e.target.value)}
            disabled={isProcessing}
            style={styles.input}
          />
        </label>

        <label style={styles.label}>
          <span>Safety Officer / Inspector</span>
          <input
            type="text"
            value={config.inspector_name}
            onChange={(e) => handleChange('inspector_name', e.target.value)}
            disabled={isProcessing}
            style={styles.input}
          />
        </label>

        <label style={styles.label}>
          <span>Audit Date</span>
          <input
            type="date"
            value={config.inspection_date}
            onChange={(e) => handleChange('inspection_date', e.target.value)}
            disabled={isProcessing}
            style={styles.input}
          />
        </label>
      </div>
    </div>
  );
};

const styles = {
  sidebar: {
    width: '280px',
    padding: '20px',
    backgroundColor: '#F8FAFC',
    borderRight: '1px solid #E2E8F0',
    minHeight: '100vh',
    overflowY: 'auto',
  },
  header: {
    fontSize: '18px',
    fontWeight: '600',
    color: '#1E293B',
    marginBottom: '20px',
  },
  section: {
    marginBottom: '20px',
  },
  subheader: {
    fontSize: '14px',
    fontWeight: '600',
    color: '#475569',
    marginBottom: '10px',
  },
  success: {
    padding: '8px 12px',
    backgroundColor: '#d4edda',
    color: '#155724',
    borderRadius: '4px',
    fontSize: '12px',
  },
  info: {
    padding: '8px 12px',
    backgroundColor: '#d1ecf1',
    color: '#0c5460',
    borderRadius: '4px',
    fontSize: '12px',
  },
  details: {
    marginTop: '8px',
    cursor: 'pointer',
  },
  classList: {
    listStyle: 'none',
    padding: '8px 0 0 0',
    margin: 0,
  },
  classItem: {
    padding: '4px 0',
    fontSize: '12px',
    color: '#64748B',
  },
  divider: {
    border: 'none',
    borderTop: '1px solid #E2E8F0',
    margin: '15px 0',
  },
  label: {
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
    marginBottom: '12px',
    fontSize: '12px',
    color: '#475569',
  },
  slider: {
    width: '100%',
  },
  checkboxLabel: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '12px',
    color: '#475569',
    cursor: 'pointer',
  },
  input: {
    padding: '6px',
    borderRadius: '4px',
    border: '1px solid #CBD5E1',
    fontSize: '12px',
  },
};
