from __future__ import annotations

import math
import os
import struct
import sys
import zlib
from pathlib import Path

import glfw
from OpenGL.GL import *
from OpenGL.GLU import (
    GLU_FILL,
    gluLookAt,
    gluNewQuadric,
    gluPerspective,
    gluQuadricDrawStyle,
    gluSphere,
)

# ---------------------------------------------------------------------------
# Configuración principal
# ---------------------------------------------------------------------------
WINDOW_TITLE = "Orbita Dual (GLFW) — 1/2/3/4 cambia modo, 5 captura bonita"
INITIAL_MODE = 1

ORBIT_RADIUS = 5.0
CAM_DISTANCE = 5.0
ANGLE_SPEED = 0.6

# Iluminación activada por defecto para que las esferas se vean mejor.
USE_LIGHTING = True
USE_DIRECTIONAL_LIGHT = True

WIDTH = 900
HEIGHT = 700

# Ruta pedida para guardar las imágenes del reporte.
# Si estás en Windows, se guardará aquí.
REPORT_IMAGE_DIR = Path(
    r"C:\Users\Arles Aguilar\Documents\Tareas Graficacion\Mision Orbita\Imagenes Reporte"
)

# Si por alguna razón esa ruta no existe, el programa intenta crearla.
# Si no puede crearla, usa la carpeta actual.
FALLBACK_IMAGE_DIR = Path.cwd()

_quadric = None


# ---------------------------------------------------------------------------
# Utilidad: guardar PNG sin depender de Pillow
# ---------------------------------------------------------------------------
def _png_chunk(tag: bytes, data: bytes) -> bytes:
    chunk = tag + data
    return (
        struct.pack(">I", len(data))
        + chunk
        + struct.pack(">I", zlib.crc32(chunk) & 0xFFFFFFFF)
    )


def resolve_output_dir() -> Path:
    """Devuelve la carpeta de salida para capturas."""
    try:
        REPORT_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
        return REPORT_IMAGE_DIR
    except OSError:
        FALLBACK_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
        print(
            "[AVISO] No se pudo usar la ruta del reporte. "
            f"Se guardará en: {FALLBACK_IMAGE_DIR}"
        )
        return FALLBACK_IMAGE_DIR


def save_screenshot_png(filename: str, width: int, height: int) -> Path:
    """Guarda el framebuffer actual como PNG usando solo stdlib."""
    output_dir = resolve_output_dir()
    full_path = output_dir / filename

    glPixelStorei(GL_PACK_ALIGNMENT, 1)
    raw = glReadPixels(0, 0, width, height, GL_RGB, GL_UNSIGNED_BYTE)

    # OpenGL lee de abajo hacia arriba; PNG espera arriba hacia abajo.
    row_len = width * 3
    rows = []
    for y in range(height - 1, -1, -1):
        row = raw[y * row_len : (y + 1) * row_len]
        rows.append(b"\x00" + row)

    png_data = b"".join(rows)
    compressed = zlib.compress(png_data, 9)

    header = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)

    out = (
        header
        + _png_chunk(b"IHDR", ihdr)
        + _png_chunk(b"IDAT", compressed)
        + _png_chunk(b"IEND", b"")
    )

    full_path.write_bytes(out)
    print(f"[OK] Captura guardada: {full_path}")
    return full_path


# ---------------------------------------------------------------------------
# Geometría y diseño visual
# ---------------------------------------------------------------------------
def draw_sphere(radius: float = 1.0) -> None:
    global _quadric
    if _quadric is None:
        _quadric = gluNewQuadric()
        gluQuadricDrawStyle(_quadric, GLU_FILL)
    gluSphere(_quadric, radius, 64, 40)


