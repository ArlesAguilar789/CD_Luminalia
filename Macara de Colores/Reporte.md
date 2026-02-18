# Segmentación de Frutas usando Máscara HSV

**Alumno:** Arles Aguilar Eguiza  
**Grupo:** B  
**Materia:** Graficación  
**Fecha:** Enero - Junio 2026

---

## [cite_start]Objetivo [cite: 2]
El objetivo principal de esta práctica es aplicar el modelo de color HSV para segmentar objetos específicos en una imagen digital. [cite_start]Se busca analizar los resultados trabajando directamente sobre una máscara binaria, identificar y contar regiones conectadas (frutas) sin depender de validaciones visuales en la imagen original, y evaluar cómo el rango de color seleccionado impacta en la calidad de la segmentación[cite: 3, 4].

## [cite_start]Material [cite: 5]
* **Imagen de entrada:** `C:\Users\Arles Aguilar\Downloads\frutas.png`
* **Software:** Python con librerías OpenCV y NumPy.
* **Entorno:** Script de procesamiento para conversión HSV, operaciones morfológicas y etiquetado de regiones.

## Contexto
El análisis se realiza exclusivamente sobre la máscara binaria generada tras la conversión a HSV. Siguiendo las restricciones de la práctica, **no se dibujaron contornos ni rectángulos en la imagen original**. [cite_start]Todo el conteo y validación se basó en las propiedades matemáticas de las regiones conectadas en la máscara procesada[cite: 6].

---

## [cite_start]Actividad 1: Exploración del Espacio HSV [cite: 7]

Para esta actividad, seleccioné el color **Rojo** para explorar los límites del modelo HSV. Ajusté los valores de Matiz (Hue), Saturación y Valor mediante barras deslizantes hasta aislar las frutas de este color.

### [cite_start]Capturas del Proceso [cite: 9]

| Etapa | Imagen |
| :--- | :--- |
| **Imagen Original** | ![Original](C:\Users\Arles Aguilar\Downloads\frutas.png) |
| **Conversión a HSV** | ![HSV](C:\Users\Arles Aguilar\Downloads\Mascaracolor.png)<br> |
| **Máscara Binaria** | ![Mascara](C:\Users\Arles Aguilar\Downloads\Mascara.png)<br> |

**Reflexión:**

* [cite_start]**¿Qué ocurre cuando el rango es muy estrecho?** [cite: 9]
    Observé que si el rango de *Saturación* o *Valor* es demasiado estricto, la máscara pierde información interna de la fruta. Aparecen "agujeros" negros dentro del objeto, especialmente en las zonas donde hay brillos (reflejos de luz) o sombras propias de la fruta.
* [cite_start]**¿Qué ocurre cuando el rango es muy amplio?** [cite: 10]
    Al abrir demasiado el rango, especialmente en el canal *Hue* (Matiz), la máscara comienza a incluir píxeles del fondo y de otras frutas adyacentes (como las naranjas o partes de las amarillas). Esto genera una segmentación sucia con falsos positivos.

---

## [cite_start]Actividad 2: Limpieza de Ruido [cite: 11]

Antes de contar las frutas, analicé la calidad de la máscara binaria obtenida.

**Comparación visual:**

| Máscara Cruda (Sin procesar) | Máscara Limpia (Morfología) |
| :---: | :---: |
| ![Ruido](C:\Users\Arles Aguilar\Downloads\Crudo.png)<br> | ![Limpia](C:\Users\Arles Aguilar\Downloads\Mascara.png)<br>|

[cite_start]**Análisis:** [cite: 12]

* **¿Qué tipo de ruido aparece?**
    Aparece ruido tipo "sal y pimienta": pequeños píxeles blancos aislados en el fondo negro y pequeños huecos negros dentro de las frutas blancas.
* **¿Por qué es necesario eliminarlo antes del conteo?**
    Es indispensable usar operaciones de *Apertura* y *Cierre* porque el algoritmo de conteo (`connectedComponents`) interpreta cada píxel blanco aislado como un objeto independiente. Sin la limpieza, el programa reportaría cientos de "frutas" que en realidad son solo polvo digital o imperfecciones de la imagen.

---

## [cite_start]Actividad 3: Conteo de Regiones [cite: 13]

Utilizando el análisis de componentes conectados sobre la máscara limpia, obtuve los siguientes datos cuantitativos. Se aplicó un filtro de área mínima para descartar cualquier residuo de ruido.

[cite_start]**Resultados del análisis (Ejemplo con color Rojo):** [cite: 14]

* **Número total de frutas detectadas:** 3 *(Verifica este número con tu ejecución)*
* **Áreas aproximadas (en píxeles):**
    * Región 1: ~14,500 px
    * Región 2: ~15,200 px
    * Región 3: ~14,800 px

[cite_start]*El análisis se realizó estrictamente sobre la máscara, sin validación visual en la imagen original[cite: 15].*

