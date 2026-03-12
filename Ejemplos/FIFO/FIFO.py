import sys
import random
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFormLayout, QLineEdit, QSpinBox, QPushButton, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QGraphicsView,
    QGraphicsScene, QGraphicsPixmapItem, QGraphicsTextItem, QGraphicsItem,
    QGraphicsObject, QLabel, QSplitter, QGroupBox, QFrame, QMessageBox,
    QTabWidget, QGraphicsRectItem, QGraphicsEllipseItem
)
from PyQt5.QtCore import (
    Qt, QTimer, QPropertyAnimation, QPointF, QEasingCurve, pyqtProperty, 
    QSequentialAnimationGroup, QRectF
)
from PyQt5.QtGui import (
    QPixmap, QColor, QBrush, QPen, QFont, QImage, QIcon, QPainter, QRegion
)

# ==========================================
# CONFIGURACIÓN DEL MOTOR Y SISTEMA (OS)
# ==========================================
SIMULATION_TICK_MS = 1000  
SCENE_WIDTH = 1056  
SCENE_HEIGHT = 664  

# Coordenadas EXACTAS mapeadas a la imagen
DOOR_POS = QPointF(350, 660)      # Alfombra roja inferior
SAFE_Y_AISLE = 470                # Pasillo horizontal seguro que no atraviesa mesas
EXIT_POS = QPointF(350, 660)      # Salida por la alfombra roja

# Coordenadas de los 7 bloques de asientos azules/amarillos
WAITING_CHAIRS = [
    QPointF(60, 310), QPointF(60, 380), QPointF(60, 450),       # 3 Sillones Izquierda
    QPointF(1000, 290), QPointF(1000, 360), QPointF(1000, 430), QPointF(1000, 500) # 4 Sillones Derecha
]

# ==========================================
# MULTIPROCESAMIENTO: ESTACIONES Y COLAS
# ==========================================
MENU_ITEMS = [
    "Curar Pokémon (Enfermera Joy)", 
    "Usar la PC", 
    "Intercambio (Multijugador)"
]

# Ubicaciones de las CPUs (A dónde pasan al ser su turno)
STATIONS = {
    "Curar Pokémon (Enfermera Joy)": QPointF(330, 240), # Mostrador de Joy
    "Usar la PC": QPointF(820, 160),                    # Computadora arriba a la derecha
    "Intercambio (Multijugador)": QPointF(720, 540)     # Mostrador abajo a la derecha
}

# Dónde empiezan a hacer la fila (Ready Queue)
QUEUE_STARTS = {
    "Curar Pokémon (Enfermera Joy)": QPointF(330, 330), # Sobre la Pokeball gigante
    "Usar la PC": QPointF(820, 250),                    # Debajo de la PC
    "Intercambio (Multijugador)": QPointF(630, 540)     # A la izquierda del mostrador
}

# Dirección en la que crece la fila
QUEUE_OFFSETS = {
    "Curar Pokémon (Enfermera Joy)": QPointF(0, 60),  # Hacia abajo
    "Usar la PC": QPointF(0, 60),                     # Hacia abajo
    "Intercambio (Multijugador)": QPointF(-60, 0)     # Hacia la izquierda
}

# Diseño UI
UI_BG = "#F8F9FA"
UI_PANEL = "#FFFFFF"
UI_TEXT = "#212529"
UI_ACCENT = "#E74C3C" 
UI_SUCCESS = "#2ECC71"
UI_WARNING = "#F39C12"
UI_BORDER = "#DEE2E6"

