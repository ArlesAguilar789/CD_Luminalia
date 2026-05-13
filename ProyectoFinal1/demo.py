
"""
Proyecto Final: Demo Procedural Magistral con OpenCV
Autor: Arles Aguilar
Curso: Graficacion / Computacion Grafica

Requisitos cumplidos:
- Python 3 + numpy + opencv-python.
- Resolucion 800x600, 30 FPS objetivo.
- 42 segundos por defecto, 6 escenas con timeline y transiciones.
- Sin imagenes externas: todo se genera con matematicas y primitivas OpenCV.
- 6+ curvas parametricas con cv2.polylines.
- Transformaciones afines visibles: traslacion, rotacion, escala, shear y espejo.
- Composicion por capas, mascaras, addWeighted.
- PostFX: bloom, vignette, scanlines, posterize, aberracion cromatica y glitch.
- Exporta MP4 y capturas de cada escena.
"""

from __future__ import annotations

import argparse
import math
import os
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Tuple

import cv2
import numpy as np


# =========================
# Configuracion general
# =========================
W, H = 800, 600
FPS = 30
DURATION = 30.0
SCENE_COUNT = 6
SCENE_LEN = DURATION / SCENE_COUNT
TRANSITION = 1.15

BGR = Tuple[int, int, int]


# =========================
# Utilidades matematicas
# =========================
def clamp01(x: float) -> float:
    return 0.0 if x < 0.0 else (1.0 if x > 1.0 else x)


def smoothstep(a: float, b: float, x: float) -> float:
    if abs(b - a) < 1e-8:
        return 1.0 if x >= b else 0.0
    y = clamp01((x - a) / (b - a))
    return y * y * (3.0 - 2.0 * y)


def ease_out_cubic(x: float) -> float:
    x = clamp01(x)
    return 1.0 - (1.0 - x) ** 3


def ease_in_out_sine(x: float) -> float:
    x = clamp01(x)
    return 0.5 - 0.5 * math.cos(math.pi * x)


def hsv_to_bgr(h: float, s: float = 230, v: float = 240) -> BGR:
    """Convierte HSV estilo OpenCV a BGR."""
    hsv = np.uint8([[[int(h) % 180, int(np.clip(s, 0, 255)), int(np.clip(v, 0, 255))]]])
    return tuple(int(x) for x in cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)[0, 0])


def rotate_point_cloud(points: np.ndarray, angle: float) -> np.ndarray:
    c, s = math.cos(angle), math.sin(angle)
    R = np.array([[c, -s], [s, c]], dtype=np.float32)
    return points @ R.T


def as_polyline(x: np.ndarray, y: np.ndarray, cx: float, cy: float, sx: float, sy: float) -> np.ndarray:
    pts = np.stack([cx + sx * x, cy + sy * y], axis=1)
    return np.round(pts).astype(np.int32).reshape((-1, 1, 2))


def poly_param(
    fx: Callable[[np.ndarray], np.ndarray],
    fy: Callable[[np.ndarray], np.ndarray],
    t0: float,
    t1: float,
    n: int,
    cx: float,
    cy: float,
    sx: float,
    sy: float,
) -> np.ndarray:
    ts = np.linspace(t0, t1, n, dtype=np.float32)
    return as_polyline(fx(ts), fy(ts), cx, cy, sx, sy)


def affine_transform_points(pts: np.ndarray, M: np.ndarray) -> np.ndarray:
    p = pts.reshape(-1, 2).astype(np.float32)
    p_h = np.hstack([p, np.ones((p.shape[0], 1), dtype=np.float32)])
    out = p_h @ M.T
    return np.round(out).astype(np.int32).reshape((-1, 1, 2))


# =========================
# Buffers y datos globales
# =========================
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
NX = (XX - W * 0.5) / (W * 0.5)
NY = (YY - H * 0.5) / (H * 0.5)
RADIUS = np.sqrt(NX * NX + NY * NY)
ANGLE = np.arctan2(NY, NX)

# Fondo en baja resolucion: se genera proceduralmente y se escala a 800x600.
# Esto mantiene el resultado final a la resolucion requerida y hace viable exportar el MP4.
BGW, BGH = 200, 150
BYY, BXX = np.mgrid[0:BGH, 0:BGW].astype(np.float32)
BNX = (BXX - BGW * 0.5) / (BGW * 0.5)
BNY = (BYY - BGH * 0.5) / (BGH * 0.5)
BRADIUS = np.sqrt(BNX * BNX + BNY * BNY)
BANGLE = np.arctan2(BNY, BNX)

VIGNETTE_MASK = np.clip(1.0 - 0.72 * (NX * NX + NY * NY), 0.0, 1.0).astype(np.float32)
SCANLINE_MASK = (1.0 - 0.10 * (0.5 + 0.5 * np.sin(2.0 * np.pi * np.arange(H, dtype=np.float32) / 3.0))).reshape(H, 1, 1)

RNG_STARS = np.random.default_rng(2026)
STAR_X = RNG_STARS.integers(0, W, 620)
STAR_Y = RNG_STARS.integers(0, H, 620)
STAR_Z = RNG_STARS.random(620).astype(np.float32)
STAR_H = RNG_STARS.integers(120, 180, 620)

PARTICLE_RNG = np.random.default_rng(808)
PART_X0 = PARTICLE_RNG.random(1800).astype(np.float32) * W
PART_Y0 = PARTICLE_RNG.random(1800).astype(np.float32) * H
PART_PHASE = PARTICLE_RNG.random(1800).astype(np.float32) * 2 * np.pi


# =========================
# Fondos, primitivas y texto
# =========================
def clear(img: np.ndarray, color: BGR = (0, 0, 0)) -> None:
    img[:] = color


