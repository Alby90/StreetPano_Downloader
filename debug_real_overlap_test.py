# Debug script: prova conversione cubemap a partire da equirettangolari scaricate
from advanced_downloader import AdvancedStreetViewDownloader
import tkinter as tk
import os
import re

IMG_LIST = 'imag.txt'
OUT_DIR = 'debug_outputs'

if not os.path.exists(OUT_DIR):
    os.makedirs(OUT_DIR)

# Avvia una root tk minima per usare la classe (richiesta dal costruttore)
root = tk.Tk()
root.withdraw()
app = AdvancedStreetViewDownloader(root)

# Leggi le prime 5 righe del file
with open(IMG_LIST, 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f.readlines() if l.strip()]

panoids = []
for line in lines[:5]:
    # cerca panoid pattern
    m = re.search(r'panoid%3D([a-zA-Z0-9_-]{20,})', line)
    if not m:
        m = re.search(r'panoid=([a-zA-Z0-9_-]{20,})', line)
    if not m:
        # try common panoid pattern in URLs
        m = re.search(r'1s([a-zA-Z0-9_-]{20,})', line)
    if m:
        pano = m.group(1)
        panoids.append(pano)

print('Found panoids:', panoids)

for panoid in panoids:
    print('\n--- Processing', panoid)
    img = app.download_streetview_image(panoid, zoom=2)
    if img is None:
        print('Download failed for', panoid)
        continue
    # save base
    base_path = os.path.join(OUT_DIR, f'{panoid}_base.jpg')
    img.save(base_path)
    print('Saved base image to', base_path)

    # convert to cubemap (no overlap)
    faces = app.equirect_to_cubemap(img, face_size=None)
    if isinstance(faces, dict):
        for name, face in faces.items():
            p = os.path.join(OUT_DIR, f'{panoid}_face_{name}.jpg')
            face.save(p)
            print('Saved face', name, '->', p)
    else:
        print('Cubemap conversion returned unexpected type', type(faces))

print('\nDone')
root.destroy()