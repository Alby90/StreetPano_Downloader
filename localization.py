"""
Sistema di localizzazione per Street View Downloader
Supporta italiano e inglese
"""

# Dizionario traduzioni
TRANSLATIONS = {
    'it': {
        # Titolo applicazione
        'app_title': 'Google Street View Downloader - Versione Avanzata',
        
        # Tab principali
        'tab_streetview': 'Street View',
        'tab_local_files': 'File Locali',
        'tab_batch': 'Download Multipli',
        
        # Sezione Street View
        'sv_title': 'Download Singolo da Google Street View',
        'sv_url_label': 'URL Google Maps:',
        'sv_url_placeholder': 'Incolla qui l\'URL di Google Street View...',
        'sv_extract_btn': 'Estrai PanoID',
        'sv_download_btn': 'Download',
        'sv_save_btn': 'Salva Immagine',
        'sv_options_title': 'Opzioni Download',
        'sv_resolution_label': 'Risoluzione:',
        'sv_overlap_label': 'Overlap SfM:',
        'sv_overlap_suffix': '% (per photogrammetry)',
        'sv_format_label': 'Formato Output:',
        'sv_format_equirect': 'Equirettangolare',
        'sv_format_cubemap': 'Cubemap',
        'sv_preview_title': 'Anteprima',
        
        # Sezione File Locali
        'lf_title': 'Conversione File Locali',
        'lf_input_label': 'File/Cartella Input:',
        'lf_browse_btn': 'Sfoglia',
        'lf_output_label': 'Cartella Output:',
        'lf_convert_title': 'Converti da:',
        'lf_convert_equirect_cube': 'Equirettangolare → Cubemap',
        'lf_convert_cube_equirect': 'Cubemap → Equirettangolare',
        'lf_overlap_label': 'Overlap SfM:',
        'lf_overlap_suffix': '% (solo per equirettangolari)',
        'lf_convert_btn': 'Avvia Conversione',
        
        # Sezione Download Multipli
        'batch_title': 'Download Multipli',
        'batch_urls_label': 'Lista URL:',
        'batch_add_btn': 'Aggiungi URL',
        'batch_import_btn': 'Importa da File',
        'batch_export_btn': 'Esporta Lista',
        'batch_clear_btn': 'Svuota Lista',
        'batch_output_label': 'Cartella Output:',
        'batch_options_title': 'Opzioni Batch',
        'batch_resolution_label': 'Risoluzione:',
        'batch_overlap_label': 'Overlap SfM:',
        'batch_format_label': 'Formato:',
        'batch_start_btn': 'Avvia Download',
        'batch_stop_btn': 'Ferma Download',
        
        # Messaggi di stato
        'status_ready': 'Pronto',
        'status_extracting': 'Estrazione PanoID...',
        'status_downloading': 'Download in corso...',
        'status_converting': 'Conversione in corso...',
        'status_complete': 'Completato!',
        'status_error': 'Errore',
        'status_overlap_applying': 'Applicazione overlap',
        
        # Messaggi vari
        'panoid_extracted': 'PanoID estratto',
        'download_complete': 'Download completato! Immagine',
        'cubemap_generated': 'Cubemap generato! 6 facce',
        'overlap_info': 'overlap',
        'from_equirect_overlap': 'da equirect con overlap',
        'processing': 'Elaborazione',
        'tiles': 'tiles',
        'of': 'di',
        
        # Errori
        'error_invalid_url': 'URL non valido o PanoID non trovato',
        'error_download_failed': 'Download fallito',
        'error_conversion_failed': 'Conversione fallita',
        'error_no_image': 'Nessuna immagine da salvare',
        'error_save_failed': 'Salvataggio fallito',
        
        # Dialog e messaggi
        'save_dialog_title': 'Salva Immagine',
        'folder_dialog_title': 'Seleziona Cartella',
        'file_dialog_title': 'Seleziona File',
        'confirm_title': 'Conferma',
        'info_title': 'Informazione',
        'warning_title': 'Attenzione',
        
        # Language selector
        'language_label': 'Lingua:',
        'language_italian': 'Italiano',
        'language_english': 'English',
        
        # Additional UI elements
        'validate_btn': 'Valida',
        'clear_btn': '🗑️ Pulisci',
        'no_image_loaded': 'Nessuna immagine caricata',
        'menu_file': 'File',
        'menu_exit': 'Esci',
        'menu_language': 'Lingua'
    },
    
    'en': {
        # Application title
        'app_title': 'Google Street View Downloader - Advanced Version',
        
        # Main tabs
        'tab_streetview': 'Street View',
        'tab_local_files': 'Local Files',
        'tab_batch': 'Batch Download',
        
        # Street View section
        'sv_title': 'Single Download from Google Street View',
        'sv_url_label': 'Google Maps URL:',
        'sv_url_placeholder': 'Paste Google Street View URL here...',
        'sv_extract_btn': 'Extract PanoID',
        'sv_download_btn': 'Download',
        'sv_save_btn': 'Save Image',
        'sv_options_title': 'Download Options',
        'sv_resolution_label': 'Resolution:',
        'sv_overlap_label': 'SfM Overlap:',
        'sv_overlap_suffix': '% (for photogrammetry)',
        'sv_format_label': 'Output Format:',
        'sv_format_equirect': 'Equirectangular',
        'sv_format_cubemap': 'Cubemap',
        'sv_preview_title': 'Preview',
        
        # Local Files section
        'lf_title': 'Local File Conversion',
        'lf_input_label': 'Input File/Folder:',
        'lf_browse_btn': 'Browse',
        'lf_output_label': 'Output Folder:',
        'lf_convert_title': 'Convert from:',
        'lf_convert_equirect_cube': 'Equirectangular → Cubemap',
        'lf_convert_cube_equirect': 'Cubemap → Equirectangular',
        'lf_overlap_label': 'SfM Overlap:',
        'lf_overlap_suffix': '% (equirectangular only)',
        'lf_convert_btn': 'Start Conversion',
        
        # Batch Download section
        'batch_title': 'Batch Download',
        'batch_urls_label': 'URL List:',
        'batch_add_btn': 'Add URL',
        'batch_import_btn': 'Import from File',
        'batch_export_btn': 'Export List',
        'batch_clear_btn': 'Clear List',
        'batch_output_label': 'Output Folder:',
        'batch_options_title': 'Batch Options',
        'batch_resolution_label': 'Resolution:',
        'batch_overlap_label': 'SfM Overlap:',
        'batch_format_label': 'Format:',
        'batch_start_btn': 'Start Download',
        'batch_stop_btn': 'Stop Download',
        
        # Status messages
        'status_ready': 'Ready',
        'status_extracting': 'Extracting PanoID...',
        'status_downloading': 'Downloading...',
        'status_converting': 'Converting...',
        'status_complete': 'Complete!',
        'status_error': 'Error',
        'status_overlap_applying': 'Applying overlap',
        
        # Various messages
        'panoid_extracted': 'PanoID extracted',
        'download_complete': 'Download complete! Image',
        'cubemap_generated': 'Cubemap generated! 6 faces',
        'overlap_info': 'overlap',
        'from_equirect_overlap': 'from equirect with overlap',
        'processing': 'Processing',
        'tiles': 'tiles',
        'of': 'of',
        
        # Errors
        'error_invalid_url': 'Invalid URL or PanoID not found',
        'error_download_failed': 'Download failed',
        'error_conversion_failed': 'Conversion failed',
        'error_no_image': 'No image to save',
        'error_save_failed': 'Save failed',
        
        # Dialogs and messages
        'save_dialog_title': 'Save Image',
        'folder_dialog_title': 'Select Folder',
        'file_dialog_title': 'Select File',
        'confirm_title': 'Confirm',
        'info_title': 'Information',
        'warning_title': 'Warning',
        
        # Language selector
        'language_label': 'Language:',
        'language_italian': 'Italiano',
        'language_english': 'English',
        
        # Additional UI elements
        'validate_btn': 'Validate',
        'clear_btn': '🗑️ Clear',
        'no_image_loaded': 'No image loaded',
        'menu_file': 'File',
        'menu_exit': 'Exit',
        'menu_language': 'Language'
    }
}

