"""
Google Street View Downloader - Versione Avanzata
Supporta download multipli, conversione cubemap e elaborazione file locali
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests
import re
from PIL import Image, ImageTk
import os
import threading
import time
import urllib.parse
import json
from datetime import datetime
import math
import glob


class AdvancedStreetViewDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("Google Street View Downloader - Versione Avanzata")
        self.root.geometry("1000x800")
        
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
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configura l'interfaccia utente avanzata"""
        
        # Notebook per le diverse sezioni
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tab 1: Download da Street View
        self.streetview_frame = ttk.Frame(notebook)
        notebook.add(self.streetview_frame, text="📍 Download Street View")
        self.setup_streetview_tab()
        
        # Tab 2: Conversione File Locali
        self.local_frame = ttk.Frame(notebook)
        notebook.add(self.local_frame, text="📁 Conversione File Locali")
        self.setup_local_tab()
        
        # Tab 3: Download Multipli
        self.batch_frame = ttk.Frame(notebook)
        notebook.add(self.batch_frame, text="📋 Download Multipli")
        self.setup_batch_tab()
        
        # Status bar globale
        self.setup_status_bar()
        
    def setup_streetview_tab(self):
        """Configura il tab per download singolo da Street View"""
        frame = self.streetview_frame
        
        # Titolo
        title_label = ttk.Label(frame, text="Download Singolo da Google Street View", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(10, 20))
        
        # Frame principale
        main_frame = ttk.Frame(frame)
        main_frame.pack(fill="both", expand=True, padx=20)
        
        # URL Input
        url_frame = ttk.LabelFrame(main_frame, text="URL Street View", padding="10")
        url_frame.pack(fill="x", pady=(0, 10))
        
        self.url_var = tk.StringVar()
        url_entry = ttk.Entry(url_frame, textvariable=self.url_var, width=60)
        url_entry.pack(side="left", fill="x", expand=True)
        
        ttk.Button(url_frame, text="Estrai PanoID", 
                  command=self.extract_panoid_single).pack(side="right", padx=(10, 0))
        
        # PanoID
        panoid_frame = ttk.LabelFrame(main_frame, text="PanoID", padding="10")
        panoid_frame.pack(fill="x", pady=(0, 10))
        
        self.panoid_var = tk.StringVar()
        panoid_entry = ttk.Entry(panoid_frame, textvariable=self.panoid_var, width=60)
        panoid_entry.pack(side="left", fill="x", expand=True)
        
        ttk.Button(panoid_frame, text="Valida", 
                  command=self.validate_panoid_single).pack(side="right", padx=(10, 0))
        
        # Opzioni di download
        options_frame = ttk.LabelFrame(main_frame, text="Opzioni Download", padding="10")
        options_frame.pack(fill="x", pady=(0, 10))
        
        # Risoluzione
        res_frame = ttk.Frame(options_frame)
        res_frame.pack(fill="x", pady=(0, 5))
        
        ttk.Label(res_frame, text="Risoluzione:").pack(side="left")
        self.resolution_var = tk.StringVar(value="2")
        resolution_combo = ttk.Combobox(res_frame, textvariable=self.resolution_var, 
                                       values=["0", "1", "2", "3", "4"], state="readonly", width=5)
        resolution_combo.pack(side="left", padx=(10, 0))
        
        # Overlap per Structure from Motion
        overlap_frame = ttk.Frame(options_frame)
        overlap_frame.pack(fill="x", pady=(5, 5))
        
        ttk.Label(overlap_frame, text="Overlap SfM:").pack(side="left")
        self.overlap_var = tk.StringVar(value="0")
        overlap_combo = ttk.Combobox(overlap_frame, textvariable=self.overlap_var,
                                    values=["0", "10", "20", "30", "40", "50"], 
                                    state="readonly", width=5)
        overlap_combo.pack(side="left", padx=(10, 0))
        ttk.Label(overlap_frame, text="% (per photogrammetry)").pack(side="left", padx=(5, 0))
        
        ttk.Label(res_frame, text="(0=512px, 1=1024px, 2=2048px, 3=4096px, 4=8192px)", 
                 font=("Arial", 8)).pack(side="left", padx=(10, 0))
        
        # Formato di output
        format_frame = ttk.Frame(options_frame)
        format_frame.pack(fill="x", pady=(5, 0))
        
        ttk.Label(format_frame, text="Formato Output:").pack(side="left")
        self.output_format_var = tk.StringVar(value="equirectangular")
        
        equirect_radio = ttk.Radiobutton(format_frame, text="Equirettangolare", 
                                       variable=self.output_format_var, value="equirectangular")
        equirect_radio.pack(side="left", padx=(10, 0))
        
        cubemap_radio = ttk.Radiobutton(format_frame, text="Cubemap (6 file)", 
                                      variable=self.output_format_var, value="cubemap")
        cubemap_radio.pack(side="left", padx=(10, 0))
        
        # Pulsanti azione
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=20)
        
        ttk.Button(button_frame, text="📥 Download", 
                  command=self.download_single).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="💾 Salva", 
                  command=self.save_single).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="🗑️ Pulisci", 
                  command=self.clear_single).pack(side="left")
        
        # Progress bar
        self.progress_single_var = tk.DoubleVar()
        self.progress_single = ttk.Progressbar(main_frame, variable=self.progress_single_var, 
                                             maximum=100, length=400)
        self.progress_single.pack(fill="x", pady=(10, 0))
        
        # Status label
        self.status_single_var = tk.StringVar(value="Pronto")
        self.status_single = ttk.Label(main_frame, textvariable=self.status_single_var)
        self.status_single.pack(pady=(5, 0))
        
        # Anteprima
        preview_frame = ttk.LabelFrame(main_frame, text="Anteprima", padding="10")
        preview_frame.pack(fill="both", expand=True, pady=(10, 0))
        
        self.preview_single = ttk.Label(preview_frame, text="Nessuna immagine caricata")
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
                    # Applica overlap se richiesto
                    overlap_percent = int(self.overlap_var.get())
                    if overlap_percent > 0:
                        self.status_single_var.set(f"Applicazione overlap {overlap_percent}%...")
                        equirect_image = self.create_overlap_image(equirect_image, overlap_percent, panoid)
                    
                    self.current_image = equirect_image
                    
                    if output_format == "equirectangular":
                        self.show_preview_single(equirect_image)
                        overlap_info = f" (overlap {overlap_percent}%)" if overlap_percent > 0 else ""
                        self.status_single_var.set(f"✅ Download completato! Immagine {equirect_image.size[0]}×{equirect_image.size[1]}{overlap_info}")
                    else:  # cubemap
                        self.status_single_var.set("Conversione in cubemap...")
                        cubemap_faces = self.equirect_to_cubemap(equirect_image)
                        self.current_image = cubemap_faces  # Salva le 6 facce
                        
                        # Mostra anteprima della faccia frontale
                        if 'front' in cubemap_faces:
                            self.show_preview_single(cubemap_faces['front'])
                        
                        overlap_info = f" (da equirect con overlap {overlap_percent}%)" if overlap_percent > 0 else ""
                        self.status_single_var.set(f"✅ Cubemap generato! 6 facce {list(cubemap_faces.values())[0].size[0]}×{list(cubemap_faces.values())[0].size[1]}{overlap_info}")
                    
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
            zoom_config = {
                0: (1, 1),
                1: (2, 1), 
                2: (4, 2),
                3: (8, 4),
                4: (16, 8)
            }
            
            tiles_x, tiles_y = zoom_config[zoom]
            
            # Crea immagine finale
            final_width = tiles_x * tile_size
            final_height = tiles_y * tile_size
            final_image = Image.new('RGB', (final_width, final_height))
            
            total_tiles = tiles_x * tiles_y
            downloaded_tiles = 0
            
            # Download tiles
            for y in range(tiles_y):
                for x in range(tiles_x):
                    url = self.get_tile_url(panoid, x, y, zoom)
                    
                    try:
                        response = requests.get(url, timeout=10)
                        if response.status_code == 200:
                            from io import BytesIO
                            tile_image = Image.open(BytesIO(response.content))
                            final_image.paste(tile_image, (x * tile_size, y * tile_size))
                        else:
                            # Tile vuota
                            empty_tile = Image.new('RGB', (tile_size, tile_size), (64, 64, 64))
                            final_image.paste(empty_tile, (x * tile_size, y * tile_size))
                    
                    except Exception as e:
                        # Tile errore
                        error_tile = Image.new('RGB', (tile_size, tile_size), (128, 0, 0))
                        final_image.paste(error_tile, (x * tile_size, y * tile_size))
                    
                    downloaded_tiles += 1
                    
                    # Aggiorna progress
                    if progress_var:
                        progress = (downloaded_tiles / total_tiles) * 100
                        progress_var.set(progress)
                    
                    if status_var:
                        status_var.set(f"Download: {downloaded_tiles}/{total_tiles} tiles")
            
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
        """
        Crea immagine con overlap per Structure from Motion
        
        Args:
            base_image: Immagine equirettangolare base
            overlap_percent: Percentuale di overlap (0-50)
            panoid: PanoID per cercare immagini adiacenti
        
        Returns:
            PIL Image con overlap sui bordi
        """
        if overlap_percent <= 0:
            return base_image
            
        try:
            width, height = base_image.size
            overlap_ratio = overlap_percent / 100.0
            
            # Calcola nuove dimensioni con overlap
            new_width = int(width * (1 + overlap_ratio))
            new_height = int(height * (1 + overlap_ratio * 0.5))  # Overlap verticale minore
            
            # Crea immagine espansa
            expanded_image = Image.new('RGB', (new_width, new_height), (0, 0, 0))
            
            # Calcola offset per centrare l'immagine base
            offset_x = int(width * overlap_ratio * 0.5)
            offset_y = int(height * overlap_ratio * 0.25)
            
            # Incolla immagine base al centro
            expanded_image.paste(base_image, (offset_x, offset_y))
            
            # Genera bordi con overlap utilizzando wrapping panoramico
            self._fill_overlap_borders(expanded_image, base_image, offset_x, offset_y, overlap_ratio)
            
            return expanded_image
            
        except Exception as e:
            print(f"Errore creazione overlap: {e}")
            return base_image
    
    def _fill_overlap_borders(self, expanded_image, base_image, offset_x, offset_y, overlap_ratio):
        """Riempie i bordi dell'immagine espansa con overlap panoramico"""
        width, height = base_image.size
        
        # Bordo sinistro - wraparound orizzontale
        if offset_x > 0:
            # Prendi parte destra dell'immagine base per il bordo sinistro
            right_strip_width = offset_x
            right_strip = base_image.crop((width - right_strip_width, 0, width, height))
            expanded_image.paste(right_strip, (0, offset_y))
        
        # Bordo destro - wraparound orizzontale  
        exp_width, exp_height = expanded_image.size
        if exp_width > offset_x + width:
            # Prendi parte sinistra dell'immagine base per il bordo destro
            left_strip_width = exp_width - (offset_x + width)
            left_strip = base_image.crop((0, 0, left_strip_width, height))
            expanded_image.paste(left_strip, (offset_x + width, offset_y))
        
        # Bordo superiore - stretch dell'equatore
        if offset_y > 0:
            # Usa le righe equatoriali per il bordo superiore
            equator_y = height // 2
            top_strip_height = offset_y
            equator_strip = base_image.crop((0, equator_y - 10, width, equator_y + 10))
            equator_resized = equator_strip.resize((width, top_strip_height), Image.Resampling.LANCZOS)
            expanded_image.paste(equator_resized, (offset_x, 0))
        
        # Bordo inferiore - stretch dell'equatore
        if exp_height > offset_y + height:
            # Usa le righe equatoriali per il bordo inferiore
            equator_y = height // 2
            bottom_strip_height = exp_height - (offset_y + height)
            equator_strip = base_image.crop((0, equator_y - 10, width, equator_y + 10))
            equator_resized = equator_strip.resize((width, bottom_strip_height), Image.Resampling.LANCZOS)
            expanded_image.paste(equator_resized, (offset_x, offset_y + height))
        
        # Riempi gli angoli con interpolazione
        self._fill_corner_overlaps(expanded_image, base_image, offset_x, offset_y)
    
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
            
            # Converte in array per elaborazione più veloce
            import numpy as np
            if 'numpy' not in globals():
                # Fallback senza numpy
                return self.equirect_to_cubemap_simple(equirect_image, face_size)
            
            img_array = np.array(equirect_image)
            
            for i, face_name in enumerate(face_names):
                face = np.zeros((face_size, face_size, 3), dtype=np.uint8)
                
                for v in range(face_size):
                    for u in range(face_size):
                        # Coordinate normalizzate [0,1]
                        uf = (u + 0.5) / face_size
                        vf = (v + 0.5) / face_size
                        
                        # Converte coordinate cubo in coordinate sferiche
                        theta, phi = self.cube_to_sphere_coords(uf, vf, i)
                        
                        # Mappa su coordinate equirettangolari
                        x = int((theta / (2 * math.pi) + 0.5) * width) % width
                        y = int((phi / math.pi) * height)
                        y = max(0, min(height - 1, y))
                        
                        face[v, u] = img_array[y, x]
                
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
        u = u * 2.0 - 1.0
        v = v * 2.0 - 1.0
        
        # Coordinate 3D del cubo
        if face == 0:  # front
            x, y, z = 1.0, -v, -u
        elif face == 1:  # right
            x, y, z = u, -v, 1.0
        elif face == 2:  # back
            x, y, z = -1.0, -v, u
        elif face == 3:  # left
            x, y, z = -u, -v, -1.0
        elif face == 4:  # up
            x, y, z = u, 1.0, v
        elif face == 5:  # down
            x, y, z = u, -1.0, -v
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
            faces[face_name] = Image.new('RGB', (face_size, face_size), (128, 128, 128))
        
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
