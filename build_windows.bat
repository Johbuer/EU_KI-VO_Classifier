@echo off
title EU AI Act Compliance Classifier - Compiler
echo ========================================================
echo   Kompiliere eigenstaendige Windows-Anwendung...
echo ========================================================
echo.

:: Prüfe virtuelle Umgebung
if not exist .venv (
    echo [INFO] Virtuelle Umgebung (.venv) fehlt. Erstelle venv...
    python -m venv .venv
)

echo Aktiviere virtuelle Umgebung...
call .venv\Scripts\activate.bat

echo Installiere Voraussetzungen...
pip install -r requirements.txt
pip install pyinstaller

echo.
echo Starte PyInstaller Kompilierung...
echo (Dies kann 1-2 Minuten dauern, bitte warten...)
echo.

pyinstaller --clean --noconfirm --onefile --name="EU_AI_Act_Classifier" --collect-all streamlit --collect-all fpdf2 --add-data "app.py;." --add-data "src;src" --add-data ".streamlit;.streamlit" run_app.py

if %errorlevel% equ 0 (
    echo.
    echo ========================================================
    echo   Kompilierung ERFOLGREICH!
    echo   Die fertige Anwendung (.exe) befindet sich im Ordner:
    echo   %cd%\dist\EU_AI_Act_Classifier.exe
    echo ========================================================
) else (
    echo.
    echo [FEHLER] Kompilierung fehlgeschlagen!
)

echo.
pause
