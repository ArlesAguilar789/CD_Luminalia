import math
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *

WIDTH = 900
HEIGHT = 700
rotation = 0.0


def set_material(color, specular, shininess):
    glColor4f(color[0], color[1], color[2], color[3])
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, specular)
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, shininess)


def sphere(radius, slices=80, stacks=80):
    q = gluNewQuadric()
    gluQuadricNormals(q, GLU_SMOOTH)
    gluSphere(q, radius, slices, stacks)
    gluDeleteQuadric(q)


def disk(radius, inner=0.0, slices=128):
    q = gluNewQuadric()
    gluQuadricNormals(q, GLU_SMOOTH)
    gluDisk(q, inner, radius, slices, 1)
    gluDeleteQuadric(q)


def ellipse_disk(radius, sx, sy):
    glPushMatrix()
    glScalef(sx, sy, 1.0)
    disk(radius)
    glPopMatrix()


def draw_arc(cx, cy, z, rx, ry, a0, a1, width):
    glDisable(GL_LIGHTING)
    glColor3f(0.015, 0.012, 0.014)
    glLineWidth(width)
    glBegin(GL_LINE_STRIP)
    for i in range(90):
        t = math.radians(a0 + (a1 - a0) * i / 89.0)
        glVertex3f(cx + math.cos(t) * rx, cy + math.sin(t) * ry, z)
    glEnd()
    glLineWidth(1.0)
    glEnable(GL_LIGHTING)


def draw_lashes():
    glDisable(GL_LIGHTING)
    glColor3f(0.015, 0.012, 0.014)
    glLineWidth(3.5)
    glBegin(GL_LINES)
    for a in [-145, -125, -105, -85, -65, -45, -25]:
        t = math.radians(a)
        x = math.cos(t) * 1.02
        y = 0.08 - math.sin(t) * 0.50
        dx = math.cos(t) * 0.18
        dy = -math.sin(t) * 0.22
        glVertex3f(x, y, 0.57)
        glVertex3f(x + dx, y + dy, 0.60)
    glEnd()
    glLineWidth(1.0)
    glEnable(GL_LIGHTING)


def draw_eye():
    glPushMatrix()

    set_material([0.98, 0.97, 0.93, 1.0], [0.90, 0.90, 0.86, 1.0], 80.0)
    glPushMatrix()
    glScalef(1.32, 0.82, 0.58)
    sphere(1.0)
    glPopMatrix()

    set_material([0.02, 0.025, 0.06, 1.0], [0.20, 0.22, 0.30, 1.0], 24.0)
    glPushMatrix()
    glTranslatef(0.0, -0.02, 0.615)
    ellipse_disk(0.53, 0.82, 1.0)
    glPopMatrix()

    set_material([0.06, 0.28, 0.88, 1.0], [0.45, 0.62, 1.00, 1.0], 48.0)
    glPushMatrix()
    glTranslatef(0.0, -0.02, 0.625)
    ellipse_disk(0.47, 0.82, 1.0)
    glPopMatrix()

    set_material([0.13, 0.65, 1.00, 1.0], [0.50, 0.75, 1.00, 1.0], 70.0)
    glPushMatrix()
    glTranslatef(0.0, -0.07, 0.635)
    ellipse_disk(0.31, 0.76, 1.08)
    glPopMatrix()

    set_material([0.005, 0.005, 0.008, 1.0], [0.04, 0.04, 0.05, 1.0], 12.0)
    glPushMatrix()
    glTranslatef(0.0, -0.04, 0.648)
    ellipse_disk(0.19, 0.78, 1.18)
    glPopMatrix()

    set_material([1.0, 1.0, 1.0, 1.0], [1.0, 1.0, 1.0, 1.0], 128.0)
    glPushMatrix()
    glTranslatef(0.15, 0.20, 0.662)
    ellipse_disk(0.105, 0.80, 1.0)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(-0.12, -0.14, 0.664)
    ellipse_disk(0.045, 0.75, 1.0)
    glPopMatrix()

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDepthMask(GL_FALSE)
    set_material([0.90, 0.98, 1.0, 0.22], [1.0, 1.0, 1.0, 1.0], 128.0)
    glPushMatrix()
    glScalef(1.34, 0.84, 0.60)
    sphere(1.006)
    glPopMatrix()
    glDepthMask(GL_TRUE)
    glDisable(GL_BLEND)

    draw_arc(0.0, -0.05, 0.69, 1.05, 0.56, 25, 155, 5.0)
    draw_arc(0.0, -0.06, 0.69, 0.92, 0.40, 205, 335, 2.5)
    draw_lashes()

    glPopMatrix()


def setup_lighting():
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)
    glEnable(GL_NORMALIZE)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.16, 0.16, 0.16, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 0.96, 0.90, 1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])

    glLightfv(GL_LIGHT1, GL_AMBIENT, [0.02, 0.03, 0.06, 1.0])
    glLightfv(GL_LIGHT1, GL_DIFFUSE, [0.16, 0.22, 0.42, 1.0])
    glLightfv(GL_LIGHT1, GL_SPECULAR, [0.08, 0.12, 0.20, 1.0])

    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.05, 0.05, 0.06, 1.0])
    glLightModeli(GL_LIGHT_MODEL_LOCAL_VIEWER, GL_TRUE)
    glShadeModel(GL_SMOOTH)


def place_lights():
    glLightfv(GL_LIGHT0, GL_POSITION, [2.6, 2.1, 3.0, 1.0])
    glLightfv(GL_LIGHT1, GL_POSITION, [-2.5, -0.8, 2.0, 1.0])


def draw_floor():
    set_material([0.28, 0.35, 0.37, 1.0], [0.04, 0.04, 0.04, 1.0], 6.0)
    glBegin(GL_QUADS)
    glNormal3f(0.0, 1.0, 0.0)
    glVertex3f(-4.0, -1.35, -2.5)
    glVertex3f(4.0, -1.35, -2.5)
    glVertex3f(4.0, -1.35, 2.5)
    glVertex3f(-4.0, -1.35, 2.5)
    glEnd()


def main():
    global rotation

    if not glfw.init():
        return

    window = glfw.create_window(WIDTH, HEIGHT, "Ojo 3D Anime Profesional", None, None)

    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.swap_interval(1)

    glViewport(0, 0, WIDTH, HEIGHT)
    glClearColor(0.62, 0.78, 0.90, 1.0)

    setup_lighting()

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, WIDTH / HEIGHT, 0.1, 100.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(0.0, 0.0, 5.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

        place_lights()
        draw_floor()

        glPushMatrix()
        rotation = (rotation + 0.65) % 360.0
        glRotatef(rotation, 0.0, 1.0, 0.0)
        draw_eye()
        glPopMatrix()

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()


if __name__ == "__main__":
    main()