class Localization:
    def __init__(self, language='it'):
        self.current_language = language
        self.callbacks = []  # Callbacks per aggiornare UI quando cambia lingua
    
    def set_language(self, language):
        """Cambia lingua e aggiorna UI"""
        if language in TRANSLATIONS:
            self.current_language = language
            # Chiama tutti i callbacks registrati per aggiornare l'UI
            for callback in self.callbacks:
                try:
                    callback()
                except Exception as e:
                    print(f"Errore callback localizzazione: {e}")
    
    def get_language(self):
        """Ritorna lingua corrente"""
        return self.current_language
    
    def get_available_languages(self):
        """Ritorna lingue disponibili"""
        return list(TRANSLATIONS.keys())
    
    def register_callback(self, callback):
        """Registra callback per aggiornamenti UI"""
        self.callbacks.append(callback)
    
    def t(self, key, default=None):
        """Traduce una chiave"""
        try:
            return TRANSLATIONS[self.current_language][key]
        except KeyError:
            # Fallback a inglese se chiave non trovata
            try:
                return TRANSLATIONS['en'][key]
            except KeyError:
                # Fallback al default o alla chiave stessa
                return default if default is not None else key
    
    def format(self, key, *args, **kwargs):
        """Traduce e formatta una stringa"""
        text = self.t(key)
        try:
            return text.format(*args, **kwargs)
        except:
            return text


# Istanza globale di localizzazione
_localization = Localization()

def set_language(language):
    """Funzione helper per cambiare lingua"""
    _localization.set_language(language)

def get_language():
    """Funzione helper per ottenere lingua corrente"""
    return _localization.get_language()

def get_available_languages():
    """Funzione helper per ottenere lingue disponibili"""
    return _localization.get_available_languages()

def register_callback(callback):
    """Funzione helper per registrare callback"""
    _localization.register_callback(callback)

def t(key, default=None):
    """Funzione helper per tradurre"""
    return _localization.t(key, default)

def format_text(key, *args, **kwargs):
    """Funzione helper per tradurre e formattare"""
    return _localization.format(key, *args, **kwargs)