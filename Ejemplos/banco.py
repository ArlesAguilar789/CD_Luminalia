import time

class Cliente:
    def __init__(self, nombre, rafaga):
        self.nombre = nombre
        self.rafaga = rafaga
        self.espera = 0
        self.salida = 0

def iniciar_simulacion():
    print("\n" + "="*60)
    print("      SIMULADOR: FCFS vs FILA DE BANCO")
    print("="*60)
    
    lista_clientes = []
    try:
        cantidad = int(input("¿Cuántos clientes/procesos hay en la fila?: "))
    except ValueError:
        print("Error: Ingresa un número válido.")
        return

    print("-" * 60)
    for i in range(cantidad):
        print(f"Datos del Cliente #{i + 1}:")
        nombre = input("   Nombre: ")
        try:
            rafaga = int(input("   Tiempo de trámite (minutos): "))
        except ValueError:
            rafaga = 1
        lista_clientes.append(Cliente(nombre, rafaga))
        print("   ---")

    tiempo_actual = 0
    total_espera = 0
    
    print("\n" + "="*60)
    print(" 🏦  INICIANDO ATENCIÓN EN VENTANILLA (EJECUCIÓN)")
    print("="*60)

    for c in lista_clientes:
        c.espera = tiempo_actual
        total_espera += c.espera
        
        print(f"\n➡️  ATENDIENDO A: {c.nombre}")
        print(f"    ⏳ Esperó en la fila: {c.espera} min")
        print(f"    ⚙️  Trabajando ({c.rafaga} min): ", end="")
        
        for _ in range(c.rafaga):
            time.sleep(0.3)
            print("█", end="", flush=True)
            
        print(" ✅ Terminado")
        tiempo_actual += c.rafaga
        c.salida = tiempo_actual

    print("\n\n" + "="*60)
    print(" 📊 TABLA COMPARATIVA DE RESULTADOS")
    print("="*60)
    print(f"{'CLIENTE/PROCESO':<20} | {'DURACIÓN':<10} | {'ESPERA':<10} | {'SALIDA':<10}")
    print("-" * 60)

    for c in lista_clientes:
        print(f"{c.nombre:<20} | {c.rafaga:<10} | {c.espera:<10} | {c.salida:<10}")

    print("-" * 60)
    promedio = total_espera / len(lista_clientes)
    print(f"⏱️  TIEMPO PROMEDIO DE ESPERA: {promedio:.2f} minutos")
    print("="*60)
    input("\nPresiona ENTER para cerrar...")

if __name__ == "__main__":
    iniciar_simulacion()