# KI-VO Classifier - Ideen & Backlog 🚀

In diesem Dokument sammeln wir zukünftige Erweiterungsideen, Refaktorierungsschritte und funktionale Upgrades für den Klassifizierer.

---

## Mittelfristige Ideen & Konzepte

### 1. Aussagen-basiertes Klassifizieren (statt einfachem Ja/Nein)
- **Konzept**: Weg von abstrakten juristischen Ja/Nein-Fragen (z. B. *"Sind Sie Anbieter?"*), hin zu konkreten Aussagen aus der Betriebspraxis, die der Nutzer per Checkliste anklickt.
- **Beispiel**:
  - *Statt*: "Sind Sie Betreiber?"
  - *Auswahlmöglichkeiten (Mehrfachauswahl)*:
    - [ ] "Ich verwende das KI-System in meiner eigenen Organisation für geschäftliche Zwecke."
    - [ ] "Ich habe das System selbst entwickelt und nutze es nur intern."
    - [ ] "Ich stelle das System Dritten entgeltlich oder unentgeltlich zur Verfügung."
- **Vorteil**: Deutliche Senkung der Hürde für Nicht-Juristen und präzisere, kontextbasierte Rollen- und Risikoermittlung.

### 2. Multi-Plattform Standalone Builds (CI/CD)
- Automatisierung des Kompilierungsprozesses für macOS und Windows über GitHub Actions.
- Bereitstellung fertiger Releases direkt auf GitHub, um manuelle lokale Builds über `build_mac.sh` / `build_windows.bat` zu vermeiden.

### 3. Erweiterter Pflichten-Tracker
- Ein interaktiver Modus im Ergebnis-Dashboard, bei dem der Nutzer die generierten Pflichten abhaken und als "in Bearbeitung" oder "erfüllt" markieren kann.
- Speicherung dieses Fortschritts in der exportierten JSON-Datei.

---

## Kleinere Optimierungen (Technischer Backlog)
- [ ] Tooltips und weiterführende Info-Boxen für Spezialbegriffe wie *On-Premise* oder *RAG-Pipeline* direkt in der Benutzeroberfläche verlinken.
- [ ] Optimierung der FPDF2-Tabellen-Spaltenbreiten basierend auf der Textlänge, um Umbrüche in schmalen Spalten weiter zu minimieren.
