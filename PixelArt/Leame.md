# Reporte (Markdown): Pixel Art en OpenCV (400×400) con “pixel lógico” y switch Color/Grises

> **Idea general:** dibujar un sprite tipo pixel-art en un lienzo de **400×400** sin cargar imágenes externas.  
> La figura se construye con **coordenadas + ciclos**, pintando “pixeles lógicos” que en realidad son **bloques** (por ejemplo 16×16).

---

## 1) Historia rápida (cómo llegué a esta solución)

Al principio yo pensé que esto era tan fácil como el ejemplo de clase: hacer una imagen blanca y poner un pixel negro en una coordenada. El problema fue que… **un pixel en 400×400 casi ni se ve**, y el dibujo se suponía que se notara bien.

Entonces me atoré: no sabía cómo hacer que se viera “pixel art” pero sin usar imágenes. Me tocó buscar por fuera (videos y ejemplos) y me topé con una idea que me salvó: **hacer un “pixel lógico”**, o sea que cada “pixel” del dibujo sea en realidad un bloque grande (por ejemplo 16×16).  
Así el dibujo sigue siendo “pixel por pixel” porque por dentro sí pinto pixel a pixel, solo que agrandado para que sea visible.

Luego para no morir escribiendo 160,000 asignaciones, armé el dibujo por **filas con rangos**, tipo: “de x=6 a x=11 pinta con este color”. Eso hizo que el código quedara editable.

---

## 2) Imports (librerías)

```python
import cv2 as cv
import numpy as np
```

### ¿Qué hace esta parte?
- `cv2` (OpenCV) se usa para mostrar la imagen (`imshow`) y manejar ventanas.
- `numpy` se usa para crear la matriz de la imagen (el lienzo) y trabajar con valores.

### ¿Qué pasa si lo modifico?
- Si no importo `cv2`, no puedo usar `imshow`, `waitKey`, etc. → error.
- Si no importo `numpy`, no puedo crear el lienzo → error.

---

## 3) Tamaño del lienzo y escala del “pixel lógico”

```python
H, W = 400, 400

P = 16                 
SPR_W, SPR_H = 18, 24  

x_off = (W - SPR_W * P) // 2
y_off = (H - SPR_H * P) // 2
```

### ¿Qué hace esta parte?
- `H, W` define el tamaño final del lienzo (400×400).
- `P` es el tamaño del bloque (pixel lógico).  
  Si `P=16`, cada “celda” del sprite se pinta como un bloque de 16×16 pixeles reales.
- `SPR_W, SPR_H` es el tamaño del sprite en celdas lógicas (18×24).  
- `x_off, y_off` centran el sprite dentro del lienzo:
  - `SPR_W * P` da el ancho real que ocupará el sprite en pixeles.
  - `SPR_H * P` da la altura real.
  - El sobrante se divide entre 2 para centrar.

### ¿Qué pasa si lo modifico?
- Si cambias `H, W`:
  - Más grande → más espacio en blanco alrededor.
  - Más chico → puedes recortar el sprite si ya no cabe.
- Si cambias `P`:
  - `P` más grande → el sprite se ve más grande, pero **se puede salir** del lienzo.
  - `P` más pequeño → el sprite se ve más “fino”, pero también más pequeño.
- Si cambias `SPR_W, SPR_H` sin cambiar `ROWS`:
  - El centrado queda mal, porque `ROWS` define el sprite real.
  - Si pones valores que no corresponden, se puede mover raro (no explota, pero se descuadra).
- Si cambias `x_off` / `y_off`:
  - Mueves el sprite.
  - Si los haces negativos o muy grandes, parte del dibujo puede quedar fuera del lienzo.

---

## 4) Switch: Color vs Escala de grises

```python
COLOR = False
```

### ¿Qué hace?
- `COLOR = True` → crea imagen de **3 canales** (color).
- `COLOR = False` → crea imagen de **1 canal** (escala de grises).

Esto lo hice porque el profe manejaba el ejemplo en grises, pero también quería ver que funcionara con colores.

### ¿Qué pasa si lo modifico?
- Si lo pones en `True` tienes colores reales, pero necesitas paleta en tuplas `(B,G,R)`.
- Si lo pones en `False` solo usas intensidades 0..255.

---

## 5) Creación del lienzo y paleta de colores / grises

### 5.1 Si está en color (`COLOR=True`)

