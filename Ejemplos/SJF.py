def algoritmo_sjf(procesos):
    procesos.sort(key=lambda x: x['rafaga'])
    n = len(procesos)
    tiempo_espera = [0] * n
    tiempo_retorno = [0] * n

    tiempo_espera[0] = 0
    tiempo_retorno[0] = procesos[0]['rafaga']

    for i in range(1, n):
        tiempo_espera[i] = tiempo_espera[i-1] + procesos[i-1]['rafaga']
        tiempo_retorno[i] = tiempo_espera[i] + procesos[i]['rafaga']

    print(f"\n{'Proceso':<10} | {'Ráfaga':<8} | {'Espera':<8} | {'Retorno':<8}")
    print("-" * 45)
    for i in range(n):
        print(f"{procesos[i]['id']:<10} | {procesos[i]['rafaga']:<8} | {tiempo_espera[i]:<8} | {tiempo_retorno[i]:<8}")

    promedio_espera = sum(tiempo_espera) / n
    promedio_retorno = sum(tiempo_retorno) / n
    
    print("\nMétricas de Rendimiento:")
    print(f"Tiempo de espera promedio:  {promedio_espera:.2f}")
    print(f"Tiempo de retorno promedio: {promedio_retorno:.2f}")

def ingresar_procesos():
    lista_procesos = []
    n = int(input("Ingrese la cantidad de procesos a planificar: "))
    
    for i in range(n):
        print(f"\nDatos del proceso {i+1}:")
        id_proceso = input("ID del proceso (ej. P1): ")
        rafaga = int(input(f"Tiempo de ráfaga para {id_proceso}: "))
        lista_procesos.append({'id': id_proceso, 'rafaga': rafaga})
        
    return lista_procesos

procesos_usuario = ingresar_procesos()
algoritmo_sjf(procesos_usuario)