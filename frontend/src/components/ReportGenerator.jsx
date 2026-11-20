import React, { useState } from 'react';

export const ReportGenerator = ({ assessment, auditMetadata }) => {
  const [loading, setLoading] = useState(false);

  const handleGenerateReport = async (format) => {
    setLoading(true);
    try {
      const response = await fetch('/api/generate-report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          site_assessment: assessment,
          audit_metadata: auditMetadata,
          report_format: format,
        }),
      });

      if (!response.ok) throw new Error('Report generation failed');

      const data = await response.json();

      if (format === 'html') {
        // Open in new window
        const htmlWindow = window.open();
        htmlWindow.document.write(data.content);
        htmlWindow.document.close();

        // Also offer download
        const blob = new Blob([data.content], { type: 'text/html' });
        downloadFile(blob, `Safety_Report_${new Date().toISOString().split('T')[0]}.html`);
      } else if (format === 'pdf') {
        // Convert hex back to bytes
        const bytes = new Uint8Array(data.content.match(/.{1,2}/g).map((x) => parseInt(x, 16)));
        const blob = new Blob([bytes], { type: 'application/pdf' });
        downloadFile(blob, data.filename);
      }
    } catch (error) {
      alert(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const downloadFile = (blob, filename) => {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.header}>📄 Downloadable Detection Summary</h2>
      <p style={styles.description}>
        Detections require human review and do not establish compliance or site safety.
      </p>

      <div style={styles.buttonGrid}>
        <button
          onClick={() => handleGenerateReport('html')}
          disabled={loading}
          style={{ ...styles.button, ...styles.buttonPrimary }}
        >
          📥 Download HTML Detection Summary
        </button>
        <button
          onClick={() => handleGenerateReport('pdf')}
          disabled={loading}
          style={{ ...styles.button, ...styles.buttonSecondary }}
        >
          📄 Download PDF Detection Summary
        </button>
      </div>

      {loading && <p style={styles.loading}>Generating report...</p>}
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
    marginBottom: '10px',
    color: '#1E293B',
  },
  description: {
    color: '#64748B',
    marginBottom: '15px',
    fontSize: '14px',
  },
  buttonGrid: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '15px',
  },
  button: {
    padding: '12px 20px',
    borderRadius: '6px',
    border: 'none',
    cursor: 'pointer',
    fontWeight: '500',
    fontSize: '14px',
    transition: 'all 0.3s ease',
  },
  buttonPrimary: {
    backgroundColor: '#0066cc',
    color: '#fff',
  },
  buttonSecondary: {
    backgroundColor: '#28a745',
    color: '#fff',
  },
  loading: {
    marginTop: '15px',
    color: '#0066cc',
    textAlign: 'center',
  },
};