def draw_wire_sphere(radius: float = 1.015) -> None:
    """Dibuja líneas tipo meridianos/paralelos sobre la esfera."""
    lighting_was_on = glIsEnabled(GL_LIGHTING)
    if lighting_was_on:
        glDisable(GL_LIGHTING)

    glColor3f(1.0, 1.0, 1.0)
    glLineWidth(1.0)

    # Paralelos
    for lat in range(-60, 75, 15):
        y = radius * math.sin(math.radians(lat))
        r = radius * math.cos(math.radians(lat))

        glBegin(GL_LINE_LOOP)
        for i in range(96):
            a = 2.0 * math.pi * i / 96.0
            glVertex3f(r * math.cos(a), y, r * math.sin(a))
        glEnd()

    # Meridianos
    for lon in range(0, 180, 15):
        glBegin(GL_LINE_LOOP)
        for i in range(96):
            a = 2.0 * math.pi * i / 96.0
            x = radius * math.sin(a) * math.cos(math.radians(lon))
            y = radius * math.cos(a)
            z = radius * math.sin(a) * math.sin(math.radians(lon))
            glVertex3f(x, y, z)
        glEnd()

    if lighting_was_on:
        glEnable(GL_LIGHTING)


def draw_orbit_ring(radius: float = 5.0) -> None:
    """Anillo en el plano XZ para visualizar la órbita."""
    lighting_was_on = glIsEnabled(GL_LIGHTING)
    if lighting_was_on:
        glDisable(GL_LIGHTING)

    glColor3f(0.7, 0.7, 0.75)
    glLineWidth(1.5)
    glBegin(GL_LINE_LOOP)
    for i in range(160):
        a = 2.0 * math.pi * i / 160.0
        glVertex3f(radius * math.cos(a), -1.25, radius * math.sin(a))
    glEnd()

    if lighting_was_on:
        glEnable(GL_LIGHTING)


def draw_reference_axes(length: float = 2.4) -> None:
    """Ejes simples para visualizar orientación."""
    lighting_was_on = glIsEnabled(GL_LIGHTING)
    if lighting_was_on:
        glDisable(GL_LIGHTING)

    glLineWidth(2.0)
    glBegin(GL_LINES)

    # X rojo
    glColor3f(1.0, 0.12, 0.12)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(length, 0.0, 0.0)

    # Y verde
    glColor3f(0.12, 1.0, 0.12)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(0.0, length, 0.0)

    # Z azul
    glColor3f(0.2, 0.45, 1.0)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(0.0, 0.0, length)

    glEnd()

    if lighting_was_on:
        glEnable(GL_LIGHTING)


def draw_floor_grid(size: int = 8, step: float = 1.0) -> None:
    """Cuadrícula suave para dar más sensación de escena 3D."""
    lighting_was_on = glIsEnabled(GL_LIGHTING)
    if lighting_was_on:
        glDisable(GL_LIGHTING)

    glColor3f(0.22, 0.22, 0.28)
    glLineWidth(1.0)
    glBegin(GL_LINES)

    half = size
    y = -1.3

    for i in range(-half, half + 1):
        glVertex3f(i * step, y, -half * step)
        glVertex3f(i * step, y, half * step)

        glVertex3f(-half * step, y, i * step)
        glVertex3f(half * step, y, i * step)

    glEnd()

    if lighting_was_on:
        glEnable(GL_LIGHTING)


def draw_designed_sphere(
    base_color: tuple[float, float, float],
    angle: float,
    show_wire: bool = True,
) -> None:
    """
    Esfera con material, brillo, líneas y un aro inclinado para que se vea mejor
    en capturas del reporte.
    """
    glColor3f(*base_color)
    draw_sphere(1.0)

    if show_wire:
        draw_wire_sphere(1.018)

    # Aro inclinado decorativo, como una órbita local.
    lighting_was_on = glIsEnabled(GL_LIGHTING)
    if lighting_was_on:
        glDisable(GL_LIGHTING)

    glPushMatrix()
    glRotatef(65.0, 1.0, 0.0, 0.0)
    glRotatef(angle * 0.35, 0.0, 1.0, 0.0)

    glColor3f(1.0, 0.95, 0.65)
    glLineWidth(2.0)
    glBegin(GL_LINE_LOOP)
    for i in range(160):
        a = 2.0 * math.pi * i / 160.0
        glVertex3f(1.35 * math.cos(a), 0.0, 1.35 * math.sin(a))
    glEnd()

    glPopMatrix()

    if lighting_was_on:
        glEnable(GL_LIGHTING)


def draw_scene_helpers() -> None:
    draw_floor_grid()
    draw_orbit_ring(ORBIT_RADIUS)
    draw_reference_axes()


