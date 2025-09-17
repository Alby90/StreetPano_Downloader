"""
DOCUMENTAZIONE TECNICA - Google Street View Downloader
====================================================

OVERVIEW
--------
Questo programma permette di scaricare immagini panoramiche equirettangolari 
da Google Street View utilizzando l'API non documentata di tiles.

ARCHITETTURA
------------

1. ESTRAZIONE PANOID
   - Pattern regex per identificare il PanoID dall'URL
   - Validazione tramite richiesta HTTP di test
   - Fallback su inserimento manuale

2. DOWNLOAD TILES
   - Calcolo matrice tiles basato su livello zoom
   - Download parallelo/sequenziale delle tiles
   - Ricostruzione immagine equirettangolare

3. INTERFACCIA UTENTE
   - Tkinter per GUI cross-platform
   - Thread separati per operazioni I/O
   - Progress bar e status updates

API ENDPOINT
------------
Base URL: https://streetviewpixels-pa.googleapis.com/v1/tile

Parametri:
- cb_client: maps_sv.tactile
- panoid: Identificativo panorama
- x, y: Coordinate tile
- zoom: Livello di dettaglio (0-4)
- nbt: 1 (parametro fisso)
- fover: 2 (field of view)

ZOOM LEVELS
-----------
Zoom 0: 1×1 tiles   = 512×512 pixel
Zoom 1: 2×1 tiles   = 1024×512 pixel  
Zoom 2: 4×2 tiles   = 2048×1024 pixel
Zoom 3: 8×4 tiles   = 4096×2048 pixel
Zoom 4: 16×8 tiles  = 8192×4096 pixel

PATTERN PANOID
--------------
Regex patterns utilizzati per estrazione:
1. !1s([a-zA-Z0-9_-]{20,})           # Google Maps standard
2. "pano":"([a-zA-Z0-9_-]{20,})"     # JSON format
3. panoid=([a-zA-Z0-9_-]{20,})       # URL parameter
4. photosphereId=([a-zA-Z0-9_-]{20,}) # Alternative format

GESTIONE ERRORI
---------------
- Timeout richieste HTTP: 10 secondi
- Retry automatico per tiles mancanti
- Fallback su tiles vuote (grigie) per zone non disponibili
- Validazione PanoID prima del download

LIMITAZIONI
-----------
- Rate limiting di Google (non documentato)
- Alcune aree geografiche non disponibili
- Qualità variabile in base alla zona
- Dipendenza da API non ufficiale

SICUREZZA
---------
- Nessuna autenticazione richiesta
- User-Agent standard per evitare blocchi
- Rispetto delle best practices HTTP

PERFORMANCE
-----------
- Download sequenziale per evitare rate limiting
- Gestione memoria ottimizzata per immagini grandi
- Threading per UI responsiva

FILE STRUCTURE
--------------
simple_downloader.py    # Main application (versione semplificata)
streetview_downloader.py # Main application (versione completa)
streetview_utils.py     # Utility functions
config.py              # Configuration constants
test_functionality.py  # Test suite
start.bat             # Windows launcher
README.md            # User documentation

DEPENDENCIES
------------
Core:
- tkinter (GUI)
- requests (HTTP)
- PIL/Pillow (images)
- re (regex)
- threading (async)

Optional:
- selenium (browser automation)
- numpy (image processing)
- opencv (advanced image processing)

TESTING
-------
1. test_functionality.py - Comprehensive test suite
2. Manual testing via GUI
3. URL pattern validation
4. Tile download verification

FUTURE IMPROVEMENTS
-------------------
- Caching system for downloaded tiles
- Batch download multiple locations
- Export to different formats (cube map, etc.)
- Integration with mapping APIs
- Better error recovery
- Support for other panorama services

TROUBLESHOOTING
---------------
Common issues and solutions:

1. "PanoID not found"
   -> Check URL format, ensure Street View mode active
   
2. "Download failed"
   -> Check internet connection, try lower resolution
   
3. "Tiles missing"
   -> Normal for some locations, Google doesn't cover all angles
   
4. "Memory error"
   -> Use lower zoom level, close other applications

LEGAL CONSIDERATIONS
--------------------
- Rispettare Terms of Service di Google Maps
- Uso educativo/personale consigliato
- Non per scopi commerciali senza autorizzazione
- Privacy: alcune aree possono essere censurate

VERSION HISTORY
---------------
v1.0 - Initial release with basic functionality
v1.1 - Added simple version without selenium dependency
v1.2 - Improved error handling and user interface

CONTRIBUTING
------------
Per contribuire al progetto:
1. Fork repository
2. Create feature branch
3. Implement changes with tests
4. Submit pull request
5. Follow coding standards

CONTACT
-------
Per supporto tecnico consultare:
- README.md per guida utente
- test_functionality.py per diagnostica
- GitHub issues per bug reports
"""
