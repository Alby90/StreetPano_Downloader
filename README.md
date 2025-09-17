# Google Street View Downloader

Un programma Python con interfaccia Tkinter per scaricare e ricostruire immagini equirettangolari da Google Street View.

## 🚀 Avvio Rapido

1. **Avvia il programma:**
   ```bash
   python simple_downloader.py
   ```
   
   Oppure su Windows:
   ```bash
   start.bat
   ```

2. **Ottieni un'immagine Street View:**
   - Vai su [Google Maps](https://maps.google.com)
   - Cerca una località e attiva Street View (trascina l'omino giallo)
   - Copia l'URL completo dalla barra degli indirizzi
   - Incolla l'URL nel programma e clicca "Estrai PanoID"
   - Seleziona la risoluzione e clicca "Download Immagine"

## ✨ Caratteristiche

- **🖥️ Interfaccia grafica intuitiva** con Tkinter
- **🔍 Estrazione automatica del PanoID** dall'URL di Google Street View
- **📸 Download ad alta risoluzione** (fino a 8192×4096 pixel)
- **🔧 Ricostruzione automatica** dell'immagine equirettangolare dalle tiles
- **👁️ Anteprima integrata** dell'immagine scaricata
- **✅ Validazione PanoID** per verificare la disponibilità
- **💾 Salvataggio in JPEG/PNG**

## 📋 Requisiti

- **Python 3.6+**
- **Dipendenze Python:**
  - `requests` (per download HTTP)
  - `pillow` (per elaborazione immagini)
  - `tkinter` (incluso con Python)

## 🛠️ Installazione

1. **Clona o scarica questo repository**

2. **Installa le dipendenze:**
   ```bash
   pip install requests pillow
   ```

3. **Avvia il programma:**
   ```bash
   python simple_downloader.py
   ```

## 📖 Guida all'uso

### Come ottenere l'URL di Street View

1. Vai su [Google Maps](https://maps.google.com)
2. Cerca una località o naviga sulla mappa
3. Trascina l'**omino giallo** (Street View) sulla mappa
4. Quando si apre la vista Street View, **copia l'URL completo** dalla barra degli indirizzi
5. L'URL dovrebbe assomigliare a questo:
   ```
   https://www.google.com/maps/@40.748817,-73.985428,3a,75y,90t/data=!3m6!1e1!3m4!1sAF1QipM...
   ```

### Utilizzo del programma

1. **Inserisci l'URL:** Incolla l'URL nel campo "URL Street View"
2. **Estrai PanoID:** Clicca "Estrai PanoID" per ottenere l'identificativo dell'immagine
3. **Valida:** Il programma validerà automaticamente se il PanoID è disponibile
4. **Seleziona risoluzione:** Scegli la qualità dell'immagine desiderata
5. **Download:** Clicca "Download Immagine" e attendi il completamento
6. **Salva:** Usa "Salva Immagine" per salvare il risultato

### Livelli di risoluzione

| Livello | Risoluzione | Tiles | Dimensione file | Tempo download |
|---------|-------------|-------|-----------------|----------------|
| 0 - Bassa | 512×512 | 1×1 | ~100 KB | Molto veloce |
| 1 - Media | 1024×512 | 2×1 | ~200 KB | Veloce |
| 2 - Alta | 2048×1024 | 4×2 | ~800 KB | Normale ⭐ |
| 3 - Molto Alta | 4096×2048 | 8×4 | ~3 MB | Lento |
| 4 - Massima | 8192×4096 | 16×8 | ~12 MB | Molto lento |

*⭐ Livello raccomandato per uso normale*

## 📁 Struttura del progetto

```
StreetPano/
├── simple_downloader.py      # 🎯 Programma principale (AVVIA QUESTO)
├── start.bat                 # 🚀 Launcher Windows
├── test_functionality.py     # 🧪 Test delle funzionalità
├── streetview_downloader.py  # 📦 Versione avanzata (richiede più dipendenze)
├── streetview_utils.py       # 🔧 Utilità avanzate
├── config.py                 # ⚙️ Configurazioni
└── README.md                 # 📚 Questo file
```

## 🧪 Test

Per testare le funzionalità del programma:

```bash
python test_functionality.py
```

Questo verificherà:
- ✅ Dipendenze installate
- ✅ Estrazione PanoID da URL
- ✅ Download di tiles
- ✅ Pattern di riconoscimento URL

## 🔧 Risoluzione problemi

### ❌ "PanoID non trovato nell'URL"
- **Causa:** L'URL non contiene un PanoID valido
- **Soluzione:** 
  - Assicurati di essere in modalità Street View su Google Maps
  - Copia l'URL completo, non solo l'indirizzo della località
  - Prova a muoverti leggermente in Street View per generare un nuovo URL

### ❌ "PanoID non valido"
- **Causa:** Il PanoID esiste ma non è accessibile
- **Soluzione:**
  - Alcune aree potrebbero essere riservate o temporaneamente non disponibili
  - Prova con una località diversa
  - Verifica la connessione internet

### ❌ Download lento o bloccato
- **Causa:** Connessione lenta o limitazioni di Google
- **Soluzione:**
  - Riduci il livello di risoluzione
  - Aspetta qualche minuto prima di riprovare
  - Verifica la connessione internet

### ❌ "Errore nell'importazione"
- **Causa:** Dipendenze mancanti
- **Soluzione:**
  ```bash
  pip install --upgrade requests pillow
  ```

### ❌ Tiles mancanti (quadrati grigi/rossi)
- **Causa:** Alcune parti dell'immagine non sono disponibili
- **Questo è normale:** Google Street View non copre tutte le angolazioni

## 🎯 Esempi di URL validi

```
✅ VALIDI:
https://www.google.com/maps/@40.748817,-73.985428,3a,75y,90t/data=!3m6!1e1!3m4!1s...
https://maps.google.com/?q=40.748817,-73.985428&layer=c&cbll=40.748817,-73.985428&panoid=...

❌ NON VALIDI:
https://www.google.com/maps/@40.748817,-73.985428,15z
https://maps.google.com/maps?q=New+York
```

## ⚖️ Limitazioni e Note Legali

- ⚠️ **Rispetta i termini di servizio di Google** quando usi questo software
- 🚫 **Non usare per scopi commerciali** senza autorizzazione
- 📊 **Limitazioni di rate**: Google potrebbe limitare richieste eccessive
- 🌍 **Disponibilità**: Non tutte le aree del mondo hanno Street View
- 🔒 **Privacy**: Alcune aree potrebbero essere censurate o non disponibili

## 🤝 Contributi

I contributi sono benvenuti! Per migliorare il programma:

1. 🍴 Fork del repository
2. 🌟 Crea un branch per la tua feature
3. 📝 Commit delle modifiche
4. 📤 Push del branch
5. 🔄 Apri una Pull Request

## 📞 Supporto

Se riscontri problemi:

1. 🧪 Esegui `python test_functionality.py` per diagnosticare
2. 📋 Verifica che tutte le dipendenze siano installate
3. 🌐 Controlla la connessione internet
4. 📖 Leggi la sezione "Risoluzione problemi"

---

**🎉 Buon download con Google Street View Downloader!**
