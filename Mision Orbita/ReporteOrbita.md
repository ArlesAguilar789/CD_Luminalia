# Reporte de Misión: Órbita Dual — Cámara vs Objeto

**Agente Especial:** Arles Aguilar  
**Archivo del programa:** `MisionOrbita.py`  
**Librerías usadas:** Python 3, PyOpenGL, PyOpenGL_accelerate opcional, GLFW y GLU.

---

## Objetivo

El objetivo de esta práctica fue comparar dos formas de interpretar el movimiento en una escena con OpenGL clásico usando `GL_MODELVIEW`:

1. Rotar el objeto mientras la cámara permanece fija.
2. Orbitar la cámara alrededor de un objeto fijo.
3. Usar `gluLookAt` para describir la cámara con ojo, objetivo y vector arriba.
4. Observar cómo la iluminación cambia dependiendo del espacio donde se defina la luz.

La idea principal es que mover la cámara equivale matemáticamente a aplicar la transformación inversa sobre el mundo, aunque semánticamente no es lo mismo que mover el objeto.

---

## Evidencias

### Misión 1: Rotar objeto vs orbitar cámara

#### Objeto rota

![Objeto rota](<Imagenes Reporte/m1_objeto_rota.png>)

En este modo se usa una cámara fija. Primero se aleja la escena sobre el eje Z negativo:

```python
glTranslatef(0.0, 0.0, -CAM_DISTANCE)
```

Después se rota el objeto:

```python
glRotatef(angle, 0.0, 1.0, 0.0)
```

Esto produce una esfera que gira sobre su propio eje Y mientras la cámara permanece estable.

---

#### Cámara orbita

![Cámara orbita](<Imagenes Reporte/m1_camara_orbita.png>)

En este modo el objeto permanece conceptualmente fijo en el origen. La vista se transforma para simular que la cámara orbita alrededor del objeto:

```python
glRotatef(-angle, 0.0, 1.0, 0.0)
glTranslatef(0.0, 0.0, -CAM_DISTANCE)
```

El signo negativo en la rotación es importante porque mover la cámara equivale a aplicar la transformación inversa al mundo.

---

#### Variante comparativa: translate + rotate

![Variante B](<Imagenes Reporte/m1_camara_orbita_variante_b.png>)

La variante B usa:

```python
glTranslatef(0.0, 0.0, -CAM_DISTANCE)
glRotatef(angle, 0.0, 1.0, 0.0)
```

Aunque usa los mismos valores numéricos, el resultado no es igual. Esto ocurre porque el orden de multiplicación de matrices cambia el sistema de referencia donde se aplica cada transformación.

---

## Misión 2: Cámara declarativa con `gluLookAt`

![LookAt órbita](<Imagenes Reporte/m2_lookat_orbita.png>)

En esta misión se implementó una cámara orbital usando `gluLookAt`. La posición de la cámara se calcula con seno y coseno para formar una órbita circular alrededor del origen:

```python
a = math.radians(angle)
cam_x = ORBIT_RADIUS * math.sin(a)
cam_z = ORBIT_RADIUS * math.cos(a)

gluLookAt(
    cam_x, 0.0, cam_z,
    0.0, 0.0, 0.0,
    0.0, 1.0, 0.0
)
```

El ojo se mueve alrededor del objeto, el objetivo siempre es el origen y el vector arriba se mantiene como `(0, 1, 0)`.

---

## Misión 3: Luces

### Luz con objeto rotando

![Luz objeto](<Imagenes Reporte/m3_luz_objeto.png>)

### Luz con cámara orbitando

![Luz cámara](<Imagenes Reporte/m3_luz_camara.png>)

La iluminación se activó con:

```python
USE_LIGHTING = True
```

La posición de la luz se definió con:

```python
pos = [0.5, 0.8, 1.0, 0.0]
glLightfv(GL_LIGHT0, GL_POSITION, pos)
```

Como `w = 0.0`, la luz se comporta como direccional. Si se cambia a `w = 1.0`, la luz se interpreta como puntual.

