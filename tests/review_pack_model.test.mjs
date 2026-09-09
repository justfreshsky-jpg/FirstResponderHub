import test from 'node:test';
import assert from 'node:assert/strict';
import { TEMPLATES, createPack, validate, updateItem, exportMarkdown } from '../static/review_pack_model.mjs';

test('each original workflow starts incomplete and bounded', () => {
  for (const type of Object.keys(TEMPLATES)) {
    const pack = createPack(type, 'Review', 'No identifying details');
    assert.equal(pack.items.length, 6);
    assert.equal(pack.items.filter(item => item.complete).length, 0);
    assert.deepEqual(validate(pack), pack);
  }
});

test('completion changes require explicit user action and preserve prior value', () => {
  const initial = createPack('meeting_review', 'Meeting review');
  const changed = updateItem(initial, 'purpose', { complete: true, evidence: 'Purpose reviewed by authorized chair' });
  assert.equal(changed.items[0].complete, true);
  assert.equal(changed.revision, 1);
  assert.equal(initial.items[0].complete, false);
});

test('imports reject another product, altered checklist, and oversized notes', () => {
  const pack = createPack('readiness_review', 'Readiness');
  assert.throws(() => validate({ ...pack, product_id: 'other' }));
  assert.throws(() => validate({ ...pack, items: pack.items.slice(1) }));
  assert.throws(() => updateItem(pack, 'scope', { complete: true, evidence: 'x'.repeat(1001) }));
});

test('readable export reports gaps without readiness or compliance claims', () => {
  const output = exportMarkdown(createPack('report_handoff', 'Handoff'));
  assert.match(output, /Completeness: 0 of 6/);
  assert.match(output, /No completion evidence recorded/);
  assert.match(output, /does not establish operational readiness, compliance, certification/);
});
