"""Evaluasi rumus (pola terbatas yg dipakai di workbook ini) dari TEKS rumusnya sendiri,
lalu tanam hasilnya sbg cached value <v> di XML — pengganti recalc LibreOffice yg rusak."""
import re, sys, zipfile, shutil
from lxml import etree
import openpyxl
from openpyxl.utils import range_boundaries, column_index_from_string

path = sys.argv[1]
wb = openpyxl.load_workbook(path)
memo = {}

def ref(sheet, coord):
    coord = coord.replace('$', '')
    key = (sheet, coord)
    if key in memo: return memo[key]
    v = wb[sheet][coord].value
    if isinstance(v, str) and v.startswith('='):
        v = evaluate(sheet, v[1:])
    memo[key] = v
    return v

def rng(sheet, text):
    if '!' in text:
        sh, a = text.rsplit('!', 1); sheet = sh.strip("'")
    else:
        a = text
    c1, r1, c2, r2 = range_boundaries(a.replace('$', ''))
    return [ref(sheet, f"{openpyxl.utils.get_column_letter(c)}{r}") for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)]

def operand(sheet, t):
    t = t.strip()
    if t.startswith('"'): return t.strip('"')
    if re.fullmatch(r'-?\d+(\.\d+)?', t): return float(t)
    if '!' in t:
        sh, a = t.rsplit('!', 1); return ref(sh.strip("'"), a)
    return ref(sheet, t)

def split_args(s):
    out, depth, cur, q = [], 0, '', False
    for ch in s:
        if ch == '"': q = not q
        if not q and ch == '(': depth += 1
        if not q and ch == ')': depth -= 1
        if ch == ',' and depth == 0 and not q:
            out.append(cur); cur = ''
        else:
            cur += ch
    out.append(cur)
    return out

def num(x): return 0 if x is None else x

def evaluate(sheet, f):
    m = re.fullmatch(r'(SUMIFS|COUNTIFS|SUM|IF)\((.*)\)', f)
    if m:
        fn, args = m.group(1), split_args(m.group(2))
        if fn == 'SUM':
            return sum(num(v) for v in rng(sheet, args[0]) if isinstance(v, (int, float)) or v is None)
        if fn == 'SUMIFS':
            vals, crit_r, crit = rng(sheet, args[0]), rng(sheet, args[1]), operand(sheet, args[2])
            return sum(num(v) for v, k in zip(vals, crit_r) if str(k).lower() == str(crit).lower())
        if fn == 'COUNTIFS':
            crit_r, crit = rng(sheet, args[0]), operand(sheet, args[1])
            return sum(1 for k in crit_r if str(k).lower() == str(crit).lower())
        if fn == 'IF':
            cm = re.fullmatch(r'(.+?)(<=|>=|<|>|=)(.+)', args[0])
            a, op, b = operand(sheet, cm.group(1)), cm.group(2), operand(sheet, cm.group(3))
            ok = {'<=': a <= b, '>=': a >= b, '<': a < b, '>': a > b, '=': a == b}[op]
            return operand(sheet, args[1] if ok else args[2])
    m = re.fullmatch(r'([^/\-]+)([/\-])(.+)', f)
    if m:
        a, b = num(operand(sheet, m.group(1))), num(operand(sheet, m.group(3)))
        return a / b if m.group(2) == '/' else a - b
    raise ValueError(f"pola rumus tidak dikenal: {sheet} ={f}")

# hitung semua sel rumus
results = {}
for ws in wb.worksheets:
    for row in ws.iter_rows():
        for c in row:
            if isinstance(c.value, str) and c.value.startswith('='):
                results[(ws.title, c.coordinate)] = ref(ws.title, c.coordinate)
print("rumus dievaluasi:", len(results))

# peta nama sheet -> file xml
z = zipfile.ZipFile(path)
ns = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
wbx = etree.fromstring(z.read('xl/workbook.xml'))
rels = etree.fromstring(z.read('xl/_rels/workbook.xml.rels'))
rid2t = {r.get('Id'): r.get('Target') for r in rels}
name2xml = {}
for s in wbx.find('m:sheets', ns):
    t = rid2t[s.get('{%s}id' % ns['r'])]
    name2xml[s.get('name')] = 'xl/' + t.lstrip('/').replace('xl/', '') if not t.startswith('/xl/') else t.lstrip('/')

tmp = path + '.tmp'
zout = zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED)
xml2name = {v: k for k, v in name2xml.items()}
n_set = 0
for item in z.infolist():
    data = z.read(item.filename)
    if item.filename in xml2name:
        sh = xml2name[item.filename]
        root = etree.fromstring(data)
        for c in root.iter('{%s}c' % ns['m']):
            fnode = c.find('m:f', ns)
            if fnode is None: continue
            val = results[(sh, c.get('r'))]
            v = c.find('m:v', ns)
            if v is None:
                v = etree.SubElement(c, '{%s}v' % ns['m'])
            if isinstance(val, str):
                c.set('t', 'str'); v.text = val
            else:
                c.attrib.pop('t', None); v.text = repr(float(val)) if isinstance(val, float) else str(val)
            n_set += 1
        data = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
    zout.writestr(item, data)
zout.close(); z.close()
shutil.move(tmp, path)
print("cached value ditanam:", n_set)
