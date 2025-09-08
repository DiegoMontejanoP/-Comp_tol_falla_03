import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import multiprocessing
import asyncio
import time
import concurrent.futures
from functools import partial
import math


class PerformanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Comparador de Rendimiento de Procesos")
        self.root.geometry("1000x800")

        # Variables de control
        self.task_var = tk.StringVar(value="suma")
        self.iterations_var = tk.IntVar(value=1000)
        self.threads_var = tk.IntVar(value=4)
        self.processes_var = tk.IntVar(value=4)

        # Resultados
        self.results = {
            "hilos": 0,
            "procesos": 0,
            "demonios": 0,
            "asincrona": 0
        }

        # Referencia a widgets que necesitan ser deshabilitados
        self.control_widgets = []

        self.setup_ui()

    def setup_ui(self):
        # Frame de controles
        control_frame = ttk.LabelFrame(self.root, text="Controles", padding=10)
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        # Selección de tarea
        ttk.Label(control_frame, text="Tarea:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        task_combo = ttk.Combobox(control_frame, textvariable=self.task_var,
                                  values=["suma", "multiplicacion", "fibonacci", "exponencial"])
        task_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.control_widgets.append(task_combo)

        # Número de iteraciones
        ttk.Label(control_frame, text="Iteraciones:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        iterations_spin = ttk.Spinbox(control_frame, from_=100, to=1000000, increment=100,
                                      textvariable=self.iterations_var)
        iterations_spin.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.control_widgets.append(iterations_spin)

        # Número de hilos
        ttk.Label(control_frame, text="Hilos:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        threads_spin = ttk.Spinbox(control_frame, from_=1, to=64, increment=1, textvariable=self.threads_var)
        threads_spin.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        self.control_widgets.append(threads_spin)

        # Número de procesos
        ttk.Label(control_frame, text="Procesos:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        processes_spin = ttk.Spinbox(control_frame, from_=1, to=multiprocessing.cpu_count(), increment=1,
                                     textvariable=self.processes_var)
        processes_spin.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        self.control_widgets.append(processes_spin)

        # Botón de ejecución
        self.run_button = ttk.Button(control_frame, text="Ejecutar Comparación", command=self.run_comparison)
        self.run_button.grid(row=4, column=0, columnspan=2, pady=10)
        self.control_widgets.append(self.run_button)

        # Frame de resultados
        result_frame = ttk.LabelFrame(self.root, text="Resultados", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Gráfica de resultados
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, result_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Tabla de resultados
        self.result_table = ttk.Treeview(result_frame, columns=("Tipo", "Tiempo"), show="headings", height=5)
        self.result_table.heading("Tipo", text="Tipo de Proceso")
        self.result_table.heading("Tiempo", text="Tiempo (segundos)")
        self.result_table.column("Tipo", width=150)
        self.result_table.column("Tiempo", width=150)
        self.result_table.pack(fill=tk.X, pady=5)

    def run_comparison(self):
        # Deshabilitar controles durante la ejecución
        self.root.config(cursor="watch")
        self.disable_controls()

        # Ejecutar en un hilo separado para no bloquear la interfaz
        thread = threading.Thread(target=self.execute_comparisons)
        thread.daemon = True
        thread.start()

    def disable_controls(self):
        """Deshabilita solo los widgets de control"""
        for widget in self.control_widgets:
            try:
                widget.config(state="disabled")
            except:
                pass  # Ignorar widgets que no tienen la opción state

    def enable_controls(self):
        """Habilita los widgets de control"""
        for widget in self.control_widgets:
            try:
                widget.config(state="normal")
            except:
                pass  # Ignorar widgets que no tienen la opción state

    def execute_comparisons(self):
        try:
            # Obtener parámetros
            task = self.task_var.get()
            iterations = self.iterations_var.get()
            num_threads = self.threads_var.get()
            num_processes = self.processes_var.get()

            # Ejecutar y medir cada tipo de proceso
            start_time = time.time()
            self.run_with_threads(task, iterations, num_threads)
            self.results["hilos"] = time.time() - start_time

            start_time = time.time()
            self.run_with_processes(task, iterations, num_processes)
            self.results["procesos"] = time.time() - start_time

            start_time = time.time()
            self.run_with_daemons(task, iterations, num_threads)
            self.results["demonios"] = time.time() - start_time

            start_time = time.time()
            asyncio.run(self.run_async(task, iterations))
            self.results["asincrona"] = time.time() - start_time

            # Actualizar la interfaz
            self.root.after(0, self.update_results)

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            # Rehabilitar la interfaz
            self.root.after(0, self.enable_ui)

    def enable_ui(self):
        self.root.config(cursor="")
        self.enable_controls()

    def run_with_threads(self, task, iterations, num_threads):
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            # Dividir el trabajo entre los hilos
            chunk_size = max(1, iterations // num_threads)
            futures = []

            for i in range(num_threads):
                start = i * chunk_size
                end = (i + 1) * chunk_size if i < num_threads - 1 else iterations
                futures.append(executor.submit(self.execute_task, task, start, end))

            # Esperar a que todos los hilos terminen
            concurrent.futures.wait(futures)

    def run_with_processes(self, task, iterations, num_processes):
        with concurrent.futures.ProcessPoolExecutor(max_workers=num_processes) as executor:
            # Dividir el trabajo entre los procesos
            chunk_size = max(1, iterations // num_processes)
            futures = []

            for i in range(num_processes):
                start = i * chunk_size
                end = (i + 1) * chunk_size if i < num_processes - 1 else iterations
                futures.append(executor.submit(self.execute_task, task, start, end))

            # Esperar a que todos los procesos terminen
            concurrent.futures.wait(futures)

    def run_with_daemons(self, task, iterations, num_threads):
        threads = []

        # Dividir el trabajo entre los hilos demonio
        chunk_size = max(1, iterations // num_threads)

        for i in range(num_threads):
            start = i * chunk_size
            end = (i + 1) * chunk_size if i < num_threads - 1 else iterations
            thread = threading.Thread(target=self.execute_task, args=(task, start, end))
            thread.daemon = True
            threads.append(thread)
            thread.start()

        # Esperar a que todos los hilos terminen
        for thread in threads:
            thread.join()

    async def run_async(self, task, iterations):
        # Ejecutar la tarea de forma asíncrona
        await asyncio.get_event_loop().run_in_executor(
            None, partial(self.execute_task, task, 0, iterations))

    def execute_task(self, task, start, end):
        if task == "suma":
            result = 0
            for i in range(start, end):
                result += i
        elif task == "multiplicacion":
            result = 1
            for i in range(max(1, start), max(1, end)):
                result *= i
        elif task == "fibonacci":
            # Para fibonacci, calculamos el valor para el rango dado
            for i in range(start, min(end, start + 100)):  # Limitar para evitar tiempos excesivos
                self.fibonacci(i % 30)  # Limitar a un valor razonable
        elif task == "exponencial":
            result = 0
            for i in range(start, end):
                result += math.exp(i / 1000)  # Escalar para evitar overflow

    def fibonacci(self, n):
        if n <= 1:
            return n
        return self.fibonacci(n - 1) + self.fibonacci(n - 2)

    def update_results(self):
        # Limpiar tabla
        for item in self.result_table.get_children():
            self.result_table.delete(item)

        # Actualizar tabla
        for tipo, tiempo in self.results.items():
            self.result_table.insert("", "end", values=(tipo.capitalize(), f"{tiempo:.4f}"))

        # Actualizar gráfica
        self.ax.clear()
        tipos = [tipo.capitalize() for tipo in self.results.keys()]
        tiempos = list(self.results.values())

        bars = self.ax.bar(tipos, tiempos, color=['blue', 'green', 'red', 'orange'])
        self.ax.set_ylabel('Tiempo (segundos)')
        self.ax.set_title('Comparación de Rendimiento')

        # Añadir valores en las barras
        for bar, tiempo in zip(bars, tiempos):
            height = bar.get_height()
            self.ax.text(bar.get_x() + bar.get_width() / 2., height,
                         f'{tiempo:.4f}s', ha='center', va='bottom')

        self.canvas.draw()


if __name__ == "__main__":
    # Configuración para multiprocessing en Windows
    multiprocessing.freeze_support()
    root = tk.Tk()
    app = PerformanceApp(root)
    root.mainloop()