def background_nebula(img: np.ndarray, t: float, hue0: float, hue1: float, energy: float = 1.0) -> None:
    """Fondo procedural en HSV, calculado en baja resolucion y escalado a 800x600."""
    ys = np.linspace(0.0, 1.0, BGH, dtype=np.float32)[:, None]
    xs = np.linspace(0.0, 1.0, BGW, dtype=np.float32)[None, :]

    wave = (
        0.50 * np.sin(6.0 * xs + 1.4 * t)
        + 0.35 * np.cos(5.0 * ys - 0.9 * t)
        + 0.30 * np.sin(4.0 * (xs + ys) + 0.7 * t)
        + 0.22 * np.cos(10.0 * BRADIUS - 1.8 * t)
    )
    hue = hue0 + (hue1 - hue0) * ys + 15.0 * wave
    sat = 165 + 45 * np.clip(energy, 0.0, 1.5)
    val = 32 + 95 * (1.0 - ys) + 34 * wave + 35 * np.exp(-2.8 * BRADIUS)

    hsv_small = np.zeros((BGH, BGW, 3), dtype=np.uint8)
    hsv_small[:, :, 0] = np.mod(hue, 180).astype(np.uint8)
    hsv_small[:, :, 1] = np.clip(sat + 18 * np.sin(BANGLE * 3 + t), 0, 255).astype(np.uint8)
    hsv_small[:, :, 2] = np.clip(val, 0, 255).astype(np.uint8)
    bgr_small = cv2.cvtColor(hsv_small, cv2.COLOR_HSV2BGR)
    img[:] = cv2.resize(bgr_small, (W, H), interpolation=cv2.INTER_CUBIC)

def draw_starfield(img: np.ndarray, t: float, intensity: float = 1.0) -> None:
    drift_x = (STAR_X + (t * (16 + 40 * STAR_Z)).astype(int) if hasattr(t, "astype") else STAR_X + (t * (16 + 40 * STAR_Z)).astype(np.int32)) % W
    drift_y = (STAR_Y + (6 * np.sin(t * 0.8 + STAR_Z * 8)).astype(np.int32)) % H
    brightness = np.clip(110 + 145 * (0.5 + 0.5 * np.sin(t * 2.3 + STAR_Z * 13.0)), 0, 255)
    for size in (1, 2):
        idx = STAR_Z > (0.72 if size == 2 else 0.0)
        xs = drift_x[idx].astype(np.int32)
        ys = drift_y[idx].astype(np.int32)
        vals = (brightness[idx] * intensity).astype(np.uint8)
        color = np.stack([vals, vals, vals], axis=1)
        img[ys, xs] = np.maximum(img[ys, xs], color)
        if size == 2:
            xs2 = np.clip(xs + 1, 0, W - 1)
            img[ys, xs2] = np.maximum(img[ys, xs2], color)


def draw_centered_text(
    img: np.ndarray,
    text: str,
    y: int,
    scale: float,
    color: BGR,
    thickness: int = 2,
    alpha: float = 1.0,
    font: int = cv2.FONT_HERSHEY_SIMPLEX,
) -> None:
    alpha = clamp01(alpha)
    if alpha <= 0:
        return
    (tw, th), baseline = cv2.getTextSize(text, font, scale, thickness)
    x = int((W - tw) * 0.5)
    if alpha >= 0.999:
        cv2.putText(img, text, (x, y), font, scale, color, thickness, cv2.LINE_AA)
        return
    layer = np.zeros_like(img)
    cv2.putText(layer, text, (x, y), font, scale, color, thickness, cv2.LINE_AA)
    cv2.addWeighted(layer, alpha, img, 1.0, 0, dst=img)


def draw_horizon_grid(img: np.ndarray, t: float, hue: float = 110) -> None:
    """Grid estilo pista sintetica, hecho con lineas."""
    overlay = np.zeros_like(img)
    vanish = np.array([W * 0.5 + 40 * math.sin(t * 0.5), H * 0.54], dtype=np.float32)
    base_y = int(H * 0.83)
    color = hsv_to_bgr(hue, 190, 180)

    # Lineas hacia punto de fuga
    for x in np.linspace(-W * 0.2, W * 1.2, 22):
        p1 = (int(x), H)
        p2 = (int(vanish[0] + (x - W * 0.5) * 0.04), int(vanish[1]))
        cv2.line(overlay, p1, p2, color, 1, cv2.LINE_AA)

    # Lineas horizontales con espaciado no lineal
    for i in range(28):
        f = i / 27.0
        y = int(vanish[1] + (base_y - vanish[1]) * (f * f))
        alpha = 0.2 + 0.8 * f
        cv2.line(overlay, (0, y), (W, y), tuple(int(c * alpha) for c in color), 1, cv2.LINE_AA)

    cv2.addWeighted(overlay, 0.52, img, 1.0, 0, dst=img)


def draw_glow_polyline(
    img: np.ndarray,
    pts: np.ndarray,
    color: BGR,
    thickness: int = 2,
    glow: int = 12,
    closed: bool = False,
    alpha: float = 1.0,
) -> None:
    """Linea con halo rapido: trazo ancho + trazo nitido. El bloom global remata el brillo."""
    alpha = clamp01(alpha)
    if alpha <= 0:
        return
    glow_color = tuple(int(c * 0.38 * alpha) for c in color)
    crisp_color = tuple(int(c * alpha) for c in color)
    cv2.polylines(img, [pts], closed, glow_color, max(thickness + 2, int(glow * 0.45)), cv2.LINE_AA)
    cv2.polylines(img, [pts], closed, crisp_color, thickness, cv2.LINE_AA)

