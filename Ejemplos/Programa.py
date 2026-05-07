import time

# 1. El Controlador del Hardware (Simula el dispositivo y sus registros)
class ControladorSTRH:
    def __init__(self):
        # Mapeo de Registros (Valores iniciales)
        self.registro_estado = 0b00000001  # Bit 0 en 1 = Listo/Idle
        self.registro_orden = 0x00
        self.buffer_in = {"x": 0, "y": 0, "z": 0} # Datos desde el hardware
        self.buffer_out = 0                       # Datos hacia el hardware

    def ciclo_reloj_hardware(self):
        """Simula la respuesta del hardware interno al recibir una orden de la CPU"""
        if self.registro_orden == 0x01: # ORDEN: LEER SENSOR
            # El hardware se pone "Ocupado" (Bit 0 = 0)
            self.registro_estado = 0b00000000 
            print("[Hardware] Capturando trazos del giroscopio...")
            time.sleep(1) # Simulando latencia del dispositivo
            
            # Hardware escribe en el Buffer de Entrada
            self.buffer_in = {"x": 145, "y": 80, "z": 12}
            
            # Operación terminada, vuelve a estar "Listo" (Bit 0 = 1) y lanza Interrupción
            self.registro_estado = 0b00000011 # Bit 0 (Listo) + Bit 1 (Datos Listos)
            print("[Hardware] ¡Interrupción! Datos listos en buffer.\n")

        elif self.registro_orden == 0x02: # ORDEN: ACTIVAR VIBRACIÓN (HÁPTICA)
            self.registro_estado = 0b00000000
            fuerza = self.buffer_out
            print(f"[Hardware] Activando motor háptico al {fuerza}% de potencia.\n")
            self.registro_estado = 0b00000001 # Listo


# 2. La CPU (Ejecuta las operaciones de E/S sobre el controlador)
class CPU:
    def __init__(self, bus_controlador):
        self.io_bus = bus_controlador

    def operacion_lectura(self):
        print("[CPU] Iniciando lectura de gesto (Operación de LECTURA)...")
        # 1. CPU escribe la orden 0x01 en el registro de orden
        self.io_bus.registro_orden = 0x01
        self.io_bus.ciclo_reloj_hardware() # Simula que el tiempo pasa
        
        # 2. CPU bifurca/gestiona la interrupción (Verifica si hay datos)
        if self.io_bus.registro_estado & 0b00000010: # Máscara bitwise para checar Bit 1
            # 3. Extrae los datos del Buffer
            datos = self.io_bus.buffer_in
            print(f"[CPU] Gesto leído exitosamente: X={datos['x']}, Y={datos['y']}, Z={datos['z']}")
            # Limpia bandera de datos
            self.io_bus.registro_estado = 0b00000001 
            return datos

    def operacion_escritura(self, intensidad):
        print("\n[CPU] Detectó colisión en el juego. Iniciando respuesta háptica (Operación de ESCRITURA)...")
        # 1. CPU escribe los datos en el Buffer de Salida ANTES de dar la orden
        self.io_bus.buffer_out = intensidad
        
        # 2. CPU da la orden de ejecutar vibración
        self.io_bus.registro_orden = 0x02
        self.io_bus.ciclo_reloj_hardware()
        print("[CPU] Operación háptica completada.")

# --- EJECUCIÓN DEL SISTEMA ---
if __name__ == "__main__":
    # Conectamos los componentes
    controlador = ControladorSTRH()
    procesador = CPU(controlador)

    # El programa de usuario solicita leer un movimiento y luego hace vibrar el dispositivo
    coordenadas = procesador.operacion_lectura()
    procesador.operacion_escritura(intensidad=85)