import simpy
import random
import numpy as np
import matplotlib.pyplot as plt

# Definir la semilla para la generación de números aleatorios
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# Parámetros de la simulación
NUM_PROCESOS = [25, 50, 100, 150, 200, 250, 300, 400, 550]
INTERVALO = 10
MEMORIA_RAM = 100
VELOCIDAD_CPU = 3  # Instrucciones por unidad de tiempo
NUM_CPUS = 1

# Contenedores para almacenar los tiempos de ejecución de los procesos
tiempos_ejecucion = []

class Proceso:
    def __init__(self, env, nombre, memoria, instrucciones):
        self.env = env
        self.nombre = nombre
        self.memoria = memoria
        self.instrucciones = instrucciones

    def ejecutar(self, cpu):
        inicio = self.env.now
        with cpu.request() as req:
            yield req
            while self.instrucciones > 0:
                tiempo_necesario = min(self.instrucciones, VELOCIDAD_CPU)
                yield self.env.timeout(tiempo_necesario)
                self.instrucciones -= tiempo_necesario
            fin = self.env.now
        tiempo_ejecucion = fin - inicio
        tiempos_ejecucion.append(tiempo_ejecucion)

# Función para simular con una cantidad específica de procesos
def simular(num_procesos):
    env = simpy.Environment()
    ram = simpy.Container(env, init=MEMORIA_RAM, capacity=MEMORIA_RAM)
    cpu = simpy.Resource(env, capacity=NUM_CPUS)
    for i in range(num_procesos):
        nombre = f'Proceso-{i+1}'
        memoria_necesaria = random.randint(1, 10)
        instrucciones = random.randint(1, 10)
        proceso = Proceso(env, nombre, memoria_necesaria, instrucciones)
        env.process(proceso.ejecutar(cpu))
    env.run(until=1000)

# Ejecutar la simulación con diferentes cantidades de procesos
promedios_tiempos_ejecucion = []

for num_procesos in NUM_PROCESOS:
    tiempos_ejecucion = []
    simular(num_procesos)
    promedio = np.mean(tiempos_ejecucion)
    promedios_tiempos_ejecucion.append(promedio)

# Mostrar resultados
print("Promedios de tiempos de ejecución:", promedios_tiempos_ejecucion)

# Graficar tiempos de ejecución
plt.plot(promedios_tiempos_ejecucion, NUM_PROCESOS, marker='o')
plt.xlabel('Tiempo de Ejecución Promedio')
plt.ylabel('Número de Procesos')
plt.title('Número de Procesos vs Tiempo de Ejecución Promedio')
plt.grid(True)
plt.show()