def draw_orbital_primitives(img: np.ndarray, t: float, center: Tuple[int, int], hue: float) -> None:
    cx, cy = center
    for i, r in enumerate([55, 86, 125, 172, 228]):
        a = t * (0.25 + i * 0.05) + i
        color = hsv_to_bgr(hue + i * 9, 160, 120 + i * 20)
        cv2.ellipse(img, (cx, cy), (r, int(r * (0.34 + 0.05 * math.sin(t + i)))), math.degrees(a), 0, 360, color, 1, cv2.LINE_AA)
        px = int(cx + r * math.cos(a) * 0.95)
        py = int(cy + r * math.sin(a) * 0.34)
        cv2.circle(img, (px, py), 3 + i % 2, hsv_to_bgr(hue + 70 + i * 7, 180, 250), -1, cv2.LINE_AA)


def regular_star(n: int = 5, r1: float = 70, r2: float = 30) -> np.ndarray:
    pts = []
    for i in range(n * 2):
        r = r1 if i % 2 == 0 else r2
        a = -math.pi / 2 + i * math.pi / n
        pts.append([r * math.cos(a), r * math.sin(a)])
    return np.array(pts, dtype=np.float32).reshape((-1, 1, 2))


# =========================
# Curvas parametricas
# =========================
def curve_lissajous(t: float, cx: float, cy: float, sx: float, sy: float, n: int = 720) -> np.ndarray:
    a = 3.0 + 0.22 * math.sin(t * 0.7)
    b = 4.0 + 0.22 * math.cos(t * 0.5)
    delta = math.pi / 2 + 0.85 * math.sin(t * 0.35)
    return poly_param(lambda u: np.sin(a * u + delta), lambda u: np.sin(b * u), 0, 2 * math.pi, n, cx, cy, sx, sy)


def curve_rose(t: float, cx: float, cy: float, sx: float, sy: float, k: int = 7, n: int = 820) -> np.ndarray:
    phase = 0.28 * t
    return poly_param(
        lambda th: np.cos(k * th + 0.4 * np.sin(t * 0.3)) * np.cos(th + phase),
        lambda th: np.cos(k * th + 0.4 * np.sin(t * 0.3)) * np.sin(th + phase),
        0,
        2 * math.pi,
        n,
        cx,
        cy,
        sx,
        sy,
    )


def curve_archimedean_spiral(t: float, cx: float, cy: float, sx: float, sy: float, n: int = 760) -> np.ndarray:
    return poly_param(
        lambda th: (0.030 * th) * np.cos(th + 0.45 * t),
        lambda th: (0.030 * th) * np.sin(th + 0.45 * t),
        0,
        12.5 * math.pi,
        n,
        cx,
        cy,
        sx,
        sy,
    )


def curve_hypotrochoid(t: float, cx: float, cy: float, sx: float, sy: float, n: int = 720) -> np.ndarray:
    R, r, d = 8.0, 3.0, 5.0
    w = (R - r) / r
    mod = 0.38 * math.sin(t * 0.55)
    return poly_param(
        lambda u: ((R - r) * np.cos(u) + d * np.cos(w * u + mod)) / 10.0,
        lambda u: ((R - r) * np.sin(u) - d * np.sin(w * u + mod)) / 10.0,
        0,
        14 * math.pi,
        n,
        cx,
        cy,
        sx,
        sy,
    )


def curve_lemniscate(t: float, cx: float, cy: float, sx: float, sy: float, n: int = 700) -> np.ndarray:
    phase = 0.5 * t
    return poly_param(
        lambda u: (np.sqrt(2.0) * np.cos(u + phase)) / (np.sin(u + phase) ** 2 + 1.0),
        lambda u: (np.sqrt(2.0) * np.cos(u + phase) * np.sin(u + phase)) / (np.sin(u + phase) ** 2 + 1.0),
        0,
        2 * math.pi,
        n,
        cx,
        cy,
        sx,
        sy,
    )


def curve_butterfly(t: float, cx: float, cy: float, sx: float, sy: float, n: int = 720) -> np.ndarray:
    # Curva mariposa clasica: e^sin(u)-2cos(4u)+sin^5((2u-pi)/24)
    return poly_param(
        lambda u: np.sin(u + 0.08 * t)
        * (np.exp(np.cos(u)) - 2 * np.cos(4 * u) - np.sin((u / 12.0) - 0.25 * t) ** 5)
        / 3.4,
        lambda u: np.cos(u + 0.08 * t)
        * (np.exp(np.cos(u)) - 2 * np.cos(4 * u) - np.sin((u / 12.0) - 0.25 * t) ** 5)
        / 3.4,
        0,
        12 * math.pi,
        n,
        cx,
        cy,
        sx,
        sy,
    )


def curve_epicycloid(t: float, cx: float, cy: float, sx: float, sy: float, n: int = 760) -> np.ndarray:
    R, r = 4.0, 1.0
    phase = 0.35 * t
    return poly_param(
        lambda u: ((R + r) * np.cos(u + phase) - r * np.cos(((R + r) / r) * u + phase)) / 6.0,
        lambda u: ((R + r) * np.sin(u + phase) - r * np.sin(((R + r) / r) * u + phase)) / 6.0,
        0,
        2 * math.pi,
        n,
        cx,
        cy,
        sx,
        sy,
    )


# =========================
# PostFX
# =========================
def post_vignette(img: np.ndarray, strength: float = 1.0) -> np.ndarray:
    mask = (1.0 - strength) + strength * VIGNETTE_MASK
    return np.clip(img.astype(np.float32) * mask[..., None], 0, 255).astype(np.uint8)


def post_scanlines(img: np.ndarray, strength: float = 0.16) -> np.ndarray:
    s = 1.0 - strength + strength * SCANLINE_MASK
    return np.clip(img.astype(np.float32) * s, 0, 255).astype(np.uint8)


