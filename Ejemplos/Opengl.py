from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

def draw():
    # Limpiar la pantalla
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    # Cambiar el color de fondo a un azul oscuro
    glClearColor(0.1, 0.1, 0.2, 1.0)
    
    # Intercambiar los buffers para mostrar lo dibujado
    glutSwapBuffers()

def main():
    # Inicializar GLUT
    glutInit()
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(500, 500)
    
    # Crear la ventana
    glutCreateWindow(b"Mi primera ventana OpenGL en Python")
    
    # Asignar la función de dibujo
    glutDisplayFunc(draw)
    
    # Iniciar el bucle principal
    glutMainLoop()

if __name__ == "__main__":
    main()