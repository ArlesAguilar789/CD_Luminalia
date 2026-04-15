import cv2
import numpy as np
import math

img1 = cv2.imread("TAREA ALERTA/ImagenesDeMision/m1_oscura 1.png", cv2.IMREAD_GRAYSCALE)
h, w = img1.shape

img_x50_raw = np.zeros((h, w), dtype=np.uint8)
for y in range(h):
    for x in range(w):
        val = int(img1[y, x]) * 50
        img_x50_raw[y, x] = min(max(val, 0), 255)

cv2.imwrite("TAREA ALERTA/ImagenesDeMision/m1_recuperado_x50.png", img_x50_raw)

img_mas20_raw = np.zeros((h, w), dtype=np.uint8)
for y in range(h):
    for x in range(w):
        val = int(img_x50_raw[y, x]) + 20
        img_mas20_raw[y, x] = min(max(val, 0), 255)

cv2.imwrite("TAREA ALERTA/ImagenesDeMision/m1_recuperado_x50_mas20.png", img_mas20_raw)

img_x50_vec = np.clip(img1.astype(np.int32) * 50, 0, 255).astype(np.uint8)
img_mas20_vec = np.clip(img_x50_vec.astype(np.int32) + 20, 0, 255).astype(np.uint8)

mitad1 = cv2.imread("TAREA ALERTA/ImagenesDeMision/m2_mitad1 1.png")
mitad2 = cv2.imread("TAREA ALERTA/ImagenesDeMision/m2_mitad2 1.png")

lienzo = np.full((400, 400, 3), 255, dtype=np.uint8)

h1, w1 = mitad1.shape[:2]
dx1, dy1 = 50, 50
M_trans = np.float32([[1, 0, dx1], [0, 1, dy1]])
mitad1_enderezada = cv2.warpAffine(mitad1, M_trans, (400, 400), borderValue=(255, 255, 255))

h2, w2 = mitad2.shape[:2]
centro = (w2 // 2, h2 // 2)
M_rot = cv2.getRotationMatrix2D(centro, 180, 1.0)
mitad2_rotada = cv2.warpAffine(mitad2, M_rot, (w2, h2), borderValue=(255, 255, 255))

dx2, dy2 = 50, 50 + h1
M_trans2 = np.float32([[1, 0, dx2], [0, 1, dy2]])
mitad2_enderezada = cv2.warpAffine(mitad2_rotada, M_trans2, (400, 400), borderValue=(255, 255, 255))

lienzo = cv2.bitwise_and(mitad1_enderezada, mitad2_enderezada)
cv2.imwrite("TAREA ALERTA/ImagenesDeMision/m2_qr_reconstruido.png", lienzo)

img3 = np.zeros((600, 600, 3), dtype=np.uint8)
img3[:] = (40, 20, 20)

cv2.circle(img3, (300, 300), 170, (0, 255, 255), 3)
cv2.circle(img3, (300, 300), 110, (0, 255, 255), 2)
cv2.rectangle(img3, (250, 260), (350, 340), (0, 0, 255), -1)
cv2.line(img3, (0, 0), (600, 600), (255, 255, 255), 2)
cv2.line(img3, (600, 0), (0, 600), (255, 255, 255), 2)

for i in range(8):
    angle = i * (2 * math.pi / 8)
    cx = int(300 + 140 * math.cos(angle))
    cy = int(300 + 140 * math.sin(angle))
    cv2.circle(img3, (cx, cy), 8, (0, 255, 0), -1)

texto = "SECTOR-9"
fuente = cv2.FONT_HERSHEY_SIMPLEX
tamaño_texto = cv2.getTextSize(texto, fuente, 1, 2)[0]
x_texto = (600 - tamaño_texto[0]) // 2
cv2.putText(img3, texto, (x_texto, 560), fuente, 1, (255, 255, 255), 2)

cv2.imwrite("TAREA ALERTA/ImagenesDeMision/m3_sello_forjado_v2.png", img3)

img4 = cv2.imread("TAREA ALERTA/ImagenesDeMision/m4_ruido 1.png")

kernel = np.ones((3, 3), np.float32) / 9
img_suavizada = cv2.filter2D(img4, -1, kernel)
cv2.imwrite("TAREA ALERTA/ImagenesDeMision/m4_suavizada.png", img_suavizada)

hsv = cv2.cvtColor(img_suavizada, cv2.COLOR_BGR2HSV)

lower_cyan = np.array([80, 100, 100])
upper_cyan = np.array([100, 255, 255])

mask = cv2.inRange(hsv, lower_cyan, upper_cyan)
cv2.imwrite("TAREA ALERTA/ImagenesDeMision/m4_mask_cyan.png", mask)

img_ruido = np.random.randint(0, 256, (300, 700, 3), dtype=np.uint8)

texto_mask = np.zeros((300, 700), dtype=np.uint8)
cv2.putText(texto_mask, "CLAVE: NEBULA_42", (20, 150), cv2.FONT_HERSHEY_SIMPLEX, 2, 255, 4)

img_ruido[texto_mask == 255] = [50, 250, 50]
cv2.imwrite("TAREA ALERTA/ImagenesDeMision/m5_tricolor.png", img_ruido)

img_load = cv2.imread("TAREA ALERTA/ImagenesDeMision/m5_tricolor.png")
b, g, r = cv2.split(img_load)

diferencia = cv2.absdiff(g, b)

diferencia_norm = cv2.normalize(diferencia, None, 0, 255, cv2.NORM_MINMAX)
_, umbral = cv2.threshold(diferencia_norm, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

cv2.imwrite("TAREA ALERTA/ImagenesDeMision/m5_mensaje.png", umbral)