from manim import *
import numpy as np

class FourierSquare(Scene):
    def square_series(self, t, N):
        """Suma parcial de la serie de Fourier de una onda cuadrada."""
        y = np.zeros_like(t, dtype=float)
        for k in range(1, N + 1):
            n = 2 * k - 1
            y += (4 / np.pi) * (1 / n) * np.sin(2 * np.pi * n * t)
        return y

    def construct(self):
        maxN = 100

        # --------- ESCENA / ESTILO ----------
        self.camera.background_color = "#0b0f14"  

        # --------- EJES ----------
        axes = Axes(
            x_range=[0, 2, 0.5],
            y_range=[-1.5, 1.5, 0.5],
            x_length=10,
            y_length=4,
            tips=False,
        ).to_edge(DOWN)

        x_label = axes.get_x_axis_label(Tex("t"), edge=RIGHT, direction=RIGHT)
        y_label = axes.get_y_axis_label(Tex("f(t)"), edge=UP, direction=UP)

        
        self.play(Create(axes), FadeIn(x_label), FadeIn(y_label), run_time=1.6)

        # --------- DOMINIO ----------
        t_vals = np.linspace(0, 2, 2500)  

        # --------- ONDA CUADRADA IDEAL ----------
        ideal_y = np.sign(np.sin(2 * np.pi * t_vals))
        ideal_y[ideal_y == 0] = 1

        ideal_graph = axes.plot_line_graph(
            x_values=t_vals,
            y_values=ideal_y,
            add_vertex_dots=False,
        ).set_stroke(width=4).set_color(WHITE)

      
        self.play(Create(ideal_graph), run_time=2.2)
        self.wait(0.4)

        # --------- FORMULA (sale después) ----------
        formula = MathTex(
            r"f(t)=\sum_{k=1}^{N}\frac{4}{\pi}\frac{1}{2k-1}\sin\left(2\pi(2k-1)t\right)"
        ).scale(0.9).to_edge(UP)

        self.play(Write(formula), run_time=1.4)
        self.wait(0.3)

        # --------- TEXTO: N ----------
        n_tracker = ValueTracker(1)

        n_text = always_redraw(
            lambda: Tex(
                f"N = {int(n_tracker.get_value())}",
                font_size=36
            ).next_to(formula, DOWN)
        )
        self.play(FadeIn(n_text), run_time=0.6)

        # --------- “PRIMER SENO” (k=1) ----------
        # Mostramos explícitamente el primer término antes de empezar a sumar todo
        first_term = MathTex(
            r"\frac{4}{\pi}\sin(2\pi t)"
        ).scale(0.9).next_to(formula, DOWN, buff=0.6)

        self.play(Transform(n_text, first_term), run_time=1.0)
        self.wait(0.3)

        # Curva aproximada: se recalcula según N actual (fluido)
        approx_graph = always_redraw(lambda: axes.plot_line_graph(
            x_values=t_vals,
            y_values=self.square_series(t_vals, int(n_tracker.get_value())),
            add_vertex_dots=False,
        ).set_stroke(width=3).set_color(RED))

        # Primero dibuja la aproximación con N=1 (primer seno)
        self.add(approx_graph)
        self.wait(0.2)

        # Regresamos el texto a N=...
        self.play(Transform(n_text, Tex(f"N = {int(n_tracker.get_value())}", font_size=36).next_to(formula, DOWN)),
                  run_time=0.6)
        self.wait(0.2)

        # --------- ANIMACIÓN PRINCIPAL: N 1 → 100 ----------
        # Un poco más lenta y elegante para ver la formación
        self.play(
            n_tracker.animate.set_value(maxN),
            run_time=16,
            rate_func=linear
        )

        self.wait(1.2)