def post_posterize(img: np.ndarray, q: int = 18) -> np.ndarray:
    q = max(2, int(q))
    return ((img // q) * q).astype(np.uint8)


def post_bloom(img: np.ndarray, amount: float = 0.34, sigma: float = 3.3, threshold: int = 120) -> np.ndarray:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    bright = cv2.bitwise_and(img, img, mask=mask)
    small = cv2.resize(bright, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    blur = cv2.GaussianBlur(small, (0, 0), max(0.8, sigma * 0.35))
    blur = cv2.resize(blur, (W, H), interpolation=cv2.INTER_LINEAR)
    return cv2.addWeighted(img, 1.0, blur, amount, 0)

def post_chromatic_aberration(img: np.ndarray, amount: float = 1.5) -> np.ndarray:
    shift = int(round(amount))
    if shift <= 0:
        return img
    out = img.copy()
    out[:, :, 0] = np.roll(img[:, :, 0], -shift, axis=1)
    out[:, :, 2] = np.roll(img[:, :, 2], shift, axis=1)
    return out

def post_global(img: np.ndarray, t: float) -> np.ndarray:
    out = post_bloom(img, 0.30 + 0.08 * math.sin(t * 0.7), 3.0, 116)
    out = post_chromatic_aberration(out, 1.0 + 0.7 * (0.5 + 0.5 * math.sin(t * 0.35)))
    out = post_vignette(out, 1.0)
    out = post_scanlines(out, 0.13)
    return out


def transition_glitch(a: np.ndarray, b: np.ndarray, progress: float, t: float) -> np.ndarray:
    p = smoothstep(0.0, 1.0, progress)
    mixed = cv2.addWeighted(a, 1.0 - p, b, p, 0)

    # Barras horizontales procedurales para que la transicion se note.
    out = mixed.copy()
    rng = np.random.default_rng(int(760 + 60 * t))
    intensity = math.sin(math.pi * p)
    bands = int(7 + 10 * intensity)
    for _ in range(bands):
        y = int(rng.integers(0, H - 4))
        h = int(rng.integers(2, 14))
        dx = int(rng.integers(-30, 31) * intensity)
        out[y : min(H, y + h)] = np.roll(out[y : min(H, y + h)], dx, axis=1)

    flash = smoothstep(0.78, 1.0, p)
    if flash > 0:
        out = cv2.addWeighted(out, 1.0, np.full_like(out, 255), 0.12 * flash, 0)

    return out


# =========================
# Escenas
# =========================
@dataclass
class RenderState:
    heat: np.ndarray
    scratch_a: np.ndarray
    scratch_b: np.ndarray


def scene_intro(img: np.ndarray, t: float, local: float, state: RenderState) -> None:
    p = clamp01(local / SCENE_LEN)
    background_nebula(img, t, 158, 92, 0.75)
    draw_starfield(img, t, intensity=1.0)
    draw_horizon_grid(img, t, 128)
    draw_orbital_primitives(img, t, (W // 2, int(H * 0.45)), 155)

    # Poligono central como prisma/observatorio
    prism = np.array(
        [
            [W * 0.50, H * 0.25],
            [W * 0.62, H * 0.48],
            [W * 0.55, H * 0.64],
            [W * 0.45, H * 0.64],
            [W * 0.38, H * 0.48],
        ],
        dtype=np.int32,
    ).reshape((-1, 1, 2))
    layer = np.zeros_like(img)
    cv2.fillPoly(layer, [prism], hsv_to_bgr(152, 120, 80), cv2.LINE_AA)
    cv2.polylines(layer, [prism], True, hsv_to_bgr(170, 180, 255), 2, cv2.LINE_AA)
    cv2.addWeighted(layer, 0.54, img, 1.0, 0, dst=img)

    a = smoothstep(0.05, 0.40, p)
    draw_centered_text(img, "DEMO PROCEDURAL", 270, 1.22, (245, 245, 245), 2, a)
    draw_centered_text(img, "OpenCV + NumPy + Matematicas", 318, 0.75, (210, 245, 255), 2, a)
    draw_centered_text(img, "6 escenas / curvas / transformaciones / postFX", 360, 0.55, (185, 215, 230), 1, smoothstep(0.26, 0.58, p))


def scene_lissajous(img: np.ndarray, t: float, local: float, state: RenderState) -> None:
    p = clamp01(local / SCENE_LEN)
    background_nebula(img, t, 8, 62, 1.0)
    draw_horizon_grid(img, t, 28)

    # Sol geometrico con primitivas ellipse/circle.
    sun_layer = np.zeros_like(img)
    for r, alpha, h in [(180, 0.16, 24), (124, 0.22, 31), (72, 0.38, 40)]:
        cv2.circle(sun_layer, (W // 2, int(H * 0.48)), r, hsv_to_bgr(h, 180, 250), -1, cv2.LINE_AA)
        cv2.addWeighted(sun_layer, alpha, img, 1.0, 0, dst=img)
        sun_layer[:] = 0

    # Varias Lissajous, misma familia con diferente fase.
    for i in range(5):
        pts = curve_lissajous(t + i * 0.45, W * 0.50, H * 0.46, 250 - i * 24, 175 - i * 12, 720)
        angle = (t * 6.0 + i * 18.0) % 360
        M = cv2.getRotationMatrix2D((W * 0.5, H * 0.46), angle * 0.06, 1.0 + 0.04 * math.sin(t + i))
        pts = affine_transform_points(pts, M)
        draw_glow_polyline(img, pts, hsv_to_bgr(22 + i * 14 + 8 * math.sin(t), 220, 245), 2, 10 - i, False, 0.92)

    # Nodos animados con circle.
    ring_n = 20
    for i in range(ring_n):
        a = 2 * math.pi * i / ring_n + t * 0.75
        r = 230 + 16 * math.sin(t * 1.2 + i)
        x = int(W * 0.5 + r * math.cos(a))
        y = int(H * 0.46 + 0.65 * r * math.sin(a))
        cv2.circle(img, (x, y), 3, hsv_to_bgr(55 + i * 3, 200, 230), -1, cv2.LINE_AA)

    draw_centered_text(img, "LISSAJOUS CATHEDRAL", 66, 0.72, (245, 245, 235), 2, smoothstep(0.04, 0.22, p))


def scene_rose_mandala(img: np.ndarray, t: float, local: float, state: RenderState) -> None:
    p = clamp01(local / SCENE_LEN)
    background_nebula(img, t, 104, 164, 1.1)
    cx, cy = int(W * 0.5), int(H * 0.49)

    # Mascara radial + composicion.
    mask = np.clip(255 * (1.0 - RADIUS), 0, 255).astype(np.uint8)
    ring_layer = np.zeros_like(img)
    for i in range(12):
        r = 38 + i * 21
        cv2.ellipse(ring_layer, (cx, cy), (r, int(r * 0.72)), t * 5 + i * 11, 0, 360, hsv_to_bgr(128 + i * 4, 150, 170), 1, cv2.LINE_AA)
    ring_layer = cv2.bitwise_and(ring_layer, ring_layer, mask=mask)
    cv2.addWeighted(ring_layer, 0.55, img, 1.0, 0, dst=img)

    for i, k in enumerate([5, 7, 9]):
        pts = curve_rose(t * (1.0 + i * 0.06), cx, cy, 230 - 45 * i, 230 - 45 * i, k=k, n=860)
        draw_glow_polyline(img, pts, hsv_to_bgr(128 + 17 * i + 8 * math.sin(t), 230, 245), 2, 13 - i * 2, True, 0.98)

    # Espiral encima, otra curva distinta.
    spiral = curve_archimedean_spiral(t, cx, cy, 720, 720, 720)
    draw_glow_polyline(img, spiral, hsv_to_bgr(165 + 8 * math.sin(t * 0.5), 170, 235), 2, 8, False, 0.74)

    # Petalos rellenos con fillPoly.
    petal_layer = np.zeros_like(img)
    for i in range(10):
        a = i * 2 * math.pi / 10 + t * 0.22
        tip = (cx + int(145 * math.cos(a)), cy + int(145 * math.sin(a)))
        left = (cx + int(65 * math.cos(a - 0.18)), cy + int(65 * math.sin(a - 0.18)))
        right = (cx + int(65 * math.cos(a + 0.18)), cy + int(65 * math.sin(a + 0.18)))
        tri = np.array([left, tip, right], dtype=np.int32).reshape((-1, 1, 2))
        cv2.fillPoly(petal_layer, [tri], hsv_to_bgr(142 + i * 2, 160, 135), cv2.LINE_AA)
    cv2.addWeighted(petal_layer, 0.22, img, 1.0, 0, dst=img)

    draw_centered_text(img, "ROSA POLAR + ESPIRAL", 66, 0.70, (235, 255, 252), 2, smoothstep(0.02, 0.18, p))


def scene_transform_lab(img: np.ndarray, t: float, local: float, state: RenderState) -> None:
    p = clamp01(local / SCENE_LEN)
    background_nebula(img, t, 40, 122, 0.9)
    draw_horizon_grid(img, t, 82)

    base = regular_star(6, 58, 26)
    center_positions = [(160, 310), (320, 300), (480, 300), (640, 310)]
    labels = ["rotacion+escala", "shear", "espejo", "warpAffine"]
    colors = [hsv_to_bgr(42, 220, 250), hsv_to_bgr(78, 220, 245), hsv_to_bgr(116, 220, 245), hsv_to_bgr(150, 220, 245)]

    for i, (cx, cy) in enumerate(center_positions):
        pts = base.copy()
        pts[:, 0, 0] += cx
        pts[:, 0, 1] += cy

        if i == 0:
            scale = 0.75 + 0.38 * (0.5 + 0.5 * math.sin(t * 1.1))
            M = cv2.getRotationMatrix2D((cx, cy), math.degrees(t * 0.85), scale)
            out = affine_transform_points(pts, M)
        elif i == 1:
            sh = 0.55 * math.sin(t * 1.15)
            M = np.float32([[1, sh, -sh * cy], [0, 1, 0]])
            out = affine_transform_points(pts, M)
        elif i == 2:
            mirror = -1 if math.sin(t * 1.5) > 0 else 1
            M = np.float32([[mirror, 0, cx * (1 - mirror)], [0, 1.0 + 0.12 * math.sin(t), 0]])
            out = affine_transform_points(pts, M)
        else:
            # Figura en una capa, luego warpAffine real: rotacion, escala y traslacion.
            state.scratch_a[:] = 0
            local_pts = base.copy()
            local_pts[:, 0, 0] += cx
            local_pts[:, 0, 1] += cy
            cv2.fillPoly(state.scratch_a, [local_pts.astype(np.int32)], colors[i], cv2.LINE_AA)
            cv2.polylines(state.scratch_a, [local_pts.astype(np.int32)], True, (255, 255, 255), 2, cv2.LINE_AA)
            M = cv2.getRotationMatrix2D((cx, cy), 26 * math.sin(t * 1.2), 0.9 + 0.22 * math.cos(t))
            M[0, 2] += 18 * math.sin(t * 0.9)
            M[1, 2] += 13 * math.cos(t * 0.7)
            warped = cv2.warpAffine(state.scratch_a, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_TRANSPARENT)
            cv2.addWeighted(warped, 0.95, img, 1.0, 0, dst=img)
            out = local_pts.astype(np.int32)

        if i != 3:
            fill_col = tuple(int(c * 0.42) for c in colors[i])
            cv2.fillPoly(img, [out], fill_col, cv2.LINE_AA)
            cv2.polylines(img, [out], True, colors[i], 2, cv2.LINE_AA)
            cv2.polylines(img, [out], True, (255, 255, 255), 1, cv2.LINE_AA)

        cv2.putText(img, labels[i], (cx - 72, cy + 106), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (220, 240, 230), 1, cv2.LINE_AA)
        cv2.line(img, (cx - 70, cy + 82), (cx + 70, cy + 82), colors[i], 1, cv2.LINE_AA)

    # Curva hipotrocoide al fondo, para mantener el lenguaje visual.
    pts = curve_hypotrochoid(t, W * 0.50, H * 0.33, 220, 150, 820)
    draw_glow_polyline(img, pts, hsv_to_bgr(86, 180, 210), 1, 8, False, 0.48)
    draw_centered_text(img, "LABORATORIO DE TRANSFORMACIONES AFINES", 64, 0.62, (240, 245, 230), 2, smoothstep(0.04, 0.20, p))


def scene_vector_field(img: np.ndarray, t: float, local: float, state: RenderState) -> None:
    p = clamp01(local / SCENE_LEN)
    background_nebula(img, t, 170, 110, 1.0)

    # Particulas de campo vectorial deterministas.
    xs = (PART_X0 + 96 * np.sin(PART_Y0 / 58.0 + t * 1.65) + 34 * np.cos(PART_PHASE + t * 0.8)) % W
    ys = (PART_Y0 + 86 * np.cos(PART_X0 / 72.0 + t * 1.15) + 26 * np.sin(PART_PHASE * 1.7 + t)) % H

    # Dibujo de trazos en subconjunto para simular direccion/velocidad.
    field_layer = np.zeros_like(img)
    idx_lines = np.arange(0, len(xs), 7)
    x2 = (xs[idx_lines] + 14 * np.sin(ys[idx_lines] / 38.0 + t)).astype(np.int32)
    y2 = (ys[idx_lines] + 14 * np.cos(xs[idx_lines] / 41.0 - t)).astype(np.int32)
    x1 = xs[idx_lines].astype(np.int32)
    y1 = ys[idx_lines].astype(np.int32)
    for j in range(len(idx_lines)):
        h = 118 + int(35 * math.sin(t + j * 0.03))
        cv2.line(field_layer, (x1[j], y1[j]), (int(x2[j] % W), int(y2[j] % H)), hsv_to_bgr(h, 170, 170), 1, cv2.LINE_AA)

    # Puntos brillantes con indexacion directa.
    valid_x = xs.astype(np.int32)
    valid_y = ys.astype(np.int32)
    field_layer[valid_y, valid_x] = np.maximum(field_layer[valid_y, valid_x], np.array(hsv_to_bgr(132, 210, 240), dtype=np.uint8))
    field_layer = cv2.GaussianBlur(field_layer, (0, 0), 0.8)
    cv2.addWeighted(field_layer, 0.92, img, 1.0, 0, dst=img)

    # Lemniscata y mariposa: curvas protagonistas.
    lem = curve_lemniscate(t, W * 0.50, H * 0.49, 190, 135, 760)
    but = curve_butterfly(t * 0.9, W * 0.50, H * 0.49, 116, 116, 1450)
    draw_glow_polyline(img, lem, hsv_to_bgr(150 + 12 * math.sin(t), 210, 250), 2, 13, False, 0.95)
    draw_glow_polyline(img, but, hsv_to_bgr(174 + 8 * math.cos(t), 190, 230), 1, 9, False, 0.74)

    # Barras de energia con primitivas rectangulares.
    for i in range(28):
        x = 36 + i * 26
        h = int(18 + 40 * (0.5 + 0.5 * math.sin(t * 2.0 + i * 0.65)))
        cv2.rectangle(img, (x, H - 44), (x + 10, H - 44 - h), hsv_to_bgr(120 + i * 2, 180, 220), -1)
    draw_centered_text(img, "CAMPO DE PARTICULAS + LEMNISCATA", 64, 0.62, (230, 255, 245), 2, smoothstep(0.03, 0.18, p))


def scene_final_synthesis(img: np.ndarray, t: float, local: float, state: RenderState) -> None:
    p = clamp01(local / SCENE_LEN)

    # Fondo de calor procedural, inspirado en fuego pero mas abstracto.
    heat = state.heat
    heat *= 0.90
    base = (np.sin(XX * 0.028 + t * 3.0) + np.cos(YY * 0.021 - t * 2.2) + np.sin((XX + YY) * 0.014 + t)) * 0.33
    injection = np.clip(0.45 + base + np.exp(-((YY - H * 0.84) ** 2) / (2 * 48 ** 2)), 0.0, 1.0)
    heat[:] = np.maximum(heat, injection.astype(np.float32) * (0.58 + 0.42 * math.sin(t * 1.2) ** 2))
    heat[:] = cv2.GaussianBlur(heat, (0, 0), 2.4)
    heat[:-3, :] = heat[3:, :]
    heat[-3:, :] *= 0.0

    h = (18 - 18 * np.clip(heat, 0, 1) + 25 * RADIUS).astype(np.uint8) % 180
    s = np.clip(190 + 50 * heat, 0, 255).astype(np.uint8)
    v = np.clip(42 + 190 * heat + 55 * np.exp(-2.4 * RADIUS), 0, 255).astype(np.uint8)
    img[:] = cv2.cvtColor(np.dstack([h, s, v]).astype(np.uint8), cv2.COLOR_HSV2BGR)

    # Mascara hexagonal central.
    hex_pts = []
    for i in range(6):
        a = math.pi / 6 + i * math.pi / 3 + 0.11 * math.sin(t)
        hex_pts.append([W * 0.5 + 260 * math.cos(a), H * 0.48 + 210 * math.sin(a)])
    hex_pts = np.array(hex_pts, dtype=np.int32).reshape((-1, 1, 2))
    mask = np.zeros((H, W), dtype=np.uint8)
    cv2.fillPoly(mask, [hex_pts], 255, cv2.LINE_AA)

    curve_layer = np.zeros_like(img)
    curves = [
        (curve_lissajous(t, W * 0.50, H * 0.48, 220, 160, 720), 25),
        (curve_rose(t, W * 0.50, H * 0.48, 210, 210, k=8, n=1200), 52),
        (curve_archimedean_spiral(t, W * 0.50, H * 0.48, 700, 700, 720), 80),
        (curve_hypotrochoid(t, W * 0.50, H * 0.48, 230, 230, 850), 108),
        (curve_lemniscate(t, W * 0.50, H * 0.48, 190, 130, 700), 138),
        (curve_epicycloid(t, W * 0.50, H * 0.48, 240, 240, 760), 166),
    ]

    for i, (pts, hue) in enumerate(curves):
        M = cv2.getRotationMatrix2D((W * 0.5, H * 0.48), math.degrees(t * 0.08) + i * 7, 1.0 + 0.03 * math.sin(t + i))
        pts = affine_transform_points(pts, M)
        draw_glow_polyline(curve_layer, pts, hsv_to_bgr(hue + 10 * math.sin(t + i), 220, 245), 1 + (i % 2), 10, False, 0.90)

    curve_layer = cv2.bitwise_and(curve_layer, curve_layer, mask=mask)
    cv2.addWeighted(curve_layer, 1.0, img, 1.0, 0, dst=img)
    cv2.polylines(img, [hex_pts], True, hsv_to_bgr(30 + 30 * math.sin(t), 160, 245), 2, cv2.LINE_AA)

    # Rayos y cierre.
    for i in range(36):
        a = i * 2 * math.pi / 36 + t * 0.18
        r0 = 72 + 16 * math.sin(t * 1.7 + i)
        r1 = 270 + 28 * math.cos(t * 0.9 + i)
        x0 = int(W * 0.5 + r0 * math.cos(a))
        y0 = int(H * 0.48 + r0 * math.sin(a))
        x1 = int(W * 0.5 + r1 * math.cos(a))
        y1 = int(H * 0.48 + r1 * math.sin(a))
        cv2.line(img, (x0, y0), (x1, y1), hsv_to_bgr(22 + i * 2, 180, 210), 1, cv2.LINE_AA)

    fade_title = smoothstep(0.20, 0.50, p) * (1.0 - smoothstep(0.78, 1.0, p))
    draw_centered_text(img, "SINTESIS FINAL", 80, 0.92, (255, 245, 230), 2, fade_title)
    draw_centered_text(img, "sin assets externos: solo ecuaciones, primitivas y tiempo", H - 45, 0.52, (235, 230, 220), 1, fade_title)


SCENES = [
    ("01_intro_observatorio", scene_intro),
    ("02_lissajous_cathedral", scene_lissajous),
    ("03_rose_spiral_mandala", scene_rose_mandala),
    ("04_transform_lab", scene_transform_lab),
    ("05_vector_field", scene_vector_field),
    ("06_final_synthesis", scene_final_synthesis),
]


# =========================
# Timeline y render
# =========================
def make_state() -> RenderState:
    return RenderState(
        heat=np.zeros((H, W), dtype=np.float32),
        scratch_a=np.zeros((H, W, 3), dtype=np.uint8),
        scratch_b=np.zeros((H, W, 3), dtype=np.uint8),
    )


def render_scene(scene_id: int, frame: np.ndarray, t: float, state: RenderState) -> None:
    scene_id = int(np.clip(scene_id, 0, SCENE_COUNT - 1))
    local = t - scene_id * SCENE_LEN
    SCENES[scene_id][1](frame, t, local, state)


def render_timeline(t: float, state: RenderState, buf_a: np.ndarray, buf_b: np.ndarray) -> np.ndarray:
    block = int(min(SCENE_COUNT - 1, max(0, t // SCENE_LEN)))
    local = t - block * SCENE_LEN
    render_scene(block, buf_a, t, state)
    frame = buf_a

    # Transicion en el ultimo tramo de cada escena.
    start = SCENE_LEN - TRANSITION
    if block < SCENE_COUNT - 1 and local >= start:
        # Copiar el estado para evitar que la escena final "heat" se contamine dos veces.
        render_scene(block, buf_a, t, state)
        render_scene(block + 1, buf_b, t, state)
        progress = (local - start) / TRANSITION
        frame = transition_glitch(buf_a, buf_b, progress, t)

    # Fade global.
    fade_in = smoothstep(0.0, 1.2, t)
    fade_out = 1.0 - smoothstep(DURATION - 1.8, DURATION, t)
    f = fade_in * fade_out
    if f < 0.999:
        frame = np.clip(frame.astype(np.float32) * f, 0, 255).astype(np.uint8)

    return post_global(frame, t)


def save_postfx_masks(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    vignette = np.clip(VIGNETTE_MASK * 255, 0, 255).astype(np.uint8)
    cv2.imwrite(str(out_dir / "mask_01_vignette.png"), vignette)

    radial = np.clip((1.0 - RADIUS) * 255, 0, 255).astype(np.uint8)
    cv2.imwrite(str(out_dir / "mask_02_radial_composite.png"), radial)

    hex_mask = np.zeros((H, W), dtype=np.uint8)
    hex_pts = []
    for i in range(6):
        a = math.pi / 6 + i * math.pi / 3
        hex_pts.append([W * 0.5 + 260 * math.cos(a), H * 0.48 + 210 * math.sin(a)])
    cv2.fillPoly(hex_mask, [np.array(hex_pts, dtype=np.int32).reshape((-1, 1, 2))], 255, cv2.LINE_AA)
    cv2.imwrite(str(out_dir / "mask_03_hexagonal_final.png"), hex_mask)

    scan = np.clip(SCANLINE_MASK.reshape(H, 1) * 255, 0, 255).astype(np.uint8)
    scan = np.repeat(scan, W, axis=1)
    cv2.imwrite(str(out_dir / "mask_04_scanlines.png"), scan)


def export_screenshots(out_dir: Path) -> List[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    state = make_state()
    buf_a = np.zeros((H, W, 3), dtype=np.uint8)
    buf_b = np.zeros((H, W, 3), dtype=np.uint8)
    saved: List[Path] = []

    # Tiempos centrados en cada escena.
    for i, (name, _) in enumerate(SCENES):
        t = i * SCENE_LEN + SCENE_LEN * 0.50
        frame = render_timeline(t, state, buf_a, buf_b)
        path = out_dir / f"{name}.png"
        cv2.imwrite(str(path), frame)
        saved.append(path)

    save_postfx_masks(out_dir)
    return saved


def export_video(out_path: Path, fps: int = FPS, duration: float = DURATION, render_fps: int = 2) -> None:
    """Exporta MP4 a 30 FPS.

    Si FFmpeg esta disponible, se mandan frames BGR crudos por stdin. Es mucho mas rapido que
    VideoWriter para clips largos. Si no existe FFmpeg, se usa fallback con cv2.VideoWriter.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    state = make_state()
    buf_a = np.zeros((H, W, 3), dtype=np.uint8)
    buf_b = np.zeros((H, W, 3), dtype=np.uint8)
    render_fps = max(1, min(int(render_fps), int(fps)))
    total_unique = int(duration * render_fps)

    if shutil.which("ffmpeg"):
        cmd = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-nostats",
            "-y",
            "-f",
            "rawvideo",
            "-vcodec",
            "rawvideo",
            "-pix_fmt",
            "bgr24",
            "-s",
            f"{W}x{H}",
            "-r",
            str(render_fps),
            "-i",
            "-",
            "-vf",
            f"fps={fps}",
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            str(out_path),
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        assert proc.stdin is not None
        for i in range(total_unique):
            t = i / render_fps
            frame = render_timeline(t, state, buf_a, buf_b)
            proc.stdin.write(frame.tobytes())
            if i % max(1, render_fps * 3) == 0:
                print(f"[export] frame unico {i:04d}/{total_unique}")
        proc.stdin.close()
        code = proc.wait()
        if code != 0:
            raise RuntimeError(f"FFmpeg termino con codigo {code}")
        return

    # Fallback puro OpenCV.
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(out_path), fourcc, fps, (W, H))
    if not writer.isOpened():
        raise RuntimeError(f"No se pudo abrir VideoWriter para {out_path}")

    total_out = int(duration * fps)
    duplicate = max(1, int(round(fps / render_fps)))
    last_frame = None
    for i in range(total_out):
        if i % duplicate == 0 or last_frame is None:
            t = i / fps
            last_frame = render_timeline(t, state, buf_a, buf_b)
        writer.write(last_frame)
        if i % max(1, fps * 3) == 0:
            print(f"[export] frame {i:04d}/{total_out}")
    writer.release()


def export_frames(out_dir: Path, fps: int = FPS, duration: float = DURATION) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    state = make_state()
    buf_a = np.zeros((H, W, 3), dtype=np.uint8)
    buf_b = np.zeros((H, W, 3), dtype=np.uint8)
    total = int(duration * fps)
    for i in range(total):
        t = i / fps
        frame = render_timeline(t, state, buf_a, buf_b)
        cv2.imwrite(str(out_dir / f"frame_{i:05d}.png"), frame)
        if i % max(1, fps * 3) == 0:
            print(f"[frames] frame {i:04d}/{total}")


def preview() -> None:
    state = make_state()
    buf_a = np.zeros((H, W, 3), dtype=np.uint8)
    buf_b = np.zeros((H, W, 3), dtype=np.uint8)
    t0 = time.perf_counter()
    i = 0
    while True:
        t = (time.perf_counter() - t0) % DURATION
        frame = render_timeline(t, state, buf_a, buf_b)
        cv2.imshow("Demo Procedural Magistral - ESC para salir", frame)
        key = cv2.waitKey(max(1, int(760 / FPS))) & 0xFF
        if key == 27:
            break
        i += 1
    cv2.destroyAllWindows()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Demo procedural con OpenCV: 6 escenas, curvas, transformaciones y postFX.")
    parser.add_argument("--preview", action="store_true", help="Muestra el demo en ventana OpenCV.")
    parser.add_argument("--export-video", action="store_true", help="Exporta renders/final_demo.mp4.")
    parser.add_argument("--screenshots", action="store_true", help="Guarda una captura por escena y mascaras.")
    parser.add_argument("--frames", action="store_true", help="Exporta secuencia PNG completa en renders/frames/.")
    parser.add_argument("--out", default="renders/final_demo.mp4", help="Ruta del video de salida.")
    parser.add_argument("--fps", type=int, default=FPS, help="FPS de exportacion.")
    parser.add_argument("--duration", type=float, default=DURATION, help="Duracion de exportacion en segundos.")
    parser.add_argument("--render-fps", type=int, default=2, help="FPS internos de render; el MP4 se guarda a --fps.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Si no se indica nada, se genera el entregable base.
    if not (args.preview or args.export_video or args.screenshots or args.frames):
        args.export_video = True
        args.screenshots = True

    if args.screenshots:
        saved = export_screenshots(Path("renders"))
        print("[ok] capturas:")
        for p in saved:
            print("  -", p)

    if args.export_video:
        export_video(Path(args.out), fps=args.fps, duration=args.duration, render_fps=args.render_fps)
        print("[ok] video:", args.out)

    if args.frames:
        export_frames(Path("renders") / "frames", fps=args.fps, duration=args.duration)
        print("[ok] frames en renders/frames")

    if args.preview:
        preview()


if __name__ == "__main__":
    main()
