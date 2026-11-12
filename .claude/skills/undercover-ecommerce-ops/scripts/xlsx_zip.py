"""Pembaca xlsx ringan berbasis zipfile + XML (tanpa openpyxl).

Kenapa: openpyxl GAGAL membuka export Shopee ("Value must be one of {bottomLeft...}" pada activePane) dan
lambat untuk sheet TikTok yang XML-nya ~28 MB. Pembaca ini hanya membaca sel (nilai teks/angka sebagai string).

    from xlsx_zip import load_xlsx
    w = load_xlsx(path)                 # {nama_sheet: [(nomor_baris, [nilai kolom A, B, C...]), ...]}
    for r, v in w["Template"]: ...      # v[0] = kolom A; sel kosong = None; baris kosong dilewati

Hanya membaca. Untuk MENGUBAH sel, edit XML mentah (lihat references/workflow-fill-blank-sku.md).
"""
import zipfile, re, xml.etree.ElementTree as ET
NS={"m":"http://schemas.openxmlformats.org/spreadsheetml/2006/main","r":"http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
def col2n(c):
    n=0
    for ch in c: n=n*26+ord(ch)-64
    return n-1
def load_xlsx(path):
    z=zipfile.ZipFile(path)
    ss=[]
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si",NS):
            ss.append("".join(t.text or "" for t in si.iter("{%s}t"%NS["m"])))
    wb=ET.fromstring(z.read("xl/workbook.xml"))
    rels={r.get("Id"):r.get("Target") for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    out={}
    for s in wb.find("m:sheets",NS):
        rid=s.get("{%s}id"%NS["r"]); t=rels[rid]; t=t.lstrip("/"); t=t if t.startswith("xl/") else "xl/"+t
        rows=[]
        for row in ET.fromstring(z.read(t)).iter("{%s}row"%NS["m"]):
            r=int(row.get("r")); cells={}
            for c in row.findall("m:c",NS):
                ref=c.get("r"); ci=col2n(re.match(r"[A-Z]+",ref).group())
                ty=c.get("t"); v=c.find("m:v",NS)
                if ty=="s" and v is not None: val=ss[int(v.text)]
                elif ty=="inlineStr": val="".join(x.text or "" for x in c.iter("{%s}t"%NS["m"]))
                elif v is not None: val=v.text
                else: val=None
                if val not in (None,""): cells[ci]=val
            if cells:
                mx=max(cells); rows.append((r,[cells.get(i) for i in range(mx+1)]))
        out[s.get("name")]=rows
    return out
