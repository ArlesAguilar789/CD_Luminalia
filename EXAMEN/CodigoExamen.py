import cv2
import numpy as np
import math
import os

# --- CONFIGURACIÓN DE RUTAS ---
# Usamos tu ruta específica. Recuerda usar barras dobles \\ o el prefijo r"" en Windows.
base_path = r"C:\Users\Arles Aguilar\Documents\Tareas Graficacion\EXAMEN"

print("Iniciando operaciones de Graficación Táctica...")

# ==========================================
# MISIÓN 1: El Mensaje Subexpuesto
# ==========================================
print("Ejecutando Misión 1...")
img1_path = os.path.join(base_path, 'm1_oscura.png')
img1 = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE)

if img1 is not None:
    # --- MODO RAW ---
    h, w = img1.shape
    img1_raw = np.zeros((h, w), dtype=np.uint8)
    for y in range(h):
        for x in range(w):
            # Se multiplica y se usa clip para no exceder 255
            img1_raw[y, x] = np.clip(img1[y, x] * 50, 0, 255)
    
    # --- MODO OPENCV ---
    img1_cv = cv2.multiply(img1, 50)
    
    cv2.imwrite(os.path.join(base_path, 'm1_recuperada.png'), img1_cv)
else:
    print("Error: No se encontró m1_oscura.png")

# ==========================================
# MISIÓN 2: El QR Fragmentado
# ==========================================
print("Ejecutando Misión 2...")
img2_1_path = os.path.join(base_path, 'm2_mitad1.png')
img2_2_path = os.path.join(base_path, 'm2_mitad2.png')

mitad1 = cv2.imread(img2_1_path)
mitad2 = cv2.imread(img2_2_path)

if mitad1 is not None and mitad2 is not None:
    # 1. Crear lienzo de 400x400 (3 canales)
    lienzo_qr = np.zeros((400, 400, 3), dtype=np.uint8)
    
    # 2. Trasladar mitad 1 al origen (0,0)
    # Matriz de traslación identidad (tx=0, ty=0)
    M1 = np.float32([[1, 0, 0], [0, 1, 0]])
    res1 = cv2.warpAffine(mitad1, M1, (400, 400))
    
    # 3. Rotar mitad 2 180° y trasladarla a la parte inferior
    h2, w2 = mitad2.shape[:2]
    # Matriz de rotación sobre su centro
    M2 = cv2.getRotationMatrix2D((w2 // 2, h2 // 2), 180, 1.0)
    # Como queremos que vaya abajo, desplazamos en el eje Y según el alto de la imagen
    M2[1, 2] += (400 - h2) 
    res2 = cv2.warpAffine(mitad2, M2, (400, 400))
    
    # Unir ambas imágenes
    qr_completo = cv2.bitwise_or(res1, res2)
    cv2.imwrite(os.path.join(base_path, 'm2_qr_reparado.png'), qr_completo)
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

# ==========================================
# MISIÓN 4: La Frecuencia Térmica
# ==========================================
print("Ejecutando Misión 4...")
# Nota: Tu archivo en la carpeta era .jpg, asegúrate de que el nombre coincida.
img4_path = os.path.join(base_path, 'm4_ruido.jpg') 
img4 = cv2.imread(img4_path)

if img4 is not None:
    # 1. Convertir a HSV
    hsv = cv2.cvtColor(img4, cv2.COLOR_BGR2HSV)
    
    # 2. Crear máscara con los rangos sugeridos para el Cyan
    lower_cyan = np.array([80, 100, 100])
    upper_cyan = np.array([100, 255, 255])
    mascara_cyan = cv2.inRange(hsv, lower_cyan, upper_cyan)
    
    cv2.imwrite(os.path.join(base_path, 'm4_clave_revelada.png'), mascara_cyan)
else:
    print("Error: No se encontró m4_ruido.jpg")

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

print("¡Todas las misiones completadas! Revisa la carpeta para ver los resultados.")