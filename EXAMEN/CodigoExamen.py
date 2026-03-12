import cv2
import numpy as np
import math
import os

# --- CONFIGURACIÓN DE RUTAS ---
base_path = r"C:\Users\Arles Aguilar\Documents\Tareas Graficacion\EXAMEN"

print("Iniciando operaciones de Graficación Táctica...")

# ==========================================
# MISIÓN 1: El Mensaje Subexpuesto
# ==========================================
print("Ejecutando Misión 1...")
img1_path = os.path.join(base_path, 'm1_oscura.png')
img1 = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE)

if img1 is not None:
    # --- MODO OPENCV ---
    # Usamos cv2.multiply que maneja automáticamente el límite de 255 (saturación)
    img1_cv = cv2.multiply(img1, 50)
    
    cv2.imwrite(os.path.join(base_path, 'm1_recuperada.png'), img1_cv)
    print("Misión 1 completada.")
else:
    print(f"Error: No se encontró la imagen en {img1_path}")

# ==========================================
# MISIÓN 2: El QR Fragmentado
# ==========================================
print("Ejecutando Misión 2...")
img2_1_path = os.path.join(base_path, 'm2_mitad1.png')
img2_2_path = os.path.join(base_path, 'm2_mitad2.png')

mitad1 = cv2.imread(img2_1_path)
mitad2 = cv2.imread(img2_2_path)

if mitad1 is not None and mitad2 is not None:
    # 1. Crear lienzo blanco de 400x400 (3 canales)
    lienzo_qr = np.ones((400, 400, 3), dtype=np.uint8) * 255
    
    # 2. Obtener dimensiones de las mitades
    h1, w1 = mitad1.shape[:2]
    h2, w2 = mitad2.shape[:2]

    # 3. Colocar la mitad 1 en la parte superior del lienzo
    lienzo_res1 = np.ones((400, 400, 3), dtype=np.uint8) * 255
    lienzo_res1[0:h1, 0:w1] = mitad1
    
    # 4. Rotar mitad 2 180°
    M_rot = cv2.getRotationMatrix2D((w2 / 2, h2 / 2), 180, 1.0)
    mitad2_rotada = cv2.warpAffine(mitad2, M_rot, (w2, h2), borderValue=(255, 255, 255))
    
    # 5. Colocar la mitad 2 rotada en la parte inferior del lienzo
    lienzo_res2 = np.ones((400, 400, 3), dtype=np.uint8) * 255
    # Asumimos que la mitad 2 va en la mitad inferior (de la fila 200 a la 400)
    lienzo_res2[400-h2:400, 0:w2] = mitad2_rotada
    
    # 6. Unir ambas imágenes usando AND (mantiene los trazos negros sobre fondo blanco)
    qr_completo = cv2.bitwise_and(lienzo_res1, lienzo_res2)
    
    cv2.imwrite(os.path.join(base_path, 'm2_qr_reparado.png'), qr_completo)
    print("Misión 2 completada.")
else:
    print("Error: No se encontraron las mitades del QR")

# ==========================================
# MISIÓN 3: El Sello Biométrico
# ==========================================
print("Ejecutando Misión 3...")
# 1. Crear el lienzo con color base BGR(50, 20, 20)
sello = np.zeros((500, 500, 3), dtype=np.uint8)
sello[:] = (50, 20, 20)

# 2. Dibujar círculo (centro 250,250, radio 100, amarillo BGR(0, 255, 255), grosor 3)
cv2.circle(sello, (250, 250), 100, (0, 255, 255), 3)

# 3. Dibujar rectángulo rojo sólido (200,200 a 300,300, BGR(0, 0, 255), grosor -1 para rellenar)
cv2.rectangle(sello, (200, 200), (300, 300), (0, 0, 255), -1)

# 4. Trazar líneas blancas diagonales (grosor 2)
cv2.line(sello, (0, 0), (500, 500), (255, 255, 255), 2)
cv2.line(sello, (500, 0), (0, 500), (255, 255, 255), 2)

cv2.imwrite(os.path.join(base_path, 'm3_sello_forjado.png'), sello)
print("Misión 3 completada.")

# ==========================================
# MISIÓN 4: La Frecuencia Térmica
# ==========================================
print("Ejecutando Misión 4...")
# Buscamos el archivo .png como aparecía en tu captura de GitHub
img4_path = os.path.join(base_path, 'm4_ruido.png') 
img4 = cv2.imread(img4_path)

if img4 is not None:
    # 1. Convertir a HSV
    hsv = cv2.cvtColor(img4, cv2.COLOR_BGR2HSV)
    
    # 2. Crear máscara con los rangos sugeridos para el Cyan
    lower_cyan = np.array([80, 100, 100])
    upper_cyan = np.array([100, 255, 255])
    mascara_cyan = cv2.inRange(hsv, lower_cyan, upper_cyan)
    
    cv2.imwrite(os.path.join(base_path, 'm4_clave_revelada.png'), mascara_cyan)
    print("Misión 4 completada.")
else:
    print(f"Error: No se encontró la imagen en {img4_path}")

# ==========================================
# MISIÓN 5: La Antena Parabólica
# ==========================================
print("Ejecutando Misión 5...")
# 1. Crear lienzo negro 500x500
lienzo_antena = np.zeros((500, 500, 3), dtype=np.uint8)

# 2. Bucle para t
t = 0.0
while t <= 6.28:
    # 3. Calcular x e y, redondearlos a int
    x = int(250 + 150 * math.sin(3 * t))
    y = int(250 + 150 * math.sin(2 * t))
    
    # 4. Pintar el punto
    cv2.circle(lienzo_antena, (x, y), 1, (255, 255, 255), -1)
    
    t += 0.01

cv2.imwrite(os.path.join(base_path, 'm5_antena.png'), lienzo_antena)
print("Misión 5 completada.")

print("\n¡Todas las misiones completadas! Revisa la carpeta EXAMEN para ver los resultados.")