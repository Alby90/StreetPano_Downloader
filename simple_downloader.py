"""
Google Street View Downloader - Versione Semplificata
Un programma per scaricare e ricostruire immagini equirettangolari da Google Street View
Versione che non richiede Selenium
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


class SimpleStreetViewDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("Google Street View Downloader (Versione Semplificata)")
        self.root.geometry("800x600")
        
        # Variabili per il download
        self.current_image = None
        self.current_photo = None
        
        # Pattern per estrazione PanoID
        self.panoid_patterns = [
            r'!1s([a-zA-Z0-9_-]{20,})',  # Pattern principale Google Maps
            r'"pano":"([a-zA-Z0-9_-]{20,})"',  # Pattern JSON
            r'"panoid":"([a-zA-Z0-9_-]{20,})"',  # Pattern JSON alternativo
            r'pano:"([a-zA-Z0-9_-]{20,})"',  # Pattern JS
            r'"panoId":"([a-zA-Z0-9_-]{20,})"',  # Pattern alternativo
            r'photosphereId=([a-zA-Z0-9_-]{20,})',  # Pattern photosphere
            r'panoid=([a-zA-Z0-9_-]{20,})',  # Pattern URL diretto
            r'pano=([a-zA-Z0-9_-]{20,})',  # Pattern pano
        ]
        
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
        
        # Istruzioni
        info_text = """ISTRUZIONI:
