"""
Utility avanzate per conversioni tra formati panoramici
Supporta conversioni equirettangolare ↔ cubemap con algoritmi ottimizzati
"""

import math
import os
from PIL import Image
import glob

# Import opzionali
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    import cv2
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False


class PanoramaConverter:
    """Classe per conversioni tra formati panoramici"""
    
    def __init__(self):
        self.face_names = ['front', 'right', 'back', 'left', 'up', 'down']
        self.face_vectors = {
            'front': (1, 0, 0),   # +X
            'right': (0, 0, 1),   # +Z  
            'back': (-1, 0, 0),   # -X
            'left': (0, 0, -1),   # -Z
            'up': (0, 1, 0),      # +Y
            'down': (0, -1, 0)    # -Y
        }
    
    def equirectangular_to_cubemap(self, equirect_image, face_size=None, method='fast'):
        """
        Converte immagine equirettangolare in cubemap
        
        Args:
            equirect_image: PIL Image equirettangolare
            face_size: Dimensione facce cubo (None = auto)
            method: 'fast' o 'quality' 
        
        Returns:
            dict: {face_name: PIL_Image}
        """
        width, height = equirect_image.size
        
        if face_size is None:
            face_size = height // 2
        
        if method == 'quality' and HAS_NUMPY:
            return self._equirect_to_cube_numpy(equirect_image, face_size)
        else:
            return self._equirect_to_cube_simple(equirect_image, face_size)
    
    def _equirect_to_cube_numpy(self, equirect_image, face_size):
        """Conversione ottimizzata con NumPy"""
        width, height = equirect_image.size
        img_array = np.array(equirect_image)
        
        faces = {}
        
        for i, face_name in enumerate(self.face_names):
            # Crea griglia coordinate per la faccia
            u_coords = np.linspace(0, 1, face_size, endpoint=False) + 0.5/face_size
            v_coords = np.linspace(0, 1, face_size, endpoint=False) + 0.5/face_size
            
            u_grid, v_grid = np.meshgrid(u_coords, v_coords)
            
            # Converte coordinate cubo in sferiche (vettorizzato)
            theta_grid, phi_grid = self._cube_to_sphere_vectorized(u_grid, v_grid, i)
            
            # Mappa su coordinate equirettangolari
            x_coords = ((theta_grid / (2 * np.pi) + 0.5) * width).astype(int) % width
            y_coords = ((phi_grid / np.pi) * height).astype(int)
            y_coords = np.clip(y_coords, 0, height - 1)
            
            # Estrai pixel
            face_array = img_array[y_coords, x_coords]
            faces[face_name] = Image.fromarray(face_array.astype(np.uint8))
        
        return faces
    
    def _equirect_to_cube_simple(self, equirect_image, face_size):
        """Conversione semplice pixel per pixel"""
        width, height = equirect_image.size
        faces = {}
        
        for i, face_name in enumerate(self.face_names):
            face = Image.new('RGB', (face_size, face_size))
            
            for v in range(face_size):
                for u in range(face_size):
                    # Coordinate normalizzate
                    uf = (u + 0.5) / face_size
                    vf = (v + 0.5) / face_size
                    
                    # Converte in coordinate sferiche
                    theta, phi = self._cube_to_sphere_single(uf, vf, i)
                    
                    # Mappa su equirettangolare
                    x = int((theta / (2 * math.pi) + 0.5) * width) % width
                    y = int((phi / math.pi) * height)
                    y = max(0, min(height - 1, y))
                    
                    pixel = equirect_image.getpixel((x, y))
                    face.putpixel((u, v), pixel)
            
            faces[face_name] = face
        
        return faces
    
    def _cube_to_sphere_vectorized(self, u_grid, v_grid, face_index):
        """Conversione vettorizzata cubo → sfera con NumPy"""
        # Normalizza a [-1, 1]
        u_norm = u_grid * 2.0 - 1.0
        v_norm = v_grid * 2.0 - 1.0
        
        # Coordinate 3D del cubo
        if face_index == 0:  # front (+X)
            x, y, z = np.ones_like(u_norm), -v_norm, -u_norm
        elif face_index == 1:  # right (+Z)
            x, y, z = u_norm, -v_norm, np.ones_like(u_norm)
        elif face_index == 2:  # back (-X)
            x, y, z = -np.ones_like(u_norm), -v_norm, u_norm
        elif face_index == 3:  # left (-Z)
            x, y, z = -u_norm, -v_norm, -np.ones_like(u_norm)
        elif face_index == 4:  # up (+Y)
            x, y, z = u_norm, np.ones_like(u_norm), v_norm
        elif face_index == 5:  # down (-Y)
            x, y, z = u_norm, -np.ones_like(u_norm), -v_norm
        
        # Normalizza vettori
        length = np.sqrt(x*x + y*y + z*z)
        x, y, z = x/length, y/length, z/length
        
        # Coordinate sferiche
        theta = np.arctan2(z, x)
        phi = np.arccos(np.clip(y, -1, 1))
        
        return theta, phi
    
    def _cube_to_sphere_single(self, u, v, face_index):
        """Conversione singola cubo → sfera"""
        # Normalizza a [-1, 1]
        u = u * 2.0 - 1.0
        v = v * 2.0 - 1.0
        
        # Coordinate 3D del cubo
        if face_index == 0:  # front
            x, y, z = 1.0, -v, -u
        elif face_index == 1:  # right
            x, y, z = u, -v, 1.0
        elif face_index == 2:  # back
            x, y, z = -1.0, -v, u
        elif face_index == 3:  # left
            x, y, z = -u, -v, -1.0
        elif face_index == 4:  # up
            x, y, z = u, 1.0, v
        elif face_index == 5:  # down
            x, y, z = u, -1.0, -v
        else:
            x, y, z = 1.0, 0.0, 0.0
        
        # Normalizza
        length = math.sqrt(x*x + y*y + z*z)
        x, y, z = x/length, y/length, z/length
        
        # Coordinate sferiche
        theta = math.atan2(z, x)
        phi = math.acos(max(-1, min(1, y)))
        
        return theta, phi
    
    def cubemap_to_equirectangular(self, cubemap_faces, output_size=(2048, 1024)):
        """
        Converte cubemap in immagine equirettangolare
        
        Args:
            cubemap_faces: dict {face_name: PIL_Image}
            output_size: (width, height) output
        
        Returns:
            PIL Image equirettangolare
        """
        width, height = output_size
        
        if HAS_NUMPY:
            return self._cube_to_equirect_numpy(cubemap_faces, width, height)
        else:
            return self._cube_to_equirect_simple(cubemap_faces, width, height)
    
    def _cube_to_equirect_numpy(self, cubemap_faces, width, height):
        """Conversione cubemap → equirect con NumPy"""
        # Crea griglia coordinate equirettangolari
        u_coords = np.linspace(0, 1, width, endpoint=False) + 0.5/width
        v_coords = np.linspace(0, 1, height, endpoint=False) + 0.5/height
        
        u_grid, v_grid = np.meshgrid(u_coords, v_coords)
        
        # Converte in coordinate sferiche
        theta = (u_grid - 0.5) * 2 * np.pi
        phi = v_grid * np.pi
        
        # Converte in coordinate cartesiane
        x = np.cos(theta) * np.sin(phi)
        y = np.cos(phi)
        z = np.sin(theta) * np.sin(phi)
        
        # Determina quale faccia del cubo per ogni pixel
        abs_x, abs_y, abs_z = np.abs(x), np.abs(y), np.abs(z)
        
        # Inizializza output
        result = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Per ogni faccia del cubo
        for face_idx, face_name in enumerate(self.face_names):
            if face_name not in cubemap_faces:
                continue
                
            face_img = np.array(cubemap_faces[face_name])
            face_size = face_img.shape[0]
            
            # Determina maschera per questa faccia
            if face_idx == 0:  # front (+X)
                mask = (abs_x >= abs_y) & (abs_x >= abs_z) & (x > 0)
                u_face = (-z / x + 1) / 2
                v_face = (-y / x + 1) / 2
            elif face_idx == 1:  # right (+Z)
                mask = (abs_z >= abs_x) & (abs_z >= abs_y) & (z > 0)
                u_face = (x / z + 1) / 2
                v_face = (-y / z + 1) / 2
            elif face_idx == 2:  # back (-X)
                mask = (abs_x >= abs_y) & (abs_x >= abs_z) & (x < 0)
                u_face = (z / (-x) + 1) / 2
                v_face = (-y / (-x) + 1) / 2
            elif face_idx == 3:  # left (-Z)
                mask = (abs_z >= abs_x) & (abs_z >= abs_y) & (z < 0)
                u_face = (-x / (-z) + 1) / 2
                v_face = (-y / (-z) + 1) / 2
            elif face_idx == 4:  # up (+Y)
                mask = (abs_y >= abs_x) & (abs_y >= abs_z) & (y > 0)
                u_face = (x / y + 1) / 2
                v_face = (z / y + 1) / 2
            elif face_idx == 5:  # down (-Y)
                mask = (abs_y >= abs_x) & (abs_y >= abs_z) & (y < 0)
                u_face = (x / (-y) + 1) / 2
                v_face = (-z / (-y) + 1) / 2
            
            # Converte coordinate faccia in indici pixel
            u_face = np.clip(u_face, 0, 1)
            v_face = np.clip(v_face, 0, 1)
            
            u_indices = (u_face * (face_size - 1)).astype(int)
            v_indices = (v_face * (face_size - 1)).astype(int)
            
            # Applica maschera e copia pixel
            valid_mask = mask
            result[valid_mask] = face_img[v_indices[valid_mask], u_indices[valid_mask]]
        
        return Image.fromarray(result)
    
    def _cube_to_equirect_simple(self, cubemap_faces, width, height):
        """Conversione semplice cubemap → equirect"""
        result = Image.new('RGB', (width, height))
        
        for y in range(height):
            for x in range(width):
                # Coordinate normalizzate
                u = (x + 0.5) / width
                v = (y + 0.5) / height
                
                # Coordinate sferiche
                theta = (u - 0.5) * 2 * math.pi
                phi = v * math.pi
                
                # Coordinate cartesiane
                cart_x = math.cos(theta) * math.sin(phi)
                cart_y = math.cos(phi)
                cart_z = math.sin(theta) * math.sin(phi)
                
                # Determina faccia e coordinate
                face_name, face_u, face_v = self._sphere_to_cube_face(cart_x, cart_y, cart_z)
                
                if face_name in cubemap_faces:
                    face_img = cubemap_faces[face_name]
                    face_size = face_img.size[0]
                    
                    # Coordinate pixel nella faccia
                    pixel_u = int(face_u * (face_size - 1))
                    pixel_v = int(face_v * (face_size - 1))
                    
                    pixel_u = max(0, min(face_size - 1, pixel_u))
                    pixel_v = max(0, min(face_size - 1, pixel_v))
                    
                    pixel = face_img.getpixel((pixel_u, pixel_v))
                    result.putpixel((x, y), pixel)
        
        return result
    
    def _sphere_to_cube_face(self, x, y, z):
        """Determina faccia del cubo e coordinate UV da coordinate cartesiane"""
        abs_x, abs_y, abs_z = abs(x), abs(y), abs(z)
        
        if abs_x >= abs_y and abs_x >= abs_z:
            if x > 0:  # front
                return 'front', (-z / x + 1) / 2, (-y / x + 1) / 2
            else:  # back
                return 'back', (z / (-x) + 1) / 2, (-y / (-x) + 1) / 2
        elif abs_y >= abs_x and abs_y >= abs_z:
            if y > 0:  # up
                return 'up', (x / y + 1) / 2, (z / y + 1) / 2
            else:  # down
                return 'down', (x / (-y) + 1) / 2, (-z / (-y) + 1) / 2
        else:
            if z > 0:  # right
                return 'right', (x / z + 1) / 2, (-y / z + 1) / 2
            else:  # left
                return 'left', (-x / (-z) + 1) / 2, (-y / (-z) + 1) / 2


