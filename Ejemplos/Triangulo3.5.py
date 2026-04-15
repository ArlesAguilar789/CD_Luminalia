import sys
import math
import random
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# Variables globales de animación
tiempo = 0.0
sobrecarga = 1.0  # Multiplicador de energía interactiva

# Variables de Cámara e Interacción
cam_zoom = -8.0
cam_rot_x = 15.0
cam_rot_y = 0.0
mouse_down = False
last_mouse_x = 0
last_mouse_y = 0

# Pre-calcular partículas
num_particulas = 60
particulas = []
for _ in range(num_particulas):
    particulas.append([random.uniform(1.5, 3.5), random.uniform(-50, 50), random.uniform(-2.0, 2.0), random.uniform(0, 10)])

def init():
    glClearColor(0.02, 0.0, 0.05, 1.0)
    glEnable(GL_DEPTH_TEST)
    
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_LINE_SMOOTH)
    glEnable(GL_POINT_SMOOTH)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, 800/600, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

vertices = [
    [ 0.0,  1.0,  0.0],
    [-1.0, -0.5,  0.8],
    [ 1.0, -0.5,  0.8],
    [ 0.0, -0.5, -1.0]
]

caras = [(0, 1, 2), (0, 2, 3), (0, 3, 1), (1, 3, 2)]

def get_neon_color(t, offset, alpha=1.0, misticismo=False):
    if misticismo:
        r = (math.sin(t + offset) * 0.5 + 0.5)
        g = (math.sin(t * 0.8 + offset + 2.0) * 0.5 + 0.5)
        b = (math.sin(t * 1.2 + offset + 4.0) * 0.5 + 0.5)
        # La sobrecarga hace que brille en blanco temporalmente
        brillo_extra = (sobrecarga - 1.0) * 0.5
        return (min(1.0, r + brillo_extra), min(1.0, g + brillo_extra), min(1.0, b + brillo_extra), alpha)
    else:
        return (0.4 + math.sin(t)*0.2, 0.8 + math.sin(t+2)*0.2, 1.0, alpha)

def draw_tetrahedron(t, mode, alpha_multiplier):
    glBegin(mode)
    for cara in caras:
        for vertex_index in cara:
            v = vertices[vertex_index]
            # La velocidad del color también aumenta con la sobrecarga
            color = get_neon_color(t * 2.0 * sobrecarga, vertex_index * 1.5, 0.7 * alpha_multiplier, True)
            glColor4fv(color)
            glVertex3fv(v)
    glEnd()

def dibujar_anillo(radio, segmentos=50):
    glBegin(GL_LINE_LOOP)
    for i in range(segmentos):
        theta = 2.0 * math.pi * float(i) / float(segmentos)
        x = radio * math.cos(theta)
        z = radio * math.sin(theta)
        glVertex3f(x, 0.0, z)
    glEnd()

def display():
    global tiempo, sobrecarga
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    # --- INTERACTIVIDAD: CÁMARA ORBITAL ---
    glTranslatef(0, 0.0, cam_zoom) # Zoom interactivo
    glRotatef(cam_rot_x, 1.0, 0.0, 0.0) # Rotación Arriba/Abajo del ratón
    glRotatef(cam_rot_y, 0.0, 1.0, 0.0) # Rotación Izquierda/Derecha del ratón

    # --- 1. EL CÍRCULO DE INVOCACIÓN ---
    glPushMatrix()
    glTranslatef(0.0, -2.5, 0.0)
    glRotatef(tiempo * 15 * sobrecarga, 0.0, 1.0, 0.0) # Gira más rápido al pulsar espacio
    
    glColor4f(0.0, 0.8, 1.0, 0.3)
    glLineWidth(2.0)
    dibujar_anillo(3.0, 60)
    dibujar_anillo(2.8, 6) 
    dibujar_anillo(1.5, 3) 
    
    glColor4f(0.0, 0.5, 1.0, 0.1)
    dibujar_anillo(0.5, 20)
    glPopMatrix()

    # --- 2. PARTÍCULAS INTERACTIVAS ---
    glPointSize(3.0)
    glBegin(GL_POINTS)
    for p in particulas:
        radio, vel_orbita, altura, offset = p
        # Las partículas se expanden hacia afuera durante la sobrecarga
        radio_actual = radio * (1.0 + (sobrecarga - 1.0) * 0.5)
        angulo = math.radians(tiempo * vel_orbita * sobrecarga + offset * 10)
        px = radio_actual * math.cos(angulo)
        pz = radio_actual * math.sin(angulo)
        brillo = (math.sin(tiempo * 5 + offset) * 0.5 + 0.5) * 0.8
        glColor4f(1.0, 1.0, 1.0, brillo)
        glVertex3f(px, altura + math.sin(tiempo+offset)*0.5, pz)
    glEnd()

    # --- 3. ANILLOS DE ASTROLABIO ---
    glLineWidth(3.0)
    glPushMatrix()
    levitacion = math.sin(tiempo * 0.8) * 0.3
    glTranslatef(0, levitacion, 0)
    
    glPushMatrix()
    glRotatef(tiempo * 45 * sobrecarga, 1.0, 0.0, 1.0)
    glColor4f(1.0, 0.8, 0.0, 0.5)
    dibujar_anillo(2.2 + (sobrecarga-1.0)*0.2, 40) # Se expanden un poco
    glPopMatrix()

    glPushMatrix()
    glRotatef(-tiempo * 60 * sobrecarga, 0.0, 1.0, 1.0)
    glColor4f(0.8, 0.0, 1.0, 0.5)
    dibujar_anillo(1.9 + (sobrecarga-1.0)*0.2, 40)
    glPopMatrix()
    glPopMatrix()

    # --- 4. EL NÚCLEO MÍSTICO ---
    glPushMatrix()
    glTranslatef(0, levitacion, 0)
    
    glRotatef(tiempo * 25 * sobrecarga, 0.5, 1.0, 0.2)
    
    # La sobrecarga hace que el núcleo palpite más grande
    factor_respiracion = (1.0 + math.sin(tiempo * 2.0) * 0.1) * (1.0 + (sobrecarga-1.0)*0.3)
    glScalef(factor_respiracion, factor_respiracion, factor_respiracion)

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

    render_magia(1.0)
    glPushMatrix()
    glScalef(1.0, -1.0, 1.0)
    render_magia(1.0)
    glPopMatrix()

    glPopMatrix()

    glutSwapBuffers()

