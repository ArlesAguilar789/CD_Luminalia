import tkinter as tk
from tkinter import ttk

class SimuladorDMA(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulador Visual DMA")
        self.geometry("800x500")
        self.configure(bg="#2b2b2b")
        self.resizable(False, False)

        self.animating = False
        self.data_count = 5
        self.current_data = 0
        self.packet = None

        self._setup_ui()
        self._draw_architecture()

    def _setup_ui(self):
        control_frame = tk.Frame(self, bg="#3c3f41", pady=10)
        control_frame.pack(fill=tk.X, side=tk.TOP)

        tk.Label(control_frame, text="Modo DMA:", bg="#3c3f41", fg="white", font=("Arial", 12)).pack(side=tk.LEFT, padx=10)
        
        self.combo_mode = ttk.Combobox(control_frame, values=["Ráfaga", "Robo de Ciclo", "Transparente"], state="readonly", font=("Arial", 11))
        self.combo_mode.current(0)
        self.combo_mode.pack(side=tk.LEFT, padx=10)

        self.btn_run = tk.Button(control_frame, text="Ejecutar Simulación", bg="#4CAF50", fg="white", font=("Arial", 11, "bold"), relief=tk.FLAT, command=self._start_simulation)
        self.btn_run.pack(side=tk.LEFT, padx=20)

        self.lbl_status = tk.Label(control_frame, text="Estado: Listo", bg="#3c3f41", fg="#ffeb3b", font=("Arial", 12, "bold"))
        self.lbl_status.pack(side=tk.RIGHT, padx=20)

        self.canvas = tk.Canvas(self, bg="#1e1e1e", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def _draw_architecture(self):
        self.canvas.create_rectangle(50, 100, 200, 250, fill="#2196F3", outline="", tags="cpu_box")
        self.canvas.create_text(125, 175, text="CPU", fill="white", font=("Arial", 16, "bold"))
        self.cpu_status = self.canvas.create_text(125, 210, text="Activa", fill="white", font=("Arial", 10))

        self.canvas.create_rectangle(325, 100, 475, 250, fill="#FF9800", outline="", tags="dma_box")
        self.canvas.create_text(400, 175, text="DMAC", fill="white", font=("Arial", 16, "bold"))

        self.canvas.create_rectangle(600, 100, 750, 250, fill="#4CAF50", outline="", tags="ram_box")
        self.canvas.create_text(675, 175, text="MEMORIA", fill="white", font=("Arial", 16, "bold"))

        self.canvas.create_line(125, 250, 125, 350, fill="gray", width=4)
        self.canvas.create_line(400, 250, 400, 350, fill="gray", width=4)
        self.canvas.create_line(675, 250, 675, 350, fill="gray", width=4)
        self.canvas.create_line(50, 350, 750, 350, fill="gray", width=8)
        self.canvas.create_text(400, 370, text="BUS DEL SISTEMA (Datos, Direcciones, Control)", fill="gray", font=("Arial", 12, "bold"))

    def _update_cpu_state(self, state, color, status_text):
        self.canvas.itemconfig("cpu_box", fill=color)
        self.canvas.itemconfig(self.cpu_status, text=status_text)

    def _start_simulation(self):
        if self.animating:
            return
        
        self.animating = True
        self.btn_run.config(state=tk.DISABLED)
        self.current_data = 0
        self.combo_mode.config(state=tk.DISABLED)
        
        mode = self.combo_mode.get()
        self.lbl_status.config(text=f"Ejecutando: {mode}")

        if mode == "Ráfaga":
            self._seq_burst_start()
        elif mode == "Robo de Ciclo":
            self._seq_cycle_start()
        elif mode == "Transparente":
            self._seq_transparent_start()

    def _create_packet(self):
        if self.packet:
            self.canvas.delete(self.packet)
        self.packet = self.canvas.create_rectangle(385, 220, 415, 250, fill="#E91E63", outline="white", width=2)

    def _animate_packet(self, path, step=0, callback=None):
        if step < len(path):
            dx, dy = path[step]
            self.canvas.move(self.packet, dx, dy)
            self.after(20, self._animate_packet, path, step + 1, callback)
        else:
            self.canvas.delete(self.packet)
            if callback:
                callback()

    def _get_dma_to_ram_path(self):
        path = []
        path.extend([(0, 5)] * 20)  
        path.extend([(5, 0)] * 55)  
        path.extend([(0, -5)] * 20) 
        return path

    def _finish_simulation(self):
        self._update_cpu_state("active", "#2196F3", "Activa")
        self.lbl_status.config(text="Estado: Finalizado")
        self.animating = False
        self.btn_run.config(state=tk.NORMAL)
        self.combo_mode.config(state="readonly")

    def _seq_burst_start(self):
        self._update_cpu_state("halt", "#F44336", "Bloqueada (HALT)")
        self.after(500, self._burst_transfer)

    def _burst_transfer(self):
        if self.current_data < self.data_count:
            self._create_packet()
            self._animate_packet(self._get_dma_to_ram_path(), callback=self._burst_next)
        else:
            self.after(500, self._finish_simulation)

    def _burst_next(self):
        self.current_data += 1
        self.after(100, self._burst_transfer)

    def _seq_cycle_start(self):
        self._cycle_transfer()

    def _cycle_transfer(self):
        if self.current_data < self.data_count:
            self._update_cpu_state("halt", "#F44336", "Pausada (1 ciclo)")
            self.after(300, self._cycle_animate)
        else:
            self._finish_simulation()

    def _cycle_animate(self):
        self._create_packet()
        self._animate_packet(self._get_dma_to_ram_path(), callback=self._cycle_restore)

    def _cycle_restore(self):
        self.current_data += 1
        self._update_cpu_state("active", "#2196F3", "Ejecutando")
        self.after(600, self._cycle_transfer)

    def _seq_transparent_start(self):
        self._transparent_transfer()

    def _transparent_transfer(self):
        if self.current_data < self.data_count:
            self._update_cpu_state("alu", "#9C27B0", "ALU Interna")
            self.after(400, self._transparent_animate)
        else:
            self._finish_simulation()

    def _transparent_animate(self):
        self._create_packet()
        self._animate_packet(self._get_dma_to_ram_path(), callback=self._transparent_restore)

    def _transparent_restore(self):
        self.current_data += 1
        self._update_cpu_state("active", "#2196F3", "Uso de Bus")
        self.after(800, self._transparent_transfer)

if __name__ == "__main__":
    app = SimuladorDMA()
    app.mainloop()