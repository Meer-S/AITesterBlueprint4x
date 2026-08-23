#!/usr/bin/env node
/*
 * build_resume.js — render a resume JSON spec to .docx
 *
 *   node build_resume.js spec.json                 # working copy (highlights + placeholders kept)
 *   node build_resume.js spec.json --clean         # send-ready (highlights stripped; fails if [placeholders] remain)
 *   node build_resume.js spec.json --out other.docx
 *
 * Inline markup inside any text field:
 *   ==text==   highlighted as a tailoring change (yellow)   -> stripped in --clean
 *   [text]     placeholder the candidate must fill (red)    -> blocks --clean
 *   **text**   bold
 *
 * See references/resume-json.md for the full schema.
 */
const { Document, Packer, Paragraph, TextRun, AlignmentType, BorderStyle,
        LevelFormat, convertInchesToTwip, ExternalHyperlink } = require('docx');
const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
const specPath = args.find(a => !a.startsWith('--'));
if (!specPath) { console.error('usage: build_resume.js <spec.json> [--clean] [--out file.docx]'); process.exit(1); }
const CLEAN = args.includes('--clean');
const outFlag = args.indexOf('--out');
const spec = JSON.parse(fs.readFileSync(specPath, 'utf8'));

const T = Object.assign({
  ink: '1A1A1A', slate: '3D4451', accent: '2B5F8C', fill: 'B02A1F',
  muted: '6B7280', rule: '9AA0A6', font: 'Calibri', highlight: 'yellow'
}, spec.theme || {});

// ---- placeholder audit -------------------------------------------------
const found = [];
(function walk(n) {
  if (typeof n === 'string') { const m = n.match(/\[[^\]]+\]/g); if (m) found.push(...m); }
  else if (Array.isArray(n)) n.forEach(walk);
  else if (n && typeof n === 'object') Object.values(n).forEach(walk);
})(spec);
if (CLEAN && found.length) {
  console.error(`refusing to build a clean copy: ${found.length} placeholder(s) still unfilled.`);
  [...new Set(found)].forEach(p => console.error('  ' + p));
  console.error('Fill them or delete the lines that carry them, then re-run.');
  process.exit(2);
}

// ---- inline markup -----------------------------------------------------
function runs(text, base) {
  const out = [];
  const re = /(==[^=]+==|\[[^\]]+\]|\*\*[^*]+\*\*)/g;
  let last = 0, m;
  const push = (t, extra) => { if (t) out.push(new TextRun({ ...base, ...extra, text: t, font: T.font })); };
  while ((m = re.exec(text)) !== null) {
    push(text.slice(last, m.index));
    const tok = m[0];
    if (tok.startsWith('==')) {
      const inner = tok.slice(2, -2);
      const style = CLEAN ? {} : { highlight: T.highlight };
      out.push(...runs2(inner, { ...base, ...style }));
    } else if (tok.startsWith('[')) {
      push(tok, { color: T.fill, bold: true });
    } else {
      push(tok.slice(2, -2), { bold: true, color: T.ink });
    }
    last = m.index + tok.length;
  }
  push(text.slice(last));
  return out;
}
function runs2(text, base) {           // nested: [placeholder] / **bold** inside ==highlight==
  const out = [];
  const re = /(\[[^\]]+\]|\*\*[^*]+\*\*)/g;
  let last = 0, m;
  const push = (t, extra) => { if (t) out.push(new TextRun({ ...base, ...extra, text: t, font: T.font })); };
  while ((m = re.exec(text)) !== null) {
    push(text.slice(last, m.index));
    const tok = m[0];
    if (tok.startsWith('[')) push(tok, { color: T.fill, bold: true });
    else push(tok.slice(2, -2), { bold: true, color: T.ink });
    last = m.index + tok.length;
  }
  push(text.slice(last));
  return out;
}

