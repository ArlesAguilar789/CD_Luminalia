import sys
import math
import random
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# Variables globales
tiempo = 0.0

# Pre-calcular algunas partículas mágicas para que orbiten
num_particulas = 60
particulas = []
for _ in range(num_particulas):
    # radio, velocidad_orbita, altura, offset_tiempo
    particulas.append([random.uniform(1.5, 3.5), random.uniform(-50, 50), random.uniform(-2.0, 2.0), random.uniform(0, 10)])

def init():
    # Fondo del "abismo", casi negro con un toque violeta
    glClearColor(0.02, 0.0, 0.05, 1.0)
    glEnable(GL_DEPTH_TEST)
    
    # Blending mágico para los brillos
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_LINE_SMOOTH)
    glEnable(GL_POINT_SMOOTH) # Suavizar las partículas
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, 800/600, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

vertices = [
    [ 0.0,  1.0,  0.0],  # Superior
    [-1.0, -0.5,  0.8],  # Base Frente Izq
    [ 1.0, -0.5,  0.8],  # Base Frente Der
    [ 0.0, -0.5, -1.0]   # Base Atrás
]

caras = [(0, 1, 2), (0, 2, 3), (0, 3, 1), (1, 3, 2)]

def get_neon_color(t, offset, alpha=1.0, misticismo=False):
    # Si es el núcleo místico, lo hacemos brillar más hacia el cian/magenta
    if misticismo:
        r = (math.sin(t + offset) * 0.5 + 0.5)
        g = (math.sin(t * 0.8 + offset + 2.0) * 0.5 + 0.5)
        b = (math.sin(t * 1.2 + offset + 4.0) * 0.5 + 0.5)
        return (r, g, b, alpha)
    else:
        # Colores etéreos (Dorados, Azules celestiales)
        return (0.4 + math.sin(t)*0.2, 0.8 + math.sin(t+2)*0.2, 1.0, alpha)

def draw_tetrahedron(t, mode, alpha_multiplier):
    glBegin(mode)
    for cara in caras:
        for vertex_index in cara:
            v = vertices[vertex_index]
            color = get_neon_color(t * 2.0, vertex_index * 1.5, 0.7 * alpha_multiplier, True)
            glColor4fv(color)
            glVertex3fv(v)
    glEnd()

# Nueva función: Dibuja anillos para la magia
def dibujar_anillo(radio, segmentos=50):
    glBegin(GL_LINE_LOOP)
    for i in range(segmentos):
        theta = 2.0 * math.pi * float(i) / float(segmentos)
        x = radio * math.cos(theta)
        z = radio * math.sin(theta)
        glVertex3f(x, 0.0, z)
    glEnd()

def display():
    global tiempo
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    # Alejar la cámara un poco más para ver la majestuosidad
    glTranslatef(0, 0.0, -8.0)
    
    # Inclinación general para verlo desde arriba ligeramente
    glRotatef(15, 1.0, 0.0, 0.0)

    # --- 1. EL CÍRCULO DE INVOCACIÓN EN EL SUELO ---
    glPushMatrix()
    glTranslatef(0.0, -2.5, 0.0) # Lo ponemos en el piso
    glRotatef(tiempo * 15, 0.0, 1.0, 0.0) # Gira lentamente
    
    # Colores del círculo rúnico (Cian mágico)
    glColor4f(0.0, 0.8, 1.0, 0.3)
    glLineWidth(2.0)
    dibujar_anillo(3.0, 60) # Anillo exterior
    dibujar_anillo(2.8, 6)  # Hexágono interior
    dibujar_anillo(1.5, 3)  # Triángulo interior
    
    # Brillo central en el suelo
    glColor4f(0.0, 0.5, 1.0, 0.1)
    dibujar_anillo(0.5, 20)
    glPopMatrix()

    # --- 2. PARTÍCULAS DE POLVO MÁGICO ---
    glPointSize(3.0)
    glBegin(GL_POINTS)
    for p in particulas:
        radio, vel_orbita, altura, offset = p
        angulo = math.radians(tiempo * vel_orbita + offset * 10)
        px = radio * math.cos(angulo)
        pz = radio * math.sin(angulo)
        # Hacemos que brillen de forma intermitente
        brillo = (math.sin(tiempo * 5 + offset) * 0.5 + 0.5) * 0.8
        glColor4f(1.0, 1.0, 1.0, brillo)
        glVertex3f(px, altura + math.sin(tiempo+offset)*0.5, pz)
    glEnd()

    # --- 3. ANILLOS DE ASTROLABIO (Escudos del Núcleo) ---
    glLineWidth(3.0)
    glPushMatrix()
    # Levitación compartida con el núcleo
    levitacion = math.sin(tiempo * 0.8) * 0.3
    glTranslatef(0, levitacion, 0)
    
    # Anillo 1 (Gira en X y Z)
    glPushMatrix()
    glRotatef(tiempo * 45, 1.0, 0.0, 1.0)
    glColor4f(1.0, 0.8, 0.0, 0.5) # Dorado
    dibujar_anillo(2.2, 40)
    glPopMatrix()

    # Anillo 2 (Gira en Y y Z en dirección contraria)
    glPushMatrix()
    glRotatef(-tiempo * 60, 0.0, 1.0, 1.0)
    glColor4f(0.8, 0.0, 1.0, 0.5) # Magenta/Morado
    dibujar_anillo(1.9, 40)
    glPopMatrix()
    glPopMatrix()

    # --- 4. EL NÚCLEO MÍSTICO (Estrella Tetraédrica / Merkaba) ---
    glPushMatrix()
    glTranslatef(0, levitacion, 0)
    
    # Rotación base del núcleo entero
    glRotatef(tiempo * 25, 0.5, 1.0, 0.2)
    
    factor_respiracion = 1.0 + math.sin(tiempo * 2.0) * 0.1
    glScalef(factor_respiracion, factor_respiracion, factor_respiracion)

    # Función auxiliar para dibujar las 3 capas del artefacto
    def render_magia(escala):
        glPushMatrix()
        glScalef(escala, escala, escala)
        glDepthMask(GL_FALSE)
        draw_tetrahedron(tiempo, GL_TRIANGLES, 0.4)
        glDepthMask(GL_TRUE)
        glLineWidth(8.0)
        draw_tetrahedron(tiempo, GL_LINE_LOOP, 0.3)
        glLineWidth(2.0)
        draw_tetrahedron(tiempo, GL_LINE_LOOP, 1.0)
        glPopMatrix()

    # Dibujamos el Tetraedro Normal (Apunta hacia arriba)
    render_magia(1.0)

    # El truco maestro: Lo invertimos (escala negativa) para crear una estrella 3D
    glPushMatrix()
    glScalef(1.0, -1.0, 1.0) # Invertir en el eje Y
    render_magia(1.0)
    glPopMatrix()

    glPopMatrix() # Fin del núcleo

    glutSwapBuffers()

def idle():
    global tiempo
    tiempo += 0.015 
    glutPostRedisplay()

def keyboard(key, x, y):
    if key == b'\x1b':
        glutDestroyWindow(glutGetWindow())
        sys.exit()

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH | GLUT_MULTISAMPLE)
    glutInitWindowSize(1000, 800)
    glutCreateWindow(b"Nucleo de Mana Sagrado - Nivel Maximo")
    
    init()
    
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard)
    
    print("Contempla el Nucleo Sagrado. Presiona ESC para salir.")
    glutMainLoop()

if __name__ == "__main__":
    main()