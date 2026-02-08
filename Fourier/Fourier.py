from manim import *
import numpy as np

class FourierSquare(Scene):
    def square_series(self, t, N):
        """
        f(t) = sum_{k=1..N} (4/pi) * (1/(2k-1)) * sin(2*pi*(2k-1)*t)
        Devuelve un arreglo y(t) para t arreglo.
        """
        y = np.zeros_like(t, dtype=float)
        for k in range(1, N + 1):
            n = 2 * k - 1
            y += (4 / np.pi) * (1 / n) * np.sin(2 * np.pi * n * t)
        return y

    def construct(self):
        maxN = 100

        # Ejes
        axes = Axes(
            x_range=[0, 2, 0.5],
            y_range=[-1.5, 1.5, 0.5],
            x_length=10,
            y_length=4,
            tips=False
        ).to_edge(DOWN)

        x_label = axes.get_x_axis_label(Tex("t"), edge=RIGHT, direction=RIGHT)
        y_label = axes.get_y_axis_label(Tex("f(t)"), edge=UP, direction=UP)

        self.add(axes, x_label, y_label)

        # Dominio para dibujar (una rejilla fina)
        t_vals = np.linspace(0, 2, 2000)

        # Onda cuadrada ideal (blanca): sign(sin(2*pi*t))
        ideal_y = np.sign(np.sin(2 * np.pi * t_vals))
        # Para evitar el 0 exacto en discontinuidades:
        ideal_y[ideal_y == 0] = 1

        ideal_graph = axes.plot_line_graph(
            x_values=t_vals,
            y_values=ideal_y,
            line_color=WHITE,
            add_vertex_dots=False,
        )

        self.add(ideal_graph)

        # Precomputar todas las sumas parciales para que vaya fluido (1..100)
        partials = [None]  # índice 0 no se usa
        for N in range(1, maxN + 1):
            partials.append(self.square_series(t_vals, N))

        # Tracker para N
        n_tracker = ValueTracker(1)

        # Curva aproximada (roja), siempre se redibuja con el N actual
        approx_graph = always_redraw(lambda: axes.plot_line_graph(
            x_values=t_vals,
            y_values=partials[int(n_tracker.get_value())],
            line_color=RED,
            add_vertex_dots=False,
        ))

        self.add(approx_graph)

        # Texto de la fórmula (arriba), actualizando N
        formula = MathTex(
            r"f(t)=\sum_{k=1}^{N}\frac{4}{\pi}\frac{1}{2k-1}\sin\left(2\pi(2k-1)t\right)"
        ).to_edge(UP)

        n_text = always_redraw(lambda: Tex(
            f"N = {int(n_tracker.get_value())}",
            font_size=36
        ).next_to(formula, DOWN))

        self.add(formula, n_text)

        # Animación de N: 1 -> 100
        self.play(n_tracker.animate.set_value(100), run_time=12, rate_func=linear)
        self.wait(1)
