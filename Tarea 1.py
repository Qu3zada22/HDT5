import simpy
import random
import numpy as np
import matplotlib.pyplot as plt

RANDOM_SEED = 42
NUM_PROCESSES = 25
CPU_SPEED = 3  # Velocidad del CPU (instrucciones por unidad de tiempo)
MEM_CAPACITY = 100  # Capacidad de la memoria RAM
INTERVAL = 10  # Intervalo para la distribución exponencial de llegada de procesos

waiting_times = []  # Lista para almacenar los tiempos de espera de cada proceso
ram_utilization = []  # Lista para almacenar la utilización de RAM en cada instante

class CPU:
    def __init__(self, env):
        self.env = env
        self.cpu = simpy.Resource(env, capacity=1)

    def execute(self, process):
        instructions_left = process.instructions
        while instructions_left > 0:
            with self.cpu.request() as req:
                yield req
                yield self.env.timeout(1 / CPU_SPEED)  # Simula el tiempo que toma ejecutar una instrucción
                instructions_left -= CPU_SPEED
                if instructions_left <= 0:
                    break
        process.end_time = self.env.now
        waiting_times.append(process.end_time - process.arrival_time)
        print(f"Proceso {process.id} terminado en tiempo {self.env.now}")


class Process:
    def __init__(self, env, id, ram_request):
        self.env = env
        self.id = id
        self.instructions = random.randint(1, 10)
        self.arrival_time = None
        self.end_time = None
        self.ram_request = ram_request

    def run(self, cpu, ram):
        self.arrival_time = self.env.now
        print(f"Proceso {self.id} llega en tiempo {self.arrival_time} y solicita {self.ram_request} de RAM.")
        with ram.get(self.ram_request) as req:
            yield req
            yield self.env.process(cpu.execute(self))
            ram_utilization.append(MEM_CAPACITY - ram.level)


def setup(env, num_processes, cpu, ram):
    for i in range(num_processes):
        ram_request = random.randint(1, 10)  # Solicita una cantidad aleatoria de RAM entre 1 y 10
        p = Process(env, i, ram_request)
        env.process(p.run(cpu, ram))
        t = random.expovariate(1.0 / INTERVAL)
        yield env.timeout(t)


env = simpy.Environment()
cpu = CPU(env)
ram = simpy.Container(env, capacity=MEM_CAPACITY, init=MEM_CAPACITY)  # Inicializa la RAM con su capacidad máxima
env.process(setup(env, NUM_PROCESSES, cpu, ram))
env.run()

# Cálculo de promedio de tiempo de espera
if len(waiting_times) > 0:
    avg_time = np.mean(waiting_times)
    print("Promedio de tiempo de espera:", avg_time)
else:
    print("No se han completado suficientes procesos para calcular el promedio de tiempo de espera.")

# Gráfica de utilización de RAM
plt.plot(range(len(ram_utilization)), ram_utilization)
plt.xlabel("Tiempo")
plt.ylabel("Utilización de RAM")
plt.title("Utilización de RAM durante la simulación")
plt.grid(True)
plt.show()
