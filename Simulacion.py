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
def simular(env, num_procesos, ram, cpu):
    yield env.timeout(0)
    tiempo_inicio = env.now
    for i in range(num_procesos):
        nombre = f'Proceso-{i+1}'
        memoria_necesaria = random.randint(1, 10)
        instrucciones = random.randint(1, 10)
        proceso = Proceso(env, nombre, memoria_necesaria, instrucciones)
        env.process(proceso.ejecutar(cpu, ram))
        tiempos_ejecucion.append(env.now - tiempo_inicio)

# Lista para almacenar los tiempos de ejecución promedio
promedios_tiempos_ejecucion = []

# Simulación para cada cantidad de procesos
for num_procesos in NUM_PROCESOS:
    env = simpy.Environment()
    ram = simpy.Container(env, capacity=MEMORIA_RAM, init=MEMORIA_RAM)
    cpu = simpy.Resource(env, capacity=NUM_CPUS)

    # Lanzar los procesos
    env.process(simular(env, num_procesos, ram, cpu))

    # Ejecutar la simulación
    env.run()

    # Calcular el tiempo promedio de ejecución
    promedio = np.mean(tiempos_ejecucion)
    promedios_tiempos_ejecucion.append(promedio)

    # Mostrar resultados
    print(f"Simulación finalizada para {num_procesos} procesos.")
    print(f"Tiempo promedio de ejecución: {promedio}")

# Graficar tiempos de ejecución promedio
plt.figure(figsize=(10, 6))
plt.plot(NUM_PROCESOS, promedios_tiempos_ejecucion, marker='o', color='b')
plt.xlabel('Número de Procesos')
plt.ylabel('Tiempo de Ejecución Promedio')
plt.title('Tiempo de Ejecución Promedio vs Número de Procesos')
plt.grid(True)
plt.show()
