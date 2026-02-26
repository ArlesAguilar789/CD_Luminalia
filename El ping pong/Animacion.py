import cv2 as cv
import numpy as np

# --- Configuración de la ventana ---
WIDTH, HEIGHT = 600, 400
PADDLE_W, PADDLE_H = 15, 80
BALL_R = 10


ball_x, ball_y = WIDTH // 2, HEIGHT // 2
ball_vx, ball_vy = 12, 12 

print("Mostrando animación de Ping Pong...")
print("Presiona la tecla 'ESC' para cerrar la ventana.")

while True:
    # 1. Crear fondo negro
    img = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    
    # 2. Decoración de la cancha (Línea central y círculo)
    cv.line(img, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), (100, 100, 100), 2)
    cv.circle(img, (WIDTH // 2, HEIGHT // 2), 60, (100, 100, 100), 2)

    # --- LÓGICA DE LA PELOTA ---
    ball_x += ball_vx
    ball_y += ball_vy

    # Rebote superior e inferior
    if ball_y - BALL_R <= 0 or ball_y + BALL_R >= HEIGHT:
        ball_vy *= -1

    # --- LÓGICA AUTOMÁTICA (Las paletas siguen la pelota) ---
    # Centramos la paleta con la altura actual de la pelota
    left_paddle_y = ball_y - (PADDLE_H // 2)
    right_paddle_y = ball_y - (PADDLE_H // 2)

    # Evitamos que las paletas se salgan de la pantalla visualmente
    left_paddle_y = max(0, min(left_paddle_y, HEIGHT - PADDLE_H))
    right_paddle_y = max(0, min(right_paddle_y, HEIGHT - PADDLE_H))

    # --- REBOTES EN LAS PALETAS ---
    if (ball_x - BALL_R <= 20 + PADDLE_W) and (left_paddle_y <= ball_y <= left_paddle_y + PADDLE_H):
        ball_vx *= -1
        ball_x = 20 + PADDLE_W + BALL_R 

    if (ball_x + BALL_R >= WIDTH - 20 - PADDLE_W) and (right_paddle_y <= ball_y <= right_paddle_y + PADDLE_H):
        ball_vx *= -1
        ball_x = WIDTH - 20 - PADDLE_W - BALL_R

    # --- DIBUJAR LOS ELEMENTOS ---
    # Paletas
    cv.rectangle(img, (20, left_paddle_y), (20 + PADDLE_W, left_paddle_y + PADDLE_H), (255, 0, 0), -1)
    cv.rectangle(img, (WIDTH - 20 - PADDLE_W, right_paddle_y), (WIDTH - 20, right_paddle_y + PADDLE_H), (0, 0, 255), -1)
    
    # Pelota
    cv.circle(img, (ball_x, ball_y), BALL_R, (0, 255, 0), -1)

    # 3. Mostrar y esperar
    cv.imshow('Animacion Ping Pong', img)
    
    # Solo comprobamos si se presiona la tecla ESC (código 27) para salir
    if cv.waitKey(30) & 0xFF == 27: 
        break

cv.destroyAllWindows()