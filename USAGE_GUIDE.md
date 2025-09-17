# 🌍 Street View Panorama Downloader - Guida Completa

## 📋 Panoramica

Questo progetto fornisce strumenti avanzati per scaricare e convertire immagini panoramiche da Google Street View. Include due applicazioni principali e utilità per la conversione tra formati panoramici.

## 🚀 Applicazioni Disponibili

### 1. Simple Downloader (`simple_downloader.py`)
- **Scopo**: Downloader semplice e affidabile
- **Dipendenze**: Solo `requests` e `PIL`
- **Caratteristiche**:
  - Interfaccia semplice e intuitiva
  - Download di immagini equirettangolari
  - Estrazione automatica PanoID da URL Google Maps
  - Anteprima immagini
  - Salvataggio in alta qualità

### 2. Advanced Downloader (`advanced_downloader.py`)
- **Scopo**: Strumento completo con funzionalità avanzate
- **Caratteristiche**:
  - **3 Tab specializzati**:
    - 🔍 **Street View**: Download singoli con anteprima
    - 📁 **File Locali**: Conversione file esistenti
    - 📦 **Download Multipli**: Processamento batch
  - **Formati supportati**: Equirettangolare e Cubemap
  - **Conversioni**: Equirect ↔ Cubemap
  - **Download multipli**: Elaborazione di liste URL
  - **Anteprima avanzata**: Zoom e dettagli immagine

## 🛠️ Installazione e Setup

### Requisiti di Sistema
- **Windows 10/11**
- **Python 3.7+**
- **Connessione Internet**

### 1. Installazione Dipendenze
```bash
# Dipendenze base (obbligatorie)
pip install requests pillow

# Dipendenze opzionali per performance migliorate
pip install numpy opencv-python

# Per la GUI
pip install tkinter  # Di solito incluso con Python
```

### 2. Verifica Installazione
```bash
python test_functionality.py
```

## 🎯 Come Usare

### Avvio Rapido - Simple Downloader
```bash
python simple_downloader.py
```

