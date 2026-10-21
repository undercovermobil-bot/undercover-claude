// Mock minimal SpreadsheetApp untuk menguji Kode.gs di Node.
// Ketat: range di luar ukuran sheet & dimensi setValues salah -> throw (seperti Sheets asli).
'use strict';
const fs = require('fs');
const vm = require('vm');

class Cell { constructor() { this.v = ''; this.f = ''; this.note = ''; this.bg = null; this.fc = null; this.nf = null; this.dv = null; } }

class Sheet {
  constructor(ss, name, rows = 1000, cols = 26) {
    this.ss = ss; this.name = name; this.maxRows = rows; this.maxCols = cols;
    this.cells = new Map(); this.merges = []; this.frozenRows = 0; this.frozenCols = 0; this.protections = [];
  }
  cell(r, c) { const k = r + ',' + c; if (!this.cells.has(k)) this.cells.set(k, new Cell()); return this.cells.get(k); }
  peek(r, c) { return this.cells.get(r + ',' + c); }
  getName() { return this.name; }
  setName(n) { if (this.ss.getSheetByName(n)) throw new Error('nama sheet sudah dipakai ' + n); this.name = n; return this; }
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
  insertRowsBefore(pos, n) {
    if (pos < 1 || pos > this.maxRows) throw new Error('Those rows are out of bounds.');
    const baru = new Map();
    for (const [k, x] of this.cells) { const [r, c] = k.split(',').map(Number); baru.set((r >= pos ? r + n : r) + ',' + c, x); }
    this.cells = baru; this.maxRows += n;
  }
  deleteRows(pos, n) {
    if (pos < 1 || pos + n - 1 > this.maxRows) throw new Error('Those rows are out of bounds.');
    if (this.maxRows - n < this.frozenRows + 1) throw new Error('You cannot delete all the non-frozen rows on a sheet.');
    const baru = new Map();
    for (const [k, x] of this.cells) { const [r, c] = k.split(',').map(Number); if (r >= pos && r < pos + n) continue; baru.set((r >= pos + n ? r - n : r) + ',' + c, x); }
    this.cells = baru; this.maxRows -= n;
  }
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
  canEdit() { return this.bolehEdit !== false; }
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
  tampil(x) {
    const v = x.f ? (x.calc === undefined ? '' : x.calc) : x.v;
    if (typeof v === 'number' && x.nf && /yyyy/.test(x.nf)) return new Date(wallKeInstant(v * 86400000 + Date.UTC(1899, 11, 30), this.sh.ss.tz));
    return v;
  }
  getValues() { const out = []; for (let i = 0; i < this.nr; i++) { const row = []; for (let j = 0; j < this.nc; j++) { const x = this.sh.peek(this.r + i, this.c + j); row.push(x ? this.tampil(x) : ''); } out.push(row); } return out; }
  getValue() { return this.getValues()[0][0]; }
  getFormula() { return this.getFormulas()[0][0]; }
  getFormulas() { const out = []; for (let i = 0; i < this.nr; i++) { const row = []; for (let j = 0; j < this.nc; j++) { const x = this.sh.peek(this.r + i, this.c + j); row.push(x ? x.f : ''); } out.push(row); } return out; }
  setValues(a) { this.dims(a, 'setValues'); return this.each((x, i, j) => { let v = a[i][j]; if (Object.prototype.toString.call(v) === '[object Date]') v = instanKeSerial(v.getTime(), this.sh.ss.tz); if (typeof v === 'string' && v.startsWith('=')) { x.f = v; x.v = ''; } else { x.v = v === null || v === undefined ? '' : v; x.f = ''; } }); }
  setFormulas(a) { this.dims(a, 'setFormulas'); return this.each((x, i, j) => { const f = a[i][j]; if (f && !String(f).startsWith('=')) throw new Error('formula tanpa = : ' + f); x.f = f; x.v = ''; }); }
  setValue(v) { return this.each(x => { if (typeof v === 'string' && v.startsWith('=')) { x.f = v; x.v = ''; } else { x.v = v; x.f = ''; } }); }
  clearContent() { return this.each(x => { x.v = ''; x.f = ''; }); }
  setNote(n) { return this.each(x => { x.note = n || ''; }); }
  getNote() { return this.sh.cell(this.r, this.c).note; }
  getNotes() { const o = []; for (let i = 0; i < this.nr; i++) { const row = []; for (let j = 0; j < this.nc; j++) { const x = this.sh.peek(this.r + i, this.c + j); row.push(x ? x.note : ''); } o.push(row); } return o; }
  setBackground(b) { return this.each(x => { x.bg = b; }); }
  setFontColor(c) { return this.each(x => { x.fc = c; }); }
  getBackground() { return this.sh.cell(this.r, this.c).bg; }
  setDataValidation(dv) { if (dv && dv.galat && dv.galatDi === 'apply') throw dv.galat; return this.each(x => { x.dv = dv; }); }
  merge() { this.sh.merges.push([this.r, this.c, this.nr, this.nc]); return this; }
  setFontWeight() { return this; } setHorizontalAlignment() { return this; } setVerticalAlignment() { return this; }
  setWrap() { return this; }
  setNumberFormat(f) { return this.each(x => { x.nf = f; }); }
  copyTo(tujuan) {
    if (tujuan.nr !== this.nr || tujuan.nc !== this.nc) throw new Error('copyTo: ukuran beda');
    const salinan = [];
    this.each((x, i, j) => salinan.push([i, j, Object.assign(new Cell(), x)]));
    salinan.forEach(([i, j, x]) => { tujuan.sh.cells.set((tujuan.r + i) + ',' + (tujuan.c + j), x); });
    return this;
  }
  clearFormat() { return this.each(x => { x.bg = null; x.fc = null; x.nf = null; }); }
  setBorder(...a) { if (a.length !== 6) throw new Error('setBorder butuh 6 argumen'); return this; }
}

