const state = {
  dashboard: null,
  experience: null,
  selectedOption: null,
  submitting: false,
  submitted: false,
};

const $ = (selector, parent = document) => parent.querySelector(selector);
const escapeHtml = (value = '') => String(value).replace(/[&<>"']/g, (character) => ({
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  "'": '&#39;',
}[character]));

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed (${response.status})`);
  }

  return response.json();
}

function displayDate() {
  $('#today-date').textContent = new Intl.DateTimeFormat(undefined, {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
  }).format(new Date());
}

function statusLabel(status) {
  return ({
    mastered: 'Evidence gathered',
    developing: 'In progress',
    needs_reinforcement: 'Revisit',
    new: 'Ahead',
  })[status] || status;
}

function updateHero(concept) {
  const title = $('#hero-title');
  const description = $('#hero-description');
  const button = $('#hero-start');
  const subject = $('#hero-subject');

  if (!concept) {
    title.textContent = 'Your next idea is taking shape';
    description.textContent = 'There are no experiences ready yet. Add a grounded experience spec to begin.';
    button.disabled = true;
    subject.textContent = 'COMPUTER NETWORKS · EXPLORATION';
    return;
  }

  const experience = concept.experiences[0];
  title.textContent = experience?.title || concept.name;
  description.textContent = `Continue exploring ${concept.name}. Your next step responds to the evidence you have gathered.`;
  subject.innerHTML = `${escapeHtml(concept.name.toUpperCase())} <span>·</span> ${concept.status === 'new' ? 'READY TO EXPLORE' : 'PICK UP WHERE YOU LEFT OFF'}`;
  button.disabled = !experience;
  button.dataset.experienceId = experience?.id || '';
}

function renderPath(concepts, relationships) {
  const available = concepts.filter((concept) => concept.experience_count > 0);
  const linkedIds = new Set();
  relationships.forEach((relationship) => {
    if (available.some((item) => item.id === relationship.from)
      && available.some((item) => item.id === relationship.to)) {
      linkedIds.add(relationship.from);
      linkedIds.add(relationship.to);
    }
  });
  const pathConcepts = available.filter((concept) => linkedIds.has(concept.id));
  const shown = pathConcepts.length ? pathConcepts : available;

  if (!shown.length) {
    $('#path-list').innerHTML = '<div class="empty-evidence">No grounded experiences are available yet.</div>';
    return;
  }

  $('#path-list').innerHTML = shown.map((concept, index) => {
    const experience = concept.experiences[0];
    const clickable = Boolean(experience);
    const symbol = concept.status === 'mastered' ? '✓' : concept.status === 'developing' ? '◉' : String(index + 1).padStart(2, '0');
    return `
      <div class="path-row ${escapeHtml(concept.status)} ${index ? 'has-link' : ''} ${clickable ? 'available' : ''}"
        ${clickable ? `data-experience-id="${escapeHtml(experience.id)}" role="button" tabindex="0"` : ''}>
        <div class="path-node">${symbol}</div>
        <div class="path-info">
          <div class="path-name">${escapeHtml(concept.name)}</div>
          <div class="path-subtitle">${escapeHtml(experience?.title || 'Concept in the graph')}</div>
        </div>
        <span class="path-status">${escapeHtml(statusLabel(concept.status))}</span>
      </div>`;
  }).join('');
}

function relativeTime(event) {
  const parsed = event.timestamp ? new Date(event.timestamp) : null;
  if (!parsed || Number.isNaN(parsed.getTime())) return 'Learning evidence recorded';
  const minutes = Math.max(0, Math.floor((Date.now() - parsed.getTime()) / 60000));
  if (minutes < 1) return 'Just now';
  if (minutes < 60) return `${minutes} min ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours} hr ago`;
  return `${Math.floor(hours / 24)} days ago`;
}

function renderEvidence(events, total) {
  $('#evidence-total').textContent = `${total} ${total === 1 ? 'moment' : 'moments'}`;
  if (!events.length) {
    $('#evidence-list').innerHTML = '<div class="empty-evidence">Your learning moments will appear here as you explore.</div>';
    return;
  }

  $('#evidence-list').innerHTML = events.map((event) => `
    <div class="evidence-item">
      <div class="evidence-mark ${event.correct ? 'correct' : 'incorrect'}">${event.correct ? '✓' : '↻'}</div>
      <div class="evidence-main">
        <div class="evidence-title">${escapeHtml(event.concept)} <span>·</span> ${event.correct ? 'Applied the idea' : 'A chance to revisit'}</div>
        <div class="evidence-detail">${escapeHtml(event.mastery_signal || 'Learning evidence recorded')} · ${escapeHtml(relativeTime(event))}</div>
      </div>
      <div class="evidence-kind">${escapeHtml((event.evidence_type || 'evidence').replaceAll('_', ' '))}</div>
    </div>`).join('');
}

function renderDashboard(dashboard) {
  state.dashboard = dashboard;
  const { stats, available_concepts: available, concepts, relationships, recent_evidence: evidence } = dashboard;
  const next = dashboard.next_concept;

  $('#stat-concepts').textContent = `${String(stats.concepts_explored).padStart(2, '0')}`;
  $('#stat-progress').textContent = `${String(stats.concepts_in_progress).padStart(2, '0')}`;
  $('#stat-evidence').textContent = `${String(stats.evidence_events).padStart(2, '0')}`;
  $('#footer-source').textContent = dashboard.source?.section
    ? `SOURCE TRACE · SECTION ${escapeHtml(dashboard.source.section)}`
    : '';
  updateHero(next);
  renderPath(concepts, relationships);
  renderEvidence(evidence, stats.evidence_events);
}

function showToast(message) {
  const toast = $('#toast');
  toast.textContent = message;
  toast.classList.add('visible');
  window.clearTimeout(showToast.timeout);
  showToast.timeout = window.setTimeout(() => toast.classList.remove('visible'), 3200);
}

async function refreshDashboard() {
  try {
    renderDashboard(await api('/api/dashboard'));
  } catch (error) {
    showToast(`Could not load your learning space: ${error.message}`);
  }
}

function sourceCitation(traceability) {
  const source = traceability?.source;
  if (!source) return '';
  const section = source.section ? `Section ${escapeHtml(source.section)}` : '';
  const title = source.section_title ? ` · ${escapeHtml(source.section_title)}` : '';
  return `<div class="source-citation"><span>✧</span> Source: ${section}${title} <span>·</span> Experience and assessment are generated fields</div>`;
}

function renderExperience(experience) {
  const { experience: scene, assessment, learning_objective: objective } = experience;
  const letters = ['A', 'B', 'C', 'D', 'E', 'F'];
  $('#experience-body').innerHTML = `
    <div class="experience-category">${escapeHtml(experience.concept.toUpperCase())} <span>·</span> ${escapeHtml((experience.experience.type || 'experience').toUpperCase())}</div>
    <h1 class="experience-title" id="experience-title">${escapeHtml(scene.title)}</h1>
    <p class="experience-objective">${escapeHtml(objective.statement)}</p>
    <div class="experience-scene">
      <div class="scene-label">THE SCENE</div>
      <p class="scene-text">${escapeHtml(scene.scenario)}</p>
    </div>
    <p class="challenge-copy">${escapeHtml(scene.challenge)}</p>
    <div class="question-block">
      <div class="question-label">YOUR DECISION</div>
      <h2 class="question-text">${escapeHtml(assessment.question)}</h2>
      <div class="answer-options" role="radiogroup" aria-label="Choose your answer">
        ${assessment.options.map((option, index) => `
          <label class="answer-option" data-option-id="${escapeHtml(option.id)}">
            <input type="radio" name="answer" value="${escapeHtml(option.id)}">
            <span class="option-letter">${letters[index] || '•'}</span>
            <span class="option-copy">${escapeHtml(option.text)}</span>
          </label>`).join('')}
      </div>
      <div class="answer-actions">
        <span class="answer-hint" id="answer-hint">Choose the action that feels right.</span>
        <button class="button button-submit" id="answer-submit" type="button" disabled>Lock in decision <span>→</span></button>
      </div>
      <div id="answer-result" aria-live="polite"></div>
    </div>
    ${sourceCitation(experience.traceability)}`;

  $('.answer-options').addEventListener('change', (event) => {
    if (event.target.name !== 'answer') return;
    state.selectedOption = event.target.value;
    document.querySelectorAll('.answer-option').forEach((option) => {
      option.classList.toggle('selected', option.dataset.optionId === state.selectedOption);
    });
    $('#answer-submit').disabled = false;
    $('#answer-hint').textContent = 'Ready when you are.';
  });
  $('#answer-submit').addEventListener('click', submitAnswer);
}

async function openExperience(experienceId) {
  if (!experienceId) return;
  state.experience = null;
  state.selectedOption = null;
  state.submitted = false;
  $('#experience-overlay').hidden = false;
  document.body.style.overflow = 'hidden';
  $('#experience-body').innerHTML = '<div class="loading-state">Preparing your experience…</div>';
  $('#experience-close').focus();

  try {
    state.experience = await api(`/api/experiences/${encodeURIComponent(experienceId)}`);
    renderExperience(state.experience);
    $('.experience-dialog').scrollTop = 0;
  } catch (error) {
    $('#experience-body').innerHTML = `<div class="empty-evidence">${escapeHtml(error.message)}</div>`;
  }
}

async function submitAnswer() {
  if (!state.experience || !state.selectedOption || state.submitting || state.submitted) return;
  state.submitting = true;
  const submit = $('#answer-submit');
  submit.disabled = true;
  submit.textContent = 'Saving your evidence…';

  try {
    const result = await api(`/api/experiences/${encodeURIComponent(state.experience.experience_id)}/answer`, {
      method: 'POST',
      body: JSON.stringify({ option_id: state.selectedOption }),
    });
    state.submitted = true;
    const stateLabel = statusLabel(result.learner_state.status);
    $('#answer-result').innerHTML = `
      <div class="result-card ${result.correct ? 'correct' : 'incorrect'}">
        <div class="result-heading">${result.correct ? 'A strong connection.' : 'Every attempt adds signal.'}</div>
        <p class="result-copy">${escapeHtml(result.feedback)}</p>
        <div class="result-evidence"><strong>Evidence:</strong> ${escapeHtml(result.mastery_signal)}<br>
          ${escapeHtml(result.evidence_type.replaceAll('_', ' '))} · ${result.learner_state.attempts} recorded ${result.learner_state.attempts === 1 ? 'moment' : 'moments'}</div>
        <div class="result-status"><span>Concept status · ${escapeHtml(stateLabel)}</span><strong>${Math.round(result.learner_state.mastery * 100)}% evidence-weighted accuracy</strong></div>
      </div>
      ${sourceCitation({ source: result.source })}`;
    $('#answer-hint').textContent = 'Your evidence has been saved to your learning model.';
    submit.textContent = 'Return to your learning space';
    submit.disabled = false;
    submit.classList.remove('button-submit');
    submit.classList.add('button-primary');
    submit.addEventListener('click', closeExperience, { once: true });
    await refreshDashboard();
  } catch (error) {
    showToast(`Could not save your answer: ${error.message}`);
    submit.disabled = false;
    submit.textContent = 'Try saving again →';
  } finally {
    state.submitting = false;
  }
}

function closeExperience() {
  $('#experience-overlay').hidden = true;
  document.body.style.overflow = '';
  state.experience = null;
  state.selectedOption = null;
  $('#hero-start').focus();
}

function bindNavigation() {
  document.querySelectorAll('.nav-item').forEach((item) => {
    item.addEventListener('click', () => {
      document.querySelectorAll('.nav-item').forEach((nav) => nav.classList.remove('active'));
      item.classList.add('active');
    });
  });
}

$('#hero-start').addEventListener('click', (event) => openExperience(event.currentTarget.dataset.experienceId));
$('#path-list').addEventListener('click', (event) => {
  const row = event.target.closest('[data-experience-id]');
  if (row) openExperience(row.dataset.experienceId);
});
$('#path-list').addEventListener('keydown', (event) => {
  if (event.key !== 'Enter' && event.key !== ' ') return;
  const row = event.target.closest('[data-experience-id]');
  if (row) {
    event.preventDefault();
    openExperience(row.dataset.experienceId);
  }
});
$('#experience-close').addEventListener('click', closeExperience);
$('#experience-overlay').addEventListener('click', (event) => {
  if (event.target === $('#experience-overlay')) closeExperience();
});
document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' && !$('#experience-overlay').hidden) closeExperience();
});

displayDate();
bindNavigation();
refreshDashboard();