Un detalle importante es que `glLightfv(GL_LIGHT0, GL_POSITION, pos)` usa la matriz `GL_MODELVIEW` activa en ese momento. Por eso, colocar la luz antes o después de transformar la cámara, el mundo o el objeto cambia el resultado visual.

---

## Cambios de constantes

- `CAM_DISTANCE = 5.0`: controla qué tan lejos se coloca la cámara respecto al objeto. Si aumenta, la esfera se ve más pequeña porque la cámara está más alejada.
- `ORBIT_RADIUS = 5.0`: controla el radio de la órbita usada por `gluLookAt`. Si aumenta, la cámara describe una órbita más amplia y se aleja más del objeto.
- `ANGLE_SPEED = 0.6`: controla la velocidad angular de la animación. Si aumenta, la rotación u órbita avanza más rápido en cada frame.

---

## Código final

El código final completo está en el archivo:

```text
MisionOrbita.py
```

Controles principales:

| Tecla | Acción |
|---|---|
| `1` | Modo objeto rota |
| `2` | Modo cámara orbita |
| `3` | Modo `gluLookAt` |
| `4` | Variante comparativa translate + rotate |
| `L` | Activar/desactivar iluminación |
| `P` | Guardar captura PNG |
| `ESC` o `Q` | Salir |

---

## Análisis del Analista

### 1. Orden de matrices

¿Por qué en OpenGL fijo el orden en que escribes `glTranslatef` / `glRotatef` cambia el resultado aunque uses los mismos números?

> En OpenGL clásico, cada llamada como `glTranslatef` o `glRotatef` modifica la matriz actual. Las transformaciones se componen en la matriz `GL_MODELVIEW`, y el orden de composición cambia el sistema de referencia en el que actúa cada transformación. Por eso no es lo mismo trasladar y luego rotar que rotar y luego trasladar. Con los mismos números se pueden obtener resultados diferentes: una rotación sobre el eje propio del objeto o una órbita alrededor de otro punto.

---

### 2. Objeto vs cámara

En la práctica, ¿cuándo prefieres rotar el modelo y cuándo orbitar la cámara?

> Prefiero rotar el modelo cuando quiero inspeccionar un objeto individual, por ejemplo una esfera, una pieza o un personaje frente a una cámara fija. En cambio, prefiero orbitar la cámara cuando quiero explorar una escena o mirar un objeto fijo desde diferentes puntos de vista. Rotar el objeto cambia la transformación del modelo; orbitar la cámara cambia la vista del observador.

---

### 3. `gluLookAt` vs `translate + rotate`

¿Qué ventaja tiene describir la cámara con ojo–objetivo–arriba para equipos de desarrollo?

> `gluLookAt` es más claro porque describe directamente la cámara mediante tres ideas: dónde está el ojo, hacia dónde mira y cuál es la dirección arriba. Esto evita depender tanto del orden manual de `glTranslatef` y `glRotatef`. Para un equipo de desarrollo, este estilo es más legible, más fácil de mantener y más cercano a cómo se piensa una cámara en una escena 3D.

---

### 4. Luces

Si la luz se define en el frame de la cámara sin reubicarla al mundo, ¿qué artefacto visual esperas al rotar solo el objeto?

> Si la luz se define en el frame de la cámara, la iluminación puede parecer pegada al observador. Al rotar solo el objeto, las zonas iluminadas y sombreadas pueden no comportarse como si la luz estuviera fija en el mundo. El artefacto esperado es que los brillos y sombras se sientan poco naturales, porque la referencia de la luz no coincide con la referencia física de la escena.

---

## Conclusión

La práctica demuestra que en OpenGL clásico no basta con usar las mismas transformaciones: el orden y el signo importan. Rotar un objeto y orbitar una cámara pueden parecer similares en pantalla, pero representan ideas distintas dentro del código. Además, la iluminación depende del espacio de coordenadas donde se coloque la luz, por lo que la semántica de cámara, mundo y objeto sí afecta el resultado final.
