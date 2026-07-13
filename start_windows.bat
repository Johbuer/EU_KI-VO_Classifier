@echo off
title EU AI Act Compliance Classifier
echo ========================================================
echo   Starte EU AI Act Compliance Classifier...
echo ========================================================
echo.

:: Prüfe, ob Python installiert ist
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [FEHLER] Python wurde auf diesem System nicht gefunden!
    echo Bitte installiere Python 3.10 oder neuer von: https://www.python.org/
    echo Achte darauf, bei der Installation "Add Python to PATH" anzuhaken.
    echo.
    pause
    exit /b 1
)

:: Erstelle venv, falls nicht vorhanden
if not exist .venv (
    echo Erstelle virtuelle Umgebung (.venv)...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [FEHLER] Erstellung der virtuellen Umgebung fehlgeschlagen!
        pause
        exit /b 1
    )
)

:: Aktiviere venv und installiere requirements
echo Aktiviere virtuelle Umgebung und pruefe Pakete...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip >nul 2>nul
echo Installiere/Aktualisiere requirements.txt...
pip install -r requirements.txt

:: Starte App
echo.
echo ========================================================
echo   Die Anwendung wird im Browser geoeffnet.
echo   Schliesse dieses Fenster nicht, solange du arbeitest.
echo ========================================================
echo.
streamlit run app.py

pause
