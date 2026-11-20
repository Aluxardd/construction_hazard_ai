import React, { useState, useEffect } from 'react';
import { Loader } from 'lucide-react';
import { ConfigPanel } from './components/ConfigPanel';
import { ImageUploader } from './components/ImageUploader';
import { KPICard } from './components/KPICard';
import { DetectionResults } from './components/DetectionResults';
import { HazardRegister } from './components/HazardRegister';
import { ReportGenerator } from './components/ReportGenerator';
import './App.css';

const API_BASE = '/api';

function App() {
  const [config, setConfig] = useState({
    conf_threshold: 0.3,
    iou_threshold: 0.45,
    show_compliant: true,
    site_name: 'Bolton Central Construction Phase 2',
    inspector_name: 'S. Coceban (Safety Lead)',
    inspection_date: new Date().toISOString().split('T')[0],
    model_name: 'best.pt',
    is_custom_model: false,
    class_names: [],
  });

  const [systemConfig, setSystemConfig] = useState(null);
  const [images, setImages] = useState([]);
  const [useSample, setUseSample] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [results, setResults] = useState(null);
  const [siteAssessment, setSiteAssessment] = useState(null);
  const [activeTab, setActiveTab] = useState(0);
  const [hazardFilterMode, setHazardFilterMode] = useState(0);
  const [errorMessage, setErrorMessage] = useState('');

  // Load system config on mount
  useEffect(() => {
    const loadConfig = async () => {
      try {
        const response = await fetch(`${API_BASE}/config`);
        const data = await response.json();
        setSystemConfig(data);
        setConfig((prev) => ({
          ...prev,
          is_custom_model: data.is_custom_model,
          class_names: data.class_names || [],
          detector_status: data.detector_status,
        }));
      } catch (error) {
        console.error('Failed to load system config:', error);
      }
    };
    loadConfig();
  }, []);

  const handleImagesSelected = (selectedImages, isSample) => {
    setImages(selectedImages);
    setUseSample(isSample);
    setResults(null);
    setSiteAssessment(null);
    setErrorMessage('');
  };

  const handleProcessImages = async () => {
    if (!images.length && !useSample) {
      alert('Please select images to process');
      return;
    }

    setIsProcessing(true);
    setErrorMessage('');
    setResults(null);
    setSiteAssessment(null);
    try {
      let selectedImages = images;
      if (useSample) {
        const sample = await fetch(`${API_BASE}/sample-image`);
        if (!sample.ok) throw new Error('Could not load the sample image.');
        selectedImages = [new File([await sample.blob()], 'sample_site.jpg', { type: 'image/jpeg' })];
      }
      const formData = new FormData();
      if (selectedImages.length > 0) {
        if (selectedImages.length > 1) {
          selectedImages.forEach((img) => formData.append('files', img));
        } else {
          formData.append('file', selectedImages[0]);
        }
      }

      formData.append('conf_threshold', config.conf_threshold);
      formData.append('iou_threshold', config.iou_threshold);
      formData.append('show_compliant', config.show_compliant);

      const endpoint = selectedImages.length > 1 ? '/detect-batch' : '/detect';
      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(typeof errorData?.detail === 'string' ? errorData.detail : `Detection failed (${response.status}).`);
      }

      const data = await response.json();
      if (selectedImages.length > 1) {
        setResults(data.results);
        setSiteAssessment(data.site_assessment);
      } else {
        setResults([data]);
        setSiteAssessment(data.evaluation);
      }

      setActiveTab(0);
    } catch (error) {
      setErrorMessage(error.message);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div style={styles.app}>
      {/* Header */}
      <div style={styles.header}>
        <div style={styles.headerContent}>
          <h1 style={styles.mainTitle}>🏗️ Construction Safety AI: PPE Detection</h1>
          <p style={styles.subtitle}>
            BSc (Hons) Computer Science Final Year Project • Serghei Coceban • University of Bolton & Regent College London
          </p>
        </div>
      </div>

      {/* Main Layout */}
      <div style={styles.mainLayout}>
        {/* Sidebar */}
        <ConfigPanel
          config={config}
          onConfigChange={setConfig}
          isProcessing={isProcessing}
        />

        {/* Main Content */}
        <div style={styles.mainContent}>
          {/* Upload Section */}
          <ImageUploader
            onImagesSelected={handleImagesSelected}
            isProcessing={isProcessing}
          />

          <button
            onClick={handleProcessImages}
            disabled={isProcessing || (!images.length && !useSample)}
            style={{
              ...styles.processButton,
              opacity: isProcessing || (!images.length && !useSample) ? 0.5 : 1,
              cursor: isProcessing || (!images.length && !useSample) ? 'not-allowed' : 'pointer',
            }}
          >
            {isProcessing ? (
              <>
                <Loader size={16} style={styles.spinner} /> Processing...
              </>
            ) : (
              'Analyze Images'
            )}
          </button>
          {errorMessage && <p role="alert" style={{ color: '#b91c1c' }}>{errorMessage}</p>}

          {/* Results Section */}
          {siteAssessment && (
            <>
              {/* KPI Dashboard */}
              <div style={styles.kpiGrid}>
                <KPICard title="Detections" value={siteAssessment.total_detections} color="#0066cc" />
                <KPICard title="PPE detections" value={siteAssessment.total_ppe_items} color="#28a745" />
                <KPICard title="People detected" value={siteAssessment.total_workers} color="#0066cc" />
                <KPICard title="Compliance" value="Not assessed" color="#64748b" />
              </div>

              {/* Tabs */}
              <div style={styles.tabsContainer}>
                <div style={styles.tabsList}>
                  {['🖼️ Visual Detection', '📊 5×5 Risk Matrix', '📋 Hazard Register', '📄 Report Generator'].map(
                    (tab, idx) => (
                      <button
                        key={idx}
                        onClick={() => setActiveTab(idx)}
                        style={{
                          ...styles.tabButton,
                          borderBottomColor: activeTab === idx ? '#0066cc' : 'transparent',
                          color: activeTab === idx ? '#0066cc' : '#64748B',
                          fontWeight: activeTab === idx ? '600' : '500',
                        }}
                      >
                        {tab}
                      </button>
                    )
                  )}
                </div>

                {/* Tab Content */}
                <div style={styles.tabContent}>
                  {activeTab === 0 && <DetectionResults results={results} />}
                  {activeTab === 1 && <p>Risk scoring is not available from object detections alone. Review images on site.</p>}
                  {activeTab === 2 && (
                    <>
                      <div style={styles.filterOptions}>
                        <label style={styles.radioLabel}>
                          <input
                            type="radio"
                            checked={hazardFilterMode === 0}
                            onChange={() => setHazardFilterMode(0)}
                          />
                          <span>Model no-PPE flags only</span>
                        </label>
                        <label style={styles.radioLabel}>
                          <input
                            type="radio"
                            checked={hazardFilterMode === 1}
                            onChange={() => setHazardFilterMode(1)}
                          />
                          <span>All detections</span>
                        </label>
                      </div>
                      <HazardRegister
                        assessment={siteAssessment}
                        showHazardsOnly={hazardFilterMode === 0}
                      />
                    </>
                  )}
                  {activeTab === 3 && (
                    <ReportGenerator assessment={siteAssessment} auditMetadata={config} />
                  )}
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;

const styles = {
  app: {
    backgroundColor: '#fff',
    minHeight: '100vh',
  },
  header: {
    backgroundColor: '#1E293B',
    color: '#fff',
    padding: '30px',
    textAlign: 'center',
  },
  headerContent: {
    maxWidth: '1400px',
    margin: '0 auto',
  },
  mainTitle: {
    fontSize: '28px',
    fontWeight: '700',
    marginBottom: '5px',
  },
  subtitle: {
    fontSize: '14px',
    color: '#94A3B8',
    margin: 0,
  },
  mainLayout: {
    display: 'flex',
    maxWidth: '1400px',
    margin: '0 auto',
  },
  mainContent: {
    flex: 1,
    padding: '20px',
  },
  processButton: {
    padding: '12px 24px',
    backgroundColor: '#0066cc',
    color: '#fff',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontWeight: '500',
    fontSize: '14px',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    marginBottom: '20px',
  },
  spinner: {
    animation: 'spin 1s linear infinite',
  },
  kpiGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(6, 1fr)',
    gap: '10px',
    marginBottom: '20px',
  },
  tabsContainer: {
    backgroundColor: '#fff',
    borderRadius: '8px',
    border: '1px solid #E2E8F0',
    overflow: 'hidden',
  },
  tabsList: {
    display: 'flex',
    borderBottom: '2px solid #E2E8F0',
  },
  tabButton: {
    flex: 1,
    padding: '12px',
    backgroundColor: 'transparent',
    border: 'none',
    borderBottom: '3px solid transparent',
    cursor: 'pointer',
    textAlign: 'center',
    transition: 'all 0.3s ease',
  },
  tabContent: {
    padding: '20px',
  },
  filterOptions: {
    display: 'flex',
    gap: '20px',
    marginBottom: '15px',
  },
  radioLabel: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    cursor: 'pointer',
    fontSize: '14px',
  },
};