# ---------------------------------------------------------------------------
# Iluminación
# ---------------------------------------------------------------------------
def setup_basic_lighting() -> None:
    """Configura propiedades generales de iluminación."""
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glShadeModel(GL_SMOOTH)

    # Luz ambiental, difusa y especular.
    amb = [0.22, 0.22, 0.25, 1.0]
    dif = [0.95, 0.92, 0.84, 1.0]
    spec = [0.70, 0.70, 0.72, 1.0]

    glLightfv(GL_LIGHT0, GL_AMBIENT, amb)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, dif)
    glLightfv(GL_LIGHT0, GL_SPECULAR, spec)

    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, spec)
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 48.0)


def place_light() -> None:
    """
    Coloca la luz usando la MODELVIEW actual.

    glLightfv(GL_LIGHT0, GL_POSITION, pos) transforma la luz por la matriz
    MODELVIEW activa en ese instante. Por eso importa si se llama antes o
    después de mover cámara, mundo u objeto.
    """
    if not USE_LIGHTING:
        return

    if USE_DIRECTIONAL_LIGHT:
        pos = [0.5, 0.8, 1.0, 0.0]  # w=0: luz direccional
    else:
        pos = [2.5, 2.0, 2.5, 1.0]  # w=1: luz puntual

    glLightfv(GL_LIGHT0, GL_POSITION, pos)


# ---------------------------------------------------------------------------
# Modos de render
# ---------------------------------------------------------------------------
def render_rotating_object(angle: float) -> None:
    """
    Modo 1:
    Cámara fija: se aleja la escena en -Z.
    Objeto rota sobre su propio eje Y.
    """
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glTranslatef(0.0, 0.0, -CAM_DISTANCE)
    place_light()

    draw_scene_helpers()

    glPushMatrix()
    glRotatef(angle, 0.0, 1.0, 0.0)
    draw_designed_sphere((0.22, 0.55, 1.0), angle)
    glPopMatrix()


def render_orbiting_camera(angle: float) -> None:
    """
    Modo 2:
    Objeto fijo en el origen.
    La cámara orbita aplicando la transformación inversa al mundo.
    """
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glRotatef(-angle, 0.0, 1.0, 0.0)
    glTranslatef(0.0, 0.0, -CAM_DISTANCE)

    place_light()
    draw_scene_helpers()

    draw_designed_sphere((1.0, 0.45, 0.25), angle)


def render_orbiting_camera_variant_b(angle: float) -> None:
    """
    Variante B:
    Primero translate y luego rotate. Sirve para comparar el orden.
    """
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glTranslatef(0.0, 0.0, -CAM_DISTANCE)
    glRotatef(angle, 0.0, 1.0, 0.0)

    place_light()
    draw_scene_helpers()

    draw_designed_sphere((0.35, 1.0, 0.45), angle)


def render_with_lookat(angle: float) -> None:
    """
    Modo 3:
    Cámara declarativa con gluLookAt.
    El ojo se mueve en una órbita circular alrededor del origen.
    """
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    a = math.radians(angle)
    cam_x = ORBIT_RADIUS * math.sin(a)
    cam_z = ORBIT_RADIUS * math.cos(a)

    gluLookAt(
        cam_x, 1.3, cam_z,  # eye
        0.0, 0.0, 0.0,      # center
        0.0, 1.0, 0.0,      # up
    )

    place_light()
    draw_scene_helpers()

    draw_designed_sphere((0.95, 0.78, 0.25), angle)


def capture_filename_for_mode(mode: int, lighting_enabled: bool) -> str:
    """
    Nombres compatibles con el .md.
    Si hay iluminación y el modo es 1 o 2, guarda las imágenes de Misión 3.
    """
    if lighting_enabled:
        if mode == 1:
            return "m3_luz_objeto.png"
        if mode == 2:
            return "m3_luz_camara.png"

    if mode == 1:
        return "m1_objeto_rota.png"
    if mode == 2:
        return "m1_camara_orbita.png"
    if mode == 3:
        return "m2_lookat_orbita.png"
    return "m1_camara_orbita_variante_b.png"