```python
img = np.ones((H, W, 3), np.uint8) * 255

PALETTE = [
    (255, 255, 255),  # 0 blanco
    (0, 0, 0),        # 1 negro (contorno)
    (88, 222, 253),   # 2 amarillo claro (cabello)
    (250, 118, 177),  # 3 morado (vestido)
    (194, 222, 243),  # 4 piel
    (250, 90, 235),   # 5 rosa (detalles)
    (44, 198, 235),   # 6 amarillo oscuro/sombra
    (252, 174, 245),  # 7 lila (brillos vestido)
    (48, 48, 247),    # 8 rojo (gema)
    (253, 187, 116),  # 9 azul (ojos)
]
```

**Dato clave:** OpenCV usa **BGR** (no RGB).  
Por eso el orden es `(B, G, R)`.

### 5.2 Si está en grises (`COLOR=False`)

```python
img = np.ones((H, W), np.uint8) * 255
PALETTE = [255, 0, 216, 151, 225, 152, 192, 204, 108, 173]
```

Aquí cada número es intensidad:
- `0` = negro
- `255` = blanco
- intermedios = grises

### ¿Qué pasa si le muevo a la paleta?
- Si haces los tonos muy parecidos, el dibujo pierde contraste (se ve “plano”).
- Si aumentas contraste (unos muy oscuros y otros muy claros), el pixel art se distingue mejor.
- Ojo: si un `color_idx` en `ROWS` apunta a un índice que no existe en `PALETTE` → truena con error.

---

## 6) Función `put_cell`: el “pixel lógico” pintado pixel por pixel

```python
def put_cell(cx, cy, color):
    x0 = x_off + cx * P
    y0 = y_off + cy * P
    for yy in range(y0, y0 + P):
        for xx in range(x0, x0 + P):
            img[yy, xx] = color
```

### ¿Qué hace?
- `cx, cy` son coordenadas del sprite lógico (18×24).
- Se convierten a coordenadas reales usando:
  - `x0 = x_off + cx * P`
  - `y0 = y_off + cy * P`
- Luego se pintan **todos los pixeles reales** del bloque `P×P` con ciclos.

Esto es lo que cumple el “pixel por pixel”: aunque “pinto una celda”, por dentro estoy asignando muchos pixeles reales.

### ¿Qué pasa si lo modifico?
- Si cambias `y0 + P` por `y0 + (P//2)` el bloque queda más chico → el sprite se ve con huecos.
- Si cambias `img[yy, xx] = color` por otra cosa:
  - puedes invertir colores,
  - o hacer efectos (por ejemplo, degradado), etc.
- Si quitas los ciclos y usas un “slice”, se vuelve más rápido, pero ya no sería tan literal “pixel por pixel” (depende de lo que te pida el profe).

---

## 7) Función `fill_row`: rangos para dibujar más rápido

```python
def fill_row(cy, x0, x1, color_idx):
    color = PALETTE[color_idx]
    for cx in range(x0, x1 + 1):
        put_cell(cx, cy, color)
```

### ¿Qué hace?
En una fila lógica `cy`, pinta desde `x0` hasta `x1` con un color de la paleta.

Ejemplo mental:
- “En la fila 10, pinta de x=6 a x=11 con color 1”.

### ¿Qué pasa si lo modifico?
- Si quitas el `+1` en `range(x0, x1 + 1)`, ya no pinta el último pixel (porque Python no incluye el final).
- Si cambias `color_idx`, cambias el color/tono de esa sección.
- Si `x0 > x1`, no pinta nada (rango vacío).

---

## 8) Estructura `ROWS`: el sprite (por filas y segmentos)

`ROWS` es lo más importante: aquí está el dibujo.  
Cada fila tiene una lista de segmentos `(x_inicio, x_fin, color_idx)`.

Ejemplo de una fila:

```python
[(0, 2, 0), (3, 3, 1), (4, 5, 0)]
```

Eso significa:
- de x=0..2 pinta con el color 0 (blanco),
- x=3..3 pinta con color 1 (negro),
- x=4..5 pinta con color 0.

### ¿Qué pasa si modifico `ROWS`?
- Si cambias rangos → cambias forma del dibujo (se mueve una parte, se hace más ancho, etc.).
- Si cambias `color_idx` → cambias el color/tono de esa parte.
- Si metes un índice de color que no existe en `PALETTE` → error.
- Si agregas/quitas filas → cambia la altura del sprite.

---

## 9) Render final (los ciclos que pintan todo)

```python
for y, row in enumerate(ROWS):
    for x0, x1, cidx in row:
        fill_row(y, x0, x1, cidx)
```

### ¿Qué hace?
- `enumerate(ROWS)` recorre fila por fila, y `y` es el número de fila lógica.
- `row` es la lista de segmentos de esa fila.
- Para cada segmento llama a `fill_row()`.

