# Reporte de Misión: Graficación Táctica II
**Agente Especial:** Arles Aguilar

---
## Evidencias

### Misión 1
- Imagen recuperada x50: 
![Recuperada x50](m1_recuperado_x50.png)
- Imagen recuperada x50 + 20: 
![Recuperada x50 + 20](m1_recuperado_x50_mas20.png)
- **Fragmento de Código Clave:**
```python
# Modo Vectorizado para mayor eficiencia
img_x50_vec = np.clip(img1.astype(np.int32) * 50, 0, 255).astype(np.uint8)
img_mas20_vec = np.clip(img_x50_vec.astype(np.int32) + 20, 0, 255).astype(np.uint8)
```

### Misión 2
- QR reconstruido: 
![QR Reconstruido](m2_qr_reconstruido.png)
- **Fragmento de Código Clave:**
```python
# Rotación de la mitad 2 sobre su propio centro
h2, w2 = mitad2.shape[:2]
centro = (w2 // 2, h2 // 2)
M_rot = cv2.getRotationMatrix2D(centro, 180, 1.0)
mitad2_rotada = cv2.warpAffine(mitad2, M_rot, (w2, h2), borderValue=(255, 255, 255))

# Ensamble final usando bitwise_and para combinar las partes oscuras
lienzo = cv2.bitwise_and(mitad1_enderezada, mitad2_enderezada)
```

### Misión 3
- Sello forjado: 
![Sello Forjado](m3_sello_forjado_v2.png)
- **Fragmento de Código Clave:**
```python
# Colocación de los 8 círculos usando simetría polar (seno y coseno)
for i in range(8):
    angle = i * (2 * math.pi / 8)
    cx = int(300 + 140 * math.cos(angle))
    cy = int(300 + 140 * math.sin(angle))
    cv2.circle(img3, (cx, cy), 8, (0, 255, 0), -1)
```

### Misión 4
- Máscara Cyan: 
![Máscara Cyan](m4_mask_cyan.png)
- **Fragmento de Código Clave:**
```python
# Suavizado previo para limpiar falsos positivos
kernel = np.ones((3, 3), np.float32) / 9
img_suavizada = cv2.filter2D(img4, -1, kernel)

# Segmentación en espacio HSV
hsv = cv2.cvtColor(img_suavizada, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv, np.array([80, 100, 100]), np.array([100, 255, 255]))
```

### Misión 5
- Evidencia tricolor: 
![Evidencia Tricolor](m5_tricolor.png)
- Mensaje recuperado: 
![Mensaje Recuperado](m5_mensaje.png)
- **Fragmento de Código Clave:**
```python
# Separación de canales y recuperación por diferencia absoluta
b, g, r = cv2.split(img_load)
diferencia = cv2.absdiff(g, b)

# Normalización y umbralización (Otsu) para máxima legibilidad
diferencia_norm = cv2.normalize(diferencia, None, 0, 255, cv2.NORM_MINMAX)
_, umbral = cv2.threshold(diferencia_norm, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
```

---
## Análisis del Analista (Reflexiones Finales)

1. **Operadores puntuales (M1):** ¿Qué diferencia visual hay entre recuperar con multiplicación (x50) y recuperar con suma (+50)? ¿Cuál preserva mejor el contraste del texto?
> **[Respuesta]**: Al realizar las pruebas, noté que la suma (+50) simplemente desplaza el brillo de toda la imagen por igual; aclara el fondo oscuro al mismo tiempo que el texto, dejándolo "lavado". Por el contrario, la multiplicación (x50) actúa como un amplificador: los píxeles negros del fondo (cercanos a 0) se quedan oscuros, mientras que los valores grises tenues del texto se disparan hacia el blanco. Definitivamente, la multiplicación preserva y resalta mucho mejor el contraste.

2. **Transformaciones geométricas (M2):** ¿Por qué es importante escoger el centro correcto al rotar una imagen con `getRotationMatrix2D`?
> **[Respuesta]**: Es vital porque esa coordenada se convierte en el "eje" o "pivote" de la rotación. Si no definimos el centro exacto (ancho/2 y alto/2), la imagen rotaría tomando como eje la esquina superior izquierda (0,0). Como resultado, la mitad del código QR habría salido volando fuera del lienzo (hacia coordenadas negativas) y se habría recortado, arruinando la pieza.

3. **Convolución (M4):** ¿Por qué un filtro promedio puede ayudar a reducir falsos positivos antes de segmentar por HSV, y qué desventaja tiene sobre los bordes del texto?
> **[Respuesta]**: El ruido de la imagen enemiga eran pequeños píxeles dispersos con colores extremos (altas frecuencias). Al aplicar el filtro promedio 3x3, promedié esos picos con los píxeles vecinos, difuminando el ruido estático y dejando áreas de color más uniformes, lo que limpió enormemente la máscara final. La desventaja de esto es que también suaviza (emborrona) los bordes afilados de las letras del texto, haciéndolas lucir ligeramente redondeadas o menos nítidas tras la segmentación.

4. **Canales (M5):** ¿Por qué separar canales puede revelar información que en la imagen a color “no se ve” a simple vista?
> **[Respuesta]**: Porque a simple vista, nuestro cerebro percibe la mezcla aditiva de la luz (RGB) como un color continuo y caótico. El enemigo camufló el mensaje inyectando un patrón aleatorio idéntico en todos los colores, pero alteró sutilmente las intensidades en el canal verde. Al separar los canales o usar restas como `abs(G - B)`, logré aislar esa pequeña discrepancia técnica y cancelar el "ruido de fondo" que compartían, desnudando la señal original que la imagen compuesta ocultaba.