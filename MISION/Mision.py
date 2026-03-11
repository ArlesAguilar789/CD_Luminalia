import cv2
import numpy as np
import math
import os

# Obtiene la ruta exacta de la carpeta donde está guardado este script (MISION)
ruta_actual = os.path.dirname(os.path.abspath(__file__))

print("Iniciando procesamiento de misiones...")

# ==========================================
# MISIÓN 1: TRASLACIÓN (Artefacto Desplazado)
# ==========================================
print("Ejecutando Misión 1...")
ruta_img_1 = os.path.join(ruta_actual, 'vehiculo.jpg')
img_1 = cv2.imread(ruta_img_1)

if img_1 is not None:
    alto_1, ancho_1 = img_1.shape[:2]

    # Modo Raw (Usando slicing de NumPy)
    lienzo_raw_1 = np.zeros_like(img_1)
    lienzo_raw_1[200:alto_1, 300:ancho_1] = img_1[0:alto_1-200, 0:ancho_1-300]
    cv2.imwrite(os.path.join(ruta_actual, 'mision1_raw.jpg'), lienzo_raw_1)

    # Modo OpenCV
    M_1 = np.float32([[1, 0, 300], 
                      [0, 1, 200]])
    lienzo_cv2_1 = cv2.warpAffine(img_1, M_1, (ancho_1, alto_1))
    cv2.imwrite(os.path.join(ruta_actual, 'mision1_cv2.jpg'), lienzo_cv2_1)
else:
    print(f"Error: No se encontró 'vehiculo.jpg' en {ruta_actual}")

# ==========================================
# MISIÓN 2: ROTACIÓN (Código QR Rotado)
# ==========================================
print("Ejecutando Misión 2...")
ruta_img_2 = os.path.join(ruta_actual, 'qr_rotado.jpg')
img_2 = cv2.imread(ruta_img_2)

if img_2 is not None:
    alto_2, ancho_2 = img_2.shape[:2]
    cx, cy = 250, 250

    # Modo Raw
    lienzo_raw_2 = np.zeros_like(img_2)
    theta = math.radians(45) 
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)

    for y in range(alto_2):
        for x in range(ancho_2):
            nx = x - cx
            ny = y - cy
            src_x = int(nx * cos_t - ny * sin_t) + cx
            src_y = int(nx * sin_t + ny * cos_t) + cy
            
            if 0 <= src_x < ancho_2 and 0 <= src_y < alto_2:
                lienzo_raw_2[y, x] = img_2[src_y, src_x]
    cv2.imwrite(os.path.join(ruta_actual, 'mision2_raw.jpg'), lienzo_raw_2)

    # Modo OpenCV
    M_2 = cv2.getRotationMatrix2D((cx, cy), -45, 1.0)
    lienzo_cv2_2 = cv2.warpAffine(img_2, M_2, (ancho_2, alto_2))
    cv2.imwrite(os.path.join(ruta_actual, 'mision2_cv2.jpg'), lienzo_cv2_2)
else:
    print(f"Error: No se encontró 'qr_rotado.jpg' en {ruta_actual}")

# ==========================================
# MISIÓN 3: ESCALAMIENTO (Microfilm Oculto)
# ==========================================
print("Ejecutando Misión 3...")
ruta_img_3 = os.path.join(ruta_actual, 'microfilm.jpg')
img_3 = cv2.imread(ruta_img_3)

if img_3 is not None:
    # Recorte central
    recorte = img_3[900:1100, 900:1100]
    alto_r, ancho_r = recorte.shape[:2]
    escala = 5

    # Modo Raw
    lienzo_raw_3 = np.zeros((alto_r * escala, ancho_r * escala, 3), dtype=np.uint8)
    for y in range(lienzo_raw_3.shape[0]):
        for x in range(lienzo_raw_3.shape[1]):
            lienzo_raw_3[y, x] = recorte[y // escala, x // escala]
    cv2.imwrite(os.path.join(ruta_actual, 'mision3_raw.jpg'), lienzo_raw_3)

    # Modo OpenCV
    lienzo_cv2_3 = cv2.resize(recorte, (0,0), fx=escala, fy=escala, interpolation=cv2.INTER_CUBIC)
    cv2.imwrite(os.path.join(ruta_actual, 'mision3_cv2.jpg'), lienzo_cv2_3)
else:
    print(f"Error: No se encontró 'microfilm.jpg' en {ruta_actual}")

print("¡Proceso terminado! Revisa tu carpeta MISION para ver las imágenes generadas.")