// ---- block builders ----------------------------------------------------
const P = {
  name: t => new Paragraph({ spacing: { after: 20 },
    children: [new TextRun({ text: t, bold: true, size: 52, color: T.ink, font: T.font, characterSpacing: 8 })] }),

  title: t => new Paragraph({ spacing: { after: 90 },
    children: runs(t, { size: 22, color: T.accent, characterSpacing: 12 }) }),

  contact: items => new Paragraph({ spacing: { after: 40 },
    children: items.flatMap((raw, i) => {
      const sep = i === 0 ? [] : [new TextRun({ text: '  •  ', size: 18, color: T.rule, font: T.font })];
      const [label, link] = String(raw).split('|');
      if (/[=\[*]/.test(label)) return [...sep, ...runs(label, { size: 19, color: T.slate })];
      const r = new TextRun({ text: label, size: 19, color: T.slate, font: T.font });
      return [...sep, link ? new ExternalHyperlink({ children: [r], link }) : r];
    }) }),

  heading: t => new Paragraph({ spacing: { before: 250, after: 125 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: T.accent, space: 4 } },
    children: runs(t, { bold: true, size: 21, color: T.accent, characterSpacing: 22 }) }),

  body: t => new Paragraph({ spacing: { after: 60, line: 250 },
    children: runs(t, { size: 20, color: T.slate }) }),

  role: (title, org) => new Paragraph({ spacing: { before: 130, after: 10 },
    children: [...runs(title, { bold: true, size: 21, color: T.ink }),
               ...(org ? [new TextRun({ text: '  |  ', size: 21, color: T.rule, font: T.font }),
                          new TextRun({ text: org, size: 21, color: T.accent, font: T.font })] : [])] }),

  meta: t => new Paragraph({ spacing: { after: 70 },
    children: runs(t, { size: 18, color: T.muted, italics: true }) }),

  bullet: t => new Paragraph({ numbering: { reference: 'dots', level: 0 },
    spacing: { after: 55, line: 250 }, children: runs(t, { size: 20, color: T.slate }) }),

  row: (l, v) => new Paragraph({ spacing: { after: 55, line: 250 },
    children: [...runs(l + '  ', { bold: true, size: 20, color: T.ink }),
               ...runs(v, { size: 20, color: T.slate })] }),

  note: t => new Paragraph({ spacing: { before: 60, after: 60, line: 240 },
    children: runs(t, { size: 17, color: T.fill, italics: true }) })
};

// ---- assemble ----------------------------------------------------------
const kids = [];
if (spec.name)  kids.push(P.name(spec.name));
if (spec.title) kids.push(P.title(spec.title));
(spec.contact || []).forEach(line => kids.push(P.contact(line)));

for (const s of (spec.sections || [])) {
  if (s.heading) kids.push(P.heading(s.heading));
  if (s.body)    kids.push(P.body(s.body));
  for (const [l, v] of (s.rows || [])) kids.push(P.row(l, v));
  for (const r of (s.roles || [])) {
    kids.push(P.role(r.title, r.org));
    if (r.meta) kids.push(P.meta(r.meta));
    for (const b of (r.bullets || [])) kids.push(P.bullet(b));
  }
  for (const b of (s.bullets || [])) kids.push(P.bullet(b));
  if (s.note && !CLEAN) kids.push(P.note(s.note));   // working-copy guidance never ships
}

const doc = new Document({
  creator: spec.name || 'Resume',
  title: spec.docTitle || spec.name || 'Resume',
  numbering: { config: [{ reference: 'dots', levels: [{
    level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT,
    style: { paragraph: { indent: { left: 200, hanging: 170 } }, run: { color: T.accent, size: 20 } } }] }] },
  sections: [{ properties: { page: { margin: {
      top: convertInchesToTwip(spec.margin ?? 0.5), bottom: convertInchesToTwip(spec.margin ?? 0.5),
      left: convertInchesToTwip(0.62), right: convertInchesToTwip(0.62) } } }, children: kids }]
});

const base = spec.output || path.join(path.dirname(specPath), 'resume.docx');
const out = outFlag !== -1 ? args[outFlag + 1]
          : CLEAN ? base.replace(/\.docx$/, '_CLEAN.docx') : base;

Packer.toBuffer(doc).then(b => {
  fs.mkdirSync(path.dirname(out), { recursive: true });
  fs.writeFileSync(out, b);
  console.log(`${out}  (${b.length} bytes, ${CLEAN ? 'clean' : 'working'} copy)`);
  if (!CLEAN) console.log(`${new Set(found).size} distinct placeholder(s) to fill.`);
});
