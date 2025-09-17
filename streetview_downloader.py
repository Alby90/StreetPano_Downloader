"""
Google Street View Equirectangular Image Downloader
Un programma per scaricare e ricostruire immagini equirettangolari da Google Street View
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests
import re
import json
from PIL import Image, ImageTk
import os
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import urllib.parse

# Import delle configurazioni e utilità
from config import (
    DOWNLOAD_CONFIG, BROWSER_CONFIG, UI_CONFIG, API_CONFIG, 
    ZOOM_LEVELS, PANOID_PATTERNS, MESSAGES
)
from streetview_utils import StreetViewUtils, PanoIDExtractor


class StreetViewDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("Google Street View Downloader")
        self.root.geometry("800x600")
        
        # Variabili per il download
        self.panoid = None
        self.current_image = None
        self.driver = None
        self.current_photo = None  # Per mantenere il riferimento all'immagine di anteprima
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configura l'interfaccia utente"""
        
        # Frame principale
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configurazione delle colonne e righe
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Titolo
        title_label = ttk.Label(main_frame, text="Google Street View Downloader", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # URL Input
        ttk.Label(main_frame, text="URL Street View:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(main_frame, textvariable=self.url_var, width=50)
        self.url_entry.grid(row=1, column=1, sticky="ew", pady=5, padx=(10, 0))
        
        # Pulsante per estrarre PanoID
        ttk.Button(main_frame, text="Estrai PanoID", 
                  command=self.extract_panoid).grid(row=1, column=2, padx=(10, 0), pady=5)
        
        # PanoID Input (opzionale)
        ttk.Label(main_frame, text="PanoID:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.panoid_var = tk.StringVar()
        self.panoid_entry = ttk.Entry(main_frame, textvariable=self.panoid_var, width=50)
        self.panoid_entry.grid(row=2, column=1, sticky="ew", pady=5, padx=(10, 0))
        
        # Risoluzione
        ttk.Label(main_frame, text="Risoluzione:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.resolution_var = tk.StringVar(value="2")
        resolution_combo = ttk.Combobox(main_frame, textvariable=self.resolution_var, 
                                       values=["0", "1", "2", "3", "4"], state="readonly", width=10)
        resolution_combo.grid(row=3, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Informazioni sulla risoluzione
        res_info = ttk.Label(main_frame, text="0=Bassa, 1=Media, 2=Alta, 3=Molto Alta, 4=Massima", 
                            font=("Arial", 8))
        res_info.grid(row=4, column=1, sticky=tk.W, padx=(10, 0))
        
        # Pulsanti principali
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="Download Immagine", 
                  command=self.download_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Apri Browser", 
                  command=self.open_browser).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Salva Immagine", 
                  command=self.save_image).pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, 
                                           maximum=100, length=300)
        self.progress_bar.grid(row=6, column=0, columnspan=3, pady=10, sticky="ew")
        
        # Status label
        self.status_var = tk.StringVar(value="Pronto")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.grid(row=7, column=0, columnspan=3, pady=5)
        
        # Frame per l'anteprima dell'immagine
        preview_frame = ttk.LabelFrame(main_frame, text="Anteprima", padding="10")
        preview_frame.grid(row=8, column=0, columnspan=3, pady=20, sticky="nsew")
        main_frame.rowconfigure(8, weight=1)
        
        self.preview_label = ttk.Label(preview_frame, text="Nessuna immagine caricata")
        self.preview_label.pack(expand=True)
        
    def extract_panoid_from_url(self, url):
        """Estrae il PanoID dall'URL di Google Street View"""
        patterns = [
            r'!1s([a-zA-Z0-9_-]+)',  # Pattern principale
            r'photosphereId=([a-zA-Z0-9_-]+)',  # Pattern alternativo
            r'panoid=([a-zA-Z0-9_-]+)',  # Pattern diretto
            r'pano=([a-zA-Z0-9_-]+)'  # Pattern pano
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
        
    def extract_panoid(self):
        """Estrae il PanoID dall'URL fornito"""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Errore", "Inserisci un URL di Google Street View")
            return
            
        self.status_var.set("Estrazione PanoID in corso...")
        
        def extract_thread():
            try:
                # Prima prova con regex sull'URL
                panoid = self.extract_panoid_from_url(url)
                
                if panoid:
                    self.panoid_var.set(panoid)
                    self.status_var.set(f"PanoID estratto: {panoid}")
                else:
                    # Se non funziona, prova con Selenium
                    self.extract_panoid_with_selenium(url)
                    
            except Exception as e:
                self.status_var.set(f"Errore nell'estrazione: {str(e)}")
                messagebox.showerror("Errore", f"Impossibile estrarre il PanoID: {str(e)}")
        
        threading.Thread(target=extract_thread, daemon=True).start()
        
    def extract_panoid_with_selenium(self, url):
        """Estrae il PanoID usando Selenium per analizzare la pagina"""
        try:
            self.status_var.set("Apertura browser per estrazione PanoID...")
            
            # Configura Chrome per headless
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Carica la pagina
            driver.get(url)
            time.sleep(5)  # Aspetta che la pagina si carichi
            
            # Cerca il PanoID nel codice JavaScript della pagina
            page_source = driver.page_source
            
            # Pattern per cercare il PanoID nel codice della pagina
            patterns = [
                r'"pano":"([a-zA-Z0-9_-]+)"',
                r'"panoid":"([a-zA-Z0-9_-]+)"',
                r'pano:"([a-zA-Z0-9_-]+)"',
                r'"panoId":"([a-zA-Z0-9_-]+)"'
            ]
            
            panoid = None
            for pattern in patterns:
                matches = re.findall(pattern, page_source)
                if matches:
                    panoid = matches[0]
                    break
            
            driver.quit()
            
            if panoid:
                self.panoid_var.set(panoid)
                self.status_var.set(f"PanoID estratto: {panoid}")
            else:
                self.status_var.set("PanoID non trovato nella pagina")
                messagebox.showwarning("Avviso", "Impossibile trovare il PanoID. Inseriscilo manualmente.")
                
        except Exception as e:
            self.status_var.set(f"Errore Selenium: {str(e)}")
            messagebox.showerror("Errore", f"Errore durante l'estrazione con browser: {str(e)}")
            
    def open_browser(self):
        """Apre un browser controllato per navigare Street View"""
        def browser_thread():
            try:
                self.status_var.set("Apertura browser...")
                
                chrome_options = Options()
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                
                # Apri Google Maps
                self.driver.get("https://www.google.com/maps")
                
                self.status_var.set("Browser aperto. Naviga su Street View e poi usa 'Estrai PanoID'")
                
            except Exception as e:
                self.status_var.set(f"Errore apertura browser: {str(e)}")
                messagebox.showerror("Errore", f"Impossibile aprire il browser: {str(e)}")
        
        threading.Thread(target=browser_thread, daemon=True).start()
        
    def get_tile_url(self, panoid, x, y, zoom=2):
        """Genera l'URL per scaricare una tile specifica"""
        return f"https://streetviewpixels-pa.googleapis.com/v1/tile?cb_client=maps_sv.tactile&panoid={panoid}&x={x}&y={y}&zoom={zoom}&nbt=1&fover=2"
        
    def download_image(self):
        """Scarica e ricostruisce l'immagine equirettangolare"""
        panoid = self.panoid_var.get().strip()
        if not panoid:
            messagebox.showerror("Errore", "Inserisci un PanoID")
            return
            
        def download_thread():
            try:
                zoom = int(self.resolution_var.get())
                self.status_var.set("Download in corso...")
                self.progress_var.set(0)
                
                # Calcola le dimensioni in base al livello di zoom
                tile_size = 512
                if zoom == 0:
                    tiles_x, tiles_y = 1, 1
                elif zoom == 1:
                    tiles_x, tiles_y = 2, 1
                elif zoom == 2:
                    tiles_x, tiles_y = 4, 2
                elif zoom == 3:
                    tiles_x, tiles_y = 8, 4
                else:  # zoom == 4
                    tiles_x, tiles_y = 16, 8
                
                # Crea l'immagine finale
                final_width = tiles_x * tile_size
                final_height = tiles_y * tile_size
                final_image = Image.new('RGB', (final_width, final_height))
                
                total_tiles = tiles_x * tiles_y
                downloaded_tiles = 0
                
                # Scarica ogni tile
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
                                # Se la tile non esiste, crea una tile vuota
                                empty_tile = Image.new('RGB', (tile_size, tile_size), (0, 0, 0))
                                final_image.paste(empty_tile, (x * tile_size, y * tile_size))
                                
                        except Exception as e:
                            print(f"Errore nel download della tile ({x}, {y}): {e}")
                            # Crea una tile vuota in caso di errore
                            empty_tile = Image.new('RGB', (tile_size, tile_size), (128, 128, 128))
                            final_image.paste(empty_tile, (x * tile_size, y * tile_size))
                        
                        downloaded_tiles += 1
                        progress = (downloaded_tiles / total_tiles) * 100
                        self.progress_var.set(progress)
                        self.status_var.set(f"Download: {downloaded_tiles}/{total_tiles} tiles")
                
                # Salva l'immagine corrente
                self.current_image = final_image
                
                # Mostra l'anteprima
                self.show_preview(final_image)
                
                self.status_var.set(f"Download completato! Immagine {final_width}x{final_height}")
                self.progress_var.set(100)
                
            except Exception as e:
                self.status_var.set(f"Errore nel download: {str(e)}")
                messagebox.showerror("Errore", f"Errore durante il download: {str(e)}")
                self.progress_var.set(0)
        
        threading.Thread(target=download_thread, daemon=True).start()
        
    def show_preview(self, image):
        """Mostra l'anteprima dell'immagine"""
        # Ridimensiona per l'anteprima
        preview_size = (400, 200)
        preview_image = image.copy()
        preview_image.thumbnail(preview_size, Image.Resampling.LANCZOS)
        
        # Converte per Tkinter
        photo = ImageTk.PhotoImage(preview_image)
        self.preview_label.configure(image=photo, text="")
        # Mantiene un riferimento per evitare garbage collection
        self.current_photo = photo
        
    def save_image(self):
        """Salva l'immagine corrente"""
        if self.current_image is None:
            messagebox.showerror("Errore", "Nessuna immagine da salvare")
            return
            
        # Chiedi dove salvare il file
        filename = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=[
                ("JPEG files", "*.jpg"),
                ("PNG files", "*.png"),
                ("All files", "*.*")
            ]
        )
        
        if filename:
            try:
                self.current_image.save(filename, quality=95)
                self.status_var.set(f"Immagine salvata: {filename}")
                messagebox.showinfo("Successo", f"Immagine salvata con successo in:\n{filename}")
            except Exception as e:
                messagebox.showerror("Errore", f"Errore nel salvataggio: {str(e)}")


def main():
    root = tk.Tk()
    app = StreetViewDownloader(root)
    root.mainloop()


if __name__ == "__main__":
    main()
