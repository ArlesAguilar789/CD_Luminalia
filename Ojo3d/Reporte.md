# Misión: Iluminación y Materiales en un Ojo 3D  
## GLFW + PyOpenGL

---

## Portada

**Nombre completo:** Arles Aguilar Eguiza  
**Grupo:** B  
**No. de control:** 24120387  
**Materia:** Graficación  
**Práctica:** Iluminación y Materiales en un Ojo 3D  
**Tecnologías utilizadas:** Python, GLFW, PyOpenGL y OpenGL fijo  

---

## Objetivo de la práctica

El objetivo de esta práctica fue convertir un modelo 3D que originalmente usaba colores planos con `glColor3f()` en un objeto con una apariencia más realista mediante iluminación clásica de OpenGL y materiales.

Para lograrlo, se activó el sistema de iluminación de OpenGL, se configuraron luces ambientales, difusas y especulares, se agregaron normales suaves a las figuras GLU y se aplicaron materiales con diferentes niveles de brillo a cada parte del ojo.  
El resultado final es un ojo 3D estilo anime con iris, pupila, brillo especular, sombras suaves y rotación completa de 360°.

---

## Descripción del proyecto

El programa genera un ojo 3D usando GLFW y PyOpenGL.  
El modelo conserva el uso de primitivas basadas en esferas y discos, pero mejora su presentación visual con iluminación y materiales.

El ojo incluye:

- Esclerótica o parte blanca del ojo.
- Iris azul estilo anime.
- Pupila negra.
- Brillos blancos especulares.
- Contorno y pestañas.
- Córnea transparente.
- Luz principal cálida.
- Luz secundaria azul tenue como luz de relleno.
- Rotación completa de 360°.

---

## Capturas de pantalla

### Vista general del ojo

En esta captura se observa el ojo completo con iris, pupila, contorno, pestañas, volumen e iluminación aplicada.

![Vista general del ojo](Capturas/Vista%20General%20Ojo.png)

---

### Vista con brillo especular

En esta imagen se aprecia el brillo especular generado por la luz principal.  
El reflejo blanco permite notar que el material de la superficie tiene una apariencia más pulida.

![Vista con brillo](Capturas/Vista%20con%20Brillo.png)

---

### Zona con sombra

Esta captura muestra una zona menos iluminada del ojo, lo que demuestra que la luz no es plana y que OpenGL está calculando la iluminación dependiendo del ángulo de la superficie.

![Zona con sombra](Capturas/Zona%20con%20sombra.png)

---

### Video de rotación

El siguiente video muestra la rotación del ojo y permite observar cómo cambian las zonas iluminadas, las sombras y los brillos especulares.

[Ver video de rotación](Capturas/Ojo%20rotando.mp4)

---

## Tabla comparativa de resultados

| Elemento evaluado | Antes: colores planos | Después: iluminación y materiales |
|---|---|---|
| Iluminación | El objeto se veía plano, sin reacción real a la luz. | El ojo muestra zonas iluminadas, sombras suaves y cambios de intensidad al rotar. |
| Esclerótica | Blanco uniforme sin profundidad. | Blanco con brillo especular y apariencia más pulida. |
| Iris | Color simple sin detalle visual. | Iris azul estilo anime con diferentes tonos y volumen visual. |
| Pupila | Figura negra plana. | Pupila oscura con poco brillo para conservar contraste. |
| Brillo especular | No existía reflejo visible. | Se observan reflejos blancos en el ojo y en el iris. |
| Sombras | No había sombreado real. | Las sombras cambian dependiendo de la posición del objeto frente a la luz. |
| Normales | No estaban configuradas explícitamente. | Se usaron normales suaves con `gluQuadricNormals()`. |
| Materiales | Solo se usaban colores básicos. | Se aplicaron materiales con propiedades especulares y diferentes niveles de `shininess`. |
| Rotación | El objeto podía rotar, pero sin efecto realista de luz. | El ojo rota 360° y la iluminación cambia durante el movimiento. |
| Presentación final | Modelo simple. | Ojo 3D estilo anime con apariencia más profesional. |

---

## Cumplimiento de misiones

| Misión | Descripción | Estado |
|---|---|---|
| Misión 1: Enciende la luz | Activar `GL_DEPTH_TEST`, `GL_LIGHTING` y `GL_LIGHT0`; configurar luz ambiental, difusa y especular. | Cumplida |
| Misión 2: La esfera necesita normales | Agregar normales suaves con `gluQuadricNormals(quad, GLU_SMOOTH)`. | Cumplida |
| Misión 3: Materiales | Crear y aplicar materiales diferentes para cada parte del ojo. | Cumplida |
| Misión 4: Que `glColor` afecte el material | Activar `GL_COLOR_MATERIAL` y usar `glColorMaterial()`. | Cumplida |
| Misión 5: ¿Por qué la luz cambia cuando rota? | Posicionar la luz usando la matriz `MODELVIEW` y explicar su comportamiento. | Cumplida |
| Bonus | Agregar una segunda luz `GL_LIGHT1` como luz de relleno. | Cumplido |