class BatchProcessor:
    """Processore batch per conversioni multiple"""
    
    def __init__(self):
        self.converter = PanoramaConverter()
        self.supported_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
    
    def process_folder(self, input_folder, output_folder, conversion_type='equirect_to_cube', 
                      face_size=None, output_size=(2048, 1024), progress_callback=None):
        """
        Processa tutti i file in una cartella
        
        Args:
            input_folder: Cartella input
            output_folder: Cartella output
            conversion_type: 'equirect_to_cube' o 'cube_to_equirect'
            face_size: Dimensione facce cubemap (None = auto)
            output_size: Dimensione output equirettangolare
            progress_callback: Funzione callback(current, total, filename)
        
        Returns:
            dict: Statistiche processamento
        """
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        # Trova tutti i file immagine
        image_files = []
        for ext in self.supported_extensions:
            image_files.extend(glob.glob(os.path.join(input_folder, f"*{ext}")))
            image_files.extend(glob.glob(os.path.join(input_folder, f"*{ext.upper()}")))
        
        total_files = len(image_files)
        processed = 0
        errors = []
        
        for i, file_path in enumerate(image_files):
            try:
                if progress_callback:
                    progress_callback(i, total_files, os.path.basename(file_path))
                
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                
                if conversion_type == 'equirect_to_cube':
                    # Converti in cubemap
                    equirect_img = Image.open(file_path)
                    cubemap = self.converter.equirectangular_to_cubemap(equirect_img, face_size)
                    
                    # Salva le 6 facce
                    for face_name, face_img in cubemap.items():
                        output_path = os.path.join(output_folder, f"{base_name}_{face_name}.jpg")
                        face_img.save(output_path, quality=95)
                    
                elif conversion_type == 'cube_to_equirect':
                    # Cerca le 6 facce del cubemap
                    cubemap_faces = self._load_cubemap_faces(input_folder, base_name)
                    if cubemap_faces:
                        equirect_img = self.converter.cubemap_to_equirectangular(cubemap_faces, output_size)
                        output_path = os.path.join(output_folder, f"{base_name}_equirect.jpg")
                        equirect_img.save(output_path, quality=95)
                
                processed += 1
                
            except Exception as e:
                errors.append((file_path, str(e)))
        
        return {
            'total_files': total_files,
            'processed': processed,
            'errors': errors
        }
    
    def _load_cubemap_faces(self, folder, base_name):
        """Carica le 6 facce di un cubemap"""
        faces = {}
        face_names = ['front', 'right', 'back', 'left', 'up', 'down']
        
        for face_name in face_names:
            for ext in self.supported_extensions:
                face_path = os.path.join(folder, f"{base_name}_{face_name}{ext}")
                if os.path.exists(face_path):
                    faces[face_name] = Image.open(face_path)
                    break
        
        # Verifica che ci siano almeno 4 facce
        return faces if len(faces) >= 4 else None
    
    def convert_single_file(self, input_path, output_folder, conversion_type='equirect_to_cube',
                           face_size=None, output_size=(2048, 1024)):
        """Converte singolo file"""
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"File non trovato: {input_path}")
        
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        
        if conversion_type == 'equirect_to_cube':
            equirect_img = Image.open(input_path)
            cubemap = self.converter.equirectangular_to_cubemap(equirect_img, face_size)
            
            saved_files = []
            for face_name, face_img in cubemap.items():
                output_path = os.path.join(output_folder, f"{base_name}_{face_name}.jpg")
                face_img.save(output_path, quality=95)
                saved_files.append(output_path)
            
            return saved_files
        
        elif conversion_type == 'cube_to_equirect':
            folder = os.path.dirname(input_path)
            cubemap_faces = self._load_cubemap_faces(folder, base_name)
            
            if not cubemap_faces:
                raise ValueError("Impossibile trovare tutte le facce del cubemap")
            
            equirect_img = self.converter.cubemap_to_equirectangular(cubemap_faces, output_size)
            output_path = os.path.join(output_folder, f"{base_name}_equirect.jpg")
            equirect_img.save(output_path, quality=95)
            
            return [output_path]


# Funzioni di utilità standalone
def quick_equirect_to_cubemap(input_path, output_folder, face_size=None):
    """Conversione rapida equirect → cubemap"""
    processor = BatchProcessor()
    return processor.convert_single_file(input_path, output_folder, 'equirect_to_cube', face_size)

def quick_cubemap_to_equirect(input_folder, base_name, output_folder, output_size=(2048, 1024)):
    """Conversione rapida cubemap → equirect"""
    processor = BatchProcessor()
    converter = PanoramaConverter()
    
    # Carica facce
    faces = {}
    face_names = ['front', 'right', 'back', 'left', 'up', 'down']
    
    for face_name in face_names:
        for ext in ['.jpg', '.jpeg', '.png']:
            face_path = os.path.join(input_folder, f"{base_name}_{face_name}{ext}")
            if os.path.exists(face_path):
                faces[face_name] = Image.open(face_path)
                break
    
    if len(faces) < 4:
        raise ValueError("Impossibile trovare almeno 4 facce del cubemap")
    
    # Converti
    equirect_img = converter.cubemap_to_equirectangular(faces, output_size)
    output_path = os.path.join(output_folder, f"{base_name}_equirect.jpg")
    equirect_img.save(output_path, quality=95)
    
    return output_path
