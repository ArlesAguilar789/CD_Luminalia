# Reporte de Misión: Graficación Táctica
**Agente Especial:** Arles Aguilar

---

## Evidencias de Misión
*[Nota: Al pasar este archivo a PDF o entregarlo, asegúrate de arrastrar aquí las imágenes que generó el script de Python: `m1_recuperada.png`, `m2_qr_reparado.png`, `m3_sello_forjado.png`, `m4_clave_revelada.png` y `m5_antena.png`]*

---

## Análisis del Analista (Reflexiones Finales)

1. **Sobre los Operadores Puntuales (Misión 1):** Matemáticamente, ¿qué pasaría si en lugar de multiplicar por 50, hubieras sumado 50 a cada píxel oscuro? ¿Se revela igual el mensaje?
> **Respuesta:** No, el mensaje no se revelaría correctamente (o sería sumamente difícil de leer). Al sumar 50, los valores que estaban entre 1 y 5 pasarían a estar entre 51 y 55. Aunque la imagen sería ligeramente más gris, la *diferencia de contraste* (la distancia entre el fondo y el texto) seguiría siendo de apenas 4 o 5 valores. Al multiplicar por 50, los valores (1 a 5) se expanden a un rango de (50 a 250), "estirando" el contraste y haciendo que las letras destaquen fuertemente contra el fondo.

2. **Sobre el Espacio HSV (Misión 4):** ¿Por qué el modelo de color BGR es ineficiente para la Recuperación de Información cuando buscamos "todos los tonos de azul" (Cyan)?
> **Respuesta:** El modelo BGR acopla la información del color con la iluminación. Esto significa que un "cyan oscuro" y un "cyan brillante" tienen valores radicalmente distintos en sus canales Blue, Green y Red simultáneamente, lo que hace muy difícil definir un límite simple con sentencias condicionales. El modelo HSV (Hue, Saturation, Value) separa el Matiz (Hue) de la luz. En HSV, todo el cyan vive en un mismo rango de Matiz (alrededor de 90), independientemente de si el píxel tiene mucha sombra o mucho brillo, facilitando enormemente la creación de máscaras lógicas.

3. **Sobre Ecuaciones Paramétricas (Misión 5):** ¿Por qué las ecuaciones paramétricas (usando el parámetro t) son mejores para dibujar formas cerradas y complejas que las funciones estándar (y = f(x))?
> **Respuesta:** Las funciones matemáticas estándar $y = f(x)$ tienen una limitación estricta impuesta por la prueba de la línea vertical: para un valor de $x$, solo puede existir un único valor de $y$. Esto hace imposible dibujar curvas cerradas (como un círculo completo) o figuras que se intersectan a sí mismas (como la curva de Lissajous que dibujamos). Las ecuaciones paramétricas resuelven esto desacoplando $x$ e $y$, poniéndolas en función de una tercera variable independiente ($t$, el tiempo). Esto le da a la curva la libertad de regresar sobre sus propios valores de $x$ y crear formas cerradas.