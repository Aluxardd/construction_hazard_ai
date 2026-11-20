import React, { useState, useEffect } from 'react';
import { Loader } from 'lucide-react';
import { ConfigPanel } from './components/ConfigPanel';
import { ImageUploader } from './components/ImageUploader';
import { KPICard } from './components/KPICard';
import { DetectionResults } from './components/DetectionResults';
import { RiskMatrix } from './components/RiskMatrix';
import { HazardRegister } from './components/HazardRegister';
import { ReportGenerator } from './components/ReportGenerator';
import './App.css';

const API_BASE = 'http://localhost:8000';

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
  };

  const handleProcessImages = async () => {
    if (!images.length && !useSample) {
      alert('Please select images to process');
      return;
    }

    setIsProcessing(true);
    try {
      // Handle sample image mode
      if (useSample && !images.length) {
        // Create a sample image
        const canvas = document.createElement('canvas');
        canvas.width = 640;
        canvas.height = 480;
        const ctx = canvas.getContext('2d');
        
        // Draw a simple construction site-like image
        ctx.fillStyle = '#87CEEB';
        ctx.fillRect(0, 0, 640, 480);
        ctx.fillStyle = '#DAA520';
        ctx.fillRect(0, 350, 640, 130);
        
        // Add some shapes to represent construction elements
        ctx.fillStyle = '#FF6347';
        ctx.fillRect(100, 200, 80, 150);
        ctx.fillStyle = '#4169E1';
        ctx.fillRect(300, 250, 100, 100);
        
        canvas.toBlob((blob) => {
          const file = new File([blob], 'sample_site.png', { type: 'image/png' });
          const formData = new FormData();
          formData.append('file', file);
          formData.append('conf_threshold', config.conf_threshold || 0.5);
          formData.append('iou_threshold', config.iou_threshold || 0.45);
          formData.append('show_compliant', config.show_compliant || true);

          fetch(`${API_BASE}/detect`, {
            method: 'POST',
            body: formData,
          })
            .then((res) => {
              if (!res.ok) throw new Error('Detection failed');
              return res.json();
            })
            .then((data) => {
              setResults([
                {
                  filename: data.filename,
                  annotated_image: data.annotated_image,
                  evaluation: data.evaluation,
                },
              ]);
              setSiteAssessment(data.evaluation);
              setActiveTab(1);
            })
            .catch((error) => alert(`Error: ${error.message}`))
            .finally(() => setIsProcessing(false));
        });
        return;
      }

      // Normal file upload mode
      const formData = new FormData();

      if (images.length > 0) {
        if (images.length > 1) {
          images.forEach((img) => formData.append('files', img));
        } else {
          formData.append('file', images[0]);
        }
      }

      formData.append('conf_threshold', config.conf_threshold || 0.5);
      formData.append('iou_threshold', config.iou_threshold || 0.45);
      formData.append('show_compliant', config.show_compliant || true);

      const endpoint = images.length > 1 ? '/detect-batch' : '/detect';
      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Detection failed: ${errorText || response.statusText}`);
      }

      const data = await response.json();
      if (images.length > 1) {
        setResults(data.results);
        setSiteAssessment(data.aggregate_assessment);
      } else {
        setResults([
          {
            filename: data.filename,
            annotated_image: data.annotated_image,
            evaluation: data.evaluation,
          },
        ]);
        setSiteAssessment(data.evaluation);
      }

      setActiveTab(1); // Switch to results tab
    } catch (error) {
      alert(`Error: ${error.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const getOverallColor = (siteAssessment) => {
    if (!siteAssessment) return '#1E293B';
    const tierCounts = siteAssessment.tier_counts || {};
    if (tierCounts.Critical > 0) return '#dc3545';
    if (tierCounts.High > 0) return '#fd7e14';
    if (tierCounts.Medium > 0) return '#ffc107';
    return '#28a745';
  };

  return (
    <div style={styles.app}>
      {/* Header */}
      <div style={styles.header}>
        <div style={styles.headerContent}>
          <h1 style={styles.mainTitle}>🏗️ Construction Safety AI: Hazard Detection & 5×5 Risk Matrix</h1>
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

          {/* Results Section */}
          {siteAssessment && (
            <>
              {/* KPI Dashboard */}
              <div style={styles.kpiGrid}>
                <KPICard
                  title="Overall Status"
                  value={siteAssessment.overall_site_risk}
                  color={getOverallColor(siteAssessment)}
                />
                <KPICard
                  title="Hazards / Violations"
                  value={siteAssessment.total_hazards}
                  color={siteAssessment.total_hazards > 0 ? '#dc3545' : '#28a745'}
                />
                <KPICard
                  title="Compliant PPE"
                  value={siteAssessment.compliant_count}
                  color="#28a745"
                />
                <KPICard
                  title="Compliance Rate"
                  value={`${siteAssessment.compliance_rate}%`}
                  color={siteAssessment.compliance_rate >= 80 ? '#28a745' : '#fd7e14'}
                />
                <KPICard
                  title="Critical (15-25)"
                  value={siteAssessment.tier_counts?.Critical || 0}
                  color="#dc3545"
                />
                <KPICard
                  title="High (10-14)"
                  value={siteAssessment.tier_counts?.High || 0}
                  color="#fd7e14"
                />
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
                  {activeTab === 1 && <RiskMatrix assessment={siteAssessment} />}
                  {activeTab === 2 && (
                    <>
                      <div style={styles.filterOptions}>
                        <label style={styles.radioLabel}>
                          <input
                            type="radio"
                            checked={hazardFilterMode === 0}
                            onChange={() => setHazardFilterMode(0)}
                          />
                          <span>Hazards Only (Violations)</span>
                        </label>
                        <label style={styles.radioLabel}>
                          <input
                            type="radio"
                            checked={hazardFilterMode === 1}
                            onChange={() => setHazardFilterMode(1)}
                          />
                          <span>All Detections (Including Compliant PPE)</span>
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
