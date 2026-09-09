import { createPack, validate, updateItem, exportMarkdown } from './review_pack_model.mjs';

const $ = id => document.getElementById(id);
const node = (tag, text = '') => { const element = document.createElement(tag); element.textContent = text; return element; };
let pack = null;
let dirty = false;

function status(text) { $('pack-status').textContent = text; }
function markDirty() { dirty = true; status('Unsaved changes — download an editable copy before leaving.'); }
function download(text, name, type) {
  const url = URL.createObjectURL(new Blob([text], { type }));
  const link = node('a');
  link.href = url; link.download = name; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 2000);
}
function render() {
  $('pack-items').replaceChildren();
  if (!pack) {
    $('pack-summary').textContent = 'No pack started';
    $('pack-items').append(node('p', 'Choose a workflow above to begin.'));
    return;
  }
  const done = pack.items.filter(item => item.complete).length;
  $('pack-summary').textContent = `${done} of ${pack.items.length} items complete`;
  for (const item of pack.items) {
    const card = node('article'); card.className = 'pack-item';
    const label = node('label'); const check = node('input');
    check.type = 'checkbox'; check.checked = item.complete;
    label.append(check, node('strong', item.label)); card.append(label);
    const evidence = node('textarea'); evidence.rows = 2; evidence.maxLength = 1000;
    evidence.value = item.evidence;
    evidence.placeholder = 'Your de-identified evidence, unresolved item, or reviewer note';
    card.append(evidence);
    const save = () => { pack = updateItem(pack, item.id, { complete: check.checked, evidence: evidence.value }); markDirty(); render(); };
    check.onchange = save; evidence.onchange = save; $('pack-items').append(card);
  }
}

$('start-pack').onclick = () => {
  if (pack && dirty && !confirm('Replace the current unsaved pack?')) return;
  try { pack = createPack($('pack-type').value, $('pack-title').value, $('pack-context').value); markDirty(); render(); }
  catch (error) { status(error.message); }
};
$('save-pack').onclick = () => {
  try { if (!pack) throw Error('Start a workflow first.'); download(JSON.stringify(validate(pack), null, 2), 'civicops-review-pack.json', 'application/json'); dirty = false; status('Editable JSON download requested. Keep it securely.'); }
  catch (error) { status(error.message); }
};
$('export-pack').onclick = () => {
  try { if (!pack) throw Error('Start a workflow first.'); if (confirm('Export a readable unencrypted review pack?')) { download(exportMarkdown(pack), 'civicops-review.md', 'text/markdown'); status('Readable review-pack download requested. Inspect it before sharing.'); } }
  catch (error) { status(error.message); }
};
$('open-pack').onchange = async event => {
  const file = event.target.files[0]; if (!file) return;
  if (pack && dirty && !confirm('Replace the current unsaved pack?')) { event.target.value = ''; return; }
  try {
    if (file.size > 200000) throw Error('File is larger than the review-pack limit');
    const next = validate(JSON.parse(await file.text())); pack = next; dirty = false;
    $('pack-type').value = pack.pack_type; $('pack-title').value = pack.title; $('pack-context').value = pack.context;
    render(); status('Editable review pack opened.');
  } catch (error) { status(`${error.message}. Current work was preserved.`); }
  finally { event.target.value = ''; }
};
$('clear-pack').onclick = () => {
  if (pack && dirty && !confirm('Clear the current unsaved pack?')) return;
  pack = null; dirty = false; $('pack-context').value = ''; render(); status('Current tab cleared. Downloaded files are unchanged.');
};
window.addEventListener('beforeunload', event => { if (dirty) { event.preventDefault(); event.returnValue = ''; } });
render();
