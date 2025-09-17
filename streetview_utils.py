"""
Utilità per il download e la manipolazione delle immagini Street View
"""

import requests
import re
import json
from PIL import Image
import math

# NumPy e OpenCV sono opzionali per funzionalità avanzate
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    print("NumPy non disponibile. Alcune funzionalità avanzate saranno disabilitate.")

try:
    import cv2
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False
    print("OpenCV non disponibile. Alcune funzionalità avanzate saranno disabilitate.")


class StreetViewUtils:
    """Classe di utilità per operazioni avanzate su Street View"""
    
    @staticmethod
    def extract_panoid_from_metadata(url):
        """
        Estrae il PanoID utilizzando l'API di metadata di Google Street View
        """
        # Estrae le coordinate dall'URL se possibile
        lat_lng_pattern = r'@(-?\d+\.\d+),(-?\d+\.\d+)'
        match = re.search(lat_lng_pattern, url)
        
        if match:
            lat, lng = float(match.group(1)), float(match.group(2))
            
            # Prova a ottenere il PanoID dalle coordinate usando l'API
            metadata_url = f"https://maps.googleapis.com/maps/api/streetview/metadata"
            params = {
                'location': f"{lat},{lng}",
                'key': 'YOUR_API_KEY'  # Sostituire con una chiave API valida
            }
            
            try:
                response = requests.get(metadata_url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'OK':
                        return data.get('pano_id')
            except:
                pass
                
        return None
    
    @staticmethod
    def enhance_equirectangular(image):
        """
        Migliora la qualità dell'immagine equirettangolare
        """
        if not HAS_OPENCV or not HAS_NUMPY:
            print("OpenCV o NumPy non disponibili. Restituisco l'immagine originale.")
            return image
            
        # Converte PIL in OpenCV
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Applica miglioramenti
        # 1. Rimozione del rumore
        denoised = cv2.fastNlMeansDenoisingColored(cv_image, None, 10, 10, 7, 21)
        
        # 2. Miglioramento del contrasto
        lab = cv2.cvtColor(denoised, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        l = clahe.apply(l)
        enhanced = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        
        # Converte di nuovo in PIL
        enhanced_pil = Image.fromarray(cv2.cvtColor(enhanced, cv2.COLOR_BGR2RGB))
        return enhanced_pil
    
    @staticmethod
    def create_cube_map(equirectangular_image):
        """
        Converte un'immagine equirettangolare in una cube map
        """
        if not HAS_NUMPY:
            print("NumPy non disponibile. Funzione cube map disabilitata.")
            return {}
            
        width, height = equirectangular_image.size
        face_size = height // 2
        
        # Converte in array numpy
        img_array = np.array(equirectangular_image)
        
        faces = {}
        face_names = ['front', 'right', 'back', 'left', 'up', 'down']
        
        for i, face_name in enumerate(face_names):
            face = np.zeros((face_size, face_size, 3), dtype=np.uint8)
            
            for y in range(face_size):
                for x in range(face_size):
                    # Calcola le coordinate della sphere
                    u = (x + 0.5) / face_size
                    v = (y + 0.5) / face_size
                    
                    # Converte le coordinate del cubo in coordinate sferiche
                    theta, phi = StreetViewUtils.cube_to_sphere(u, v, i)
                    
                    # Mappa le coordinate sferiche sull'immagine equirettangolare
                    img_x = int((theta / (2 * math.pi) + 0.5) * width) % width
                    img_y = int((phi / math.pi) * height)
                    img_y = max(0, min(height - 1, img_y))
                    
                    face[y, x] = img_array[img_y, img_x]
            
            faces[face_name] = Image.fromarray(face)
        
        return faces
    
    @staticmethod
    def cube_to_sphere(u, v, face):
        """
        Converte coordinate del cubo in coordinate sferiche
        """
        u = float(u * 2.0 - 1.0)
        v = float(v * 2.0 - 1.0)
        
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
            x, y, z = 1.0, 0.0, 0.0  # default case
        
        # Normalizza
        length = math.sqrt(float(x)*float(x) + float(y)*float(y) + float(z)*float(z))
        x, y, z = float(x)/length, float(y)/length, float(z)/length
        
        # Converte in coordinate sferiche
        theta = math.atan2(z, x)
        phi = math.acos(y)
        
        return theta, phi
    
    @staticmethod
    def get_available_zoom_levels(panoid):
        """
        Determina i livelli di zoom disponibili per un PanoID
        """
        available_levels = []
        
        for zoom in range(5):  # Testa zoom da 0 a 4
            test_url = f"https://streetviewpixels-pa.googleapis.com/v1/tile?cb_client=maps_sv.tactile&panoid={panoid}&x=0&y=0&zoom={zoom}&nbt=1&fover=2"
            
            try:
                response = requests.head(test_url, timeout=5)
                if response.status_code == 200:
                    available_levels.append(zoom)
            except:
                pass
        
        return available_levels
    
    @staticmethod
    def get_panorama_info(panoid):
        """
        Ottiene informazioni dettagliate su un panorama
        """
        info = {
            'panoid': panoid,
            'available_zooms': StreetViewUtils.get_available_zoom_levels(panoid),
            'max_resolution': None,
            'estimated_size': None
        }
        
        if info['available_zooms']:
            max_zoom = max(info['available_zooms'])
            info['max_resolution'] = max_zoom
            
            # Calcola la dimensione stimata
            if max_zoom == 0:
                info['estimated_size'] = (512, 512)
            elif max_zoom == 1:
                info['estimated_size'] = (1024, 512)
            elif max_zoom == 2:
                info['estimated_size'] = (2048, 1024)
            elif max_zoom == 3:
                info['estimated_size'] = (4096, 2048)
            elif max_zoom == 4:
                info['estimated_size'] = (8192, 4096)
        
        return info


class PanoIDExtractor:
    """Classe specializzata per l'estrazione di PanoID"""
    
    def __init__(self):
        self.patterns = [
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
    
    def extract_from_url(self, url):
        """Estrae PanoID dall'URL usando regex"""
        for pattern in self.patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def extract_from_page_source(self, page_source):
        """Estrae PanoID dal codice sorgente della pagina"""
        for pattern in self.patterns:
            matches = re.findall(pattern, page_source)
            if matches:
                # Restituisce il PanoID più lungo (solitamente quello corretto)
                return max(matches, key=len)
        return None
    
    def validate_panoid(self, panoid):
        """Valida un PanoID verificando se esiste"""
        if not panoid or len(panoid) < 20:
            return False
            
        test_url = f"https://streetviewpixels-pa.googleapis.com/v1/tile?cb_client=maps_sv.tactile&panoid={panoid}&x=0&y=0&zoom=0&nbt=1&fover=2"
        
        try:
            response = requests.head(test_url, timeout=5)
            return response.status_code == 200
        except:
            return False