def idle():
    global tiempo, sobrecarga
    tiempo += 0.015 
    
    # Decaimiento de la sobrecarga (vuelve lentamente a la normalidad)
    if sobrecarga > 1.0:
        sobrecarga -= 0.05
    else:
        sobrecarga = 1.0
        
    glutPostRedisplay()

# --- FUNCIONES DE INTERACTIVIDAD (MOUSE Y TECLADO) ---

def mouse(button, state, x, y):
    global mouse_down, last_mouse_x, last_mouse_y, cam_zoom, cam_rot_x, cam_rot_y
    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            mouse_down = True
            last_mouse_x = x
            last_mouse_y = y
        elif state == GLUT_UP:
            mouse_down = False
            
    # Click derecho resetea la cámara
    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        cam_rot_x = 15.0
        cam_rot_y = 0.0
        cam_zoom = -8.0
        
    # Rueda del ratón para Zoom (En GLUT suele ser botones 3 y 4)
    elif button == 3 and state == GLUT_DOWN:
        cam_zoom += 0.5 # Acercar
    elif button == 4 and state == GLUT_DOWN:
        cam_zoom -= 0.5 # Alejar

def motion(x, y):
    global cam_rot_x, cam_rot_y, last_mouse_x, last_mouse_y
    if mouse_down:
        # Calcular cuánto se movió el ratón
        dx = x - last_mouse_x
        dy = y - last_mouse_y
        
        # Actualizar los ángulos de la cámara
        cam_rot_y += dx * 0.5
        cam_rot_x += dy * 0.5
        
        # Limitar la rotación vertical para no voltear la cámara al revés
        if cam_rot_x > 90.0: cam_rot_x = 90.0
        if cam_rot_x < -90.0: cam_rot_x = -90.0
        
        last_mouse_x = x
        last_mouse_y = y

def keyboard(key, x, y):
    global sobrecarga, cam_zoom
    if key == b'\x1b': # Tecla ESC
        glutDestroyWindow(glutGetWindow())
        sys.exit()
    elif key == b' ': # BARRA ESPACIADORA para Inyectar Energía
        sobrecarga = 4.0 # Aumenta drásticamente la velocidad y tamaño
    
    # Zoom de respaldo con teclado por si la rueda del ratón no funciona en tu PC
    elif key == GLUT_KEY_UP:
        cam_zoom += 0.5
    elif key == GLUT_KEY_DOWN:
        cam_zoom -= 0.5

# Usamos SpecialFunc para las flechas del teclado (Zoom)
def special_keys(key, x, y):
    global cam_zoom
    if key == GLUT_KEY_UP:
        cam_zoom += 0.5
    elif key == GLUT_KEY_DOWN:
        cam_zoom -= 0.5

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH | GLUT_MULTISAMPLE)
    glutInitWindowSize(1000, 800)
    glutCreateWindow(b"Nucleo Interactivo - Mueve la camara y usa ESPACIO")
    
    init()
    
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    
    # Registrar las nuevas funciones de interactividad
    glutMouseFunc(mouse)      # Clics del ratón
    glutMotionFunc(motion)    # Arrastrar el ratón
    glutKeyboardFunc(keyboard)# Teclas normales (Espacio, Esc)
    glutSpecialFunc(special_keys) # Teclas especiales (Flechas)
    
    print("--- CONTROLES ---")
    print("Clic Izquierdo + Arrastrar: Rotar cámara")
    print("Rueda del ratón / Flechas Arriba-Abajo: Acercar/Alejar (Zoom)")
    print("Clic Derecho: Reiniciar cámara")
    print("Barra Espaciadora: ¡SOBRECARGA DE ENERGÍA!")
    print("ESC: Salir")
    
    glutMainLoop()

if __name__ == "__main__":
    main()