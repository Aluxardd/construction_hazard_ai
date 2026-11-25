import React from 'react';

const PPE = [
  ['helmet', 'Helmet'], ['vest', 'High-visibility clothing'], ['boots', 'Safety footwear'],
  ['gloves', 'Gloves'], ['goggles', 'Eye protection'], ['respirator', 'Respiratory protection'],
  ['hearing_protection', 'Hearing protection'], ['fall_protection', 'Fall protection'],
];
const HAZARDS = [['height', 'Work at height'], ['substances', 'Hazardous substances'], ['noise', 'Noise']];

export const EMPTY_PROFILE = {
  jurisdiction: 'unknown',
  activity: 'unknown',
  work_area: '',
  hazards: [],
  requirements: [],
  requirement_source: 'site_rule',
  notes: '',
};

export function SiteProfile({ profile, onChange, disabled, storageError }) {
  const set = (key, value) => onChange({ ...profile, [key]: value });
  const toggle = (key, value) => set(
    key,
    profile[key].includes(value) ? profile[key].filter((item) => item !== value) : [...profile[key], value],
  );
  return (
    <section style={styles.section} aria-labelledby="site-profile-title">
      <h2 id="site-profile-title">Site assessment context</h2>
      <p>Saved in this browser on this device. These are your declarations, not automatically verified facts.</p>
      {storageError && <p role="alert">{storageError}</p>}
      <label style={styles.label}>Jurisdiction
        <select value={profile.jurisdiction} onChange={(e) => set('jurisdiction', e.target.value)} disabled={disabled}>
          <option value="unknown">Unknown</option>
          <option value="great_britain">England, Scotland or Wales (GB references included)</option>
          <option value="northern_ireland">Northern Ireland (manual HSENI/NI legal review required)</option>
        </select>
      </label>
      <label style={styles.label}>Activity
        <select value={profile.activity} onChange={(e) => set('activity', e.target.value)} disabled={disabled}>
          <option value="unknown">Unknown</option>
          <option value="construction">Construction</option>
          <option value="other">Other</option>
        </select>
      </label>
      <label style={styles.label}>Work area or activity details
        <input value={profile.work_area} maxLength={500} onChange={(e) => set('work_area', e.target.value)} disabled={disabled} />
      </label>
      <fieldset disabled={disabled}>
        <legend>Hazards identified in site context (optional)</legend>
        {HAZARDS.map(([value, label]) => (
          <label key={value} style={styles.option}>
            <input type="checkbox" checked={profile.hazards.includes(value)} onChange={() => toggle('hazards', value)} /> {label}
          </label>
        ))}
      </fieldset>
      <label style={styles.label}>Source of declared PPE requirements
        <select value={profile.requirement_source} onChange={(e) => set('requirement_source', e.target.value)} disabled={disabled}>
          <option value="site_rule">Site rule</option>
          <option value="risk_assessment">Risk assessment</option>
          <option value="construction_phase_plan">Construction phase plan</option>
        </select>
      </label>
      <fieldset disabled={disabled}>
        <legend>PPE explicitly required by the selected source</legend>
        <p>Leave items unchecked if the requirement is unknown. Unchecked does not mean PPE is unnecessary.</p>
        {PPE.map(([value, label]) => (
          <label key={value} style={styles.option}>
            <input type="checkbox" checked={profile.requirements.includes(value)} onChange={() => toggle('requirements', value)} /> {label}
          </label>
        ))}
      </fieldset>
      <label style={styles.label}>Other context or document reference
        <textarea value={profile.notes} maxLength={2000} onChange={(e) => set('notes', e.target.value)} disabled={disabled} rows={3} />
      </label>
      <button type="button" onClick={() => onChange(EMPTY_PROFILE)} disabled={disabled}>Clear saved profile</button>
    </section>
  );
}

const styles = {
  section: { background: '#f8fafc', border: '1px solid #cbd5e1', borderRadius: 6, padding: 16, marginBottom: 20 },
  label: { display: 'flex', flexDirection: 'column', gap: 5, margin: '12px 0' },
  option: { display: 'inline-flex', gap: 5, alignItems: 'center', margin: '5px 16px 5px 0' },
};