### ¿Qué pasa si lo modifico?
- Si empezaras `enumerate(ROWS, start=1)` moverías todo 1 fila hacia abajo (y puede quedar recortado).
- Si cambias el orden de segmentos dentro de una fila, puedes tapar cosas (porque se pinta en orden).

---

## 10) Mostrar resultado

```python
cv.imshow("imagen", img)
cv.waitKey(0)
cv.destroyAllWindows()
```

### ¿Qué hace?
- `imshow` abre la ventana con la imagen.
- `waitKey(0)` espera hasta que presiones una tecla.
- `destroyAllWindows()` cierra todo correctamente.

### ¿Qué pasa si lo modifico?
- Si `waitKey(0)` lo cambias por `waitKey(1000)`, la ventana se cierra sola en 1 segundo.
- Si quitas `waitKey`, la ventana puede abrir y cerrarse rápido (dependiendo del entorno).
- Si no llamas `destroyAllWindows()`, a veces quedan ventanas colgadas.

---

## 11) Código completo (el que usé)

```python
import cv2 as cv
import numpy as np

H, W = 400, 400

P = 16                 
SPR_W, SPR_H = 18, 24 

x_off = (W - SPR_W * P) // 2
y_off = (H - SPR_H * P) // 2

COLOR = False

if COLOR:
    img = np.ones((H, W, 3), np.uint8) * 255
    
    PALETTE = [
        (255, 255, 255),  # 0 blanco
        (0, 0, 0),        # 1 negro (contorno)
        (88, 222, 253),   # 2 amarillo claro (cabello)
        (250, 118, 177),  # 3 morado (vestido)
        (194, 222, 243),  # 4 piel
        (250, 90, 235),   # 5 rosa (detalles)
        (44, 198, 235),   # 6 amarillo oscuro/sombra
        (252, 174, 245),  # 7 lila (brillos vestido)
        (48, 48, 247),    # 8 rojo (gema)
        (253, 187, 116),  # 9 azul (ojos)
    ]
else:
    img = np.ones((H, W), np.uint8) * 255
    PALETTE = [255, 0, 216, 151, 225, 152, 192, 204, 108, 173]

def put_cell(cx, cy, color):
    """Pinta un pixel lógico (cx,cy) como un bloque P×P (pixel por pixel)."""
    x0 = x_off + cx * P
    y0 = y_off + cy * P
    for yy in range(y0, y0 + P):
        for xx in range(x0, x0 + P):
            img[yy, xx] = color

def fill_row(cy, x0, x1, color_idx):
    color = PALETTE[color_idx]
    for cx in range(x0, x1 + 1):
        put_cell(cx, cy, color)

ROWS = [
  [(0, 2, 0), (3, 3, 1), (4, 5, 0), (6, 11, 1), (12, 13, 0), (14, 14, 1), (15, 17, 0)],
  [(0, 4, 0), (5, 5, 1), (6, 11, 6), (12, 12, 1), (13, 17, 0)],
  [(0, 1, 0), (2, 2, 1), (3, 3, 0), (4, 4, 1), (5, 5, 6), (6, 11, 2), (12, 12, 6), (13, 13, 1), (14, 14, 0), (15, 15, 1), (16, 17, 0)],
  [(0, 1, 0), (2, 2, 1), (3, 3, 0), (4, 4, 6), (5, 12, 2), (13, 13, 6), (14, 14, 0), (15, 15, 1), (16, 17, 0)],
  [(0, 1, 0), (2, 2, 1), (3, 3, 0), (4, 4, 6), (5, 12, 2), (13, 13, 6), (14, 14, 0), (15, 15, 1), (16, 17, 0)],
  [(0, 0, 0), (1, 2, 1), (3, 3, 0), (4, 4, 6), (5, 12, 2), (13, 13, 6), (14, 14, 0), (15, 16, 1), (17, 17, 0)],
  [(0, 0, 1), (1, 1, 4), (2, 2, 1), (3, 3, 0), (4, 5, 6), (6, 7, 2), (8, 9, 6), (10, 11, 2), (12, 13, 6), (14, 14, 0), (15, 15, 1), (16, 16, 4), (17, 17, 1)],
  [(0, 0, 1), (1, 2, 4), (3, 3, 1), (4, 4, 6), (5, 5, 1), (6, 7, 6), (8, 8, 0), (9, 9, 8), (10, 11, 6), (12, 12, 1), (13, 13, 6), (14, 14, 1), (15, 16, 4), (17, 17, 1)],
  [(0, 0, 0), (1, 1, 1), (2, 2, 4), (3, 3, 1), (4, 4, 6), (5, 5, 2), (6, 7, 1), (8, 9, 8), (10, 11, 1), (12, 12, 2), (13, 13, 6), (14, 14, 1), (15, 15, 4), (16, 16, 1), (17, 17, 0)],
  [(0, 1, 0), (2, 3, 1), (4, 4, 6), (5, 7, 2), (8, 9, 1), (10, 12, 2), (13, 13, 6), (14, 15, 1), (16, 17, 0)],
  [(0, 1, 0), (2, 2, 1), (3, 3, 6), (4, 4, 4), (5, 5, 1), (6, 6, 9), (7, 10, 4), (11, 11, 9), (12, 12, 1), (13, 13, 4), (14, 14, 6), (15, 15, 1), (16, 17, 0)],
  [(0, 0, 0), (1, 1, 1), (2, 2, 6), (3, 3, 2), (4, 4, 4), (5, 5, 0), (6, 6, 9), (7, 10, 4), (11, 11, 9), (12, 12, 0), (13, 13, 4), (14, 14, 2), (15, 15, 6), (16, 16, 1), (17, 17, 0)],
  [(0, 0, 0), (1, 1, 1), (2, 2, 6), (3, 3, 2), (4, 4, 1), (5, 12, 4), (13, 13, 1), (14, 14, 2), (15, 15, 6), (16, 16, 1), (17, 17, 0)],
  [(0, 0, 0), (1, 1, 1), (2, 3, 6), (4, 4, 5), (5, 5, 1), (6, 11, 4), (12, 12, 1), (13, 13, 5), (14, 15, 6), (16, 16, 1), (17, 17, 0)],
  [(0, 0, 0), (1, 1, 1), (2, 2, 6), (3, 3, 1), (4, 4, 4), (5, 5, 5), (6, 11, 1), (12, 12, 5), (13, 13, 4), (14, 14, 1), (15, 15, 6), (16, 16, 1), (17, 17, 0)],
  [(0, 1, 0), (2, 2, 1), (3, 3, 0), (4, 4, 4), (5, 5, 1), (6, 11, 3), (12, 12, 1), (13, 13, 4), (14, 14, 0), (15, 15, 1), (16, 17, 0)],
  [(0, 1, 0), (2, 2, 1), (3, 4, 0), (5, 5, 1), (6, 6, 2), (7, 10, 3), (11, 11, 2), (12, 12, 1), (13, 14, 0), (15, 15, 1), (16, 17, 0)],
  [(0, 0, 0), (1, 1, 1), (2, 3, 0), (4, 4, 1), (5, 5, 5), (6, 6, 3), (7, 10, 2), (11, 11, 3), (12, 12, 5), (13, 13, 1), (14, 15, 0), (16, 16, 1), (17, 17, 0)],
  [(0, 1, 0), (2, 3, 1), (4, 4, 5), (5, 6, 7), (7, 7, 3), (8, 9, 2), (10, 10, 3), (11, 12, 7), (13, 13, 5), (14, 15, 1), (16, 17, 0)],
  [(0, 1, 0), (2, 2, 1), (3, 3, 5), (4, 6, 7), (7, 10, 3), (11, 13, 7), (14, 14, 5), (15, 15, 1), (16, 17, 0)],
  [(0, 1, 0), (2, 2, 1), (3, 4, 5), (5, 6, 7), (7, 10, 3), (11, 12, 7), (13, 14, 5), (15, 15, 1), (16, 17, 0)],
  [(0, 2, 0), (3, 3, 1), (4, 6, 5), (7, 10, 3), (11, 13, 5), (14, 14, 1), (15, 17, 0)],
  [(0, 3, 0), (4, 5, 1), (6, 7, 5), (8, 9, 3), (10, 11, 5), (12, 13, 1), (14, 17, 0)],
  [(0, 5, 0), (6, 11, 1), (12, 17, 0)],
]

for y, row in enumerate(ROWS):
    for x0, x1, cidx in row:
        fill_row(y, x0, x1, cidx)

cv.imshow("imagen", img)
cv.waitKey(0)
cv.destroyAllWindows()
```

---

## 12) Conclusión personal

La solución que más me funcionó fue pensar el dibujo como un sprite pequeño (en celdas lógicas) y luego “escalarlo” con bloques.  
Con eso logré que:

- Se vea bien en 400×400.
- Se siga cumpliendo el “pixel por pixel” (porque el bloque se pinta con ciclos).
- Sea fácil editar el dibujo solo cambiando rangos en `ROWS`.
- Puedo alternar entre **color y grises** sin reescribir el dibujo, solo cambiando `COLOR`.
