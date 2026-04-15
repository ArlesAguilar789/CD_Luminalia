import sys
import math
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# Variable global para el tiempo de la animación
tiempo = 0.0

def init():
    # Fondo gris muy, muy oscuro (casi negro) para dar profundidad
    glClearColor(0.01, 0.01, 0.02, 1.0)
    
    # Habilitar prueba de profundidad para renderizado 3D correcto
    glEnable(GL_DEPTH_TEST)
    
    # Habilitar Mezcla (Blending) para efectos de transparencia y brillo de neón
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Suavizado de líneas para que el neón se vea perfecto
    glEnable(GL_LINE_SMOOTH)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)

    # Configuración de perspectiva
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, 800/600, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

# Definimos los vértices de un Tetraedro Regular (Pirámide 3D) centrada
vertices = [
    [ 0.0,  1.0,  0.0],  # Superior (0)
    [-1.0, -0.5,  0.8],  # Base Frente Izq (1)
    [ 1.0, -0.5,  0.8],  # Base Frente Der (2)
    [ 0.0, -0.5, -1.0]   # Base Atrás (3)
]

# Definimos las 4 caras triangulares (índices de los vértices)
caras = [
    (0, 1, 2), # Frente
    (0, 2, 3), # Derecha
    (0, 3, 1), # Izquierda
    (1, 3, 2)  # Base
]

# Función para calcular color de neón fluido basado en tiempo y posición
def get_neon_color(t, offset, alpha=1.0):
    # Fórmulas para colores muy saturados y brillantes
    r = (math.sin(t + offset) * 0.5 + 0.5) ** 2 # Potencia para saturar
    g = (math.sin(t + offset + 2.0) * 0.5 + 0.5) ** 2
    b = (math.sin(t + offset + 4.0) * 0.5 + 0.5) ** 2
    
    # Asegurar que el color sea brillante (sumando un mínimo)
    intentisdad = 0.3
    return (r + intentisdad, g + intentisdad, b + intentisdad, alpha)

def draw_tetrahedron(t, mode, alpha_multiplier):
    glBegin(mode)
    for i, cara in enumerate(caras):
        for vertex_index in cara:
            v = vertices[vertex_index]
            
            # El color depende del tiempo y de qué vértice es (crea flujo)
            color = get_neon_color(t * 1.5, vertex_index * 1.0, 0.6 * alpha_multiplier)
            glColor4fv(color)
            glVertex3fv(v)
    glEnd()

def display():
    global tiempo
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    # 1. Cámara y Levitación suave
    # Flota arriba y abajo suavemente usando sin(tiempo)
    levitacion = math.sin(tiempo * 0.5) * 0.2
    glTranslatef(0, levitacion, -6.0) # Movemos la escena atrás para verla

    # 2. Rotación Compleja en 3 Ejes
    # Diferentes velocidades para cada eje crea un movimiento hipnótico
    glRotatef(tiempo * 20, 1.0, 0.0, 0.0) # Rotación X
    glRotatef(tiempo * 35, 0.0, 1.0, 0.0) # Rotación Y
    glRotatef(tiempo * 15, 0.0, 0.0, 1.0) # Rotación Z

    # 3. Respiración Orgánica (Escala)
    # Pulsación suave sincronizada
    factor_respiracion = 1.0 + math.sin(tiempo * 1.0) * 0.15
    glScalef(factor_respiracion, factor_respiracion, factor_respiracion)

    # --- RENDERIZADO DEL ARTEFACTO (El truco espectacular) ---

    # PASO A: Dibujar el "Núcleo de Plasma" (Sólido y transparente)
    # Usamos caras sólidas pero con mucha transparencia
    glDepthMask(GL_FALSE) # Desactivar escritura en buffer de profundidad para mejor blending
    draw_tetrahedron(tiempo, GL_TRIANGLES, 0.3)
    glDepthMask(GL_TRUE) # Reactivar

    # PASO B: Dibujar el "Aura de Neón" (Líneas gruesas y suaves)
    glLineWidth(10.0) # Línea muy gruesa
    draw_tetrahedron(tiempo, GL_LINE_LOOP, 0.2) # Muy transparente para el "glow"

    # PASO C: Dibujar el "Filamento Central" (Líneas finas y brillantes)
    glLineWidth(2.5) # Línea nítida
    draw_tetrahedron(tiempo, GL_LINE_LOOP, 1.0) # Totalmente opaca y brillante

    glutSwapBuffers()

def idle():
    global tiempo
    # Velocidad de la simulación
    tiempo += 0.01 
    glutPostRedisplay()

def keyboard(key, x, y):
    if key == b'\x1b': # ESC para salir
        glutDestroyWindow(glutGetWindow())
        sys.exit()

def main():
    glutInit(sys.argv)
    # Importante: Usar GLUT_MULTISAMPLE para antialiasing si el hardware lo soporta
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH | GLUT_MULTISAMPLE)
    glutInitWindowSize(1000, 750) # Ventana más grande para apreciar detalles
    glutCreateWindow(b"Artefacto Holografico Cuantico - OpenGL Python")
    
    init()
    
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard)
    
    print("Controles: Presiona ESC para salir.")
    glutMainLoop()

if __name__ == "__main__":
    main()