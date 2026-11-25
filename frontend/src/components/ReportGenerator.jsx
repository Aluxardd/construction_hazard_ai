import React, { useState } from 'react';

export const ReportGenerator = ({ assessment, results = null, auditMetadata }) => {
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [statusMessage, setStatusMessage] = useState('');

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

  const handleGenerateReport = async (format) => {
    setLoading(true);
    setErrorMessage('');
    setStatusMessage('');
    try {
      const response = await fetch('/api/generate-report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          site_assessment: assessment,
          audit_metadata: {
            site_name: auditMetadata.site_name,
            inspector_name: auditMetadata.inspector_name,
            inspection_date: auditMetadata.inspection_date,
          },
          report_format: format,
          results,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(typeof errorData?.detail === 'string' ? errorData.detail : 'Report generation failed.');
      }

      const data = await response.json();

      if (format === 'html') {
        const blob = new Blob([data.content], { type: 'text/html' });
        const filename = data.filename || `Safety_Report_${new Date().toISOString().split('T')[0]}.html`;
        downloadFile(blob, filename);
        setStatusMessage(`Downloaded ${filename}`);
      } else if (format === 'pdf') {
        const hexPairs = data.content ? data.content.match(/.{1,2}/g) : null;
        if (!hexPairs) {
          throw new Error('Received empty PDF payload from server.');
        }
        const bytes = new Uint8Array(hexPairs.map((x) => parseInt(x, 16)));
        const blob = new Blob([bytes], { type: 'application/pdf' });
        downloadFile(blob, data.filename || 'PPE_Compliance_Report.pdf');
        setStatusMessage(`Downloaded ${data.filename || 'PPE_Compliance_Report.pdf'}`);
      }
    } catch (error) {
      setErrorMessage(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.header}>📄 Downloadable Detection &amp; Review Summary</h2>
      <p style={styles.description}>
        Includes audit metadata, per-image legislation-informed worker findings, and raw model detections.
        Detections require human review and do not establish compliance or site safety.
      </p>

      <div className="two-col-grid">
        <button
          type="button"
          onClick={() => handleGenerateReport('html')}
          disabled={loading}
          style={{ ...styles.button, ...styles.buttonPrimary }}
        >
          📥 Download HTML Summary
        </button>
        <button
          type="button"
          onClick={() => handleGenerateReport('pdf')}
          disabled={loading}
          style={{ ...styles.button, ...styles.buttonSecondary }}
        >
          📄 Download PDF Summary
        </button>
      </div>

      {loading && <p style={styles.loading}>Generating report...</p>}
      {statusMessage && <p role="status" style={styles.success}>{statusMessage}</p>}
      {errorMessage && <p role="alert" style={styles.error}>{errorMessage}</p>}
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
    marginTop: 0,
    color: '#1E293B',
  },
  description: {
    color: '#64748B',
    marginBottom: '15px',
    fontSize: '14px',
  },
  button: {
    padding: '12px 20px',
    borderRadius: '6px',
    border: 'none',
    cursor: 'pointer',
    fontWeight: '500',
    fontSize: '14px',
    transition: 'all 0.2s ease',
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
  success: {
    marginTop: '12px',
    color: '#155724',
    fontSize: '14px',
  },
  error: {
    marginTop: '12px',
    color: '#991b1b',
    fontSize: '14px',
  },
};
