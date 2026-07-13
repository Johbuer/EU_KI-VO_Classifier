# EU AI Act Compliance Classifier

Dieses Tool klassifiziert KI-Systeme nach der neuen EU-KI-Verordnung (EU AI Act). Es ermittelt die Risikoklasse sowie die geltenden Pflichten und Rechte.

---

## 1. Starten der Anwendung (Plattformuebergreifend)

Die Anwendung laeuft lokal im Webbrowser. Es ist keine manuelle Einrichtung von Python-Umgebungen oder Paketinstallationen erforderlich. Das Startskript uebernimmt dies vollautomatisch.

### Windows
- Mache einfach einen **Doppelklick** auf die Datei [start_windows.bat](file:///start_windows.bat).
- Ein Terminal oeffnet sich, richtet die Python-Pakete ein und startet das Tool im Webbrowser.

### macOS (MacBook)
- Oeffne das Terminal im Projektverzeichnis.
- Mache die Datei ausführbar (einmalig nötig):
  ```bash
  chmod +x start_mac.sh
  ```
- Starte das Skript mit:
  ```bash
  ./start_mac.sh
  ```

---

## 2. Kompilieren zu einer eigenständigen Anwendung

Wenn du die Anwendung weitergeben oder nutzen moechtest, ohne dass Python auf dem Zielsystem installiert sein muss, kannst du sie zu einer eigenständigen ausführbaren Datei (Executable) kompilieren.

*Hinweis: Windows-Executables (`.exe`) koennen nur auf Windows gebaut werden; macOS-Anwendungen nur auf macOS.*

### Windows (Erzeugt `.exe`)
- Mache einen **Doppelklick** auf [build_windows.bat](file:///build_windows.bat).
- Nach Abschluss der Kompilierung befindet sich die eigenständige Datei im neu erstellten Ordner: `dist\EU_AI_Act_Classifier.exe`.

### macOS (Erzeugt alleinstehende Mac-App)
- Oeffne das Terminal im Projektverzeichnis.
- Mache das Build-Skript ausfuehrbar:
  ```bash
  chmod +x build_mac.sh
  ```
- Starte das Skript:
  ```bash
  ./build_mac.sh
  ```
- Die fertige App befindet sich im Ordner `dist/EU_AI_Act_Classifier`.
