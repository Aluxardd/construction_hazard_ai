import React from 'react';

const percent = (confidence) => `${(confidence * 100).toFixed(1)}%`;

export function LegalAssessment({ results }) {
  const statuses = results.map((result) => result.legal_assessment?.status).filter(Boolean);
  const overall = statuses.includes('POTENTIAL NON-COMPLIANCE')
    ? 'POTENTIAL NON-COMPLIANCE'
    : statuses.includes('REVIEW REQUIRED') ? 'REVIEW REQUIRED' : 'NOT ASSESSABLE';
  return (
    <section>
      <h2>Legislation-informed visual assessment</h2>
      <p><strong>Overall visual assessment:</strong> {overall}. This is not a site-wide legal determination.</p>
      <p>Potential site-requirement flags use a 70% confidence review heuristic for both the person and explicit no-PPE prediction. This threshold is not calibrated; all findings need human review.</p>
      {results.map((result, index) => {
        if (result.error) {
          return (
            <article key={index} style={styles.card}>
              <h3>{result.filename} — Processing error</h3>
              <p role="alert">{result.error}</p>
            </article>
          );
        }
        const assessment = result.legal_assessment;
        if (!assessment) return <p key={index}>Assessment unavailable for {result.filename}.</p>;
        return (
          <article key={index} style={styles.card}>
            <h3>{result.filename} — {assessment.status}</h3>
            <p>{assessment.notice}</p>
            <p>{assessment.jurisdiction_notice}</p>
            <p>Declared activity: {assessment.context.activity}; work area: {assessment.context.work_area || 'not supplied'}.
              Hazards: {assessment.context.hazards.join(', ') || 'not supplied'}.</p>
            {assessment.context.notes && <p>Declared context: {assessment.context.notes}</p>}
            {!assessment.workers.length && <p>No person was detected. This does not establish that the image contains no workers.</p>}
            {assessment.workers.map((worker) => (
              <section key={worker.id} style={styles.worker}>
                <h4>{worker.id} — {worker.status}</h4>
                <p>Person confidence: {percent(worker.confidence)}; box xyxy: [{worker.bbox.join(', ')}]</p>
                <p><strong>Associated AI observations:</strong> {worker.observations.length
                  ? worker.observations.map((observation) => `${observation.label} (${percent(observation.confidence)})`).join(', ')
                  : 'None; absence is not evidence that PPE is missing.'}</p>
                {!worker.findings.length && <p>No PPE requirement was declared. Provide site context for an item-specific assessment.</p>}
                {worker.findings.map((finding) => (
                  <div key={finding.ppe_item} style={styles.finding}>
                    <strong>{finding.ppe_item}: {finding.status}</strong>
                    <p>Declared requirement source: {finding.requirement_source.replaceAll('_', ' ')}</p>
                    <p>{finding.reasoning}</p>
                    <p>Observation: {finding.observations.length
                      ? finding.observations.map((o) => `${o.label} (${percent(o.confidence)})`).join(', ')
                      : 'PPE not confirmed'}</p>
                    <p>Related sources: {finding.reference_ids.join(', ') || 'jurisdiction not verified'}</p>
                    <p>{finding.recommended_action}</p>
                  </div>
                ))}
              </section>
            ))}
            {assessment.unassigned_observations.length > 0 && (
              <p>Unassigned or ambiguous model observations: {assessment.unassigned_observations.map(
                (o) => `${o.label} (${percent(o.confidence)})`,
              ).join(', ')}. Do not assign these to a worker without review.</p>
            )}
            <h4>Potentially relevant official references</h4>
            {!assessment.references.length && <p>No Great Britain references applied: confirm jurisdiction first.</p>}
            <ul>
              {assessment.references.map((reference) => (
                <li key={reference.id} style={styles.reference}>
                  <a href={reference.url} target="_blank" rel="noreferrer">{reference.title} — {reference.section}</a>
                  {' '}({reference.source_type}; {reference.source_organisation}; reviewed {reference.last_verified})
                  <br />{reference.summary} {reference.applicability}
                </li>
              ))}
            </ul>
            <p><strong>Hierarchy of controls:</strong> consider elimination, substitution, engineering controls and administrative controls before PPE. An image cannot verify their adequacy.</p>
          </article>
        );
      })}
    </section>
  );
}

const styles = {
  card: { border: '1px solid #cbd5e1', borderRadius: 6, padding: 16, margin: '16px 0' },
  worker: { borderTop: '1px solid #cbd5e1', paddingTop: 8 },
  finding: { background: '#f8fafc', padding: 12, margin: '8px 0' },
  reference: { marginBottom: 12 },
};