def pretty_capture_target_angle(mode: int) -> float:
    """
    Ángulos elegidos para que las capturas se vean bien:
    se evita tomar fotos de frente plano y se buscan diagonales.
    """
    if mode == 1:
        return 45.0
    if mode == 2:
        return 315.0
    if mode == 3:
        return 45.0
    return 45.0


def angle_distance_degrees(a: float, b: float) -> float:
    """Distancia angular mínima entre dos ángulos."""
    diff = abs((a - b + 180.0) % 360.0 - 180.0)
    return diff


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    global USE_LIGHTING

    if not glfw.init():
        print("Error: no se pudo inicializar GLFW", file=sys.stderr)
        sys.exit(1)

    # OpenGL 2.1: pipeline fijo en Linux/Windows.
    # En macOS moderno puede requerirse otro perfil o framework.
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 2)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)

    window = glfw.create_window(WIDTH, HEIGHT, WINDOW_TITLE, None, None)
    if not window:
        glfw.terminate()
        print("Error: no se pudo crear la ventana OpenGL", file=sys.stderr)
        sys.exit(1)

    glfw.make_context_current(window)
    glfw.swap_interval(1)

    mode = INITIAL_MODE

    # La tecla 5 activa esta bandera. El programa espera al ángulo bonito.
    capture_armed = False
    capture_target = pretty_capture_target_angle(mode)

    def on_key(win, key, scancode, action, mods):
        global USE_LIGHTING
        nonlocal mode, capture_armed, capture_target

        if action != glfw.PRESS:
            return

        if key in (glfw.KEY_ESCAPE, glfw.KEY_Q):
            glfw.set_window_should_close(win, True)

        elif key == glfw.KEY_1:
            mode = 1
            capture_armed = False
            print("Modo 1: objeto rota, cámara fija")

        elif key == glfw.KEY_2:
            mode = 2
            capture_armed = False
            print("Modo 2: cámara orbita, objeto fijo")

        elif key == glfw.KEY_3:
            mode = 3
            capture_armed = False
            print("Modo 3: gluLookAt")

        elif key == glfw.KEY_4:
            mode = 4
            capture_armed = False
            print("Modo 4: variante B translate + rotate")

        elif key == glfw.KEY_L:
            USE_LIGHTING = not USE_LIGHTING
            capture_armed = False
            estado = "activada" if USE_LIGHTING else "desactivada"
            print(f"Iluminación {estado}")

        elif key == glfw.KEY_5:
            capture_armed = True
            capture_target = pretty_capture_target_angle(mode)
            filename = capture_filename_for_mode(mode, USE_LIGHTING)
            print(
                "[INFO] Captura preparada. "
                f"Esperando ángulo bonito: {capture_target:.1f}°. "
                f"Archivo: {filename}"
            )

    glfw.set_key_callback(window, on_key)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_NORMALIZE)
    glClearColor(0.06, 0.065, 0.09, 1.0)

    angle = 0.0

    print("Controles:")
    print("  1/2/3/4 cambia modo")
    print("  5 prepara captura automática bonita")
    print("  L activa/desactiva iluminación")
    print("  ESC/Q salir")
    print(f"Carpeta de imágenes: {REPORT_IMAGE_DIR}")

    while not glfw.window_should_close(window):
        fb_w, fb_h = glfw.get_framebuffer_size(window)
        if fb_h <= 0:
            fb_h = 1

        glViewport(0, 0, fb_w, fb_h)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(50.0, fb_w / float(fb_h), 0.1, 100.0)

        if USE_LIGHTING:
            setup_basic_lighting()
        else:
            glDisable(GL_LIGHTING)

        if mode == 1:
            render_rotating_object(angle)
        elif mode == 2:
            render_orbiting_camera(angle)
        elif mode == 3:
            render_with_lookat(angle)
        else:
            render_orbiting_camera_variant_b(angle)

        # Tecla 5:
        # No captura al instante; espera a que el ángulo esté cerca del target.
        if capture_armed:
            if angle_distance_degrees(angle, capture_target) <= max(ANGLE_SPEED, 0.75):
                filename = capture_filename_for_mode(mode, USE_LIGHTING)
                save_screenshot_png(filename, fb_w, fb_h)
                capture_armed = False

        angle += ANGLE_SPEED
        if angle >= 360.0:
            angle -= 360.0

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()


if __name__ == "__main__":
    main()
