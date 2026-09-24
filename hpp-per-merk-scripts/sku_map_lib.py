import glob, os, re, sys, pickle
from collections import defaultdict, Counter
sys.path.insert(0, "/home/user/undercover-claude/hpp-per-merk-scripts")
from update_harga_per_sku import urai_sku, resolve_cols, cari_sheet, deteksi_channel, STARTROW
import openpyxl

S = os.environ.get("KERJA_DIR", ".")  # folder berisi listing hasil repair_xlsx.py (ua_reguler_fix/, ua_tiktok_lazada_fix/, sp_src/, op_src/, ...)
TIER = r'(reguler|premium|exclusive|exxclusive|transparan|semi outdoor|extreme outdoor|indoor dan outdoor|outdoor)'

def base_name(nm):
    s = str(nm or '')
    s = re.sub(r'under\w*\s*autocare|autocare\s*undercover', '', s, flags=re.I)
    s = re.sub(r'body\s+cover\s+mobil\s*/\s*sarung\s*/\s*selimut\s+mobil', '', s, flags=re.I)
    s = re.sub(r'(body\s+)?cover\s+mobil\s*(/\s*selimut\s+mobil)?', '', s, flags=re.I)
    s = re.sub(r'selimut\s+mobil|sarung\s+mobil', '', s, flags=re.I)
    s = s.strip(' -/')
    s = re.sub(r'\b' + TIER + r'\b.*$', '', s, flags=re.I)
    return s.strip(' -/')

def norm(s):
    return re.sub(r'[^a-z0-9]', '', str(s or '').lower())

UA_FILES = sorted(glob.glob(f"{S}/ua_reguler_fix/*.xlsx")) + sorted(glob.glob(f"{S}/ua_tiktok_lazada_fix/*.xlsx"))
SPOP_FILES = (sorted(glob.glob(f"{S}/sp_src/*.xlsx")) + sorted(glob.glob(f"{S}/op_src/*.xlsx"))
              + [f"{S}/op_tiktok1_src.xlsx", f"{S}/op_tiktok2_src.xlsx", f"{S}/lazada_src.xlsx",
                 f"{S}/sp_tiktok_fix/sp_tiktok.xlsx"])

def build(files):
    m = defaultdict(Counter)
    raw = defaultdict(Counter)
    for path in files:
        try:
            wb = openpyxl.load_workbook(path, data_only=True)
        except Exception as e:
            print("SKIP", path, e); continue
        ch = deteksi_channel(wb)
        if not ch: continue
        ws = cari_sheet(wb, ch)
        try:
            col = resolve_cols(ws, ch)
        except SystemExit as e:
            print("SKIP cols", path, e); continue
        for r in range(STARTROW[ch], ws.max_row + 1):
            nm = ws.cell(r, col['nama']).value
            pfx, kat = urai_sku(ws.cell(r, col['sku']).value)
            if not pfx: continue
            b = norm(base_name(nm))
            if b:
                m[b][pfx] += 1
                raw[b][str(nm)] += 1
    return m, raw

if __name__ == '__main__':
    ua, ua_raw = build(UA_FILES)
    spop, spop_raw = build(SPOP_FILES)
    pickle.dump({'ua': ua, 'spop': spop, 'ua_raw': ua_raw, 'spop_raw': spop_raw}, open(f"{S}/sku_map.pkl", "wb"))
    print("UA names:", len(ua), " SP/OP names:", len(spop))