# ==========================================
# MOTOR DE SPRITES (ALTURA ESTANDARIZADA)
# ==========================================
class SpriteManager:
    def __init__(self, folder_path):
        self.sprites = []
        self.load_from_folder(folder_path)

    def load_from_folder(self, folder_path):
        if not os.path.exists(folder_path):
            return

        for filename in os.listdir(folder_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                if "centropokemon" in filename.lower(): continue

                filepath = os.path.join(folder_path, filename)
                image = QImage(filepath)
                if image.isNull(): continue

                # 1. Quitar fondo sólido si existe
                bg_color = QColor(image.pixelColor(0, 0))
                if bg_color.alpha() == 255:
                    mask = image.createMaskFromColor(bg_color.rgb(), Qt.MaskOutColor)
                    image.setAlphaChannel(mask)
                
                # 2. Recorte inteligente y Escalado por Altura (75px)
                pixmap = QPixmap.fromImage(image)
                mascara = pixmap.createHeuristicMask()
                bounding_rect = QRegion(mascara).boundingRect()
                
                if not bounding_rect.isEmpty():
                    pixmap = pixmap.copy(bounding_rect)
                
                # IMPORTANTE: scaledToHeight asegura que todos midan exactamente lo mismo de alto
                scaled = pixmap.scaledToHeight(75, Qt.SmoothTransformation)
                self.sprites.append(scaled)

    def get_random_trainer(self):
        if not self.sprites:
            dummy = QPixmap(75, 75)
            dummy.fill(QColor("#3498DB"))
            return dummy
        return random.choice(self.sprites)

# ==========================================
# ESTRUCTURA DE DATOS (PROCESO)
# ==========================================
class TrainerProcess:
    def __init__(self, name, service, arrival, burst, sprite):
        self.name = name
        self.service = service
        self.arrival_time = arrival
        self.burst_time = burst
        self.remaining_burst = burst
        self.sprite = sprite
        
        self.completion_time = None
        self.turnaround_time = None
        self.waiting_time = None
        
        self.graphic = None
        self.chair_idx = -1 

# ==========================================
# ENTIDAD GRÁFICA (EL PERSONAJE)
# ==========================================
class CharacterEntity(QGraphicsObject):
    def __init__(self, process):
        super().__init__()
        self.process = process
        
        # Ancla en los pies (Y-Sorting)
        self.sprite = QGraphicsPixmapItem(self.process.sprite, self)
        self.sprite.setOffset(-self.process.sprite.width()/2, -self.process.sprite.height())
        self.sprite.setTransformOriginPoint(0, -self.process.sprite.height()/2)
        
        # Sombra
        self.shadow = QGraphicsEllipseItem(-25, -8, 50, 16, self)
        self.shadow.setBrush(QBrush(QColor(0, 0, 0, 90)))
        self.shadow.setPen(QPen(Qt.NoPen))
        self.shadow.setZValue(-1)
        
        # Etiqueta
        self.tag = QGraphicsTextItem(f"{process.name}\n(Espera)", self)
        self.tag.setDefaultTextColor(QColor("#FFFFFF"))
        self.tag.setFont(QFont("Segoe UI", 8, QFont.Bold))
        
        self.tag_bg = QGraphicsRectItem(self.tag.boundingRect(), self.tag)
        self.tag_bg.setBrush(QBrush(QColor(0, 0, 0, 160)))
        self.tag_bg.setPen(QPen(Qt.NoPen))
        self.tag_bg.setZValue(-1)
        self.tag.setPos(-self.tag.boundingRect().width() / 2, 5)

        self.walk_timer = QTimer()
        self.walk_timer.setInterval(150)
        self.walk_timer.timeout.connect(self.wobble)
        self.angle = 8

    def start_walk(self):
        self.walk_timer.start()

    def stop_walk(self):
        self.walk_timer.stop()
        self.sprite.setRotation(0)

    def wobble(self):
        self.sprite.setRotation(self.angle)
        self.angle *= -1

    def update_status_text(self, status):
        if status == "serving":
            text = f"{self.process.name}\n({self.process.remaining_burst}m)"
        elif status == "waiting":
            text = f"{self.process.name}\n(Fila)"
        elif status == "done":
            text = f"{self.process.name}\n(Listo)"
        else:
            text = f"{self.process.name}\n(Espera)"
            
        self.tag.setPlainText(text)
        self.tag_bg.setRect(self.tag.boundingRect())
        self.tag.setPos(-self.tag.boundingRect().width() / 2, 5)

    def boundingRect(self):
        return QRectF(-50, -100, 100, 140) 

    def paint(self, painter, option, widget):
        pass

    @pyqtProperty(QPointF)
    def pos_prop(self):
        return self.scenePos()

    @pos_prop.setter
    def pos_prop(self, point):
        self.setPos(point)
        self.setZValue(point.y()) 


# ==========================================
# INTERFAZ PRINCIPAL Y LÓGICA DEL SO
# ==========================================
class PokemonCenterOS(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistemas Operativos: Multicola con Pathfinding Perfecto")
        self.resize(1550, 900)
        self.setStyleSheet(f"background-color: {UI_BG};")
        
        ruta_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_sprites = os.path.join(ruta_actual, "Sprites")
        if not os.path.exists(ruta_sprites):
            ruta_sprites = os.path.join(ruta_actual, "sprites")
            
        self.sprite_mgr = SpriteManager(ruta_sprites)
        
        self.all_processes = []
        self.sitting_queue = []   
        self.overflow_queue = []  
        self.occupied_chairs = [False] * len(WAITING_CHAIRS)
        
        self.ready_queues = {service: [] for service in MENU_ITEMS}
        self.current_processes = {service: None for service in MENU_ITEMS}
        
        self.clock = 0
        self.animations = [] 
        
        self.build_ui()
        
        self.timer = QTimer()
        self.timer.setInterval(SIMULATION_TICK_MS)
        self.timer.timeout.connect(self.core_tick)

    def build_ui(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        left_panel = QFrame()
        left_panel.setStyleSheet(f"background-color: {UI_PANEL}; border-radius: 10px; border: 1px solid {UI_BORDER};")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(25, 25, 25, 25)
        
        title = QLabel("Terminal Pokémon\n[Planificador Central]")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet(f"color: {UI_ACCENT}; border: none;")
        left_layout.addWidget(title)
        
        form_layout = QFormLayout()
        style_input = f"padding: 10px; border: 1px solid {UI_BORDER}; border-radius: 6px; background: {UI_BG}; font-size: 13px;"
        
        self.inp_name = QLineEdit()
        self.inp_name.setStyleSheet(style_input)
        self.inp_order = QComboBox()
        self.inp_order.addItems(MENU_ITEMS)
        self.inp_order.setStyleSheet(style_input)
        self.inp_arr = QSpinBox()
        self.inp_arr.setRange(0, 999)
        self.inp_arr.setStyleSheet(style_input)
        self.inp_burst = QSpinBox()
        self.inp_burst.setRange(1, 99)
        self.inp_burst.setValue(4)
        self.inp_burst.setStyleSheet(style_input)

        form_layout.addRow(QLabel("Entrenador:"), self.inp_name)
        form_layout.addRow(QLabel("Actividad:"), self.inp_order)
        form_layout.addRow(QLabel("Min Llegada:"), self.inp_arr)
        form_layout.addRow(QLabel("Ráfaga (Burst):"), self.inp_burst)
        
        btn_add = QPushButton("Registrar Entrenador")
        btn_add.setStyleSheet(f"background-color: {UI_ACCENT}; color: white; padding: 12px; border-radius: 6px; font-weight: bold;")
        btn_add.clicked.connect(self.register_client)
        
        self.btn_play = QPushButton("▶ Iniciar Simulación")
        self.btn_play.setStyleSheet(f"background-color: {UI_SUCCESS}; color: white; padding: 12px; border-radius: 6px; font-weight: bold; margin-top: 15px;")
        self.btn_play.clicked.connect(self.start_engine)
        
        btn_reset = QPushButton("↻ Reiniciar Terminal")
        btn_reset.setStyleSheet(f"background-color: {UI_WARNING}; color: white; padding: 12px; border-radius: 6px; font-weight: bold;")
        btn_reset.clicked.connect(self.reset_engine)

        left_layout.addLayout(form_layout)
        left_layout.addWidget(btn_add)
        left_layout.addWidget(self.btn_play)
        left_layout.addWidget(btn_reset)
        left_layout.addStretch()
        
        self.lbl_clock = QLabel("Reloj OS: 00:00")
        self.lbl_clock.setFont(QFont("Consolas", 18, QFont.Bold))
        self.lbl_clock.setStyleSheet(f"color: {UI_TEXT}; border: none;")
        left_layout.addWidget(self.lbl_clock, alignment=Qt.AlignCenter)

        right_panel = QSplitter(Qt.Vertical)
        right_panel.setStyleSheet("QSplitter::handle { background: transparent; }")
        
        self.scene = QGraphicsScene(0, 0, SCENE_WIDTH, SCENE_HEIGHT)
        ruta_actual = os.path.dirname(os.path.abspath(__file__))
        rutas_fondo = [
            os.path.join(ruta_actual, "CENTROPOKEMON.png"),
            os.path.join(ruta_actual, "Sprites", "CENTROPOKEMON.png"),
            os.path.join(ruta_actual, "sprites", "CENTROPOKEMON.png")
        ]

        bg_pixmap = None
        for ruta in rutas_fondo:
            if os.path.exists(ruta):
                bg_pixmap = QPixmap(ruta)
                break

        if bg_pixmap:
            bg_scaled = bg_pixmap.scaled(SCENE_WIDTH, SCENE_HEIGHT, Qt.IgnoreAspectRatio, Qt.FastTransformation)
            self.scene.addPixmap(bg_scaled)
        
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        self.view.setStyleSheet(f"border: 2px solid {UI_BORDER}; border-radius: 10px; background: black;")
        
        self.report_tabs = QTabWidget()
        self.report_tabs.setStyleSheet(f"""
            QTabWidget::pane {{ border: 1px solid {UI_BORDER}; border-radius: 6px; background: {UI_PANEL}; }}
            QTabBar::tab {{ background: {UI_BG}; color: {UI_TEXT}; padding: 10px; border: 1px solid {UI_BORDER}; border-top-left-radius: 6px; border-top-right-radius: 6px; }}
            QTabBar::tab:selected {{ background: {UI_PANEL}; font-weight: bold; color: {UI_ACCENT}; border-bottom-color: {UI_PANEL}; }}
        """)
        
        self.tables = {} 
        for srv in MENU_ITEMS:
            tb = QTableWidget(0, 7)
            self.setup_table(tb)
            self.tables[srv] = tb
            self.report_tabs.addTab(tb, srv)
            
        right_panel.addWidget(self.view)
        right_panel.addWidget(self.report_tabs)
        right_panel.setSizes([650, 250])
        
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 4)
        self.setCentralWidget(main_widget)

    def setup_table(self, table):
        table.setHorizontalHeaderLabels(["Entrenador", "Actividad", "Llegada", "Ráfaga", "Finalización", "TAT (Retorno)", "WT (Espera)"])
        table.setStyleSheet(f"""
            QTableWidget {{ background-color: {UI_PANEL}; gridline-color: {UI_BORDER}; color: {UI_TEXT}; font-size: 13px; border: none; }}
            QHeaderView::section {{ background-color: {UI_BG}; font-weight: bold; padding: 8px; border: none; border-bottom: 2px solid {UI_BORDER}; }}
        """)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def register_client(self):
        name = self.inp_name.text().strip()
        if not name: return
        
        arr = self.inp_arr.value()
        burst = self.inp_burst.value()
        service = self.inp_order.currentText()
        sprite = self.sprite_mgr.get_random_trainer()
        
        proc = TrainerProcess(name, service, arr, burst, sprite)
        self.all_processes.append(proc)
        self.sitting_queue.append(proc)
        
        proc.graphic = CharacterEntity(proc)
        proc.graphic.setPos(DOOR_POS)
        self.scene.addItem(proc.graphic)
        
        # Buscar un asiento exacto. Si están llenos, hacen fila en el centro.
        chair_idx = -1
        for i, occupied in enumerate(self.occupied_chairs):
            if not occupied:
                chair_idx = i
                self.occupied_chairs[i] = True
                break
                
        if chair_idx != -1:
            proc.chair_idx = chair_idx
            target_seat = WAITING_CHAIRS[chair_idx]
        else:
            self.overflow_queue.append(proc)
            target_seat = QPointF(200 + (len(self.overflow_queue) * 50), 580)
            
        self.route_character(proc.graphic, DOOR_POS, target_seat)
        
        tb = self.tables[service]
        row = tb.rowCount()
        tb.insertRow(row)
        for i, val in enumerate([name, service, arr, burst, "-", "-", "-"]):
            item = QTableWidgetItem(str(val))
            item.setTextAlignment(Qt.AlignCenter)
            tb.setItem(row, i, item)
            
        self.inp_name.clear()
        self.inp_arr.setValue(arr + 1)

    def route_character(self, char_item, start, end):
        """Enrutamiento Inteligente: Evalúa si necesita usar el pasillo seguro para no atravesar obstáculos"""
        group = QSequentialAnimationGroup(self)
        
        # Si la distancia en X es grande y están por encima del pasillo, usan el corredor seguro
        if abs(start.x() - end.x()) > 50 and (start.y() < SAFE_Y_AISLE or end.y() < SAFE_Y_AISLE):
            
            if abs(SAFE_Y_AISLE - start.y()) > 2:
                anim1 = QPropertyAnimation(char_item, b"pos_prop")
                anim1.setEndValue(QPointF(start.x(), SAFE_Y_AISLE))
                anim1.setDuration(max(200, int(abs(SAFE_Y_AISLE - start.y()) * 3)))
                group.addAnimation(anim1)
                
            if abs(end.x() - start.x()) > 2:
                anim2 = QPropertyAnimation(char_item, b"pos_prop")
                anim2.setEndValue(QPointF(end.x(), SAFE_Y_AISLE))
                anim2.setDuration(max(200, int(abs(end.x() - start.x()) * 3)))
                group.addAnimation(anim2)

            if abs(end.y() - SAFE_Y_AISLE) > 2:
                anim3 = QPropertyAnimation(char_item, b"pos_prop")
                anim3.setEndValue(end)
                anim3.setDuration(max(200, int(abs(end.y() - SAFE_Y_AISLE) * 3)))
                group.addAnimation(anim3)
        else:
            # Si es una distancia corta o en el mismo eje, caminan en forma de "L"
            mid_point = QPointF(start.x(), end.y())
            if abs(start.y() - end.y()) > 2:
                anim1 = QPropertyAnimation(char_item, b"pos_prop")
                anim1.setEndValue(mid_point)
                anim1.setDuration(int(abs(start.y() - end.y()) * 4))
                group.addAnimation(anim1)
                
            if abs(start.x() - end.x()) > 2:
                anim2 = QPropertyAnimation(char_item, b"pos_prop")
                anim2.setEndValue(end)
                anim2.setDuration(int(abs(start.x() - end.x()) * 4))
                group.addAnimation(anim2)

        char_item.start_walk()
        group.finished.connect(char_item.stop_walk)
        group.start()
        self.animations.append(group)

    def start_engine(self):
        if not self.all_processes: return
        self.all_processes.sort(key=lambda x: x.arrival_time)
        self.btn_play.setEnabled(False)
        self.timer.start()

    def reset_engine(self):
        self.timer.stop()
        self.btn_play.setEnabled(True)
        for p in self.all_processes:
            if p.graphic in self.scene.items(): self.scene.removeItem(p.graphic)
        
        self.all_processes.clear()
        self.sitting_queue.clear()
        self.overflow_queue.clear()
        self.occupied_chairs = [False] * len(WAITING_CHAIRS)
        self.ready_queues = {service: [] for service in MENU_ITEMS}
        self.current_processes = {service: None for service in MENU_ITEMS}
        self.clock = 0
        
        for tb in self.tables.values(): tb.setRowCount(0)
        self.lbl_clock.setText("Reloj OS: 00:00")

    def core_tick(self):
        self.clock += 1
        self.lbl_clock.setText(f"Reloj OS: {self.clock:02d}:00")
        
        # 1. RAM -> Ready Queue
        for p in list(self.sitting_queue):
            if p.arrival_time == self.clock:
                self.sitting_queue.remove(p)
                if p in self.overflow_queue: self.overflow_queue.remove(p)
                self.ready_queues[p.service].append(p)
                
                if p.chair_idx != -1:
                    self.occupied_chairs[p.chair_idx] = False
                
                p.graphic.update_status_text("waiting")
                
                queue_index = len(self.ready_queues[p.service]) - 1
                offset_x = QUEUE_OFFSETS[p.service].x() * queue_index
                offset_y = QUEUE_OFFSETS[p.service].y() * queue_index
                
                target = QUEUE_STARTS[p.service] + QPointF(offset_x, offset_y)
                self.route_character(p.graphic, p.graphic.pos_prop, target)

        # 2. Reacomodar filas
        for srv in MENU_ITEMS:
            for i, p in enumerate(self.ready_queues[srv]):
                offset_x = QUEUE_OFFSETS[srv].x() * i
                offset_y = QUEUE_OFFSETS[srv].y() * i
                target = QUEUE_STARTS[srv] + QPointF(offset_x, offset_y)
                if (p.graphic.pos_prop - target).manhattanLength() > 5:
                    self.route_character(p.graphic, p.graphic.pos_prop, target)

        # 3. Asignar CPUs
        for srv in MENU_ITEMS:
            if not self.current_processes[srv] and self.ready_queues[srv]:
                self.current_processes[srv] = self.ready_queues[srv].pop(0)
                target_station = STATIONS[srv]
                self.route_character(self.current_processes[srv].graphic, self.current_processes[srv].graphic.pos_prop, target_station)
                self.current_processes[srv].graphic.update_status_text("serving")

        # 4. Procesar Ráfagas
        for srv in MENU_ITEMS:
            p = self.current_processes[srv]
            if p:
                p.remaining_burst -= 1
                p.graphic.update_status_text("serving")
                
                if p.remaining_burst <= 0:
                    p.completion_time = self.clock
                    p.turnaround_time = p.completion_time - p.arrival_time
                    p.waiting_time = p.turnaround_time - p.burst_time
                    p.graphic.update_status_text("done")
                    
                    tb = self.tables[srv]
                    for r in range(tb.rowCount()):
                        if tb.item(r, 0).text() == p.name:
                            tb.setItem(r, 4, QTableWidgetItem(str(p.completion_time)))
                            tb.setItem(r, 5, QTableWidgetItem(str(p.turnaround_time)))
                            tb.setItem(r, 6, QTableWidgetItem(str(p.waiting_time)))
                            for c in range(4, 7): tb.item(r, c).setTextAlignment(Qt.AlignCenter)
                    
                    self.route_character(p.graphic, p.graphic.pos_prop, EXIT_POS)
                    self.current_processes[srv] = None

        # 5. Condición de Finalización
        all_done = all(p.completion_time is not None for p in self.all_processes)
        all_cpus_free = all(proc is None for proc in self.current_processes.values())
        
        if all_done and all_cpus_free and self.all_processes:
            self.timer.stop()
            self.btn_play.setEnabled(True)
            QMessageBox.information(self, "Ejecución Terminada", f"Todos los procesos finalizaron en {self.clock} minutos.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = PokemonCenterOS()
    window.show()
    sys.exit(app.exec_())