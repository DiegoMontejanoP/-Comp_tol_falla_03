# Comp_tol_falla_03

## 0. Experimentos

Básicamente las pruebas fueron similares en suma multiplicacion y exponenciales, si procesos era **1** el tiempo de proceso era la mitad

![all](https://drive.google.com/uc?id=1zcILFYPf-vjgcJYLnU3w8IqbsxYbdzdz)

Sin embargo usandolos para una recursividad como la seceuncia fibonacci se nota mas fluctuante los tiempos

![fibo1](https://drive.google.com/uc?id=15AKdXdvwT-RbzNUdps60EBYLbGa8Cm6z)

Hilos < a procesos 

![fibo2](https://drive.google.com/uc?id=1alJ2OMXuZLHymTWzJjMKJnhtnkhutSuj)

Hilos == procesos

![fibo3](https://drive.google.com/uc?id=12YYSfoBibmzC1VCL4QAQhoVOokgw12Fk)

Hilos > procesos

## 1. 🧵 Hilos (Threads)
**Punto fuerte:** Ideales para operaciones I/O bound donde el programa pasa mucho tiempo esperando por recursos externos.

**Ventajas:**
* Bajo overhead de creación
* Comparten memoria global (fácil comunicación)
* Bueno para operaciones con waiting (red, disco)

**Limitaciones:**
* Sujeto al GIL (Global Interpreter Lock) en Python
* No verdadero paralelismo para CPU-bound
## 2. 🔄 Procesos (Processes)
**Punto fuerte:** Excelentes para operaciones CPU-bound que requieren verdadero paralelismo.

Ventajas:
* Verdaderamente paralelos (eluden el GIL)
* Aprovechan múltiples núcleos de CPU
* Aislamiento de memoria (mayor estabilidad)

**Limitaciones:**
* Mayor overhead de creación
* Comunicación más compleja (IPC necesario)
* Mayor consumo de memoria

## 3. 👹 Demonios (Daemons)
**Punto fuerte:** Hilos que se ejecutan en segundo plano y terminan automáticamente cuando el programa principal termina.

**Ventajas:**
* No bloquean la finalización del programa
* Útiles para tareas de background
* Automáticamente terminados al salir

**Limitaciones:**
* Pueden terminar abruptamente
* No adecuados para tareas críticas

## 4. ⚡ Programación Asíncrona (Async/Await)
**Punto fuerte:** Máximo rendimiento en operaciones I/O bound con un solo hilo.

Ventajas:
* Extremadamente eficiente para I/O
* Bajo consumo de recursos
* Escalabilidad superior para muchas conexiones

**Limitaciones:**
* Curva de aprendizaje más pronunciada
* No beneficia operaciones CPU-bound
* Requiere librerías compatibles con async