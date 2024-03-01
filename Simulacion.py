import simpy
import random
import numpy as np
import matplotlib.pyplot as plt

# Definir la semilla para la generación de números aleatorios
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# Parámetros de la simulación
NUM_PROCESOS = [25, 50, 100, 150, 200]
INTERVALOS_LLEGADA = [10, 5, 1]
MEMORIA_RAM = 100
VELOCIDAD_CPU = 3  # Instrucciones por unidad de tiempo
NUM_CPUS = 1

# Diccionario para almacenar los tiempos de ejecución de cada proceso
tiempos_ejecucion = {num_procesos: {intervalo_llegada: [] for intervalo_llegada in INTERVALOS_LLEGADA} for num_procesos in NUM_PROCESOS}

# Lista para almacenar los tiempos de ejecución promedio
promedios_tiempos_ejecucion = {intervalo_llegada: [] for intervalo_llegada in INTERVALOS_LLEGADA}

# Lista para almacenar las desviaciones estándar
desviaciones_estandar = {intervalo_llegada: [] for intervalo_llegada in INTERVALOS_LLEGADA}

class Proceso:
    def __init__(self, env, nombre, memoria, instrucciones):
        self.env = env
        self.nombre = nombre
        self.memoria = memoria
        self.instrucciones = instrucciones

    def ejecutar(self, cpu, ram):
        # Proceso pide la cantidad de memoria necesaria
        with ram.get(self.memoria) as req:
            yield req  # Espera hasta que haya suficiente memoria disponible

            # Proceso pasa a la CPU
            with cpu.request() as req_cpu:
                yield req_cpu  # Espera hasta que la CPU esté disponible
                tiempo_restante = self.instrucciones
                while tiempo_restante > 0:
                    # Simula la ejecución de las instrucciones en la CPU
                    tiempo_necesario = min(tiempo_restante, VELOCIDAD_CPU)
                    yield self.env.timeout(tiempo_necesario)
                    tiempo_restante -= tiempo_necesario

# Función para simular los procesos
def simular(env, num_procesos, intervalo_llegada, ram, cpu):
    for _ in range(num_procesos):
        tiempo_inicio = env.now
        proceso = Proceso(env, f'Proceso-{_ + 1}', random.randint(1, 10), random.randint(1, 10))
        env.process(proceso.ejecutar(cpu, ram))
        yield env.timeout(random.expovariate(1.0 / intervalo_llegada))
        tiempo_final = env.now
        tiempos_ejecucion[num_procesos][intervalo_llegada].append(tiempo_final - tiempo_inicio)

# Simulación para cada cantidad de procesos y cada intervalo de llegada
for intervalo_llegada in INTERVALOS_LLEGADA:
    for num_procesos in NUM_PROCESOS:
        env = simpy.Environment()
        ram = simpy.Container(env, capacity=MEMORIA_RAM, init=MEMORIA_RAM)
        cpu = simpy.Resource(env, capacity=NUM_CPUS)

        # Lanzar los procesos
        env.process(simular(env, num_procesos, intervalo_llegada, ram, cpu))

        # Ejecutar la simulación
        env.run(until=1000)  # Simulación durante un tiempo suficientemente largo

        # Calcular el tiempo promedio de ejecución
        tiempo_promedio = np.mean(tiempos_ejecucion[num_procesos][intervalo_llegada])
        promedios_tiempos_ejecucion[intervalo_llegada].append(tiempo_promedio)

        # Calcular la desviación estándar
        desviacion_estandar = np.std(tiempos_ejecucion[num_procesos][intervalo_llegada])
        desviaciones_estandar[intervalo_llegada].append(desviacion_estandar)

        # Mostrar resultados
        print(f"Simulación finalizada para {num_procesos} procesos con intervalo de llegada {intervalo_llegada}.")
        print(f"Tiempo promedio de ejecución: {tiempo_promedio}")
        print(f"Desviación estándar: {desviacion_estandar}")

# Graficar tiempos de ejecución promedio
plt.figure(figsize=(10, 6))
for intervalo_llegada in INTERVALOS_LLEGADA:
    plt.plot(NUM_PROCESOS, promedios_tiempos_ejecucion[intervalo_llegada], marker='o', label=f'Intervalo {intervalo_llegada}')
plt.xlabel('Número de Procesos')
plt.ylabel('Tiempo de Ejecución Promedio')
plt.title('Tiempo de Ejecución Promedio vs Número de Procesos')
plt.legend()
plt.grid(True)
plt.show()

# Graficar desviaciones estándar
plt.figure(figsize=(10, 6))
for intervalo_llegada in INTERVALOS_LLEGADA:
    plt.plot(NUM_PROCESOS, desviaciones_estandar[intervalo_llegada], marker='o', label=f'Intervalo {intervalo_llegada}')
plt.xlabel('Número de Procesos')
plt.ylabel('Desviación Estándar')
plt.title('Desviación Estándar vs Número de Procesos')
plt.legend()
plt.grid(True)
plt.show()