1. **Copia URL da Google Maps**:
   - Vai su [Google Maps](https://maps.google.com)
   - Entra in Street View (omino giallo)
   - Copia l'URL dalla barra degli indirizzi

2. **Incolla nell'applicazione**:
   - Incolla l'URL nel campo di testo
   - Clicca "Estrai PanoID" per verifica
   - Clicca "Download" per scaricare

### Avvio Avanzato - Advanced Downloader
```bash
python advanced_downloader.py
```

#### Tab 1: Street View
- **URL Input**: Incolla URL Google Maps Street View
- **Risoluzione**: Scegli qualità (0=bassa, 4=altissima)
- **Overlap SfM**: Percentuale overlap per Structure from Motion (0-50%)
- **Formato Output**: Equirettangolare o Cubemap
- **Anteprima**: Vedi preview prima del download

#### Tab 2: File Locali  
- **Conversione Formati**: Converti tra equirettangolare e cubemap
- **Tipi Input**: File singoli o cartelle complete
- **Overlap SfM**: Applica overlap alle immagini equirettangolari
- **Preview**: Anteprima immagini caricate
- **Batch Processing**: Elabora cartelle intere

#### Tab 3: Download Multipli
- **Lista URL**: Aggiungi multiple URL
- **Import/Export**: Carica liste da file di testo
- **Overlap SfM**: Applica overlap a tutti i download
- **Download Batch**: Scarica tutto automaticamente
- **Progress Tracking**: Monitora il progresso

## 📁 Struttura File

```
StreetPano/
├── 📱 simple_downloader.py      # App semplice
├── 📱 advanced_downloader.py    # App avanzata 
├── 🔧 streetview_utils.py       # Utilità Street View
├── 🔄 panorama_converter.py     # Convertitore panoramico
├── ⚙️ config.py                 # Configurazioni
├── 🧪 test_functionality.py     # Test base
├── 🧪 test_advanced.py          # Test avanzati
├── 📖 README.md                 # Documentazione base
├── 📖 USAGE_GUIDE.md            # Questa guida
├── 🚀 run_simple.bat            # Launcher Windows (semplice)
└── 🚀 run_advanced.bat          # Launcher Windows (avanzato)
```

## 📐 Funzionalità Overlap per Structure from Motion

### 🎯 Cos'è l'Overlap SfM
L'**Overlap SfM** (Structure from Motion) è una funzionalità avanzata che estende le immagini equirettangolari aggiungendo porzioni delle immagini adiacenti sui bordi. Questo è essenziale per:

- **Photogrammetry**: Ricostruzione 3D da immagini multiple
- **Structure from Motion**: Algorithms che necessitano punti comuni
- **Feature Matching**: Migliore corrispondenza tra immagini consecutive
- **Bundle Adjustment**: Calibrazione più stabile e precisa

### 🔄 Come Funziona
Quando si imposta un overlap del **30%**:
- L'immagine diventa **30% più larga** 
- **Bordi sinistro/destro**: Utilizzano il wrapping panoramico (360°)
- **Bordi alto/basso**: Stretch equatoriale per ridurre distorsioni
- **Angoli**: Interpolazione intelligente per continuità

### 📊 Raccomandazioni Overlap

| Percentuale | Uso Consigliato | Qualità SfM | Dimensione File |
|-------------|------------------|-------------|-----------------|
| **0%** | Download standard | - | Normale |
| **10%** | SfM basic, test | Buona | +10% |
| **20%** | SfM standard | Molto buona | +20% |
| **30%** | SfM alta qualità | Eccellente | +30% |
| **40%** | Scene complesse | Massima | +40% |
| **50%** | Progetti critici | Massima | +50% |

### 🎮 Scenari d'Uso

#### Scenario 1: Virtual Tour 3D
"Creo tour virtuali con navigazione fluida"
```
Overlap: 20-30%
Risoluzione: Alta (zoom 3)
Formato: Equirettangolare
Risultato: Transizioni smooth, ricostruzione 3D precisa
```

#### Scenario 2: Mapping Urbano
"Ricostruisco modelli 3D di strade e edifici"
```
Overlap: 30-40%
Risoluzione: Massima (zoom 4)  
Batch: Liste URL multiple
Risultato: Point cloud densa, geometria accurata
```

#### Scenario 3: Dataset Machine Learning
"Training data per IA di riconoscimento spaziale"
```
Overlap: 40-50%
Batch Processing: Centinaia di immagini
Conversioni: Equirect + Cubemap
Risultato: Dataset robusto con ground truth 3D
```

## 🎛️ Formati Panoramici

### Equirettangolare (360°)
- **Formato**: Immagine rettangolare 2:1 (es. 4096x2048)
- **Uso**: Standard per VR, visualizzatori 360°
- **Vantaggi**: Singolo file, compatibile universalmente
- **Svantaggi**: Distorsione ai poli

### Cubemap (6 Facce)
- **Formato**: 6 immagini quadrate (front, back, left, right, up, down)
- **Uso**: Rendering 3D, game engines
- **Vantaggi**: Nessuna distorsione, qualità uniforme
- **Svantaggi**: 6 file separati

## ⚡ Conversioni Automatiche

### Equirettangolare → Cubemap
```python
from panorama_converter import quick_equirect_to_cubemap

# Conversione rapida
files = quick_equirect_to_cubemap(
    'panorama.jpg',      # File input
    'output_folder/',    # Cartella output  
    face_size=1024       # Dimensione facce
)
# Risultato: 6 file (panorama_front.jpg, panorama_right.jpg, etc.)
```

### Cubemap → Equirettangolare
```python
from panorama_converter import quick_cubemap_to_equirect

# Conversione rapida
result = quick_cubemap_to_equirect(
    'cubemap_folder/',   # Cartella con le 6 facce
    'panorama',          # Nome base file
    'output_folder/',    # Cartella output
    output_size=(4096, 2048)  # Dimensione finale
)
# Risultato: panorama_equirect.jpg
```

## 🔧 Configurazioni Avanzate

### Qualità Download
```python
# In config.py
ZOOM_LEVELS = {
    0: (1, 416),    # Bassa qualità
    1: (2, 832),    # Media qualità  
    2: (3, 1664),   # Alta qualità
    3: (4, 3328),   # Molto alta
    4: (5, 6656)    # Massima qualità
}
```

### Timeout e Retry
```python
# Configurazioni di rete
REQUEST_TIMEOUT = 10        # Timeout richieste
MAX_RETRIES = 3            # Tentativi massimi
TILE_DOWNLOAD_DELAY = 0.1  # Pausa tra download
```

## 🚨 Risoluzione Problemi

### Errore "PanoID non trovato"
**Causa**: URL non valido o Street View non disponibile
**Soluzione**:
1. Verifica che l'URL contenga Street View (icona omino giallo)
2. Prova a muoverti nella vista e copia nuovo URL
3. Usa il test pattern nell'app per verificare l'estrazione

### Errore "Timeout download"
**Causa**: Connessione lenta o Google API sovraccariche
**Soluzione**:
1. Riduci la qualità (zoom level)
2. Riprova più tardi
3. Verifica connessione internet

### Errore "Modulo non trovato"
**Causa**: Dipendenze mancanti
**Soluzione**:
```bash
pip install --upgrade requests pillow tkinter
```

### Performance Lente
**Causa**: Immagini ad alta risoluzione senza numpy
**Soluzione**:
```bash
pip install numpy opencv-python
```

## 📊 Qualità e Dimensioni

| Zoom Level | Dimensione Finale | Qualità | Tempo Download | Dimensione File |
|------------|------------------|---------|----------------|-----------------|
| 0          | 416x208         | Bassa   | ~5 sec         | ~50 KB          |
| 1          | 832x416         | Media   | ~15 sec        | ~200 KB         |
| 2          | 1664x832        | Alta    | ~30 sec        | ~800 KB         |
| 3          | 3328x1664       | Molto Alta | ~60 sec     | ~3 MB           |
| 4          | 6656x3328       | Massima | ~120 sec       | ~12 MB          |

## 🎨 Esempi d'Uso

### Scenario 1: Tourist Virtuale
"Voglio creare un tour virtuale della mia città"
1. Usa **Advanced Downloader - Tab 3**
2. Raccogli URL da punti di interesse
3. Download batch in qualità alta (zoom 3)
4. Usa immagini equirettangolari per VR

### Scenario 2: Sviluppatore Game
"Serve background per il mio gioco 3D"
1. Usa **Advanced Downloader - Tab 1**
2. Scarica in formato Cubemap 
3. Importa le 6 facce nel game engine
4. Usa come skybox

### Scenario 3: Archivio Locale
"Voglio convertire la mia collezione panoramica"
1. Usa **Advanced Downloader - Tab 2**
2. Seleziona cartella con panorami
3. Batch conversion equirect → cubemap
4. Organizza per progetto

## 🔍 URLs di Esempio per Test

```
# Times Square, New York
https://www.google.com/maps/@40.758896,-73.985130,3a,75y,92.19h,90t/data=!3m6!1e1!3m4!1sAF1QipO5fGJGUMXv7Q1C0z-QR4n3fxOg8_5jOJxJVXpp!2e10!7i16384!8i8192

# Torre Eiffel, Parigi  
https://www.google.com/maps/@48.858370,2.294481,3a,75y,46.78h,95.61t/data=!3m6!1e1!3m4!1sAF1QipPZ9aOqk_0RXU5WlI7d39cG2bNFNRRnO6OJo6mD!2e10!7i13312!8i6656

# Colosseo, Roma
https://www.google.com/maps/@41.890251,12.492373,3a,75y,155.06h,98.41t/data=!3m6!1e1!3m4!1sAF1QipNT7i9u45R7sH1gj5r7u9vGJ9OJ0w5mP_1tF8K3!2e10!7i13312!8i6656
```

## 🎯 Tips & Trucchi

### Performance
- **Usa numpy**: Installa per conversioni 10x più veloci
- **Risoluzione ottimale**: Zoom 2-3 per bilanciare qualità/velocità
- **Batch processing**: Elabora di notte per liste lunghe

### Qualità
- **Formato originale**: Scarica sempre in equirettangolare
- **Conversione secondaria**: Converti in cubemap se necessario
- **Backup**: Mantieni originali prima di convertire

### Workflow
- **Test prima**: Prova con 1-2 immagini prima del batch
- **Organizzazione**: Usa cartelle separate per progetto
- **Naming**: I file hanno timestamp automatico

## 📞 Supporto

### Log e Debug
- I log sono visibili nella console dell'applicazione
- File di log salvati automaticamente in `logs/`
- Test diagnostici disponibili in `test_functionality.py`

### Limitazioni Note
- **Rate limiting**: Google può limitare download intensivi
- **Disponibilità**: Non tutti i luoghi hanno Street View
- **Qualità**: Dipende dalla qualità originale di Google

### Best Practices
- **Rispetta i ToS**: Usa per scopi legali e personali
- **Rate limiting**: Non abusare delle API Google
- **Storage**: Le immagini ad alta risoluzione occupano spazio

## 🎉 Conclusione

Questo toolkit fornisce tutto il necessario per lavorare con panorami Street View, dalle operazioni semplici alle conversioni avanzate. Inizia con il downloader semplice per familiarizzare, poi passa all'avanzato per funzionalità complete.

**Buon panorama downloading! 🌍📸**
