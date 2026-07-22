@echo off
setlocal enabledelayedexpansion
title Matriks Mobil Terlaris

echo ============================================================
echo   MATRIKS MOBIL TERLARIS - Top 300 (Detail Gen ^& Warna)
echo ============================================================
echo.
echo Script ini TIDAK butuh install apa pun (tidak pakai pip).
echo Cuma butuh Python biasa.
echo.

set /p FOLDER="Masukkan path folder data sales (Enter = C:\Users\OWNER\Downloads\Sales): "
if "%FOLDER%"=="" set FOLDER=C:\Users\OWNER\Downloads\Sales

where python >nul 2>nul
if %errorlevel%==0 (
    set PYCMD=python
) else (
    where py >nul 2>nul
    if %errorlevel%==0 (
        set PYCMD=py
    ) else (
        echo.
        echo [ERROR] Python tidak ditemukan di komputer ini.
        echo Install dulu: buka Microsoft Store, cari "Python 3", install ^(gratis^).
        echo Setelah itu jalankan file ini lagi.
        echo.
        pause
        exit /b 1
    )
)

echo.
echo Memproses folder: %FOLDER%
echo Memakai: %PYCMD%
echo.
"%PYCMD%" "%~dp0buat_matriks_terlaris.py" "%FOLDER%"

echo.
echo ============================================================
echo Selesai. Cek file MOBIL_TERLARIS_DETAIL_Gen_Warna.xlsx
echo di folder tempat file .bat ini berada.
echo ============================================================
pause
