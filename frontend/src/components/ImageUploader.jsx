import React, { useState, useEffect, useId } from 'react';
import { Upload, AlertCircle, X } from 'lucide-react';

const formatFileSize = (bytes) => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

export const ImageUploader = ({ onImagesSelected, isProcessing }) => {
  const [files, setFiles] = useState([]);
  const [previews, setPreviews] = useState([]);
  const [useSample, setUseSample] = useState(false);
  const inputId = useId();

  useEffect(() => {
    const nextPreviews = files.map((file) => ({
      key: `${file.name}-${file.size}-${file.lastModified}`,
      file,
      url: URL.createObjectURL(file),
    }));
    setPreviews(nextPreviews);
    return () => {
      nextPreviews.forEach((item) => URL.revokeObjectURL(item.url));
    };
  }, [files]);

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files || []);
    e.target.value = '';
    setFiles(selectedFiles);
    setUseSample(false);
    onImagesSelected(selectedFiles, false);
  };

  const handleRemoveFile = (indexToRemove) => {
    const remaining = files.filter((_, idx) => idx !== indexToRemove);
    setFiles(remaining);
    onImagesSelected(remaining, false);
  };

  const handleSampleClick = () => {
    const nextSample = !useSample;
    setUseSample(nextSample);
    if (nextSample) {
      setFiles([]);
      onImagesSelected([], true);
    } else {
      onImagesSelected([], false);
    }
  };

  return (
    <section style={styles.container} aria-labelledby="image-upload-title">
      <h2 id="image-upload-title" style={styles.header}>📸 Site Photography Inspection</h2>

      <div className="upload-dropzone" style={styles.uploadBox}>
        <label htmlFor={inputId} style={styles.label}>
          <Upload size={40} color="#0066cc" aria-hidden="true" />
          <span style={styles.text}>Upload construction site photos (JPG, PNG, WEBP)</span>
          <span style={styles.hint}>Click or focus and press Enter/Space to browse files</span>
          <input
            id={inputId}
            type="file"
            multiple
            accept="image/*"
            onChange={handleFileChange}
            className="sr-only-input"
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
        <span>Test with included sample image</span>
      </label>

      {previews.length > 0 && (
        <div style={styles.fileList}>
          <p style={styles.fileCount}>Selected: {previews.length} file(s)</p>
          <div style={styles.previewGrid}>
            {previews.map((item, idx) => (
              <div key={item.key} style={styles.previewCard}>
                <img src={item.url} alt={item.file.name} style={styles.thumb} />
                <div style={styles.fileMeta}>
                  <span style={styles.fileName}>{item.file.name}</span>
                  <span style={styles.fileSize}>{formatFileSize(item.file.size)}</span>
                </div>
                <button
                  type="button"
                  onClick={() => handleRemoveFile(idx)}
                  disabled={isProcessing}
                  aria-label={`Remove ${item.file.name}`}
                  style={styles.removeBtn}
                >
                  <X size={14} aria-hidden="true" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {!files.length && !useSample && (
        <div style={styles.info}>
          <AlertCircle size={20} aria-hidden="true" />
          <p style={{ margin: 0 }}>Please upload construction site photos or select the sample option to begin inspection.</p>
        </div>
      )}
    </section>
  );
};

const styles = {
  container: {
    marginBottom: '24px',
  },
  header: {
    fontSize: '18px',
    fontWeight: '600',
    marginBottom: '15px',
    marginTop: 0,
    color: '#1E293B',
  },
  uploadBox: {
    border: '2px dashed #0066cc',
    borderRadius: '8px',
    padding: '28px 20px',
    textAlign: 'center',
    cursor: 'pointer',
    backgroundColor: '#f0f7ff',
    position: 'relative',
  },
  label: {
    cursor: 'pointer',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '8px',
  },
  text: {
    color: '#1e293b',
    fontWeight: '500',
    fontSize: '14px',
  },
  hint: {
    color: '#64748B',
    fontSize: '12px',
  },
  divider: {
    textAlign: 'center',
    color: '#94A3B8',
    margin: '16px 0',
    fontWeight: '500',
  },
  checkboxLabel: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '10px',
    cursor: 'pointer',
    color: '#475569',
  },
  fileList: {
    marginTop: '15px',
    padding: '12px',
    backgroundColor: '#F8FAFC',
    borderRadius: '6px',
    border: '1px solid #E2E8F0',
  },
  fileCount: {
    color: '#475569',
    fontWeight: '600',
    marginTop: 0,
    marginBottom: '10px',
    fontSize: '13px',
  },
  previewGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))',
    gap: '10px',
  },
  previewCard: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    padding: '8px',
    backgroundColor: '#fff',
    border: '1px solid #CBD5E1',
    borderRadius: '6px',
  },
  thumb: {
    width: '48px',
    height: '48px',
    objectFit: 'cover',
    borderRadius: '4px',
    flexShrink: 0,
  },
  fileMeta: {
    flex: 1,
    minWidth: 0,
    display: 'flex',
    flexDirection: 'column',
  },
  fileName: {
    fontSize: '12px',
    color: '#1e293b',
    fontWeight: '500',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
  },
  fileSize: {
    fontSize: '11px',
    color: '#64748B',
  },
  removeBtn: {
    border: '1px solid #E2E8F0',
    background: '#F8FAFC',
    borderRadius: '4px',
    padding: '4px',
    cursor: 'pointer',
    color: '#475569',
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  info: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    padding: '12px',
    backgroundColor: '#e3f2fd',
    borderRadius: '6px',
    color: '#0066cc',
    marginTop: '15px',
    fontSize: '14px',
  },
};
