// Dokumen Word "Daftar 100 Produk Terlaris" utk tim produksi: 1 nomor = 1 cover (SKU), nama mobil kembar ditulis semua.
// Input JSON [{no, names[], unit}] dibuat dari sheet "Top 100 per SKU" RANKING_TOP100_PER_SKU.xlsx (kolom B dipecah " / ",
// buang label "(listing gabungan)", ganti label Rocky). Butuh `npm install docx`.
// Pemakaian: node build_docx_top100_produksi.js top100_names.json output.docx
const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, AlignmentType,
        ShadingType, BorderStyle, Header, Footer, PageNumber, LevelFormat, VerticalAlign } = require('docx');

const FIX = { 'Datsun GO': 'Datsun Go', 'Hyundai Avega': 'Hyundai Avega (Sedan)' };
const data = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'))
  .map(d => ({ ...d, names: d.names.map(n => FIX[n] || n) }));
const nNama = data.reduce((a, d) => a + d.names.length, 0);

const FONT = 'Arial';
const W = [900, 6538, 2200];            // total 9638 = A4 (11906) - margin 2 x 1134
const TOTAL = W.reduce((a, b) => a + b, 0);
const grid = { style: BorderStyle.SINGLE, size: 4, color: 'BFBFBF' };
const borders = { top: grid, bottom: grid, left: grid, right: grid };
const HEAD_FILL = '1F4E78', TWIN_FILL = 'E2EFDA';

const p = (text, opt = {}) => new Paragraph({ spacing: { after: opt.after ?? 120 }, alignment: opt.align,
  children: [new TextRun({ text, font: FONT, size: opt.size ?? 22, bold: opt.bold, color: opt.color, italics: opt.italics })] });

function cell(children, width, fill, align) {
  return new TableCell({
    width: { size: width, type: WidthType.DXA }, borders, verticalAlign: VerticalAlign.CENTER,
    shading: fill ? { type: ShadingType.CLEAR, color: 'auto', fill } : undefined,
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
    children: children.map(c => typeof c === 'string'
      ? new Paragraph({ alignment: align, children: [new TextRun({ text: c, font: FONT, size: 20 })] }) : c),
  });
}
const headCell = (t, w) => cell([new Paragraph({ alignment: AlignmentType.CENTER,
  children: [new TextRun({ text: t, font: FONT, size: 20, bold: true, color: 'FFFFFF' })] })], w, HEAD_FILL);

const rows = [new TableRow({ tableHeader: true, children: [
  headCell('No', W[0]), headCell('Nama Produk (Mobil)', W[1]), headCell('Terjual 1 Apr–16 Sep 2026 (unit)', W[2]) ] })];
for (const d of data) {
  const twin = d.names.length > 1;
  const fill = twin ? TWIN_FILL : undefined;
  const names = d.names.map((n, i) => new Paragraph({ spacing: { after: i < d.names.length - 1 ? 40 : 0 },
    children: [new TextRun({ text: n, font: FONT, size: 20, bold: twin && i === 0 })] }));
  rows.push(new TableRow({ cantSplit: true, children: [
    cell([String(d.no)], W[0], fill, AlignmentType.CENTER),
    cell(names, W[1], fill),
    cell([d.unit.toLocaleString('id-ID')], W[2], fill, AlignmentType.CENTER) ] }));
}

const bullet = (t) => new Paragraph({ numbering: { reference: 'poin', level: 0 }, spacing: { after: 80 },
  children: [new TextRun({ text: t, font: FONT, size: 21 })] });

const doc = new Document({
  styles: { default: { document: { run: { font: FONT, size: 22 } } } },
  numbering: { config: [{ reference: 'poin', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•',
    alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 270 } } } }] }] },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } } },
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT,
      children: [new TextRun({ text: 'Undercover Autocare — Daftar 100 Produk Terlaris (Q3 2026)', font: FONT, size: 16, color: '808080' })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
      children: [new TextRun({ children: ['Halaman ', PageNumber.CURRENT, ' dari ', PageNumber.TOTAL_PAGES], font: FONT, size: 16, color: '808080' })] })] }) },
    children: [
      p('Daftar 100 Produk Terlaris', { size: 36, bold: true, after: 60 }),
      p('Acuan produksi cover mobil — Undercover Autocare', { size: 24, color: '404040', after: 240 }),
      p('Cara membaca daftar ini', { size: 24, bold: true, after: 100 }),
      bullet('Satu nomor = satu jenis cover (pola sama). Totalnya 100 cover.'),
      bullet(`Nomor yang berisi lebih dari satu nama mobil (baris hijau) memakai cover yang sama, karena mobilnya kembar. Contoh: Toyota Avanza, Daihatsu Xenia, dan Toyota Veloz memakai satu cover yang sama. Karena itu 100 cover ini mencakup ${nNama} nama mobil (Daihatsu Rocky terhitung dua kali, lihat poin berikut).`),
      bullet('Daihatsu Rocky muncul di dua nomor karena modelnya beda: Rocky 2019 ke atas memakai cover Toyota Raize (No. 15), sedangkan Rocky lama (F70/F300) memakai cover Daihatsu Feroza (No. 33).'),
      bullet('Berlaku untuk semua tipe cover mobil tersebut (Reguler, Premium, Exclusive).'),
      bullet('Urutan berdasarkan jumlah terjual 1 April – 16 September 2026, gabungan toko Undercover Autocare, Otonation, Otoprotection, dan Smartprotection (Shopee & TikTok/Tokopedia). Daftar ini dievaluasi ulang setiap kuartal.'),
      new Paragraph({ spacing: { after: 200 }, children: [] }),
      new Table({ width: { size: TOTAL, type: WidthType.DXA }, columnWidths: W, rows }),
      new Paragraph({ spacing: { before: 200, after: 0 }, children: [new TextRun({
        text: `Total terjual 100 produk ini: ${data.reduce((a, d) => a + d.unit, 0).toLocaleString('id-ID')} unit (95,5% dari seluruh penjualan cover mobil pada periode tersebut).`,
        font: FONT, size: 20, italics: true, color: '404040' })] }),
    ],
  }],
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync(process.argv[3], b); console.log('ok', process.argv[3], 'nama', nNama); });
