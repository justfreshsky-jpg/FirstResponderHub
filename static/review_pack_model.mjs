export const PRODUCT_ID = 'civicops';

export const TEMPLATES = {
  meeting_review: {
    label: 'Meeting preparation and action review',
    items: [
      ['purpose', 'Purpose and decision authority are identified'],
      ['agenda', 'Agenda, timeboxes, and required participants are ready'],
      ['materials', 'Current supporting materials and local references are attached'],
      ['decisions', 'Decision owners and approval boundaries are recorded'],
      ['actions', 'Action owners, due dates, and completion evidence are defined'],
      ['followup', 'Unresolved items and the next review point are recorded'],
    ],
  },
  readiness_review: {
    label: 'Administrative readiness review',
    items: [
      ['scope', 'The administrative scope and out-of-scope operational decisions are clear'],
      ['authority', 'Controlling local policy, adopted references, and reviewers are identified'],
      ['facts', 'User-supplied facts are separated from unknown or unverified details'],
      ['resources', 'People, materials, access, and dependencies are checked'],
      ['exceptions', 'Gaps, conflicts, and escalation owners are recorded'],
      ['approval', 'Required local review and approval are complete'],
    ],
  },
  report_handoff: {
    label: 'Administrative report handoff',
    items: [
      ['period', 'Reporting period, purpose, and intended recipient are identified'],
      ['facts', 'Facts and figures were checked against the record owner'],
      ['sources', 'Current local sources and system-of-record references are listed'],
      ['privacy', 'PII, PHI, incident-sensitive details, and unrelated records are excluded'],
      ['questions', 'Conflicts, missing information, and unanswered questions are visible'],
      ['release', 'Authorized reviewer, approval state, and delivery method are recorded'],
    ],
  },
};

const clean = (value, maximum) => {
  if (typeof value !== 'string' || value.length > maximum) throw Error('Invalid text');
  return value.trim();
};

export function createPack(type, title, context = '') {
  const template = TEMPLATES[type];
  if (!template) throw Error('Choose a supported review workflow');
  return validate({
    schema_version: 1,
    product_id: PRODUCT_ID,
    pack_type: type,
    revision: 0,
    title: clean(title, 160),
    context: clean(context, 500),
    items: template.items.map(([id, label]) => ({ id, label, complete: false, evidence: '' })),
  });
}

export function validate(value) {
  if (!value || value.schema_version !== 1 || value.product_id !== PRODUCT_ID ||
      !TEMPLATES[value.pack_type] || !Number.isSafeInteger(value.revision) ||
      value.revision < 0 || !Array.isArray(value.items)) {
    throw Error('Not a supported CivicOps review pack');
  }
  clean(value.title, 160);
  clean(value.context, 500);
  const expected = TEMPLATES[value.pack_type].items;
  if (value.items.length !== expected.length) throw Error('Review checklist is incomplete');
  value.items.forEach((item, index) => {
    if (!item || item.id !== expected[index][0] || item.label !== expected[index][1] ||
        typeof item.complete !== 'boolean') throw Error('Review checklist does not match');
    clean(item.evidence, 1000);
  });
  return structuredClone(value);
}

export function updateItem(value, id, { complete, evidence }) {
  const next = validate(value);
  const item = next.items.find(entry => entry.id === id);
  if (!item) throw Error('Checklist item was not found');
  item.complete = Boolean(complete);
  item.evidence = clean(evidence, 1000);
  next.revision += 1;
  return validate(next);
}

export function exportMarkdown(value) {
  const pack = validate(value);
  const done = pack.items.filter(item => item.complete).length;
  const lines = [
    `# ${pack.title || TEMPLATES[pack.pack_type].label}`,
    '',
    `Workflow: ${TEMPLATES[pack.pack_type].label}`,
    `Completeness: ${done} of ${pack.items.length}`,
    '',
    pack.context ? `Context: ${pack.context}` : 'Context: Not recorded',
    '',
  ];
  for (const item of pack.items) {
    lines.push(`## ${item.complete ? '[x]' : '[ ]'} ${item.label}`, '',
      item.evidence || 'No completion evidence recorded.', '');
  }
  lines.push(
    'Review note: This pack records administrative checklist completion only. It does not establish operational readiness, compliance, certification, or authorization to act.',
    'Current department policy, adopted references, official systems, and authorized reviewers remain controlling.',
    '',
  );
  return lines.join('\n');
}