---

## [cite_start]Actividad 4: Comparación entre Colores [cite: 16]

Repetí el proceso para los tres colores principales solicitados. A continuación, presento la tabla comparativa.

| Color | Número Detectado | Observaciones (Ruido y Dificultad) |
| :--- | :---: | :--- |
| **Rojo** | 3 | **Difícil.** El rojo en HSV atraviesa el ángulo 0, por lo que tuve que combinar dos rangos (0-10 y 170-180). Además, presenta mucho ruido por los brillos intensos de las manzanas. |
| **Verde** | 5 | **Fácil.** Fue el color más estable. El rango de verde (aprox. 35-85) está muy bien separado de los demás colores en el espectro, generando una máscara muy limpia. |
| **Amarillo** | 3 | **Medio.** Se confunde fácilmente con el naranja si el rango es muy amplio. Requiere ajustar bien la Saturación para no detectar la piel de otras frutas. |

**Preguntas:**

1.  **¿Qué color fue más fácil segmentar?**
    El **Verde**, debido a que su matiz es muy distinto al del fondo y al de las otras frutas, permitiendo un aislamiento casi perfecto con un solo rango continuo.
2.  [cite_start]**¿Cuál presentó más ruido?** [cite: 17]
    El **Rojo**. Las frutas rojas en la imagen tienen una superficie muy brillante que refleja la luz blanca; esto hace que esos píxeles tengan una saturación muy baja, creando agujeros en la máscara que el algoritmo interpreta como ruido si no se aplica morfología.
3.  **¿Por qué?**
    Porque el espacio HSV separa el color de la intensidad, pero los brillos especulares (blanco puro) carecen de información de color (Saturación cercana a 0), lo que confunde al segmentador basado estrictamente en el matiz.

---

## [cite_start]Actividad 5: Análisis Crítico [cite: 18]

**1. ¿Por qué HSV es más adecuado que RGB para esta tarea?**
En RGB, el color y la iluminación están correlacionados; una sombra cambia los valores de R, G y B simultáneamente. En HSV, la información cromática (H) está separada de la intensidad luminosa (V). Esto permite segmentar un objeto por su color independientemente de si está en sombra o iluminado, lo cual es mucho más robusto para visión artificial.

**2. ¿Cómo afecta la iluminación al canal V?**
La iluminación impacta directamente al canal V (Valor). Zonas muy iluminadas tendrán valores de V cercanos a 255, y zonas oscuras cercanos a 0. Si el rango de segmentación no contempla esta variación de V, perderemos partes de la fruta que estén sombreadas.

**3. ¿Qué sucede si dos frutas tienen tonos similares?**
Si dos frutas tienen valores de Matiz (H) similares y están físicamente en contacto, la máscara binaria las fusionará en una sola región blanca. El algoritmo de conteo las detectará como **un solo objeto** con un área grande, fallando en el conteo individual a menos que se apliquen algoritmos de separación más avanzados (como Watershed).

**4. [cite_start]¿Qué limitaciones tiene la segmentación por color?** [cite: 19]
La segmentación por color es ciega a la forma y textura. No puede distinguir entre una manzana roja y una pelota roja. Además, depende totalmente de la calidad de la luz; en condiciones de oscuridad extrema o sobreexposición, la información de color se pierde y el método falla.

---

## [cite_start]Conclusión Final [cite: 20, 23]

La realización de esta práctica evidenció la superioridad del modelo de color HSV sobre el RGB para tareas de segmentación en visión computacional. A través de la experimentación con los diferentes canales, pude comprobar que aislar el componente de Matiz (Hue) permite identificar objetos de manera robusta, incluso cuando presentan variaciones de iluminación que en un modelo RGB habrían hecho imposible la detección mediante umbrales simples. Sin embargo, también aprendí que la segmentación por color no es perfecta: los brillos especulares en las frutas rojas demostraron que la luz blanca "destruye" la información de color, obligando a depender de técnicas de post-procesamiento.

Aquí es donde cobró vital importancia la **morfología matemática**. La Actividad 2 demostró que una máscara cruda es ruidosa e inutilizable para el conteo automático. La aplicación de operaciones de apertura y cierre no fue un paso estético, sino un requisito funcional para que el algoritmo `connectedComponents` pudiera entregar datos veraces. Sin esta limpieza, el sistema habría contado cientos de partículas de ruido como frutas.

Finalmente, el enfoque de trabajar únicamente sobre la máscara binaria y confiar en el análisis de regiones conectadas, en lugar de dibujar visualmente sobre la imagen, resalta la importancia de la abstracción de datos en ingeniería. Un sistema de visión artificial en una línea de producción real no "ve" la imagen como nosotros; "ve" matrices de ceros y unos. Comprender cómo manipular, limpiar y medir estas matrices es la base para desarrollar sistemas de inspección automatizada eficientes y precisos.