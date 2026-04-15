import sys
import math
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# Variable global para el tiempo
tiempo = 0.0

def init():
    # Fondo negro para que los colores brillen al máximo
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, 800/600, 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)

def display():
    global tiempo
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    glTranslatef(0, 0, -3.0)

    # --- NUEVO: EFECTO RESPIRACIÓN ---
    # Calculamos un factor de escala que oscila suavemente.
    # math.sin(tiempo) va de -1 a 1.
    # Multiplicado por 0.12 va de -0.12 a 0.12.
    # Sumado a 1.0, el rango final es 0.88 (contraer) a 1.12 (expandir).
    factor_escala = 1.0 + math.sin(tiempo) * 0.12

    # Aplicamos la escala uniformemente en los ejes X, Y y Z.
    # Esto debe ocurrir ANTES de glBegin(GL_TRIANGLES).
    glScalef(factor_escala, factor_escala, factor_escala)

    # --- EFECTO LÍQUIDO CON TODOS LOS COLORES (Como el anterior) ---
    glBegin(GL_TRIANGLES)
    
    # Vértice 1 (Arriba) - Cicla por todo el espectro suavemente
    r1 = (math.sin(tiempo + 0.0) + 1.0) / 2.0
    g1 = (math.sin(tiempo + 2.0) + 1.0) / 2.0
    b1 = (math.sin(tiempo + 4.0) + 1.0) / 2.0
    glColor3f(r1, g1, b1)
    glVertex3f(0.0, 1.0, 0.0)

    # Vértice 2 (Abajo a la izquierda) - Cicla con desfase
    r2 = (math.sin(tiempo + 2.0) + 1.0) / 2.0
    g2 = (math.sin(tiempo + 4.0) + 1.0) / 2.0
    b2 = (math.sin(tiempo + 0.0) + 1.0) / 2.0
    glColor3f(r2, g2, b2)
    glVertex3f(-1.0, -1.0, 0.0)

    # Vértice 3 (Abajo a la derecha) - Cicla con otro desfase
    r3 = (math.sin(tiempo + 4.0) + 1.0) / 2.0
    g3 = (math.sin(tiempo + 0.0) + 1.0) / 2.0
    b3 = (math.sin(tiempo + 2.0) + 1.0) / 2.0
    glColor3f(r3, g3, b3)
    glVertex3f(1.0, -1.0, 0.0)

    glEnd()
    glutSwapBuffers()

def idle():
    global tiempo
    # Velocidad de la animación (lenta y fluida)
    tiempo += 0.005 
    glutPostRedisplay()

def keyboard(key, x, y):
    if key == b'\x1b': # Tecla ESC para salir
        glutDestroyWindow(glutGetWindow())
        sys.exit()

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    
    glutCreateWindow(b"Triangulo - Fluidos Respirando")
    
    init()
    
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard)
    
    glutMainLoop()

if __name__ == "__main__":
    main()