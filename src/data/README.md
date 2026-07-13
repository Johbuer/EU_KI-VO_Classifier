# Inhalts-Konfiguration (Manuelle Textanpassungen)

Sie können die rechtlichen und erklärenden Inhalte des AI Act Classifiers manuell in diesem Ordner anpassen. Alle Texte wurden aus dem Python-Code in einfache JSON-Dateien ausgelagert, die Sie mit jedem Standard-Texteditor bearbeiten können.

## JSON-Dateien im Überblick

1. **[info_texts.json](file:///d:/programming/reg_ai_classifier/src/data/info_texts.json):**
   - Enthält alle umgangssprachlichen Erklärungen für die Infoboxen.
   - Wenn Sie ein Info-Feld umformulieren oder ein praktisches Beispiel hinzufügen möchten, ändern Sie einfach den entsprechenden String.

2. **[legal_texts.json](file:///d:/programming/reg_ai_classifier/src/data/legal_texts.json):**
   - Enthält die exakten Gesetzestexte der EU-KI-Verordnung (AI Act), gegliedert nach Artikelverweisen.
   - Enthält auch die Anhang III-Unterkategorien und Definitionen.

3. **[obligations.json](file:///d:/programming/reg_ai_classifier/src/data/obligations.json):**
   - Enthält den vollständigen Pflichtenkatalog (Pflichtenmatrix), der im Ergebnis-Dashboard angezeigt wird.
   - Gegliedert nach Kategorien (z.B. `high_risk_provider`, `high_risk_deployer`, `transparency`, `gpai`).
   - Jede Pflicht hat die Felder `title` (Titel), `citation` (Artikel), `description` (Beschreibung) und `addressee` (Adressat).

4. **[rights.json](file:///d:/programming/reg_ai_classifier/src/data/rights.json):**
   - Enthält die gesetzlichen Ansprüche und Rechte gegenüber Drittparteien (Zulieferern, GPAI-Anbietern).
   - Gegliedert nach Rollen (z.B. `downstream_provider`, `deployer_high_risk`).

## Wichtige Hinweise für manuelle Korrekturen

* **Umlaute & Sonderzeichen:** Bitte verwenden Sie die normale deutsche Rechtschreibung mit Umlauten (**ä, ö, ü**) und Eszett (**ß**). Die JSON-Dateien sind in UTF-8 kodiert.
* **JSON-Syntax einhalten:** 
  * Strings müssen in doppelte Anführungszeichen `"..."` eingeschlossen sein.
  * Sonderzeichen wie Anführungszeichen innerhalb des Textes müssen mit einem Backslash escaped werden (z.B. `\"` oder `'`).
  * Listen-Elemente müssen durch Kommas getrennt werden (nach dem letzten Element einer Liste/eines Dictionaries darf kein Komma stehen).
* **Automatisches Laden:** Die Anwendung liest diese Dateien bei jedem Seitenwechsel oder Rerun automatisch neu ein. Sie müssen die App nach einer Textänderung nicht neu starten!
