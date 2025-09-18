"""
Google Street View Downloader - Versione Avanzata
Supporta download multipli, conversione cubemap e elaborazione file locali
"""
import os
import json
from datetime import datetime
import math
import glob
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
import threading
import requests
from PIL import Image, ImageTk
import time

# Import localization
from localization import t, set_language, get_language, get_available_languages, register_callback

# Import opzionali con gestione errori MKL Intel
HAS_NUMPY = False
HAS_OPENCV = False

try:
    # Tenta import numpy con gestione errore MKL
    import numpy as np
    HAS_NUMPY = True
    print("✓ NumPy disponibile per performance ottimizzate")
except ImportError:
    print("⚠ NumPy non disponibile - usando implementazioni pure Python")
    HAS_NUMPY = False
except Exception as e:
    # Gestisce errori MKL Intel specificamente
    if "mkl" in str(e).lower() or "intel" in str(e).lower():
        print("⚠ Errore Intel MKL rilevato - disabilitando NumPy")
        print(f"  Errore specifico: {e}")
        print("  Suggerimento: pip uninstall numpy && pip install numpy==1.24.3")
        HAS_NUMPY = False
    else:
        print(f"⚠ Errore NumPy generico: {e}")
        HAS_NUMPY = False

try:
    import cv2
    HAS_OPENCV = True
    print("✓ OpenCV disponibile per elaborazioni avanzate")
except ImportError:
    print("⚠ OpenCV non disponibile")
    HAS_OPENCV = False
except Exception as e:
    print(f"⚠ Errore OpenCV: {e}")
    HAS_OPENCV = False


class AdvancedStreetViewDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title(t('app_title'))
        self.root.geometry("1000x800")
        
        # Registra callback per aggiornamenti localizzazione
        register_callback(self.update_ui_language)
        
        # Variabili per il download
        self.current_image = None
        self.current_photo = None
        self.download_queue = []
        self.current_download_index = 0
        self.is_downloading = False
        
        # Pattern per estrazione PanoID
        self.panoid_patterns = [
            r'!1s([a-zA-Z0-9_-]{20,})',
            r'"pano":"([a-zA-Z0-9_-]{20,})"',
            r'"panoid":"([a-zA-Z0-9_-]{20,})"',
            r'pano:"([a-zA-Z0-9_-]{20,})"',
            r'"panoId":"([a-zA-Z0-9_-]{20,})"',
            r'photosphereId=([a-zA-Z0-9_-]{20,})',
            r'panoid=([a-zA-Z0-9_-]{20,})',
            r'pano=([a-zA-Z0-9_-]{20,})',
        ]
        
        # Mappa per referenze widget che necessitano traduzione
        self.ui_elements = {}
        
        self.setup_ui()
    
    def update_ui_language(self):
        """Aggiorna tutti i testi dell'interfaccia con la lingua corrente"""
        # Aggiorna titolo finestra
        self.root.title(t('app_title'))
        
        # Aggiorna menu (solo se esiste)
        if hasattr(self, 'menubar'):
            try:
                # Ottieni i menu esistenti
                file_menu_index = 0
                lang_menu_index = 1
                
                # Aggiorna labels dei menu principali
                self.menubar.entryconfig(file_menu_index, label=t('menu_file'))
                self.menubar.entryconfig(lang_menu_index, label=t('menu_language'))
            except:
                pass  # Ignora errori menu
        
        # Aggiorna tab labels
        if hasattr(self, 'notebook'):
            try:
                self.notebook.tab(0, text=t('tab_streetview'))
                self.notebook.tab(1, text=t('tab_local_files'))
                self.notebook.tab(2, text=t('tab_batch'))
            except:
                pass  # Ignora errori tab
        
        # Aggiorna tutti i widget tracciati
        for element_key, widget in self.ui_elements.items():
            if hasattr(widget, 'config'):
                try:
                    # Per i frame LabelFrame aggiorna il testo
                    if isinstance(widget, ttk.LabelFrame):
                        if element_key.endswith('_frame'):
                            key = element_key.replace('_frame', '')
                            widget.config(text=t(key))
                    # Per i label, button e radiobutton aggiorna il testo
                    elif hasattr(widget, 'config'):
                        if element_key in ['sv_title', 'sv_resolution_label', 'sv_overlap_label', 
                                         'sv_format_label', 'sv_extract_btn', 'sv_download_btn', 
                                         'sv_save_btn', 'validate_btn', 'clear_btn']:
                            widget.config(text=t(element_key))
                        elif element_key in ['sv_format_equirect', 'sv_format_cubemap']:
                            widget.config(text=t(element_key))
                except:
                    pass  # Ignora errori di aggiornamento widget
        
        # Aggiorna status messages dinamici
        if hasattr(self, 'status_single_var'):
            try:
                current_status = self.status_single_var.get()
                if current_status in ["Pronto", "Ready"]:
                    self.status_single_var.set(t('status_ready'))
            except:
                pass
        
        # Aggiorna preview label
        if hasattr(self, 'preview_single'):
            try:
                current_text = self.preview_single.cget('text')
                if 'immagine caricata' in current_text or 'image loaded' in current_text:
                    self.preview_single.config(text=t('no_image_loaded'))
            except:
                pass
        
        # Forza aggiornamento display
        try:
            self.root.update_idletasks()
        except:
            pass
        
    def setup_ui(self):
        """Configura l'interfaccia utente avanzata"""
        
        # Crea menu con selettore lingua
        self.create_menu()
        
        # Notebook per le diverse sezioni
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tab 1: Download da Street View
        self.streetview_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.streetview_frame, text=t('tab_streetview'))
        self.setup_streetview_tab()
        
        # Tab 2: Conversione File Locali
        self.local_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.local_frame, text=t('tab_local_files'))
        self.setup_local_tab()
        
        # Tab 3: Download Multipli
        self.batch_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.batch_frame, text=t('tab_batch'))
        self.setup_batch_tab()
        
        # Status bar globale
        self.setup_status_bar()
    
    def create_menu(self):
        """Crea la barra dei menu con selettore lingua"""
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        
        # Menu File
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=t('menu_file'), menu=file_menu)
        file_menu.add_command(label=t('menu_exit'), command=self.root.quit)
        
        # Menu Lingua
        language_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=t('menu_language'), menu=language_menu)
        language_menu.add_command(label="English", command=lambda: set_language('en'))
        language_menu.add_command(label="Italiano", command=lambda: set_language('it'))
        
    def setup_streetview_tab(self):
        """Configura il tab per download singolo da Street View"""
        frame = self.streetview_frame
        
        # Titolo
        title_label = ttk.Label(frame, text=t('sv_title'), 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(10, 20))
        self.ui_elements['sv_title'] = title_label
        
        # Frame principale
        main_frame = ttk.Frame(frame)
        main_frame.pack(fill="both", expand=True, padx=20)
        
        # URL Input
        url_frame = ttk.LabelFrame(main_frame, text=t('sv_url_label'), padding="10")
        url_frame.pack(fill="x", pady=(0, 10))
        self.ui_elements['sv_url_frame'] = url_frame
        
        self.url_var = tk.StringVar()
        url_entry = ttk.Entry(url_frame, textvariable=self.url_var, width=60)
        url_entry.pack(side="left", fill="x", expand=True)
        
        extract_btn = ttk.Button(url_frame, text=t('sv_extract_btn'), 
                                command=self.extract_panoid_single)
        extract_btn.pack(side="right", padx=(10, 0))
        self.ui_elements['sv_extract_btn'] = extract_btn
        
        # PanoID
        panoid_frame = ttk.LabelFrame(main_frame, text="PanoID", padding="10")
        panoid_frame.pack(fill="x", pady=(0, 10))
        
        self.panoid_var = tk.StringVar()
        panoid_entry = ttk.Entry(panoid_frame, textvariable=self.panoid_var, width=60)
        panoid_entry.pack(side="left", fill="x", expand=True)
        
        validate_btn = ttk.Button(panoid_frame, text=t('validate_btn'), 
                                 command=self.validate_panoid_single)
        validate_btn.pack(side="right", padx=(10, 0))
        self.ui_elements['validate_btn'] = validate_btn
        
        # Opzioni di download
        options_frame = ttk.LabelFrame(main_frame, text=t('sv_options_title'), padding="10")
        options_frame.pack(fill="x", pady=(0, 10))
        self.ui_elements['sv_options_frame'] = options_frame
        
        # Risoluzione
        res_frame = ttk.Frame(options_frame)
        res_frame.pack(fill="x", pady=(0, 5))
        
        res_label = ttk.Label(res_frame, text=t('sv_resolution_label'))
        res_label.pack(side="left")
        self.ui_elements['sv_resolution_label'] = res_label
        
        self.resolution_var = tk.StringVar(value="2")
        resolution_combo = ttk.Combobox(res_frame, textvariable=self.resolution_var, 
                                       values=["0", "1", "2", "3", "4"], state="readonly", width=5)
        resolution_combo.pack(side="left", padx=(10, 0))
        
        # Overlap rimosso: manteniamo la variabile per compatibilità, ma non usiamo la feature
        self.overlap_var = tk.StringVar(value="0")

        ttk.Label(res_frame, text="(0=512px, 1=1024px, 2=2048px, 3=4096px, 4=8192px)", 
                 font=("Arial", 8)).pack(side="left", padx=(10, 0))
        
        # Formato di output
        format_frame = ttk.Frame(options_frame)
        format_frame.pack(fill="x", pady=(5, 0))
        
        format_label = ttk.Label(format_frame, text=t('sv_format_label'))
        format_label.pack(side="left")
        self.ui_elements['sv_format_label'] = format_label
        
        self.output_format_var = tk.StringVar(value="equirectangular")
        
        equirect_radio = ttk.Radiobutton(format_frame, text=t('sv_format_equirect'), 
                                       variable=self.output_format_var, value="equirectangular")
        equirect_radio.pack(side="left", padx=(10, 0))
        self.ui_elements['sv_format_equirect'] = equirect_radio
        
        cubemap_radio = ttk.Radiobutton(format_frame, text=t('sv_format_cubemap'), 
                                      variable=self.output_format_var, value="cubemap")
        cubemap_radio.pack(side="left", padx=(10, 0))
        self.ui_elements['sv_format_cubemap'] = cubemap_radio
        
        # Pulsanti azione
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=20)

        download_btn = ttk.Button(button_frame, text=t('sv_download_btn'), 
                                 command=self.download_single)
        download_btn.pack(side="left", padx=(0, 10))
        self.ui_elements['sv_download_btn'] = download_btn
        
        save_btn = ttk.Button(button_frame, text=t('sv_save_btn'), 
                             command=self.save_single)
        save_btn.pack(side="left", padx=(0, 10))
        self.ui_elements['sv_save_btn'] = save_btn
        
        clear_btn = ttk.Button(button_frame, text=t('clear_btn'), 
                              command=self.clear_single)
        clear_btn.pack(side="left")
        self.ui_elements['clear_btn'] = clear_btn
        
        # Progress bar
        self.progress_single_var = tk.DoubleVar()
        self.progress_single = ttk.Progressbar(main_frame, variable=self.progress_single_var, 
                                             maximum=100, length=400)
        self.progress_single.pack(fill="x", pady=(10, 0))
        
        # Status label
        self.status_single_var = tk.StringVar(value=t('status_ready'))
        self.status_single = ttk.Label(main_frame, textvariable=self.status_single_var)
        self.status_single.pack(pady=(5, 0))
        
        # Anteprima
        preview_frame = ttk.LabelFrame(main_frame, text=t('sv_preview_title'), padding="10")
        preview_frame.pack(fill="both", expand=True, pady=(10, 0))
        self.ui_elements['sv_preview_frame'] = preview_frame
        
        self.preview_single = ttk.Label(preview_frame, text=t('no_image_loaded'))
        self.preview_single.pack(expand=True)
        
    def setup_local_tab(self):
        """Configura il tab per conversione file locali"""
        frame = self.local_frame
        
        # Titolo
        title_label = ttk.Label(frame, text="Conversione File Locali", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(10, 20))
        
        # Frame principale
        main_frame = ttk.Frame(frame)
        main_frame.pack(fill="both", expand=True, padx=20)
        
        # Selezione file/cartella
        input_frame = ttk.LabelFrame(main_frame, text="Selezione Input", padding="10")
        input_frame.pack(fill="x", pady=(0, 10))
        
        # Tipo input
        type_frame = ttk.Frame(input_frame)
        type_frame.pack(fill="x", pady=(0, 10))
        
        self.input_type_var = tk.StringVar(value="file")
        ttk.Radiobutton(type_frame, text="📄 File singolo", 
                       variable=self.input_type_var, value="file").pack(side="left")
        ttk.Radiobutton(type_frame, text="📁 Cartella", 
                       variable=self.input_type_var, value="folder").pack(side="left", padx=(20, 0))
        
        # Path input
        path_frame = ttk.Frame(input_frame)
        path_frame.pack(fill="x")
        
        self.input_path_var = tk.StringVar()
        path_entry = ttk.Entry(path_frame, textvariable=self.input_path_var, width=60)
        path_entry.pack(side="left", fill="x", expand=True)
        
        ttk.Button(path_frame, text="Sfoglia", 
                  command=self.browse_input).pack(side="right", padx=(10, 0))
        
        # Opzioni conversione
        convert_frame = ttk.LabelFrame(main_frame, text="Opzioni Conversione", padding="10")
        convert_frame.pack(fill="x", pady=(0, 10))
        
        # Direzione conversione
        direction_frame = ttk.Frame(convert_frame)
        direction_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(direction_frame, text="Converti da:").pack(side="left")
        self.convert_direction_var = tk.StringVar(value="equirect_to_cube")
        
        ttk.Radiobutton(direction_frame, text="Equirettangolare → Cubemap", 
                       variable=self.convert_direction_var, value="equirect_to_cube").pack(side="left", padx=(10, 0))
        ttk.Radiobutton(direction_frame, text="Cubemap → Equirettangolare", 
                       variable=self.convert_direction_var, value="cube_to_equirect").pack(side="left", padx=(10, 0))
        
        # Opzioni avanzate conversione
        advanced_frame = ttk.Frame(convert_frame)
        advanced_frame.pack(fill="x", pady=(5, 10))
        
        ttk.Label(advanced_frame, text="Overlap SfM:").pack(side="left")
        self.convert_overlap_var = tk.StringVar(value="0")
        overlap_combo = ttk.Combobox(advanced_frame, textvariable=self.convert_overlap_var,
                                    values=["0", "10", "20", "30", "40", "50"], 
                                    state="readonly", width=5)
        overlap_combo.pack(side="left", padx=(10, 0))
        ttk.Label(advanced_frame, text="% (solo per equirettangolari)").pack(side="left", padx=(5, 0))
        
        # Cartella output
        output_frame = ttk.Frame(convert_frame)
        output_frame.pack(fill="x")
        
        ttk.Label(output_frame, text="Cartella Output:").pack(side="left")
        self.output_path_var = tk.StringVar()
        output_entry = ttk.Entry(output_frame, textvariable=self.output_path_var, width=50)
        output_entry.pack(side="left", fill="x", expand=True, padx=(10, 0))
        
        ttk.Button(output_frame, text="Sfoglia", 
                  command=self.browse_output).pack(side="right", padx=(10, 0))
        
        # Pulsanti azione
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=20)
        
        ttk.Button(button_frame, text="🔄 Converti", 
                  command=self.convert_local_files).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="👁️ Anteprima", 
                  command=self.preview_local).pack(side="left")
        
        # Progress bar
        self.progress_local_var = tk.DoubleVar()
        self.progress_local = ttk.Progressbar(main_frame, variable=self.progress_local_var, 
                                            maximum=100, length=400)
        self.progress_local.pack(fill="x", pady=(10, 0))
        
        # Status e log
        self.status_local_var = tk.StringVar(value="Pronto")
        self.status_local = ttk.Label(main_frame, textvariable=self.status_local_var)
        self.status_local.pack(pady=(5, 0))
        
        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="Log Conversione", padding="10")
        log_frame.pack(fill="both", expand=True, pady=(10, 0))
        
        self.log_text = tk.Text(log_frame, height=8, wrap="word")
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def setup_batch_tab(self):
        """Configura il tab per download multipli"""
        frame = self.batch_frame
        
        # Titolo
        title_label = ttk.Label(frame, text="Download Multipli", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(10, 20))
        
        # Frame principale
        main_frame = ttk.Frame(frame)
        main_frame.pack(fill="both", expand=True, padx=20)
        
        # Lista URL
        url_list_frame = ttk.LabelFrame(main_frame, text="Lista URL", padding="10")
        url_list_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Frame per input URL
        input_frame = ttk.Frame(url_list_frame)
        input_frame.pack(fill="x", pady=(0, 10))
        
        self.batch_url_var = tk.StringVar()
        url_entry = ttk.Entry(input_frame, textvariable=self.batch_url_var)
        url_entry.pack(side="left", fill="x", expand=True)
        
        ttk.Button(input_frame, text="➕ Aggiungi", 
                  command=self.add_url_to_batch).pack(side="right", padx=(10, 0))
        
        # Lista URL con scrollbar
        list_frame = ttk.Frame(url_list_frame)
        list_frame.pack(fill="both", expand=True)
        
        self.url_listbox = tk.Listbox(list_frame, height=8)
        list_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.url_listbox.yview)
        self.url_listbox.configure(yscrollcommand=list_scrollbar.set)
        
        self.url_listbox.pack(side="left", fill="both", expand=True)
        list_scrollbar.pack(side="right", fill="y")
        
        # Pulsanti gestione lista
        list_buttons_frame = ttk.Frame(url_list_frame)
        list_buttons_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(list_buttons_frame, text="❌ Rimuovi Selezionato", 
                  command=self.remove_selected_url).pack(side="left", padx=(0, 10))
        ttk.Button(list_buttons_frame, text="🗑️ Pulisci Lista", 
                  command=self.clear_url_list).pack(side="left", padx=(0, 10))
        ttk.Button(list_buttons_frame, text="📁 Carica da File", 
                  command=self.load_urls_from_file).pack(side="left", padx=(0, 10))
        ttk.Button(list_buttons_frame, text="💾 Salva in File", 
                  command=self.save_urls_to_file).pack(side="left")
        
        # Opzioni batch
        batch_options_frame = ttk.LabelFrame(main_frame, text="Opzioni Download Multipli", padding="10")
        batch_options_frame.pack(fill="x", pady=(0, 10))
        
        # Prima riga opzioni
        options1_frame = ttk.Frame(batch_options_frame)
        options1_frame.pack(fill="x", pady=(0, 5))
        
        ttk.Label(options1_frame, text="Risoluzione:").pack(side="left")
        self.batch_resolution_var = tk.StringVar(value="2")
        batch_resolution_combo = ttk.Combobox(options1_frame, textvariable=self.batch_resolution_var, 
                                             values=["0", "1", "2", "3", "4"], state="readonly", width=5)
        batch_resolution_combo.pack(side="left", padx=(10, 20))
        
        ttk.Label(options1_frame, text="Overlap SfM:").pack(side="left")
        self.batch_overlap_var = tk.StringVar(value="0")
        batch_overlap_combo = ttk.Combobox(options1_frame, textvariable=self.batch_overlap_var,
                                          values=["0", "10", "20", "30", "40", "50"], 
                                          state="readonly", width=5)
        batch_overlap_combo.pack(side="left", padx=(10, 20))
        ttk.Label(options1_frame, text="%").pack(side="left")
        
        ttk.Label(options1_frame, text="Formato:").pack(side="left", padx=(20, 0))
        self.batch_format_var = tk.StringVar(value="equirectangular")
        
        ttk.Radiobutton(options1_frame, text="Equirettangolare", 
                       variable=self.batch_format_var, value="equirectangular").pack(side="left", padx=(10, 0))
        ttk.Radiobutton(options1_frame, text="Cubemap", 
                       variable=self.batch_format_var, value="cubemap").pack(side="left", padx=(10, 0))
        
        # Seconda riga opzioni
        options2_frame = ttk.Frame(batch_options_frame)
        options2_frame.pack(fill="x")
        
        ttk.Label(options2_frame, text="Cartella Output:").pack(side="left")
        self.batch_output_var = tk.StringVar()
        batch_output_entry = ttk.Entry(options2_frame, textvariable=self.batch_output_var, width=40)
        batch_output_entry.pack(side="left", fill="x", expand=True, padx=(10, 0))
        
        ttk.Button(options2_frame, text="Sfoglia", 
                  command=self.browse_batch_output).pack(side="right", padx=(10, 0))
        
        # Pulsanti azione batch
        batch_buttons_frame = ttk.Frame(main_frame)
        batch_buttons_frame.pack(fill="x", pady=20)
        
        ttk.Button(batch_buttons_frame, text="🚀 Avvia Download Multipli", 
                  command=self.start_batch_download).pack(side="left", padx=(0, 10))
        ttk.Button(batch_buttons_frame, text="⏹️ Ferma", 
                  command=self.stop_batch_download).pack(side="left", padx=(0, 10))
        ttk.Button(batch_buttons_frame, text="✅ Valida Tutti", 
                  command=self.validate_all_urls).pack(side="left")
        
        # Progress batch
        self.progress_batch_var = tk.DoubleVar()
        self.progress_batch = ttk.Progressbar(main_frame, variable=self.progress_batch_var, 
                                            maximum=100, length=400)
        self.progress_batch.pack(fill="x", pady=(10, 0))
        
        # Status batch
        self.status_batch_var = tk.StringVar(value="Pronto")
        self.status_batch = ttk.Label(main_frame, textvariable=self.status_batch_var)
        self.status_batch.pack(pady=(5, 0))
        
    def setup_status_bar(self):
        """Configura la status bar globale"""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill="x", side="bottom", pady=(5, 0))
        
        self.global_status_var = tk.StringVar(value="Google Street View Downloader Avanzato - Pronto")
        global_status = ttk.Label(status_frame, textvariable=self.global_status_var, 
                                 font=("Arial", 9))
        global_status.pack(side="left", padx=10)
        
        # Indicatore connessione
        self.connection_status_var = tk.StringVar(value="🟢 Online")
        connection_status = ttk.Label(status_frame, textvariable=self.connection_status_var)
        connection_status.pack(side="right", padx=10)
    
    # ========================================================================================
    # METODI TAB STREET VIEW SINGOLO
    # ========================================================================================
    
    def extract_panoid_from_url(self, url):
        """Estrae il PanoID dall'URL di Google Street View"""
        for pattern in self.panoid_patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def extract_panoid_single(self):
        """Estrae il PanoID dall'URL nel tab singolo"""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Errore", "Inserisci un URL di Google Street View")
            return
            
        self.status_single_var.set("Estrazione PanoID in corso...")
        
        panoid = self.extract_panoid_from_url(url)
        
        if panoid:
            self.panoid_var.set(panoid)
            self.status_single_var.set(f"PanoID estratto: {panoid}")
            self.validate_panoid_single()
        else:
            self.status_single_var.set("PanoID non trovato nell'URL")
            messagebox.showwarning("Avviso", 
                "Impossibile estrarre il PanoID dall'URL.\n\n" +
                "Assicurati di:\n" +
                "1. Essere in modalità Street View su Google Maps\n" +
                "2. Copiare l'URL completo dalla barra degli indirizzi\n" +
                "3. L'URL deve contenere il PanoID")
    
    def validate_panoid_single(self):
        """Valida un PanoID nel tab singolo"""
        panoid = self.panoid_var.get().strip()
        if not panoid:
            messagebox.showerror("Errore", "Inserisci un PanoID")
            return
            
        if len(panoid) < 20:
            self.status_single_var.set("PanoID troppo corto - non valido")
            return
            
        self.status_single_var.set("Validazione PanoID in corso...")
        
        def validate_thread():
            try:
                test_url = f"https://streetviewpixels-pa.googleapis.com/v1/tile?cb_client=maps_sv.tactile&panoid={panoid}&x=0&y=0&zoom=0&nbt=1&fover=2"
                response = requests.head(test_url, timeout=5)
                if response.status_code == 200:
                    self.status_single_var.set(f"✅ PanoID valido: {panoid}")
                    self.connection_status_var.set("🟢 Online")
                else:
                    self.status_single_var.set(f"❌ PanoID non valido (status: {response.status_code})")
            except Exception as e:
                self.status_single_var.set(f"❌ Errore validazione: {str(e)}")
                self.connection_status_var.set("🔴 Offline")
        
        threading.Thread(target=validate_thread, daemon=True).start()
    
    def download_single(self):
        """Download singolo da Street View"""
        panoid = self.panoid_var.get().strip()
        if not panoid:
            messagebox.showerror("Errore", "Inserisci un PanoID")
            return
            
        if self.is_downloading:
            messagebox.showwarning("Avviso", "Download già in corso")
            return
            
        def download_thread():
            try:
                self.is_downloading = True
                zoom = int(self.resolution_var.get())
                output_format = self.output_format_var.get()
                
                self.status_single_var.set("Download in corso...")
                self.global_status_var.set("Download Street View in corso...")
                self.progress_single_var.set(0)
                
                # Download immagine equirettangolare
                equirect_image = self.download_streetview_image(panoid, zoom, self.progress_single_var, self.status_single_var)
                
                if equirect_image:
                    # Non applichiamo overlap: esportiamo l'immagine così com'è
                    overlap_percent = 0

                    self.current_image = equirect_image
                    
                    if output_format == "equirectangular":
                        self.show_preview_single(equirect_image)
                        self.status_single_var.set(f"✅ Download completato! Immagine {equirect_image.size[0]}×{equirect_image.size[1]}")
                    else:  # cubemap
                        self.status_single_var.set("Conversione in cubemap...")
                        cubemap_faces = self.equirect_to_cubemap(equirect_image)
                        self.current_image = cubemap_faces  # Salva le 6 facce
                        
                        # Mostra anteprima della faccia frontale
                        if 'front' in cubemap_faces:
                            self.show_preview_single(cubemap_faces['front'])
                        
                        self.status_single_var.set(f"✅ Cubemap generato! 6 facce {list(cubemap_faces.values())[0].size[0]}×{list(cubemap_faces.values())[0].size[1]}")
                    
                    self.progress_single_var.set(100)
                else:
                    self.status_single_var.set("❌ Download fallito")
                    
            except Exception as e:
                self.status_single_var.set(f"❌ Errore: {str(e)}")
                messagebox.showerror("Errore", f"Errore durante il download:\n{str(e)}")
            finally:
                self.is_downloading = False
                self.global_status_var.set("Pronto")
        
        threading.Thread(target=download_thread, daemon=True).start()
    
    def save_single(self):
        """Salva l'immagine singola"""
        if self.current_image is None:
            messagebox.showerror("Errore", "Nessuna immagine da salvare")
            return
        
        if isinstance(self.current_image, dict):  # Cubemap
            self.save_cubemap(self.current_image)
        else:  # Equirectangular
            self.save_equirectangular(self.current_image)
    
    def clear_single(self):
        """Pulisce i campi del tab singolo"""
        self.url_var.set("")
        self.panoid_var.set("")
        self.current_image = None
        self.current_photo = None
        self.preview_single.configure(image="", text="Nessuna immagine caricata")
        self.status_single_var.set("Pronto")
        self.progress_single_var.set(0)
    
    def show_preview_single(self, image):
        """Mostra anteprima nel tab singolo"""
        preview_size = (400, 200)
        preview_image = image.copy()
        preview_image.thumbnail(preview_size, Image.Resampling.LANCZOS)
        
        photo = ImageTk.PhotoImage(preview_image)
        self.preview_single.configure(image=photo, text="")
        self.current_photo = photo
    
    # ========================================================================================
    # METODI TAB FILE LOCALI
    # ========================================================================================
    
    def browse_input(self):
        """Sfoglia per selezionare file o cartella input"""
        if self.input_type_var.get() == "file":
            filename = filedialog.askopenfilename(
                title="Seleziona immagine equirettangolare",
                filetypes=[
                    ("Immagini", "*.jpg *.jpeg *.png *.bmp *.tiff"),
                    ("JPEG", "*.jpg *.jpeg"),
                    ("PNG", "*.png"),
                    ("Tutti i file", "*.*")
                ]
            )
            if filename:
                self.input_path_var.set(filename)
        else:
            folder = filedialog.askdirectory(title="Seleziona cartella con immagini")
            if folder:
                self.input_path_var.set(folder)
    
    def browse_output(self):
        """Sfoglia per selezionare cartella output"""
        folder = filedialog.askdirectory(title="Seleziona cartella di destinazione")
        if folder:
            self.output_path_var.set(folder)
    
    def convert_local_files(self):
        """Converte file locali"""
        input_path = self.input_path_var.get().strip()
        output_path = self.output_path_var.get().strip()
        
        if not input_path:
            messagebox.showerror("Errore", "Seleziona file o cartella di input")
            return
        
        if not output_path:
            messagebox.showerror("Errore", "Seleziona cartella di output")
            return
        
        if not os.path.exists(input_path):
            messagebox.showerror("Errore", "Il percorso di input non esiste")
            return
        
        def convert_thread():
            try:
                self.log_message("🚀 Avvio conversione file locali...")
                
                # Trova tutti i file da processare
                files_to_process = []
                
                if self.input_type_var.get() == "file":
                    if os.path.isfile(input_path):
                        files_to_process.append(input_path)
                else:  # folder
                    extensions = ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.tiff"]
                    for ext in extensions:
                        files_to_process.extend(glob.glob(os.path.join(input_path, ext)))
                        files_to_process.extend(glob.glob(os.path.join(input_path, ext.upper())))
                
                if not files_to_process:
                    self.log_message("❌ Nessun file immagine trovato")
                    return
                
                total_files = len(files_to_process)
                self.log_message(f"📁 Trovati {total_files} file da processare")
                
                direction = self.convert_direction_var.get()
                overlap_percent = int(self.convert_overlap_var.get())
                
                for i, file_path in enumerate(files_to_process):
                    try:
                        overlap_info = f" (overlap {overlap_percent}%)" if overlap_percent > 0 else ""
                        self.log_message(f"🔄 Elaborazione {os.path.basename(file_path)}{overlap_info}...")
                        
                        # Aggiorna progress
                        progress = (i / total_files) * 100
                        self.progress_local_var.set(progress)
                        self.status_local_var.set(f"Elaborazione {i+1}/{total_files}: {os.path.basename(file_path)}")
                        
                        # Carica immagine
                        image = Image.open(file_path)
                        base_name = os.path.splitext(os.path.basename(file_path))[0]
                        
                        if direction == "equirect_to_cube":
                            # Applica overlap se richiesto e se è equirettangolare
                            if overlap_percent > 0:
                                image = self.create_overlap_image(image, overlap_percent)
                                base_name += f"_overlap{overlap_percent}"
                            
                            # Converti da equirettangolare a cubemap
                            cubemap = self.equirect_to_cubemap(image)
                            
                            # Salva le 6 facce
                            for face_name, face_image in cubemap.items():
                                output_filename = f"{base_name}_{face_name}.jpg"
                                output_filepath = os.path.join(output_path, output_filename)
                                face_image.save(output_filepath, quality=95)
                            
                            self.log_message(f"✅ {base_name}: 6 facce cubemap salvate")
                            
                        else:  # cube_to_equirect
                            # Implementazione conversione cubemap to equirect
                            # (richiede logica più complessa per riconoscere le 6 facce)
                            self.log_message(f"⚠️ {base_name}: Conversione cubemap→equirect non ancora implementata")
                        
                    except Exception as e:
                        self.log_message(f"❌ Errore su {os.path.basename(file_path)}: {str(e)}")
                
                self.progress_local_var.set(100)
                self.status_local_var.set(f"✅ Conversione completata: {total_files} file processati")
                self.log_message("🎉 Conversione completata!")
                
            except Exception as e:
                self.log_message(f"❌ Errore generale: {str(e)}")
                messagebox.showerror("Errore", f"Errore durante la conversione:\n{str(e)}")
        
        threading.Thread(target=convert_thread, daemon=True).start()
    
    def preview_local(self):
        """Anteprima file locale"""
        input_path = self.input_path_var.get().strip()
        
        if not input_path or not os.path.exists(input_path):
            messagebox.showerror("Errore", "Seleziona un file valido")
            return
        
        if os.path.isfile(input_path):
            try:
                image = Image.open(input_path)
                
                # Crea finestra anteprima
                preview_window = tk.Toplevel(self.root)
                preview_window.title(f"Anteprima: {os.path.basename(input_path)}")
                preview_window.geometry("600x400")
                
                # Ridimensiona per anteprima
                display_image = image.copy()
                display_image.thumbnail((580, 350), Image.Resampling.LANCZOS)
                
                photo = ImageTk.PhotoImage(display_image)
                label = ttk.Label(preview_window, image=photo)
                label.pack(expand=True)
                
                # Info immagine
                info_text = f"Dimensioni: {image.size[0]}×{image.size[1]} pixel\nFormato: {image.format}\nModalità: {image.mode}"
                info_label = ttk.Label(preview_window, text=info_text)
                info_label.pack(pady=10)
                
                # Mantieni riferimento al PhotoImage per evitare garbage collection (usare setattr per evitare errori del type checker)
                setattr(label, "_image", photo)
                setattr(preview_window, "_image", photo)
                
            except Exception as e:
                messagebox.showerror("Errore", f"Impossibile aprire l'immagine:\n{str(e)}")
    
    def log_message(self, message):
        """Aggiunge messaggio al log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    # ========================================================================================
    # METODI TAB DOWNLOAD MULTIPLI
    # ========================================================================================
    
    def add_url_to_batch(self):
        """Aggiunge URL alla lista batch"""
        url = self.batch_url_var.get().strip()
        if not url:
            messagebox.showerror("Errore", "Inserisci un URL")
            return
        
        # Verifica se l'URL è già presente
        current_urls = list(self.url_listbox.get(0, tk.END))
        if url in current_urls:
            messagebox.showwarning("Avviso", "URL già presente nella lista")
            return
        
        # Aggiungi alla lista
        self.url_listbox.insert(tk.END, url)
        self.batch_url_var.set("")  # Pulisci campo input
        
        self.status_batch_var.set(f"URL aggiunti: {self.url_listbox.size()}")
    
    def remove_selected_url(self):
        """Rimuove URL selezionato dalla lista"""
        selection = self.url_listbox.curselection()
        if not selection:
            messagebox.showwarning("Avviso", "Seleziona un URL da rimuovere")
            return
        
        # Rimuovi dalla fine per mantenere gli indici corretti
        for index in reversed(selection):
            self.url_listbox.delete(index)
        
        self.status_batch_var.set(f"URL nella lista: {self.url_listbox.size()}")
    
    def clear_url_list(self):
        """Pulisce la lista URL"""
        if self.url_listbox.size() > 0:
            if messagebox.askyesno("Conferma", "Cancellare tutti gli URL dalla lista?"):
                self.url_listbox.delete(0, tk.END)
                self.status_batch_var.set("Lista URL vuota")
    
    def load_urls_from_file(self):
        """Carica URL da file di testo"""
        filename = filedialog.askopenfilename(
            title="Carica lista URL",
            filetypes=[
                ("File di testo", "*.txt"),
                ("Tutti i file", "*.*")
            ]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    urls = [line.strip() for line in f if line.strip()]
                
                for url in urls:
                    if url not in list(self.url_listbox.get(0, tk.END)):
                        self.url_listbox.insert(tk.END, url)
                
                self.status_batch_var.set(f"Caricati {len(urls)} URL da file")
                messagebox.showinfo("Successo", f"Caricati {len(urls)} URL da {os.path.basename(filename)}")
                
            except Exception as e:
                messagebox.showerror("Errore", f"Errore nel caricamento del file:\n{str(e)}")
    
    def save_urls_to_file(self):
        """Salva lista URL in file"""
        if self.url_listbox.size() == 0:
            messagebox.showwarning("Avviso", "Nessun URL da salvare")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Salva lista URL",
            defaultextension=".txt",
            filetypes=[
                ("File di testo", "*.txt"),
                ("Tutti i file", "*.*")
            ]
        )
        
        if filename:
            try:
                urls = list(self.url_listbox.get(0, tk.END))
                with open(filename, 'w', encoding='utf-8') as f:
                    for url in urls:
                        f.write(url + '\n')
                
                messagebox.showinfo("Successo", f"Salvati {len(urls)} URL in {os.path.basename(filename)}")
                
            except Exception as e:
                messagebox.showerror("Errore", f"Errore nel salvataggio:\n{str(e)}")
    
    def browse_batch_output(self):
        """Sfoglia cartella output per batch"""
        folder = filedialog.askdirectory(title="Seleziona cartella per download multipli")
        if folder:
            self.batch_output_var.set(folder)
    
    def validate_all_urls(self):
        """Valida tutti gli URL nella lista"""
        if self.url_listbox.size() == 0:
            messagebox.showwarning("Avviso", "Nessun URL da validare")
            return
        
        def validate_thread():
            urls = list(self.url_listbox.get(0, tk.END))
            valid_count = 0
            
            self.status_batch_var.set("Validazione URL in corso...")
            
            for i, url in enumerate(urls):
                progress = (i / len(urls)) * 100
                self.progress_batch_var.set(progress)
                self.status_batch_var.set(f"Validazione {i+1}/{len(urls)}: {url[:50]}...")
                
                panoid = self.extract_panoid_from_url(url)
                if panoid and self.validate_panoid(panoid):
                    valid_count += 1
            
            self.progress_batch_var.set(100)
            self.status_batch_var.set(f"Validazione completata: {valid_count}/{len(urls)} URL validi")
            
            messagebox.showinfo("Validazione Completata", 
                f"Risultato validazione:\n✅ URL validi: {valid_count}\n❌ URL non validi: {len(urls)-valid_count}")
        
        threading.Thread(target=validate_thread, daemon=True).start()
    
    def start_batch_download(self):
        """Avvia download multipli"""
        if self.url_listbox.size() == 0:
            messagebox.showwarning("Avviso", "Nessun URL nella lista")
            return
        
        output_folder = self.batch_output_var.get().strip()
        if not output_folder:
            messagebox.showerror("Errore", "Seleziona cartella di output")
            return
        
        if not os.path.exists(output_folder):
            try:
                os.makedirs(output_folder)
            except Exception as e:
                messagebox.showerror("Errore", f"Impossibile creare la cartella:\n{str(e)}")
                return
        
        if self.is_downloading:
            messagebox.showwarning("Avviso", "Download già in corso")
            return
        
        def batch_download_thread():
            try:
                self.is_downloading = True
                urls = list(self.url_listbox.get(0, tk.END))
                resolution = int(self.batch_resolution_var.get())
                output_format = self.batch_format_var.get()
                overlap_percent = int(self.batch_overlap_var.get())
                
                successful_downloads = 0
                failed_downloads = 0
                
                for i, url in enumerate(urls):
                    if not self.is_downloading:  # Check se fermato
                        break
                    
                    try:
                        # Aggiorna progress
                        progress = (i / len(urls)) * 100
                        self.progress_batch_var.set(progress)
                        overlap_info = f" (overlap {overlap_percent}%)" if overlap_percent > 0 else ""
                        self.status_batch_var.set(f"Download {i+1}/{len(urls)}: {url[:50]}...{overlap_info}")
                        self.global_status_var.set(f"Download batch: {i+1}/{len(urls)}")
                        
                        # Estrai PanoID
                        panoid = self.extract_panoid_from_url(url)
                        if not panoid:
                            failed_downloads += 1
                            continue
                        
                        # Download immagine
                        equirect_image = self.download_streetview_image(panoid, resolution)
                        
                        if equirect_image:
                            # Applica overlap se richiesto
                            if overlap_percent > 0:
                                equirect_image = self.create_overlap_image(equirect_image, overlap_percent, panoid)
                            
                            # Genera nome file
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            overlap_suffix = f"_overlap{overlap_percent}" if overlap_percent > 0 else ""
                            base_filename = f"streetview_{panoid[:8]}_{timestamp}{overlap_suffix}"
                            
                            if output_format == "equirectangular":
                                output_path = os.path.join(output_folder, f"{base_filename}.jpg")
                                equirect_image.save(output_path, quality=95)
                            else:  # cubemap
                                cubemap = self.equirect_to_cubemap(equirect_image)
                                for face_name, face_image in cubemap.items():
                                    output_path = os.path.join(output_folder, f"{base_filename}_{face_name}.jpg")
                                    face_image.save(output_path, quality=95)
                            
                            successful_downloads += 1
                        else:
                            failed_downloads += 1
                    
                    except Exception as e:
                        print(f"Errore download {url}: {e}")
                        failed_downloads += 1
                
                self.progress_batch_var.set(100)
                self.status_batch_var.set(f"✅ Batch completato: {successful_downloads} successi, {failed_downloads} fallimenti")
                
                messagebox.showinfo("Download Completato", 
                    f"Download multipli completati!\n✅ Successi: {successful_downloads}\n❌ Fallimenti: {failed_downloads}")
                
            except Exception as e:
                messagebox.showerror("Errore", f"Errore durante il download batch:\n{str(e)}")
            finally:
                self.is_downloading = False
                self.global_status_var.set("Pronto")
        
        threading.Thread(target=batch_download_thread, daemon=True).start()
    
    def stop_batch_download(self):
        """Ferma download multipli"""
        if self.is_downloading:
            if messagebox.askyesno("Conferma", "Fermare il download in corso?"):
                self.is_downloading = False
                self.status_batch_var.set("❌ Download fermato dall'utente")
                self.global_status_var.set("Pronto")
        else:
            messagebox.showinfo("Info", "Nessun download in corso")
    
    # ========================================================================================
    # METODI CORE - DOWNLOAD E CONVERSIONE
    # ========================================================================================
    
    def get_tile_url(self, panoid, x, y, zoom=2):
        """Genera l'URL per scaricare una tile specifica"""
        return f"https://streetviewpixels-pa.googleapis.com/v1/tile?cb_client=maps_sv.tactile&panoid={panoid}&x={x}&y={y}&zoom={zoom}&nbt=1&fover=2"
    
    def validate_panoid(self, panoid):
        """Valida un PanoID"""
        if not panoid or len(panoid) < 20:
            return False
            
        test_url = self.get_tile_url(panoid, 0, 0, 0)
        try:
            response = requests.head(test_url, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def download_streetview_image(self, panoid, zoom, progress_var=None, status_var=None):
        """Download immagine Street View completa"""
        try:
            # Calcola dimensioni tiles
            tile_size = 512
            # Configurazione zoom corretta per Google Street View
            zoom_config = {
                0: (1, 1),      # 512x512
                1: (2, 1),      # 1024x512  
                2: (4, 2),      # 2048x1024
                3: (8, 4),      # 4096x2048
                4: (16, 8),     # 8192x4096
                5: (32, 16)     # 16384x8192 (se disponibile)
            }
            
            # Verifica che zoom sia supportato
            if zoom not in zoom_config:
                print(f"⚠ Zoom {zoom} non supportato, uso zoom 2")
                zoom = 2
            
            tiles_x, tiles_y = zoom_config[zoom]
            print(f"📐 Download risoluzione zoom {zoom}: {tiles_x}x{tiles_y} tiles")
            
            # Crea immagine finale
            final_width = tiles_x * tile_size
            final_height = tiles_y * tile_size
            final_image = Image.new('RGB', (final_width, final_height))
            
            total_tiles = tiles_x * tiles_y
            downloaded_tiles = 0
            
            print(f"🔽 Inizio download {total_tiles} tiles...")
            
            # Download tiles con retry
            for y in range(tiles_y):
                for x in range(tiles_x):
                    url = self.get_tile_url(panoid, x, y, zoom)
                    
                    # Retry per tile fallite
                    success = False
                    for attempt in range(3):  # Max 3 tentativi
                        try:
                            response = requests.get(url, timeout=15)  # Timeout aumentato
                            if response.status_code == 200:
                                from io import BytesIO
                                tile_image = Image.open(BytesIO(response.content))
                                final_image.paste(tile_image, (x * tile_size, y * tile_size))
                                success = True
                                break
                            else:
                                print(f"  ⚠ Tile ({x},{y}) status {response.status_code}, tentativo {attempt+1}")
                        
                        except Exception as e:
                            print(f"  ❌ Tile ({x},{y}) errore: {e}, tentativo {attempt+1}")
                            time.sleep(0.5)  # Pausa prima retry
                    
                    if not success:
                        # Tile definitivamente fallita - usa grigio
                        print(f"  💀 Tile ({x},{y}) fallita definitivamente")
                        error_tile = Image.new('RGB', (tile_size, tile_size), (64, 64, 64))
                        final_image.paste(error_tile, (x * tile_size, y * tile_size))
                    
                    downloaded_tiles += 1
                    
                    # Aggiorna progress
                    if progress_var:
                        progress = (downloaded_tiles / total_tiles) * 100
                        progress_var.set(progress)
                    
                    if status_var:
                        status_var.set(f"Download: {downloaded_tiles}/{total_tiles} tiles")
                        
                    # Small delay per evitare rate limiting
                    time.sleep(0.1)
            
            return final_image
        except Exception as e:
            # Gestione errore generale del download dell'immagine
            if status_var:
                try:
                    status_var.set(f"❌ Errore download tiles: {str(e)}")
                except Exception:
                    pass
            try:
                self.connection_status_var.set("🔴 Offline")
            except Exception:
                pass
            print(f"Errore download_streetview_image: {e}")
            return None
    
    def create_overlap_image(self, base_image, overlap_percent, panoid=None):
        """Overlap removed: compatibility no-op returning base image."""
        return base_image
    
    def _fill_overlap_borders_v2(self, expanded_image, base_image, offset_x, offset_y, overlap_ratio):
        """Riempie i bordi dell'immagine espansa mantenendo proporzioni 2:1"""
        width, height = base_image.size
        exp_width, exp_height = expanded_image.size
        
        # Bordo sinistro - wraparound orizzontale
        if offset_x > 0:
            # Prendi parte destra dell'immagine base per il bordo sinistro
            strip_width = offset_x
            right_strip = base_image.crop((width - strip_width, 0, width, height))
            
            # Scala verticalmente se necessario per riempire altezza espansa
            if exp_height != height:
                right_strip = right_strip.resize((strip_width, exp_height), Image.Resampling.LANCZOS)
            
            expanded_image.paste(right_strip, (0, offset_y))
        
        # Bordo destro - wraparound orizzontale  
        remaining_width = exp_width - (offset_x + width)
        if remaining_width > 0:
            # Prendi parte sinistra dell'immagine base per il bordo destro
            left_strip = base_image.crop((0, 0, remaining_width, height))
            
            # Scala verticalmente se necessario
            if exp_height != height:
                left_strip = left_strip.resize((remaining_width, exp_height), Image.Resampling.LANCZOS)
            
            expanded_image.paste(left_strip, (offset_x + width, offset_y))
        
        # Bordi superiore e inferiore - stretch orizzontale dell'equatore
        if offset_y > 0:
            # Usa le righe equatoriali per il bordo superiore
            equator_y = height // 2
            equator_strip = base_image.crop((0, equator_y - 5, width, equator_y + 5))
            equator_resized = equator_strip.resize((width, offset_y), Image.Resampling.LANCZOS)
            expanded_image.paste(equator_resized, (offset_x, 0))
            
            # Riempi anche i bordi sinistro/destro dell'area superiore
            if offset_x > 0:
                # Bordo superiore sinistro
                eq_left = equator_strip.crop((width - offset_x, 0, width, 10))
                eq_left_resized = eq_left.resize((offset_x, offset_y), Image.Resampling.LANCZOS)
                expanded_image.paste(eq_left_resized, (0, 0))
            
            if remaining_width > 0:
                # Bordo superiore destro
                eq_right = equator_strip.crop((0, 0, remaining_width, 10))
                eq_right_resized = eq_right.resize((remaining_width, offset_y), Image.Resampling.LANCZOS)
                expanded_image.paste(eq_right_resized, (offset_x + width, 0))
        
        # Bordo inferiore
        remaining_height = exp_height - (offset_y + height)
        if remaining_height > 0:
            # Usa le righe equatoriali per il bordo inferiore
            equator_y = height // 2
            equator_strip = base_image.crop((0, equator_y - 5, width, equator_y + 5))
            equator_resized = equator_strip.resize((width, remaining_height), Image.Resampling.LANCZOS)
            expanded_image.paste(equator_resized, (offset_x, offset_y + height))
            
            # Riempi anche i bordi sinistro/destro dell'area inferiore
            if offset_x > 0:
                # Bordo inferiore sinistro
                eq_left = equator_strip.crop((width - offset_x, 0, width, 10))
                eq_left_resized = eq_left.resize((offset_x, remaining_height), Image.Resampling.LANCZOS)
                expanded_image.paste(eq_left_resized, (0, offset_y + height))
            
            if remaining_width > 0:
                # Bordo inferiore destro
                eq_right = equator_strip.crop((0, 0, remaining_width, 10))
                eq_right_resized = eq_right.resize((remaining_width, remaining_height), Image.Resampling.LANCZOS)
                expanded_image.paste(eq_right_resized, (offset_x + width, offset_y + height))
    
    def _fill_corner_overlaps(self, expanded_image, base_image, offset_x, offset_y):
        """Riempie gli angoli dell'immagine espansa con interpolazione"""
        exp_width, exp_height = expanded_image.size
        width, height = base_image.size
        
        # Dimensioni angoli
        corner_w = offset_x
        corner_h = offset_y
        
        if corner_w > 0 and corner_h > 0:
            # Angolo top-left
            corner_tl = base_image.crop((width - corner_w, 0, width, corner_h))
            expanded_image.paste(corner_tl, (0, 0))
            
            # Angolo top-right
            corner_tr = base_image.crop((0, 0, corner_w, corner_h))
            expanded_image.paste(corner_tr, (offset_x + width, 0))
            
            # Angolo bottom-left
            corner_bl = base_image.crop((width - corner_w, height - corner_h, width, height))
            expanded_image.paste(corner_bl, (0, offset_y + height))
            
            # Angolo bottom-right
            corner_br = base_image.crop((0, height - corner_h, corner_w, height))
            expanded_image.paste(corner_br, (offset_x + width, offset_y + height))

    # -----------------------------------------------------------------
    # Metodi per download metadata e creazione overlap reale
    # -----------------------------------------------------------------
    def fetch_pano_metadata(self, panoid):
        """Scarica metadata di un pano (se disponibili) per ottenere link ai vicini."""
        try:
            url = f"https://maps.google.com/cbk?output=json&panoid={panoid}"
            resp = requests.get(url, timeout=10)
            if resp.status_code != 200:
                return None
            text = resp.text
            try:
                data = resp.json()
            except Exception:
                idx = text.find('{')
                if idx >= 0:
                    try:
                        data = json.loads(text[idx:])
                    except Exception:
                        return None
                else:
                    return None
            return data
        except Exception:
            return None

    def download_equirectangular_pano(self, panoid, zoom=2):
        """Scarica l'equirectangular di un pano usando download_streetview_image."""
        try:
            return self.download_streetview_image(panoid, zoom)
        except Exception:
            return None

    def _create_true_overlap(self, base_image, panoid, overlap_percent, zoom=2):
        """Crea overlap reale usando panorami limitrofi quando disponibili.

        Restituisce un'immagine espansa con blend dei crop dai vicini o None se non applicabile.
        """
        # Require OpenCV for true-overlap pipeline (for alignment & blending)
        try:
            import cv2 as _cv2  # local import to use the environment's OpenCV
        except Exception:
            print("⚠ OpenCV non disponibile localmente: salto true-overlap")
            return None

        try:
            meta = self.fetch_pano_metadata(panoid)
            if not meta:
                print("⚠ Metadata non trovati: useremo vicini sintetici (shift dell'equirettangolare)")
                links = None

            links = None
            if isinstance(meta, dict):
                for key in ['Links', 'links', 'l', 'data']:
                    if key in meta:
                        # alcuni endpoint annidano i dati
                        links = meta[key]
                        break
                if links is None and 'data' in meta and isinstance(meta['data'], dict):
                    for key in ['Links', 'links', 'l']:
                        if key in meta['data']:
                            links = meta['data'][key]
                            break

            # Precompute sizes for synthetic neighbor creation if needed
            width, height = base_image.size
            ov_w = int(width * (overlap_percent / 100.0))
            ov_h = int(height * (overlap_percent / 100.0))

            if not links:
                # Create synthetic neighbors by horizontally rolling the base image.
                # This helps when metadata is not available but we still want a 'real' overlap.
                print("⚠ Metadata non trovati: uso vicini sintetici ottenuti shiftando l'equirettangolare")
                try:
                    def roll_image(im, dx):
                        w, h = im.size
                        dx = int(dx) % w
                        if dx == 0:
                            return im.copy()
                        left = im.crop((0, 0, dx, h))
                        right = im.crop((dx, 0, w, h))
                        new = Image.new('RGB', (w, h))
                        new.paste(right, (0, 0))
                        new.paste(left, (w - dx, 0))
                        return new

                    synth_shift = max(ov_w * 2, width // 4)
                    neigh_left_img = roll_image(base_image, synth_shift)
                    neigh_right_img = roll_image(base_image, -synth_shift)

                    links = [
                        {'img': neigh_left_img, 'side': 'left'},
                        {'img': neigh_right_img, 'side': 'right'},
                    ]
                except Exception as e:
                    print(f"⚠ Errore creazione vicini sintetici: {e}")
                    return None

            new_w = width + 2 * ov_w
            new_h = height + 2 * ov_h
            expanded = Image.new('RGB', (new_w, new_h))
            offset_x = ov_w
            offset_y = ov_h
            expanded.paste(base_image, (offset_x, offset_y))

            placed_left = False
            placed_right = False

            # ensure debug folder exists
            dbg_folder = os.path.join('debug_outputs', 'true_overlap_debug')
            try:
                os.makedirs(dbg_folder, exist_ok=True)
            except Exception:
                dbg_folder = None

            # links può essere lista di dict o array; iteriamo
            for link in links:
                try:
                    # allow pre-supplied neighbor images (synthetic case)
                    neigh_img = None
                    yaw = None
                    neighbor_panoid = None

                    if isinstance(link, dict) and 'img' in link:
                        neigh_img = link['img']
                        yaw = link.get('yaw') or None
                    else:
                        if isinstance(link, dict):
                            neighbor_panoid = link.get('pano') or link.get('panoid') or link.get('id')
                            yaw = link.get('yaw') or link.get('heading')
                        elif isinstance(link, (list, tuple)) and len(link) >= 2:
                            neighbor_panoid = link[0]
                            yaw = None

                        if neighbor_panoid:
                            neigh_img = self.download_equirectangular_pano(neighbor_panoid, zoom)

                    if neigh_img is None:
                        continue

                    # se necessario scala verticalmente
                    nw, nh = neigh_img.size
                    if nh != height:
                        neigh_scaled = neigh_img.resize((int(nw * (height / nh)), height), Image.Resampling.LANCZOS)
                    else:
                        neigh_scaled = neigh_img

                    # Decide side basandosi su yaw oppure tentativo greedy
                    side = None
                    if yaw is not None:
                        try:
                            yawf = float(yaw) % 360
                            if 45 <= yawf <= 135:
                                side = 'right'
                            elif 225 <= yawf <= 315:
                                side = 'left'
                        except Exception:
                            side = None

                    if side is None:
                        side = 'right' if not placed_right else ('left' if not placed_left else None)

                    if side == 'right' and not placed_right:
                        crop = neigh_scaled.crop((0, 0, ov_w, height))
                        crop = crop.resize((ov_w, height), Image.Resampling.LANCZOS)
                        base_strip = base_image.crop((width - ov_w, 0, width, height))
                        # Use OpenCV alignment + feather blending
                        try:
                            blended = self._align_and_feather_blend(base_strip, crop)
                        except Exception as e:
                            print(f"⚠ align/blend right failed: {e}")
                            blended = Image.blend(base_strip, crop, alpha=0.5)

                        expanded.paste(blended, (offset_x + width, offset_y))
                        placed_right = True
                        # save debug
                        if dbg_folder:
                            try:
                                base_strip.save(os.path.join(dbg_folder, f"{panoid}_base_right_strip.jpg"))
                                crop.save(os.path.join(dbg_folder, f"{panoid}_neigh_right_crop.jpg"))
                                blended.save(os.path.join(dbg_folder, f"{panoid}_blended_right.jpg"))
                            except Exception:
                                pass

                    elif side == 'left' and not placed_left:
                        crop = neigh_scaled.crop((neigh_scaled.size[0] - ov_w, 0, neigh_scaled.size[0], height))
                        crop = crop.resize((ov_w, height), Image.Resampling.LANCZOS)
                        base_strip = base_image.crop((0, 0, ov_w, height))
                        try:
                            blended = self._align_and_feather_blend(base_strip, crop)
                        except Exception as e:
                            print(f"⚠ align/blend left failed: {e}")
                            blended = Image.blend(base_strip, crop, alpha=0.5)

                        expanded.paste(blended, (0, offset_y))
                        placed_left = True
                        if dbg_folder:
                            try:
                                base_strip.save(os.path.join(dbg_folder, f"{panoid}_base_left_strip.jpg"))
                                crop.save(os.path.join(dbg_folder, f"{panoid}_neigh_left_crop.jpg"))
                                blended.save(os.path.join(dbg_folder, f"{panoid}_blended_left.jpg"))
                            except Exception:
                                pass

                    if placed_left and placed_right:
                        break

                except Exception:
                    continue

            if not (placed_left or placed_right):
                return None

            try:
                self._fill_overlap_borders_v2(expanded, base_image, offset_x, offset_y, overlap_percent/100.0)
            except Exception:
                pass

            return expanded

        except Exception as e:
            print(f"Errore _create_true_overlap: {e}")
            return None

    def _align_and_feather_blend(self, imgA, imgB, feather=0.2):
        """Allinea imgB su imgA usando feature-matching (ORB) e applica un blending sfumato.

        imgA, imgB: PIL Images (stesse dimensioni attese)
        feather: frazione della larghezza su cui applicare la dissolvenza
        """
        # Fallback semplice se OpenCV non disponibile
        if not HAS_OPENCV:
            return Image.blend(imgA, imgB, alpha=0.5)

        try:
            import cv2
            import numpy as np

            a = np.array(imgA.convert('RGB'))
            b = np.array(imgB.convert('RGB'))

            grayA = cv2.cvtColor(a, cv2.COLOR_RGB2GRAY)
            grayB = cv2.cvtColor(b, cv2.COLOR_RGB2GRAY)

            # ORB features
            # Create ORB detector (use getattr to keep static checkers happy)
            orb_creator = getattr(cv2, 'ORB_create', None)
            if orb_creator is None:
                # ORB not available in this OpenCV build - fallback
                return Image.blend(imgA, imgB, alpha=0.5)
            orb = orb_creator(1000)

            kp1, des1 = orb.detectAndCompute(grayA, None)
            kp2, des2 = orb.detectAndCompute(grayB, None)

            if des1 is None or des2 is None:
                return Image.blend(imgA, imgB, alpha=0.5)

            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
            matches = bf.match(des1, des2)
            matches = sorted(matches, key=lambda x: x.distance)

            if len(matches) < 8:
                return Image.blend(imgA, imgB, alpha=0.5)

            src_pts = np.array([kp2[m.trainIdx].pt for m in matches], dtype=np.float32).reshape(-1, 1, 2)
            dst_pts = np.array([kp1[m.queryIdx].pt for m in matches], dtype=np.float32).reshape(-1, 1, 2)

            M, mask = cv2.estimateAffinePartial2D(src_pts, dst_pts)
            if M is None:
                return Image.blend(imgA, imgB, alpha=0.5)

            h, w = grayA.shape
            warped = cv2.warpAffine(b, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

            # Create feather mask horizontally
            mask = np.zeros((h, w), dtype=np.float32)
            fw = int(w * feather)
            if fw < 1:
                fw = 1
            # Left to right fade
            mask[:, :fw] = np.linspace(1.0, 0.0, fw)
            mask[:, fw:w-fw] = 0.0
            mask[:, w-fw:] = np.linspace(0.0, 1.0, fw)

            # Combine with warped and original
            warped_f = warped.astype(np.float32)
            a_f = a.astype(np.float32)
            alpha = mask[:, :, None]
            # blended = a * (1-alpha) + warped * alpha  but we want seam across overlap area,
            # so use alpha for warped contribution
            blended = (a_f * (1.0 - alpha) + warped_f * alpha).astype(np.uint8)

            return Image.fromarray(blended)

        except Exception:
            return Image.blend(imgA, imgB, alpha=0.5)
    
    def equirect_to_cubemap(self, equirect_image, face_size=None):
        """Converte immagine equirettangolare in cubemap"""
        try:
            width, height = equirect_image.size
            
            # Dimensione automatica delle facce
            if face_size is None:
                face_size = height // 2
            
            # Le 6 facce del cubo
            faces = {}
            face_names = ['front', 'right', 'back', 'left', 'up', 'down']
            
            # Converte in array per elaborazione più veloce e usa campionamento bilineare
            import numpy as np
            if not HAS_NUMPY:
                # Fallback senza numpy
                return self.equirect_to_cubemap_simple(equirect_image, face_size)

            img_array = np.array(equirect_image).astype(np.float32)

            def bilinear_sample(xf, yf):
                # xf, yf can be floats; wrap x horizontally, clamp y
                # integer base indices (unwrapped for fractional computation)
                x0_unwrapped = np.floor(xf).astype(int)
                x0 = (x0_unwrapped % width).astype(int)
                y0 = np.floor(yf).astype(int)
                x1 = (x0 + 1) % width
                y1 = np.clip(y0 + 1, 0, height - 1)

                # fractional part (use unwrapped x0 for correct fraction)
                wx = xf - x0_unwrapped
                wy = yf - y0

                # sample four neighbors
                p00 = img_array[y0, x0]
                p10 = img_array[y0, x1]
                p01 = img_array[y1, x0]
                p11 = img_array[y1, x1]

                top = p00 * (1 - wx)[:, None] + p10 * (wx)[:, None]
                bottom = p01 * (1 - wx)[:, None] + p11 * (wx)[:, None]
                result = top * (1 - wy)[:, None] + bottom * (wy)[:, None]
                return result

            for i, face_name in enumerate(face_names):
                # Special-case pragmatic fixes requested by user:
                # - back: compose from rightmost + leftmost vertical strips (wrap-around) and resize
                # - up / down: take top/bottom strips rather than full spherical re-projection (avoids central artefacts)
                if face_name == 'back':
                    # angular width per face = 90deg -> corresponds to width/4 pixels in equirect
                    slice_w = max(1, width // 4)
                    # include a small overlap (15% of slice) to be safe
                    overlap_px = max(1, slice_w * 15 // 100)
                    right_strip = equirect_image.crop((width - slice_w - overlap_px, 0, width, height))
                    left_strip = equirect_image.crop((0, 0, slice_w + overlap_px, height))
                    combined = Image.new('RGB', (left_strip.width + right_strip.width, height))
                    # paste left then right to preserve original left/right ordering
                    combined.paste(left_strip, (0, 0))
                    combined.paste(right_strip, (left_strip.width, 0))
                    # Resize combined horizontally to face_size and vertically to face_size
                    face_img = combined.resize((face_size, face_size), Image.Resampling.LANCZOS)
                    faces[face_name] = face_img
                    continue

                if face_name == 'up' or face_name == 'down':
                    # take a tall strip from the top (up) or bottom (down) of the equirect and resize
                    # choose strip height as ~35% of image height (empirical)
                    strip_h = max(2, int(height * 0.35))
                    if face_name == 'up':
                        strip = equirect_image.crop((0, 0, width, strip_h))
                    else:
                        strip = equirect_image.crop((0, height - strip_h, width, height))
                    # center-crop horizontally to width (already full width) and resize to square face
                    face_img = strip.resize((face_size, face_size), Image.Resampling.LANCZOS)
                    faces[face_name] = face_img
                    continue

                # Generic case: spherical reprojection with bilinear sampling
                face = np.zeros((face_size, face_size, 3), dtype=np.uint8)

                for v in range(face_size):
                    uf = (np.arange(face_size, dtype=np.float32) + 0.5) / face_size
                    vf = float(v + 0.5) / face_size

                    # Converte coordinate cubo in coordinate sferiche
                    thetas = np.empty(face_size, dtype=np.float32)
                    phis = np.empty(face_size, dtype=np.float32)
                    for idx, u_val in enumerate(uf):
                        th, ph = self.cube_to_sphere_coords(float(u_val), float(vf), i)
                        thetas[idx] = th
                        phis[idx] = ph

                    # Mappa su coordinate equirettangolari (float)
                    xs = (thetas / (2 * math.pi) + 0.5) * width
                    ys = (phis / math.pi) * height
                    # ensure ys in [0, height-1]
                    ys = np.clip(ys, 0, height - 1 - 1e-6)

                    # Bilinear sampling per riga
                    samples = bilinear_sample(xs, ys)
                    face[v, :, :] = np.clip(samples, 0, 255).astype(np.uint8)

                faces[face_name] = Image.fromarray(face)
            
            return faces
            
        except Exception as e:
            print(f"Errore conversione cubemap: {e}")
            # Fallback - crea facce vuote
            return self.create_empty_cubemap(face_size or 512)
    
    def equirect_to_cubemap_simple(self, equirect_image, face_size):
        """Versione semplificata senza numpy"""
        width, height = equirect_image.size
        faces = {}
        face_names = ['front', 'right', 'back', 'left', 'up', 'down']
        
        for i, face_name in enumerate(face_names):
            face = Image.new('RGB', (face_size, face_size))
            
            for v in range(face_size):
                for u in range(face_size):
                    uf = (u + 0.5) / face_size
                    vf = (v + 0.5) / face_size
                    
                    theta, phi = self.cube_to_sphere_coords(uf, vf, i)
                    
                    x = int((theta / (2 * math.pi) + 0.5) * width) % width
                    y = int((phi / math.pi) * height)
                    y = max(0, min(height - 1, y))
                    
                    pixel = equirect_image.getpixel((x, y))
                    face.putpixel((u, v), pixel)
            
            faces[face_name] = face
        
        return faces
    
    def cube_to_sphere_coords(self, u, v, face):
        """Converte coordinate cubo in coordinate sferiche"""
        # Normalizza a [-1, 1]
        uu = u * 2.0 - 1.0
        vv = v * 2.0 - 1.0

        # Convert image Y (downward) to 3D Y (upward)
        y_common = -vv

        # Standard cube face mapping (assumes faces order: front, right, back, left, up, down)
        if face == 0:  # front (+Z)
            x, y, z = uu, y_common, 1.0
        elif face == 1:  # right (+X)
            x, y, z = 1.0, y_common, -uu
        elif face == 2:  # back (-Z)
            x, y, z = -uu, y_common, -1.0
        elif face == 3:  # left (-X)
            x, y, z = -1.0, y_common, uu
        elif face == 4:  # up (+Y)
            x, y, z = uu, 1.0, vv
        elif face == 5:  # down (-Y)
            x, y, z = uu, -1.0, -vv
        else:
            x, y, z = 1.0, 0.0, 0.0
        
        # Normalizza vettore
        length = math.sqrt(x*x + y*y + z*z)
        x, y, z = x/length, y/length, z/length
        
        # Converte in coordinate sferiche
        theta = math.atan2(z, x)
        phi = math.acos(max(-1, min(1, y)))  # Clamp per evitare errori numerici
        
        return theta, phi
    
    def create_empty_cubemap(self, face_size):
        """Crea cubemap vuoto per fallback"""
        faces = {}
        face_names = ['front', 'right', 'back', 'left', 'up', 'down']
        
        for face_name in face_names:
            faces[face_name] = Image.new('RGB', (face_size, face_size), color=(128, 128, 128))
        
        return faces
    
    # ========================================================================================
    # METODI SALVATAGGIO
    # ========================================================================================
    
    def save_equirectangular(self, image):
        """Salva immagine equirettangolare"""
        filename = filedialog.asksaveasfilename(
            title="Salva immagine equirettangolare",
            defaultextension=".jpg",
            filetypes=[
                ("JPEG files", "*.jpg"),
                ("PNG files", "*.png"),
                ("All files", "*.*")
            ]
        )
        
        if filename:
            try:
                image.save(filename, quality=95)
                messagebox.showinfo("Successo", f"Immagine salvata:\n{filename}")
            except Exception as e:
                messagebox.showerror("Errore", f"Errore nel salvataggio:\n{str(e)}")
    
    def save_cubemap(self, cubemap_faces):
        """Salva le 6 facce del cubemap"""
        folder = filedialog.askdirectory(title="Seleziona cartella per salvare cubemap")
        
        if folder:
            try:
                base_name = f"cubemap_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                saved_files = []
                
                for face_name, face_image in cubemap_faces.items():
                    filename = os.path.join(folder, f"{base_name}_{face_name}.jpg")
                    face_image.save(filename, quality=95)
                    saved_files.append(filename)
                
                files_list = '\n'.join([os.path.basename(f) for f in saved_files])
                messagebox.showinfo("Successo", f"Cubemap salvato in:\n{folder}\n\nFile creati:\n{files_list}")
                
            except Exception as e:
                messagebox.showerror("Errore", f"Errore nel salvataggio cubemap:\n{str(e)}")


def main():
    """Funzione principale"""
    root = tk.Tk()
    app = AdvancedStreetViewDownloader(root)
    
    # Centra la finestra
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()


if __name__ == "__main__":
    main()
