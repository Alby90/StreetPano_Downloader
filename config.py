"""
Configurazione per il Google Street View Downloader
"""

# Configurazioni per il download
DOWNLOAD_CONFIG = {
    # Timeout per le richieste HTTP (secondi)
    'request_timeout': 10,
    
    # Numero massimo di retry per download falliti
    'max_retries': 3,
    
    # Intervallo tra i retry (secondi)
    'retry_delay': 1,
    
    # Qualità JPEG per il salvataggio (1-100)
    'jpeg_quality': 95,
    
    # Dimensione massima dell'anteprima (pixel)
    'preview_size': (400, 200),
    
    # User-Agent per le richieste HTTP
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Configurazioni per il browser automatico
BROWSER_CONFIG = {
    # Opzioni per Chrome
    'chrome_options': [
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-blink-features=AutomationControlled',
        '--disable-extensions',
        '--no-first-run',
        '--disable-default-apps'
    ],
    
    # Opzioni per modalità headless (browser nascosto)
    'headless_options': [
        '--headless',
        '--disable-gpu',
        '--window-size=1920,1080'
    ],
    
    # Timeout per il caricamento delle pagine (secondi)
    'page_load_timeout': 30,
    
    # Tempo di attesa dopo il caricamento (secondi)
    'wait_after_load': 5
}

# Configurazioni dell'interfaccia
UI_CONFIG = {
    # Dimensioni finestra principale
    'window_size': '800x600',
    
    # Titolo dell'applicazione
    'app_title': 'Google Street View Downloader',
    
    # Colori tema
    'colors': {
        'primary': '#1f77b4',
        'secondary': '#ff7f0e',
        'success': '#2ca02c',
        'error': '#d62728',
        'background': '#f0f0f0'
    },
    
    # Font
    'fonts': {
        'title': ('Arial', 16, 'bold'),
        'normal': ('Arial', 10),
        'small': ('Arial', 8)
    }
}

# URL e endpoint per l'API Street View
API_CONFIG = {
    # Base URL per le tiles
    'tile_base_url': 'https://streetviewpixels-pa.googleapis.com/v1/tile',
    
    # Parametri standard per le tiles
    'tile_params': {
        'cb_client': 'maps_sv.tactile',
        'nbt': '1',
        'fover': '2'
    },
    
    # URL per metadata (richiede API key)
    'metadata_url': 'https://maps.googleapis.com/maps/api/streetview/metadata',
    
    # Dimensione standard delle tiles (pixel)
    'tile_size': 512
}

# Mapping dei livelli di zoom
ZOOM_LEVELS = {
    0: {'tiles_x': 1, 'tiles_y': 1, 'description': 'Bassa (512×512)'},
    1: {'tiles_x': 2, 'tiles_y': 1, 'description': 'Media (1024×512)'},
    2: {'tiles_x': 4, 'tiles_y': 2, 'description': 'Alta (2048×1024)'},
    3: {'tiles_x': 8, 'tiles_y': 4, 'description': 'Molto Alta (4096×2048)'},
    4: {'tiles_x': 16, 'tiles_y': 8, 'description': 'Massima (8192×4096)'}
}

# Pattern regex per l'estrazione del PanoID
PANOID_PATTERNS = [
    r'!1s([a-zA-Z0-9_-]{20,})',  # Pattern principale Google Maps
    r'"pano":"([a-zA-Z0-9_-]{20,})"',  # Pattern JSON
    r'"panoid":"([a-zA-Z0-9_-]{20,})"',  # Pattern JSON alternativo
    r'pano:"([a-zA-Z0-9_-]{20,})"',  # Pattern JS
    r'"panoId":"([a-zA-Z0-9_-]{20,})"',  # Pattern alternativo
    r'photosphereId=([a-zA-Z0-9_-]{20,})',  # Pattern photosphere
    r'panoid=([a-zA-Z0-9_-]{20,})',  # Pattern URL diretto
    r'pano=([a-zA-Z0-9_-]{20,})',  # Pattern pano
    r'cbp=\d+,\d+,\d+,\d+,\d+&amp;panoid=([a-zA-Z0-9_-]{20,})',  # Pattern con cbp
]

# Configurazioni per il miglioramento delle immagini
IMAGE_ENHANCEMENT = {
    # Parametri per la riduzione del rumore
    'denoise_params': {
        'h': 10,
        'hColor': 10,
        'templateWindowSize': 7,
        'searchWindowSize': 21
    },
    
    # Parametri per CLAHE (Contrast Limited Adaptive Histogram Equalization)
    'clahe_params': {
        'clipLimit': 2.0,
        'tileGridSize': (8, 8)
    },
    
    # Abilitare/disabilitare miglioramenti
    'enable_denoise': True,
    'enable_contrast_enhancement': True,
    'enable_sharpening': False
}

# Configurazioni di debug e logging
DEBUG_CONFIG = {
    # Abilitare output verbose
    'verbose': False,
    
    # Salvare tiles individuali per debug
    'save_individual_tiles': False,
    
    # Directory per file temporanei
    'temp_dir': 'temp_tiles',
    
    # Mantenere file temporanei dopo il download
    'keep_temp_files': False
}

# Messaggi dell'interfaccia (per internazionalizzazione futura)
MESSAGES = {
    'ready': 'Pronto',
    'extracting_panoid': 'Estrazione PanoID in corso...',
    'opening_browser': 'Apertura browser...',
    'downloading': 'Download in corso...',
    'download_complete': 'Download completato!',
    'saving_image': 'Salvataggio immagine...',
    'image_saved': 'Immagine salvata con successo',
    'error_no_url': 'Inserisci un URL di Google Street View',
    'error_no_panoid': 'Inserisci un PanoID',
    'error_no_image': 'Nessuna immagine da salvare',
    'error_download': 'Errore durante il download',
    'error_browser': 'Errore apertura browser',
    'error_save': 'Errore nel salvataggio',
    'panoid_extracted': 'PanoID estratto: {}',
    'panoid_not_found': 'PanoID non trovato',
    'browser_opened': 'Browser aperto. Naviga su Street View e poi usa "Estrai PanoID"',
    'download_progress': 'Download: {}/{} tiles'
}