1. Vai su Google Maps (maps.google.com)
2. Cerca una località e attiva Street View
3. Copia l'URL completo dalla barra degli indirizzi
4. Incolla l'URL qui sotto e clicca "Estrai PanoID"
5. Seleziona la risoluzione e clicca "Download Immagine" """
        
        info_label = ttk.Label(main_frame, text=info_text, justify=tk.LEFT, 
                              font=("Arial", 9), foreground="blue")
        info_label.grid(row=1, column=0, columnspan=3, pady=(0, 15), sticky="w")
        
        # URL Input
        ttk.Label(main_frame, text="URL Street View:").grid(row=2, column=0, sticky="w", pady=5)
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(main_frame, textvariable=self.url_var, width=50)
        self.url_entry.grid(row=2, column=1, sticky="ew", pady=5, padx=(10, 0))
        
        # Pulsante per estrarre PanoID
        ttk.Button(main_frame, text="Estrai PanoID", 
                  command=self.extract_panoid).grid(row=2, column=2, padx=(10, 0), pady=5)
        
        # PanoID Input (opzionale)
        ttk.Label(main_frame, text="PanoID:").grid(row=3, column=0, sticky="w", pady=5)
        self.panoid_var = tk.StringVar()
        self.panoid_entry = ttk.Entry(main_frame, textvariable=self.panoid_var, width=50)
        self.panoid_entry.grid(row=3, column=1, sticky="ew", pady=5, padx=(10, 0))
        
        # Pulsante per validare PanoID
        ttk.Button(main_frame, text="Valida", 
                  command=self.validate_panoid).grid(row=3, column=2, padx=(10, 0), pady=5)
        
        # Risoluzione
        ttk.Label(main_frame, text="Risoluzione:").grid(row=4, column=0, sticky="w", pady=5)
        self.resolution_var = tk.StringVar(value="2")
        resolution_combo = ttk.Combobox(main_frame, textvariable=self.resolution_var, 
                                       values=["0", "1", "2", "3", "4"], state="readonly", width=10)
        resolution_combo.grid(row=4, column=1, sticky="w", pady=5, padx=(10, 0))
        
        # Informazioni sulla risoluzione
        res_info = ttk.Label(main_frame, text="0=Bassa (512×512), 1=Media (1024×512), 2=Alta (2048×1024), 3=Molto Alta (4096×2048), 4=Massima (8192×4096)", 
                            font=("Arial", 8))
        res_info.grid(row=5, column=0, columnspan=3, sticky="w", padx=(10, 0))
        
        # Pulsanti principali
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="Download Immagine", 
                  command=self.download_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Salva Immagine", 
                  command=self.save_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Pulisci", 
                  command=self.clear_fields).pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, 
                                           maximum=100, length=300)
        self.progress_bar.grid(row=7, column=0, columnspan=3, pady=10, sticky="ew")
        
        # Status label
        self.status_var = tk.StringVar(value="Pronto")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.grid(row=8, column=0, columnspan=3, pady=5)
        
        # Frame per l'anteprima dell'immagine
        preview_frame = ttk.LabelFrame(main_frame, text="Anteprima", padding="10")
        preview_frame.grid(row=9, column=0, columnspan=3, pady=20, sticky="nsew")
        main_frame.rowconfigure(9, weight=1)
        
        self.preview_label = ttk.Label(preview_frame, text="Nessuna immagine caricata")
        self.preview_label.pack(expand=True)
        
    def extract_panoid_from_url(self, url):
        """Estrae il PanoID dall'URL di Google Street View"""
        for pattern in self.panoid_patterns:
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
        
        # Estrai con regex
        panoid = self.extract_panoid_from_url(url)
        
        if panoid:
            self.panoid_var.set(panoid)
            self.status_var.set(f"PanoID estratto: {panoid}")
            
            # Valida automaticamente
            self.validate_panoid()
        else:
            self.status_var.set("PanoID non trovato nell'URL")
            messagebox.showwarning("Avviso", 
                "Impossibile estrarre il PanoID dall'URL.\n\n" +
                "Assicurati di:\n" +
                "1. Essere in modalità Street View su Google Maps\n" +
                "2. Copiare l'URL completo dalla barra degli indirizzi\n" +
                "3. L'URL deve contenere il PanoID\n\n" +
                "In alternativa, inserisci manualmente il PanoID se lo conosci.")
                
    def validate_panoid(self):
        """Valida un PanoID verificando se esiste"""
        panoid = self.panoid_var.get().strip()
        if not panoid:
            messagebox.showerror("Errore", "Inserisci un PanoID")
            return
            
        if len(panoid) < 20:
            self.status_var.set("PanoID troppo corto - non valido")
            return
            
        # Testa se il PanoID esiste
        test_url = f"https://streetviewpixels-pa.googleapis.com/v1/tile?cb_client=maps_sv.tactile&panoid={panoid}&x=0&y=0&zoom=0&nbt=1&fover=2"
        
        self.status_var.set("Validazione PanoID in corso...")
        
        def validate_thread():
            try:
                response = requests.head(test_url, timeout=5)
                if response.status_code == 200:
                    self.status_var.set(f"PanoID valido: {panoid}")
                else:
                    self.status_var.set(f"PanoID non valido (status: {response.status_code})")
            except Exception as e:
                self.status_var.set(f"Errore nella validazione: {str(e)}")
        
        threading.Thread(target=validate_thread, daemon=True).start()
        
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
                zoom_config = {
                    0: (1, 1),
                    1: (2, 1),
                    2: (4, 2),
                    3: (8, 4),
                    4: (16, 8)
                }
                
                tiles_x, tiles_y = zoom_config[zoom]
                
                # Crea l'immagine finale
                final_width = tiles_x * tile_size
                final_height = tiles_y * tile_size
                final_image = Image.new('RGB', (final_width, final_height))
                
                total_tiles = tiles_x * tiles_y
                downloaded_tiles = 0
                failed_tiles = 0
                
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
                                # Se la tile non esiste, crea una tile grigia
                                empty_tile = Image.new('RGB', (tile_size, tile_size), (64, 64, 64))
                                final_image.paste(empty_tile, (x * tile_size, y * tile_size))
                                failed_tiles += 1
                                
                        except Exception as e:
                            print(f"Errore nel download della tile ({x}, {y}): {e}")
                            # Crea una tile rossa per indicare errore
                            error_tile = Image.new('RGB', (tile_size, tile_size), (128, 0, 0))
                            final_image.paste(error_tile, (x * tile_size, y * tile_size))
                            failed_tiles += 1
                        
                        downloaded_tiles += 1
                        progress = (downloaded_tiles / total_tiles) * 100
                        self.progress_var.set(progress)
                        self.status_var.set(f"Download: {downloaded_tiles}/{total_tiles} tiles")
                
                # Salva l'immagine corrente
                self.current_image = final_image
                
                # Mostra l'anteprima
                self.show_preview(final_image)
                
                success_msg = f"Download completato! Immagine {final_width}×{final_height}"
                if failed_tiles > 0:
                    success_msg += f" ({failed_tiles} tiles non disponibili)"
                
                self.status_var.set(success_msg)
                self.progress_var.set(100)
                
            except Exception as e:
                self.status_var.set(f"Errore nel download: {str(e)}")
                messagebox.showerror("Errore", f"Errore durante il download:\n{str(e)}")
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
        panoid_short = self.panoid_var.get()[:8] if self.panoid_var.get() else "streetview"
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
                self.status_var.set(f"Immagine salvata: {os.path.basename(filename)}")
                messagebox.showinfo("Successo", f"Immagine salvata con successo in:\n{filename}")
            except Exception as e:
                messagebox.showerror("Errore", f"Errore nel salvataggio: {str(e)}")
                
    def clear_fields(self):
        """Pulisce tutti i campi"""
        self.url_var.set("")
        self.panoid_var.set("")
        self.current_image = None
        self.current_photo = None
        self.preview_label.configure(image="", text="Nessuna immagine caricata")
        self.status_var.set("Pronto")
        self.progress_var.set(0)


def main():
    """Funzione principale"""
    root = tk.Tk()
    app = SimpleStreetViewDownloader(root)
    
    # Centra la finestra
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()


if __name__ == "__main__":
    main()
