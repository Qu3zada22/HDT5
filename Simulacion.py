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
INTERVALO = 10
MEMORIA_RAM = 100
VELOCIDAD_CPU = 3  # Instrucciones por unidad de tiempo
NUM_CPUS = 1

# Contenedores para almacenar los tiempos de ejecución de los procesos
tiempos_promedio = []
desviaciones_estandar = []

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
        return tiempo_ejecucion

# Función para simular con una cantidad específica de procesos
def simular(num_procesos):
    env = simpy.Environment()
    ram = simpy.Container(env, init=MEMORIA_RAM, capacity=MEMORIA_RAM)
    cpu = simpy.Resource(env, capacity=NUM_CPUS)
    tiempos_ejecucion = []
    for i in range(num_procesos):
        nombre = f'Proceso-{i+1}'
        memoria_necesaria = random.randint(1, 10)
        instrucciones = random.randint(1, 10)
        proceso = Proceso(env, nombre, memoria_necesaria, instrucciones)
        env.process(proceso.ejecutar(cpu))
    env.run(until=1000)

# Ejecutar la simulación con diferentes cantidades de procesos
for num_procesos in NUM_PROCESOS:
    simular(num_procesos)
    tiempos_promedio.append(np.mean(tiempos_ejecucion))
    desviaciones_estandar.append(np.std(tiempos_ejecucion))

# Mostrar resultados
print("Resultados:")
for i, num_procesos in enumerate(NUM_PROCESOS):
    print(f"Número de procesos: {num_procesos}, Tiempo promedio: {tiempos_promedio[i]}, Desviación estándar: {desviaciones_estandar[i]}")

# Graficar tiempo promedio y desviación estándar
plt.plot(NUM_PROCESOS, tiempos_promedio, label='Tiempo Promedio')
plt.xlabel('Número de Procesos')
plt.ylabel('Tiempo Promedio')
plt.title('Tiempo Promedio vs Número de Procesos')
plt.legend()
plt.show()

plt.plot(NUM_PROCESOS, desviaciones_estandar, label='Desviación Estándar')
plt.xlabel('Número de Procesos')
plt.ylabel('Desviación Estándar')
plt.title('Desviación Estándar vs Número de Procesos')
plt.legend()
plt.show()
