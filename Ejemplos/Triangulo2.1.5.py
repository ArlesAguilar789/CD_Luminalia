import sys
import math
import random
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# Configuración de la ventana
ANCHO = 800
ALTO = 600

# Variables globales
tiempo = 0.0
mouse_x = -1000 # Iniciar fuera de la pantalla
mouse_y = -1000
triangulos = []

class Triangulo:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        # Velocidad aleatoria inicial
        self.vx = random.uniform(-2.0, 2.0)
        self.vy = random.uniform(-2.0, 2.0)
        
        # Tamaño y hitbox (Radio de colisión)
        self.radio = 15.0 
        
        # Estética
        self.angulo = random.uniform(0, 360)
        self.vel_rotacion = random.uniform(-3.0, 3.0)
        self.color_offset = random.uniform(0.0, 10.0) # Para que cada uno tenga colores distintos

    def actualizar(self):
        # 1. Aplicar velocidad a la posición
        self.x += self.vx
        self.y += self.vy
        self.angulo += self.vel_rotacion

        # Fricción ligera para que no se aceleren infinitamente
        self.vx *= 0.98
        self.vy *= 0.98

        # 2. Rebotar en los bordes de la ventana
        if self.x - self.radio < 0:
            self.x = self.radio
            self.vx *= -1
        elif self.x + self.radio > ANCHO:
            self.x = ANCHO - self.radio
            self.vx *= -1
            
        if self.y - self.radio < 0:
            self.y = self.radio
            self.vy *= -1
        elif self.y + self.radio > ALTO:
            self.y = ALTO - self.radio
            self.vy *= -1

        # 3. Evadir el Mouse
        dx = self.x - mouse_x
        dy = self.y - mouse_y
        distancia_mouse = math.hypot(dx, dy) # Calcula la hipotenusa (distancia)
        
        radio_evasion = 150.0 # Qué tan cerca debe estar el mouse para que huyan
        
        if distancia_mouse < radio_evasion and distancia_mouse > 0:
            # Entre más cerca, más fuerte es el empujón
            fuerza = (radio_evasion - distancia_mouse) / radio_evasion
            self.vx += (dx / distancia_mouse) * fuerza * 2.0
            self.vy += (dy / distancia_mouse) * fuerza * 2.0

        # Límite de velocidad (para que no salgan volando como balas)
        vel_maxima = 8.0
        velocidad_actual = math.hypot(self.vx, self.vy)
        if velocidad_actual > vel_maxima:
            self.vx = (self.vx / velocidad_actual) * vel_maxima
            self.vy = (self.vy / velocidad_actual) * vel_maxima

    def dibujar(self, t):
        glPushMatrix() # Guardar el estado de la matriz
        
        # Mover el origen a la posición del triángulo y rotarlo
        glTranslatef(self.x, self.y, 0.0)
        glRotatef(self.angulo, 0.0, 0.0, 1.0)
        
        # Escalar al tamaño del hitbox
        glScalef(self.radio, self.radio, 1.0)

        # Dibujar el triángulo con los colores fluidos
        glBegin(GL_TRIANGLES)
        
        # Vértice 1
        r = (math.sin(t + self.color_offset + 0.0) + 1.0) / 2.0
        g = (math.sin(t + self.color_offset + 2.0) + 1.0) / 2.0
        b = (math.sin(t + self.color_offset + 4.0) + 1.0) / 2.0
        glColor3f(r, g, b)
        glVertex2f(0.0, 1.0)

        # Vértice 2
        r = (math.sin(t + self.color_offset + 2.0) + 1.0) / 2.0
        g = (math.sin(t + self.color_offset + 4.0) + 1.0) / 2.0
        b = (math.sin(t + self.color_offset + 0.0) + 1.0) / 2.0
        glColor3f(r, g, b)
        glVertex2f(-0.866, -0.5)

        # Vértice 3
        r = (math.sin(t + self.color_offset + 4.0) + 1.0) / 2.0
        g = (math.sin(t + self.color_offset + 0.0) + 1.0) / 2.0
        b = (math.sin(t + self.color_offset + 2.0) + 1.0) / 2.0
        glColor3f(r, g, b)
        glVertex2f(0.866, -0.5)

        glEnd()
        glPopMatrix() # Restaurar la matriz para el siguiente triángulo

def manejar_colisiones():
    # Compara cada triángulo con todos los demás
    for i in range(len(triangulos)):
        for j in range(i + 1, len(triangulos)):
            t1 = triangulos[i]
            t2 = triangulos[j]
            
            dx = t1.x - t2.x
            dy = t1.y - t2.y
            distancia = math.hypot(dx, dy)
            distancia_minima = t1.radio + t2.radio
            
            # Si la distancia es menor a la suma de sus radios, están colisionando
            if distancia < distancia_minima and distancia > 0:
                # Calcular cuánto se están superponiendo
                superposicion = distancia_minima - distancia
                
                # Empujarlos en direcciones opuestas para separarlos (evita que se fusionen)
                nx = dx / distancia
                ny = dy / distancia
                
                t1.x += nx * superposicion * 0.5
                t1.y += ny * superposicion * 0.5
                t2.x -= nx * superposicion * 0.5
                t2.y -= ny * superposicion * 0.5
                
                # Transferencia de energía básica (rebote suave)
                t1.vx, t2.vx = t2.vx * 0.8, t1.vx * 0.8
                t1.vy, t2.vy = t2.vy * 0.8, t1.vy * 0.8

def init():
    glClearColor(0.05, 0.05, 0.08, 1.0)
    
    # Configurar cámara 2D ortogonal (1 unidad de OpenGL = 1 pixel)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    # (Izquierda, Derecha, Abajo, Arriba, Cerca, Lejos)
    glOrtho(0, ANCHO, 0, ALTO, -1.0, 1.0)
    glMatrixMode(GL_MODELVIEW)
    
    # Crear 50 triángulos aleatorios
    for _ in range(50):
        t = Triangulo(random.randint(50, ANCHO-50), random.randint(50, ALTO-50))
        triangulos.append(t)

def display():
    global tiempo
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    
    manejar_colisiones()
    
    for t in triangulos:
        t.actualizar()
        t.dibujar(tiempo)
        
    glutSwapBuffers()

def idle():
    global tiempo
    tiempo += 0.05
    glutPostRedisplay()

# Función para rastrear el movimiento del mouse (sin hacer clic)
def mouse_motion(x, y):
    global mouse_x, mouse_y
    mouse_x = x
    # GLUT invierte el eje Y respecto a OpenGL, lo corregimos:
    mouse_y = ALTO - y 

def keyboard(key, x, y):
    if key == b'\x1b':
        glutDestroyWindow(glutGetWindow())
        sys.exit()

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(ANCHO, ALTO)
    glutCreateWindow(b"Enjambre Interactivo")
    
    init()
    
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard)
    # Esta línea activa la lectura del mouse todo el tiempo
    glutPassiveMotionFunc(mouse_motion) 
    
    print("Mueve el cursor por la ventana para asustar a los triangulos. ESC para salir.")
    glutMainLoop()

if __name__ == "__main__":
    main()