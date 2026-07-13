"""
auth.py — Tangkap sesi login Shopee sekali, simpan untuk dipakai ulang.

Shopee menolak hasil pencarian untuk sesi anonim (error 90309999 + login wall).
Jalankan `python main.py login` -> jendela browser terbuka -> login manual
(QR / password / OTP). Skrip MENDETEKSI login otomatis (cek cookie sesi) lalu
menyimpan ke config.SHOPEE_STORAGE_STATE. Tidak perlu menekan apa pun.

Catatan: sesi bisa kadaluarsa (beberapa hari–minggu). Jika scraping mulai kena
login wall lagi, jalankan ulang `python main.py login`.
"""
from __future__ import annotations

import time

import config
from utils import get_logger

log = get_logger("auth")

_STEALTH = "Object.defineProperty(navigator,'webdriver',{get:()=>undefined});"
# Cookie yang muncul/berubah setelah login berhasil.
_LOGIN_COOKIES = {"SPC_ST", "SPC_SC_SESSION", "SPC_EC"}
_LOGIN_WAIT_SECONDS = 240   # batas tunggu login manual
_POLL_INTERVAL = 3


def _is_logged_in(cookies: list[dict]) -> bool:
    by_name = {c["name"]: c.get("value", "") for c in cookies}
    if _LOGIN_COOKIES & set(by_name):
        return True
    # SPC_U = id user; bernilai "-1" saat anonim.
    return by_name.get("SPC_U", "-1") not in {"-1", ""}


def capture_login() -> bool:
    from camoufox.sync_api import Camoufox

    saved = False
    with Camoufox(headless=False, locale=["id-ID", "en-US"]) as browser:
        ctx = browser.new_context(viewport={"width": 1366, "height": 900})
        page = ctx.new_page()

        log.info("Membuka halaman login Shopee (Firefox stealth)...")
        page.goto(f"{config.SHOPEE_BASE_URL}/buyer/login", wait_until="domcontentloaded")

        print("\n" + "=" * 64)
        print("  LOGIN MANUAL di jendela Firefox yang terbuka.")
        print("  Skrip otomatis mendeteksi & menyimpan sesi setelah login.")
        print(f"  Batas waktu: {_LOGIN_WAIT_SECONDS} detik.")
        print("=" * 64, flush=True)

        deadline = time.time() + _LOGIN_WAIT_SECONDS
        while time.time() < deadline:
            try:
                if _is_logged_in(ctx.cookies()):
                    config.SHOPEE_STORAGE_STATE.parent.mkdir(parents=True, exist_ok=True)
                    ctx.storage_state(path=str(config.SHOPEE_STORAGE_STATE))
                    saved = True
                    log.info("Login terdeteksi. Sesi disimpan -> %s",
                             config.SHOPEE_STORAGE_STATE)
                    break
            except Exception:
                pass
            time.sleep(_POLL_INTERVAL)

    if saved:
        print(f"\n✓ Sesi tersimpan di {config.SHOPEE_STORAGE_STATE}")
        print("  Lanjut: python main.py discover")
    else:
        print("\n✗ Login tidak terdeteksi dalam batas waktu. Coba lagi: python main.py login")
    return saved


if __name__ == "__main__":
    capture_login()