---

## Respuestas a las preguntas de análisis

### 1. ¿Qué se hizo para que OpenGL calculara iluminación?

Se activaron los estados principales de iluminación:

```python
glEnable(GL_DEPTH_TEST)
glEnable(GL_LIGHTING)
glEnable(GL_LIGHT0)
```

También se configuraron las propiedades de la luz principal:

```python
glLightfv(GL_LIGHT0, GL_AMBIENT, ...)
glLightfv(GL_LIGHT0, GL_DIFFUSE, ...)
glLightfv(GL_LIGHT0, GL_SPECULAR, ...)
```

Con esto, OpenGL dejó de mostrar colores planos y empezó a calcular la iluminación de acuerdo con la posición de la luz, las normales y los materiales del objeto.

---

### 2. ¿Por qué son importantes las normales en las esferas?

Las normales indican la dirección de cada punto de la superficie.  
OpenGL las usa para calcular cómo incide la luz sobre el objeto.

En el proyecto se usó:

```python
gluQuadricNormals(q, GLU_SMOOTH)
```

Esto permitió que la iluminación se viera suave y redondeada, evitando que las esferas se vieran con cortes o sombras incorrectas.

---

### 3. ¿Qué función cumplen los materiales?

Los materiales controlan cómo reacciona cada parte del modelo ante la luz.  
Por ejemplo, la parte blanca del ojo tiene más brillo especular, mientras que la pupila tiene poco brillo para mantenerse oscura.

Se usaron propiedades como:

```python
glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, specular)
glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, shininess)
```

El valor `shininess` controla qué tan concentrado o fuerte se ve el brillo especular.

---

### 4. ¿Qué diferencia hay entre luz ambiental, difusa y especular?

La luz ambiental ilumina el objeto de forma general para que las zonas oscuras no queden completamente negras.

La luz difusa depende del ángulo entre la superficie y la luz.  
Esta luz ayuda a que el objeto se vea con volumen.

La luz especular genera los brillos intensos o reflejos sobre la superficie.  
En el ojo se nota principalmente en los brillos blancos y en la parte frontal de la esclerótica.

---

### 5. ¿Por qué la luz cambia cuando rota el ojo?

La posición de la luz se transforma usando la matriz `MODELVIEW` activa en el momento en que se llama a:

```python
glLightfv(GL_LIGHT0, GL_POSITION, ...)
```

En este proyecto, la luz se coloca antes de aplicar la rotación del ojo.  
Eso hace que la luz permanezca fija en la escena, mientras el ojo gira frente a ella.  
Por esa razón cambian las zonas iluminadas, las sombras y los brillos durante la rotación.

---

### 6. ¿Para qué se agregó una segunda luz?

Se agregó `GL_LIGHT1` como una luz azul tenue de relleno.  
Su función es iluminar ligeramente el lado oscuro del ojo para que no se vea completamente negro, pero sin eliminar la sensación de profundidad.

---

## Fragmentos importantes del código

### Activación de iluminación

```python
glEnable(GL_DEPTH_TEST)
glEnable(GL_LIGHTING)
glEnable(GL_LIGHT0)
glEnable(GL_LIGHT1)
glEnable(GL_NORMALIZE)
```

---

### Activación de color material

```python
glEnable(GL_COLOR_MATERIAL)
glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
```

---

### Normales suaves

```python
q = gluNewQuadric()
gluQuadricNormals(q, GLU_SMOOTH)
gluSphere(q, radius, slices, stacks)
gluDeleteQuadric(q)
```

---

### Materiales

```python
glColor4f(color[0], color[1], color[2], color[3])
glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, specular)
glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, shininess)
```

---

### Rotación completa

```python
rotation = (rotation + 0.65) % 360.0
glRotatef(rotation, 0.0, 1.0, 0.0)
```

---

## Instrucciones para ejecutar el proyecto

Instalar dependencias:

```bash
pip install glfw PyOpenGL PyOpenGL_accelerate
```

Ejecutar el programa:

```bash
python Ojo3d.py
```

---

## Estructura sugerida para el repositorio

```text
Ojo3d/
│
├── Ojo3d.py
├── README.md
└── Capturas/
    ├── Vista General Ojo.png
    ├── Vista con Brillo.png
    ├── Zona con sombra.png
    └── Ojo rotando.mp4
```

---

## Conclusión final

En esta práctica se logró mejorar un modelo 3D básico para convertirlo en un ojo con una apariencia más profesional.  
Se implementó iluminación clásica de OpenGL, normales suaves, materiales con brillo especular, color material y una segunda luz de relleno.

El resultado final muestra un ojo estilo anime con iris, pupila, brillos, pestañas y una rotación completa de 360°.  
Durante la rotación se puede observar cómo cambian las zonas iluminadas y las sombras, comprobando que la iluminación está siendo calculada correctamente por OpenGL.

Esta práctica permitió comprender la importancia de las luces, normales y materiales en la creación de objetos 3D con mayor realismo visual.
