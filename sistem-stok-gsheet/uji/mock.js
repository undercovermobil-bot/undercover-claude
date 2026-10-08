// Mock minimal SpreadsheetApp untuk menguji Kode.gs di Node.
// Ketat: range di luar ukuran sheet & dimensi setValues salah -> throw (seperti Sheets asli).
'use strict';
const fs = require('fs');
const vm = require('vm');

class Cell { constructor() { this.v = ''; this.f = ''; this.note = ''; this.bg = null; this.dv = null; } }

class Sheet {
  constructor(ss, name, rows = 1000, cols = 26) {
    this.ss = ss; this.name = name; this.maxRows = rows; this.maxCols = cols;
    this.cells = new Map(); this.merges = []; this.frozenRows = 0; this.frozenCols = 0; this.protections = [];
  }
  cell(r, c) { const k = r + ',' + c; if (!this.cells.has(k)) this.cells.set(k, new Cell()); return this.cells.get(k); }
  peek(r, c) { return this.cells.get(r + ',' + c); }
  getName() { return this.name; }
  getIndex() { return this.ss.sheets.indexOf(this) + 1; }
  getRange(a, b, c, d) {
    if (typeof a === 'string') {
      const m = a.match(/^([A-Z]+):([A-Z]+)$/);
      if (!m) throw new Error('A1 notation tidak didukung mock: ' + a);
      const c1 = colNum(m[1]), c2 = colNum(m[2]);
      return new Range(this, 1, c1, this.maxRows, c2 - c1 + 1);
    }
    return new Range(this, a, b, c === undefined ? 1 : c, d === undefined ? 1 : d);
  }
  getLastRow() { let m = 0; for (const [k, x] of this.cells) if (x.v !== '' || x.f !== '') m = Math.max(m, +k.split(',')[0]); return m; }
  getLastColumn() { let m = 0; for (const [k, x] of this.cells) if (x.v !== '' || x.f !== '') m = Math.max(m, +k.split(',')[1]); return m; }
  getMaxRows() { return this.maxRows; }
  getMaxColumns() { return this.maxCols; }
  insertRowsAfter(after, n) { this.maxRows += n; }
  insertColumnsAfter(after, n) { this.maxCols += n; }
  setFrozenRows(n) { this.frozenRows = n; }
  setFrozenColumns(n) { this.frozenCols = n; }
  setColumnWidth() {}
  setColumnWidths() {}
  protect() { const p = new Protection(); this.protections.push(p); return p; }
  getProtections() { return this.protections.slice(); }
}

class Protection {
  constructor() { this.desc = ''; this.unprot = []; this.editors = ['owner@x', 'staf@x']; }
  setDescription(d) { this.desc = d; return this; }
  getDescription() { return this.desc; }
  setUnprotectedRanges(r) { this.unprot = r; return this; }
  addEditor(u) { const e = u.getEmail(); if (!this.editors.includes(e)) this.editors.push(e); return this; }
  getEditors() { return this.editors.map(e => ({ getEmail: () => e })); }
  removeEditors(list) { const rm = list.map(u => u.getEmail()); this.editors = this.editors.filter(e => !rm.includes(e) || e === 'owner@x'); return this; }
  canDomainEdit() { return false; }
  setDomainEdit() { return this; }
  remove() { this.removed = true; }
}

