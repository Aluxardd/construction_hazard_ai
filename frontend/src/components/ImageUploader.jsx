import React, { useState } from 'react';
import { Upload, AlertCircle } from 'lucide-react';

export const ImageUploader = ({ onImagesSelected, isProcessing }) => {
  const [files, setFiles] = useState([]);
  const [useSample, setUseSample] = useState(false);

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files || []);
    e.target.value = '';
    setFiles(selectedFiles);
    setUseSample(false);
    onImagesSelected(selectedFiles, false);
  };

  const handleSampleClick = () => {
    setUseSample(!useSample);
    if (!useSample) {
      setFiles([]);
      onImagesSelected([], true);
    } else {
      onImagesSelected([], false);
    }
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.header}>📸 Site Photography Inspection</h2>

      <div style={styles.uploadBox}>
        <label style={styles.label}>
          <Upload size={40} color="#0066cc" />
          <p style={styles.text}>Upload construction site photos (JPG, PNG)</p>
          <input
            type="file"
            multiple
            accept="image/*"
            onChange={handleFileChange}
            style={styles.input}
            disabled={isProcessing}
          />
        </label>
      </div>

      <div style={styles.divider}>OR</div>

      <label style={styles.checkboxLabel}>
        <input
          type="checkbox"
          checked={useSample}
          onChange={handleSampleClick}
          disabled={isProcessing}
        />
        <span> Test with included sample image</span>
      </label>

      {files.length > 0 && (
        <div style={styles.fileList}>
          <p style={styles.fileCount}>Selected: {files.length} file(s)</p>
          {files.map((f) => (
            <div key={f.name} style={styles.fileItem}>
              ✓ {f.name}
            </div>
          ))}
        </div>
      )}

      {!files.length && !useSample && (
        <div style={styles.info}>
          <AlertCircle size={20} />
          <p>Please upload construction site photos or select the sample option to begin inspection.</p>
        </div>
      )}
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
  uploadBox: {
    border: '2px dashed #0066cc',
    borderRadius: '8px',
    padding: '30px',
    textAlign: 'center',
    cursor: 'pointer',
    backgroundColor: '#f0f7ff',
  },
  label: {
    cursor: 'pointer',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '10px',
  },
  text: {
    color: '#64748B',
    margin: 0,
  },
  input: {
    display: 'none',
  },
  divider: {
    textAlign: 'center',
    color: '#94A3B8',
    margin: '20px 0',
    fontWeight: '500',
  },
  checkboxLabel: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    cursor: 'pointer',
    color: '#475569',
  },
  fileList: {
    marginTop: '15px',
    padding: '10px',
    backgroundColor: '#F8FAFC',
    borderRadius: '6px',
  },
  fileCount: {
    color: '#64748B',
    fontWeight: '600',
    marginBottom: '8px',
  },
  fileItem: {
    color: '#28a745',
    padding: '4px 0',
  },
  info: {
    display: 'flex',
    gap: '10px',
    padding: '12px',
    backgroundColor: '#e3f2fd',
    borderRadius: '6px',
    color: '#0066cc',
    marginTop: '15px',
  },
};
