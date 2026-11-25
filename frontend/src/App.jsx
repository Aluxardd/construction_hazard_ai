import React, { useState, useEffect } from 'react';
import { Loader } from 'lucide-react';
import { ConfigPanel } from './components/ConfigPanel';
import { ImageUploader } from './components/ImageUploader';
import { KPICard } from './components/KPICard';
import { DetectionResults } from './components/DetectionResults';
import { HazardRegister } from './components/HazardRegister';
import { ReportGenerator } from './components/ReportGenerator';
import { SiteProfile, EMPTY_PROFILE } from './components/SiteProfile';
import { LegalAssessment } from './components/LegalAssessment';
import './App.css';

const API_BASE = '/api';
const PROFILE_KEY = 'construction-safety-site-profile-v1';

const TABS = [
  { id: 'visual-detection', label: '🖼️ Visual Detection' },
  { id: 'hazard-register', label: '📋 Hazard & Object Register' },
  { id: 'report-generator', label: '📄 Report Generator' },
  { id: 'legal-assessment', label: '⚖️ Legal Assessment' },
];

function loadSiteProfile() {
  try {
    const saved = localStorage.getItem(PROFILE_KEY);
    if (!saved) return { profile: EMPTY_PROFILE, error: '' };
    const profile = JSON.parse(saved);
    if (!profile || !Array.isArray(profile.hazards) || !Array.isArray(profile.requirements)) {
      throw new Error('Invalid saved profile');
    }
    return { profile: { ...EMPTY_PROFILE, ...profile }, error: '' };
  } catch {
    return { profile: EMPTY_PROFILE, error: 'Could not load the saved site profile. Check browser storage.' };
  }
}

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
    detector_status: '',
  });

  const [configStatus, setConfigStatus] = useState('loading');
  const [configError, setConfigError] = useState('');
  const [images, setImages] = useState([]);
  const [useSample, setUseSample] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [results, setResults] = useState(null);
  const [siteAssessment, setSiteAssessment] = useState(null);
  const [activeTab, setActiveTab] = useState(0);
  const [hazardFilterMode, setHazardFilterMode] = useState(0);
  const [errorMessage, setErrorMessage] = useState('');
  const [storedProfile, setStoredProfile] = useState(loadSiteProfile);
  const siteProfile = storedProfile.profile;

  useEffect(() => {
    const loadConfig = async () => {
      setConfigStatus('loading');
      setConfigError('');
      try {
        const response = await fetch(`${API_BASE}/config`);
        if (!response.ok) {
          throw new Error(`Backend returned status ${response.status}`);
        }
        const data = await response.json();
        setConfig((prev) => ({
          ...prev,
          conf_threshold: data.default_confidence ?? prev.conf_threshold,
          iou_threshold: data.default_iou_threshold ?? prev.iou_threshold,
          model_name: data.model_name || prev.model_name,
          is_custom_model: Boolean(data.is_custom_model),
          class_names: data.class_names || [],
          detector_status: data.detector_status || '',
        }));
        setConfigStatus('ready');
      } catch (error) {
        setConfigStatus('error');
        setConfigError(`Could not reach backend configuration endpoint (${error.message}).`);
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

  const handleProfileChange = (profile) => {
    let error = '';
    try {
      localStorage.setItem(PROFILE_KEY, JSON.stringify(profile));
    } catch {
      error = 'Could not save the site profile in this browser. The current values are temporary.';
    }
    setStoredProfile({ profile, error });
    setResults(null);
    setSiteAssessment(null);
  };

  const handleProcessImages = async () => {
    if (!images.length && !useSample) {
      setErrorMessage('Please select at least one image or enable the sample image before analyzing.');
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
      if (selectedImages.length > 1) {
        selectedImages.forEach((img) => formData.append('files', img));
      } else {
        formData.append('file', selectedImages[0]);
      }

      formData.append('conf_threshold', config.conf_threshold);
      formData.append('iou_threshold', config.iou_threshold);
      formData.append('show_compliant', config.show_compliant);
      formData.append('site_context', JSON.stringify(siteProfile));

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

  const allWorkers = (results || []).flatMap((result) => result.legal_assessment?.workers || []);
  const potentialFindingsCount = allWorkers
    .flatMap((worker) => worker.findings || [])
    .filter((finding) => finding.status === 'POTENTIAL NON-COMPLIANCE').length;
  const reviewWorkersCount = allWorkers.filter((worker) => worker.status === 'REVIEW REQUIRED').length;
  const notAssessableWorkersCount = allWorkers.filter((worker) => worker.status === 'NOT ASSESSABLE').length;

  return (
    <div style={styles.app}>
      <header style={styles.header}>
        <div style={styles.headerContent}>
          <h1 style={styles.mainTitle}>🏗️ Construction Safety AI: PPE Detection</h1>
          <p style={styles.subtitle}>
            BSc (Hons) Computer Science Final Year Project • Serghei Coceban • University of Bolton &amp; Regent College London
          </p>
        </div>
      </header>

      <div className="app-layout">
        <ConfigPanel
          config={config}
          onConfigChange={setConfig}
          isProcessing={isProcessing}
          configStatus={configStatus}
          configError={configError}
        />

        <main className="app-main">
          {configError && (
            <div role="alert" style={styles.errorBanner}>
              {configError}
            </div>
          )}

          <ImageUploader
            onImagesSelected={handleImagesSelected}
            isProcessing={isProcessing}
          />
          <SiteProfile
            profile={siteProfile}
            onChange={handleProfileChange}
            disabled={isProcessing}
            storageError={storedProfile.error}
          />

          <button
            type="button"
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

          {errorMessage && (
            <div role="alert" style={styles.errorBanner}>
              {errorMessage}
            </div>
          )}

          {siteAssessment && results && (
            <>
              <div className="kpi-grid">
                <KPICard title="Total detections" value={siteAssessment.total_detections} color="#0066cc" />
                <KPICard title="PPE items" value={siteAssessment.total_ppe_items} color="#28a745" />
                <KPICard title="Workers detected" value={siteAssessment.total_workers} color="#0066cc" />
                <KPICard title="Potential PPE findings" value={potentialFindingsCount} color="#b45309" />
                <KPICard title="Workers for review" value={reviewWorkersCount} color="#64748b" />
                <KPICard title="Workers not assessable" value={notAssessableWorkersCount} color="#64748b" />
              </div>

              <div style={styles.tabsContainer}>
                <div className="tabs-list" role="tablist" aria-label="Inspection results views">
                  {TABS.map((tab, idx) => (
                    <button
                      key={tab.id}
                      id={`tab-${tab.id}`}
                      type="button"
                      role="tab"
                      aria-selected={activeTab === idx}
                      aria-controls={`panel-${tab.id}`}
                      onClick={() => setActiveTab(idx)}
                      style={{
                        ...styles.tabButton,
                        borderBottomColor: activeTab === idx ? '#0066cc' : 'transparent',
                        color: activeTab === idx ? '#0066cc' : '#64748B',
                        fontWeight: activeTab === idx ? '600' : '500',
                      }}
                    >
                      {tab.label}
                    </button>
                  ))}
                </div>

                <div
                  id={`panel-${TABS[activeTab].id}`}
                  role="tabpanel"
                  aria-labelledby={`tab-${TABS[activeTab].id}`}
                  style={styles.tabContent}
                >
                  {activeTab === 0 && <DetectionResults results={results} />}
                  {activeTab === 1 && (
                    <>
                      <div style={styles.filterOptions}>
                        <label style={styles.radioLabel}>
                          <input
                            type="radio"
                            name="hazard-filter"
                            checked={hazardFilterMode === 0}
                            onChange={() => setHazardFilterMode(0)}
                          />
                          <span>Model no-PPE flags &amp; vehicle hazards</span>
                        </label>
                        <label style={styles.radioLabel}>
                          <input
                            type="radio"
                            name="hazard-filter"
                            checked={hazardFilterMode === 1}
                            onChange={() => setHazardFilterMode(1)}
                          />
                          <span>All detections</span>
                        </label>
                      </div>
                      <HazardRegister
                        assessment={siteAssessment}
                        results={results}
                        showHazardsOnly={hazardFilterMode === 0}
                      />
                    </>
                  )}
                  {activeTab === 2 && (
                    <ReportGenerator
                      assessment={siteAssessment}
                      results={results}
                      auditMetadata={config}
                    />
                  )}
                  {activeTab === 3 && <LegalAssessment results={results} />}
                </div>
              </div>
            </>
          )}
        </main>
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
    padding: '24px 20px',
    textAlign: 'center',
  },
  headerContent: {
    maxWidth: '1400px',
    margin: '0 auto',
  },
  mainTitle: {
    fontSize: '26px',
    fontWeight: '700',
    marginBottom: '6px',
    marginTop: 0,
  },
  subtitle: {
    fontSize: '14px',
    color: '#94A3B8',
    margin: 0,
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
    display: 'inline-flex',
    alignItems: 'center',
    gap: '8px',
    marginBottom: '20px',
  },
  spinner: {
    animation: 'spin 1s linear infinite',
  },
  errorBanner: {
    backgroundColor: '#fef2f2',
    border: '1px solid #fecaca',
    color: '#991b1b',
    padding: '12px 14px',
    borderRadius: '6px',
    marginBottom: '16px',
    fontSize: '14px',
  },
  tabsContainer: {
    backgroundColor: '#fff',
    borderRadius: '8px',
    border: '1px solid #E2E8F0',
    overflow: 'hidden',
  },
  tabButton: {
    flex: '1 1 160px',
    padding: '12px',
    backgroundColor: 'transparent',
    border: 'none',
    borderBottom: '3px solid transparent',
    cursor: 'pointer',
    textAlign: 'center',
    transition: 'all 0.2s ease',
  },
  tabContent: {
    padding: '20px',
  },
  filterOptions: {
    display: 'flex',
    flexWrap: 'wrap',
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