class Range {
  constructor(sh, r, c, nr, nc) {
    if (r < 1 || c < 1 || nr < 1 || nc < 1) throw new Error(`Range tidak valid ${r},${c},${nr},${nc}`);
    if (r + nr - 1 > sh.maxRows || c + nc - 1 > sh.maxCols)
      throw new Error(`Range di luar ukuran sheet "${sh.name}" (${r},${c},${nr},${nc}) max ${sh.maxRows}x${sh.maxCols}`);
    Object.assign(this, { sh, r, c, nr, nc });
  }
  each(fn) { for (let i = 0; i < this.nr; i++) for (let j = 0; j < this.nc; j++) fn(this.sh.cell(this.r + i, this.c + j), i, j); return this; }
  dims(arr, what) {
    if (!Array.isArray(arr) || arr.length !== this.nr || arr.some(x => !Array.isArray(x) || x.length !== this.nc))
      throw new Error(`${what}: dimensi ${arr.length}x${arr[0] && arr[0].length} != range ${this.nr}x${this.nc}`);
  }
  getRow() { return this.r; } getColumn() { return this.c; }
  getNumRows() { return this.nr; } getNumColumns() { return this.nc; }
  getSheet() { return this.sh; }
  getValues() { const out = []; for (let i = 0; i < this.nr; i++) { const row = []; for (let j = 0; j < this.nc; j++) { const x = this.sh.peek(this.r + i, this.c + j); row.push(x ? (x.f ? (x.calc === undefined ? '' : x.calc) : x.v) : ''); } out.push(row); } return out; }
  getValue() { return this.getValues()[0][0]; }
  getFormulas() { const out = []; for (let i = 0; i < this.nr; i++) { const row = []; for (let j = 0; j < this.nc; j++) { const x = this.sh.peek(this.r + i, this.c + j); row.push(x ? x.f : ''); } out.push(row); } return out; }
  setValues(a) { this.dims(a, 'setValues'); return this.each((x, i, j) => { const v = a[i][j]; if (typeof v === 'string' && v.startsWith('=')) { x.f = v; x.v = ''; } else { x.v = v === null || v === undefined ? '' : v; x.f = ''; } }); }
  setFormulas(a) { this.dims(a, 'setFormulas'); return this.each((x, i, j) => { const f = a[i][j]; if (f && !String(f).startsWith('=')) throw new Error('formula tanpa = : ' + f); x.f = f; x.v = ''; }); }
  setValue(v) { return this.each(x => { if (typeof v === 'string' && v.startsWith('=')) { x.f = v; x.v = ''; } else { x.v = v; x.f = ''; } }); }
  clearContent() { return this.each(x => { x.v = ''; x.f = ''; }); }
  setNote(n) { return this.each(x => { x.note = n || ''; }); }
  getNote() { return this.sh.cell(this.r, this.c).note; }
  setBackground(b) { return this.each(x => { x.bg = b; }); }
  getBackground() { return this.sh.cell(this.r, this.c).bg; }
  setDataValidation(dv) { return this.each(x => { x.dv = dv; }); }
  merge() { this.sh.merges.push([this.r, this.c, this.nr, this.nc]); return this; }
  setFontWeight() { return this; } setHorizontalAlignment() { return this; } setVerticalAlignment() { return this; }
  setWrap() { return this; } setNumberFormat() { return this; }
  setBorder(...a) { if (a.length !== 6) throw new Error('setBorder butuh 6 argumen'); return this; }
}

class Spreadsheet {
  constructor() { this.sheets = []; this.toasts = []; }
  getSheetByName(n) { return this.sheets.find(s => s.name === n) || null; }
  insertSheet(name, index) {
    if (this.getSheetByName(name)) throw new Error('sheet sudah ada ' + name);
    const s = new Sheet(this, name);
    if (index === undefined) this.sheets.push(s); else this.sheets.splice(index, 0, s);
    return s;
  }
  toast(msg, title) { this.toasts.push(title + ': ' + msg); }
  getOwner() { return { getEmail: () => 'owner@x' }; }
}

function colNum(s) { let n = 0; for (const ch of s) n = n * 26 + ch.charCodeAt(0) - 64; return n; }

function buatKonteks(ss, opsi = {}) {
  const alerts = [];
  const triggers = [];
  const dvBuilder = () => { const o = { f: null, help: '', invalid: true }; const b = {
    requireFormulaSatisfied(f) { o.f = f; return b; }, setAllowInvalid(x) { o.invalid = x; return b; },
    setHelpText(h) { o.help = h; return b; }, build() { return o; } }; return b; };
  const ui = {
    ButtonSet: { YES_NO: 'YES_NO', OK: 'OK' }, Button: { YES: 'YES', NO: 'NO' },
    alert(...a) { alerts.push(a.filter(x => typeof x === 'string' && !['YES_NO', 'OK'].includes(x)).join(' | ')); return opsi.jawab || 'YES'; },
    createMenu() { const m = { addItem: () => m, addSeparator: () => m, addToUi: () => m }; return m; },
  };
  const ctx = {
    console,
    SpreadsheetApp: {
      getActiveSpreadsheet: () => ss, getActive: () => ss, getUi: () => ui, flush() { ctx.__flush = (ctx.__flush || 0) + 1; },
      newDataValidation: dvBuilder, ProtectionType: { SHEET: 'SHEET', RANGE: 'RANGE' },
    },
    LockService: { getDocumentLock: () => ({ tryLock: () => (opsi.lockGagal ? false : true), releaseLock() {} }) },
    Session: { getEffectiveUser: () => ({ getEmail: () => 'owner@x' }), getActiveUser: () => ({ getEmail: () => '' }) },
    ScriptApp: {
      getProjectTriggers: () => triggers.slice(),
      newTrigger(fn) { const t = { getHandlerFunction: () => fn }; const b = { forSpreadsheet: () => b, onEdit: () => b, create: () => { triggers.push(t); return t; } }; return b; },
      deleteTrigger(t) { triggers.splice(triggers.indexOf(t), 1); },
    },
  };
  vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(opsi.kode, 'utf8') + '\n;globalThis.__KONFIG = KONFIG;', ctx, { filename: 'Kode.gs' });
  ctx.__alerts = alerts; ctx.__triggers = triggers;
  return ctx;
}

module.exports = { Spreadsheet, Sheet, Range, buatKonteks, colNum };