class Spreadsheet {
  constructor() { this.sheets = []; this.toasts = []; this.tz = 'America/Los_Angeles'; }
  getSpreadsheetTimeZone() { return this.tz; }
  setSpreadsheetTimeZone(z) { this.tz = z; }
  getSheetByName(n) { return this.sheets.find(s => s.name === n) || null; }
  getSheets() { return this.sheets.slice(); }
  insertSheet(name, index) {
    if (this.getSheetByName(name)) throw new Error('sheet sudah ada ' + name);
    const s = new Sheet(this, name);
    if (index === undefined) this.sheets.push(s); else this.sheets.splice(index, 0, s);
    return s;
  }
  deleteSheet(s) { this.sheets.splice(this.sheets.indexOf(s), 1); }
  toast(msg, title) { this.toasts.push(title + ': ' + msg); }
  getOwner() { return { getEmail: () => 'owner@x' }; }
}

function tzOffsetMs(ms, tz) {
  const p = {};
  new Intl.DateTimeFormat('en-GB', { timeZone: tz, year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit', hourCycle: 'h23' })
    .formatToParts(new Date(ms)).forEach(x => { p[x.type] = x.value; });
  return Date.UTC(+p.year, +p.month - 1, +p.day, +p.hour, +p.minute, +p.second) - Math.floor(ms / 1000) * 1000;
}
function wallKeInstant(wallMs, tz) { const o = tzOffsetMs(wallMs, tz); return wallMs - tzOffsetMs(wallMs - o, tz); }
function instanKeSerial(ms, tz) { return (ms + tzOffsetMs(ms, tz) - Date.UTC(1899, 11, 30)) / 86400000; }

function colNum(s) { let n = 0; for (const ch of s) n = n * 26 + ch.charCodeAt(0) - 64; return n; }

function buatKonteks(ss, opsi = {}) {
  const alerts = [];
  const triggers = [];
  // opsi.tolakValidasi = { di: 'require' | 'build' | 'apply', formula: f => bool, rentang: bool } mensimulasikan lokal file yang menolak
  // rumus validasi (mis. id_ID: pemisah argumen titik koma, rumus berkoma ditolak Google dengan "Argumen aturan validasi data ... tidak valid").
  const dvBuilder = () => {
    const o = { f: null, angka: null, help: '', invalid: true };
    const tolak = (isi, salah) => {
      const t = opsi.tolakValidasi;
      if (!t || !salah) return;
      const e = new Error('Argumen aturan validasi data "' + isi + '" tidak valid.');
      if ((t.di || 'apply') === 'require') throw e;
      o.galat = e; o.galatDi = t.di || 'apply';
    };
    const b = {
      requireFormulaSatisfied(f) { o.f = f; tolak(f, opsi.tolakValidasi && opsi.tolakValidasi.formula && opsi.tolakValidasi.formula(f)); return b; },
      requireNumberBetween(a, z) { o.angka = [a, z]; tolak(a + '..' + z, opsi.tolakValidasi && opsi.tolakValidasi.rentang); return b; },
      setAllowInvalid(x) { o.invalid = x; return b; }, setHelpText(h) { o.help = h; return b; },
      build() { if (o.galat && o.galatDi === 'build') throw o.galat; return o; },
    };
    return b;
  };
  const ui = {
    ButtonSet: { YES_NO: 'YES_NO', OK: 'OK' }, Button: { YES: 'YES', NO: 'NO' },
    alert(...a) { alerts.push(a.filter(x => typeof x === 'string' && !['YES_NO', 'OK'].includes(x)).join(' | ')); if (opsi.saatAlert) opsi.saatAlert(a); return opsi.jawab || 'YES'; },
    createMenu() { const m = { addItem: () => m, addSeparator: () => m, addToUi: () => m }; return m; },
  };
  const ctx = {
    console,
    SpreadsheetApp: {
      getActiveSpreadsheet: () => ss, getActive: () => ss, getUi: () => ui, flush() { ctx.__flush = (ctx.__flush || 0) + 1; },
      newDataValidation: dvBuilder, ProtectionType: { SHEET: 'SHEET', RANGE: 'RANGE' },
    },
    LockService: { getDocumentLock: () => ({ tryLock: () => (opsi.lockGagal ? false : true), releaseLock() {} }) },
    Utilities: {
      sleep() { ctx.__sleep = (ctx.__sleep || 0) + 1; },
      formatDate(d, tz, fmt) {
        const p = {};
        new Intl.DateTimeFormat('en-GB', { timeZone: tz, year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit', hourCycle: 'h23' })
          .formatToParts(d).forEach(x => { p[x.type] = x.value; });
        return fmt.replace('yyyy', p.year).replace('MM', p.month).replace('dd', p.day).replace('HH', p.hour).replace('mm', p.minute).replace('ss', p.second);
      },
    },
    Session: { getEffectiveUser: () => ({ getEmail: () => 'owner@x' }), getActiveUser: () => ({ getEmail: () => '' }) },
    ScriptApp: {
      getProjectTriggers: () => triggers.slice(),
      newTrigger(fn) { const t = { getHandlerFunction: () => fn }; const b = { forSpreadsheet: () => b, onEdit: () => b, timeBased: () => b, everyMinutes: n => { t.menit = n; return b; }, everyDays: n => { t.hari = n; return b; }, atHour: h => { t.jam = h; return b; }, nearMinute: m => { t.nearMenit = m; return b; }, inTimezone: z => { t.zona = z; return b; }, create: () => { triggers.push(t); return t; } }; return b; },
      deleteTrigger(t) { triggers.splice(triggers.indexOf(t), 1); },
    },
  };
  vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(opsi.kode, 'utf8') + '\n;globalThis.__KONFIG = KONFIG;', ctx, { filename: 'Kode.gs' });
  ctx.__alerts = alerts; ctx.__triggers = triggers; ctx.__opsi = opsi;
  return ctx;
}

module.exports = { Spreadsheet, Sheet, Range, buatKonteks, colNum };
