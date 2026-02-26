import cv2 as cv
import numpy as np

# --- Configuración de la ventana ---
WIDTH, HEIGHT = 600, 400
PADDLE_W, PADDLE_H = 15, 80
BALL_R = 10

# --- Estado inicial del juego ---
# Posiciones Y de las paletas
left_paddle_y = HEIGHT // 2 - PADDLE_H // 2
right_paddle_y = HEIGHT // 2 - PADDLE_H // 2

# Posición y velocidad de la pelota
ball_x, ball_y = WIDTH // 2, HEIGHT // 2
ball_vx, ball_vy = 8, 8

# Velocidad de movimiento de las paletas
PADDLE_SPEED = 30

print("¡Iniciando Ping Pong!")
print("Controles Jugador 1 (Izquierda): 'W' para subir, 'S' para bajar")
print("Controles Jugador 2 (Derecha): 'I' para subir, 'K' para bajar")
print("Presiona 'Q' o 'ESC' para salir.")

while True:
    # 1. Crear un fondo negro (Limpiar la pantalla)
    img = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    
    # 2. Dibujar la línea central (decoración)
    cv.line(img, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), (100, 100, 100), 2)

    # --- LÓGICA DE LA PELOTA ---
    # Mover la pelota
    ball_x += ball_vx
    ball_y += ball_vy

    # Rebote en la parte superior e inferior
    if ball_y - BALL_R <= 0 or ball_y + BALL_R >= HEIGHT:
        ball_vy *= -1

    # Rebote en la paleta izquierda
    if (ball_x - BALL_R <= 20 + PADDLE_W) and (left_paddle_y <= ball_y <= left_paddle_y + PADDLE_H):
        ball_vx *= -1
        ball_x = 20 + PADDLE_W + BALL_R # Evitar que la pelota se quede pegada

    # Rebote en la paleta derecha
    if (ball_x + BALL_R >= WIDTH - 20 - PADDLE_W) and (right_paddle_y <= ball_y <= right_paddle_y + PADDLE_H):
        ball_vx *= -1
        ball_x = WIDTH - 20 - PADDLE_W - BALL_R

    # Fuera de los límites (Punto anotado / Reinicio)
    if ball_x < 0 or ball_x > WIDTH:
        ball_x, ball_y = WIDTH // 2, HEIGHT // 2 # Reiniciar al centro
        ball_vx *= -1 # Sacar hacia el lado del jugador que acaba de anotar

    # --- DIBUJAR LOS ELEMENTOS ---
    # Paleta Izquierda (Azul)
    cv.rectangle(img, (20, left_paddle_y), (20 + PADDLE_W, left_paddle_y + PADDLE_H), (255, 0, 0), -1)
    # Paleta Derecha (Rojo)
    cv.rectangle(img, (WIDTH - 20 - PADDLE_W, right_paddle_y), (WIDTH - 20, right_paddle_y + PADDLE_H), (0, 0, 255), -1)
    # Pelota (Verde)
    cv.circle(img, (ball_x, ball_y), BALL_R, (0, 255, 0), -1)

    # 3. Mostrar la imagen en pantalla
    cv.imshow('Ping Pong - OpenCV', img)
    
    # --- CONTROLES Y TECLADO ---
    key = cv.waitKey(30) & 0xFF
    
    if key == 27 or key == ord('q'): # Tecla ESC o 'q' para salir
        break
    
    # Controles Jugador 1
    elif key == ord('w') and left_paddle_y > 0:
        left_paddle_y -= PADDLE_SPEED
    elif key == ord('s') and left_paddle_y < HEIGHT - PADDLE_H:
        left_paddle_y += PADDLE_SPEED
        
    # Controles Jugador 2
    elif key == ord('i') and right_paddle_y > 0:
        right_paddle_y -= PADDLE_SPEED
    elif key == ord('k') and right_paddle_y < HEIGHT - PADDLE_H:
        right_paddle_y += PADDLE_SPEED

# Cerrar las ventanas limpiamente al salir del ciclo
cv.destroyAllWindows()