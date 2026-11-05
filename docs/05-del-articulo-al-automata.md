# Ejercicio 5. Del artículo al autómata: Inteligencia Artificial de los Fantasmas de Pac-Man Ampliada

## 5.1. Elección y justificación de la ampliación (Gribkoff, 2013, Figura 3)

Se eligió la primera opción de la Sección 5.1: **el autómata finito que modela el comportamiento de los fantasmas de Pac-Man en Gribkoff (2013, Sección 4, Figura 3, p. 3)**, ampliándolo formalmente de **4 estados a 7 estados** (se añaden 3 estados nuevos) y de **4 eventos a 8 eventos** (se añaden 4 eventos nuevos).

### El modelo original de Gribkoff (2013) y sus limitaciones
En el documento de Gribkoff (2013), el comportamiento de un fantasma se simplifica en 4 estados (`Wander`, `Chase`, `Flee`, `Return to Base`) y 4 eventos (`see Pac-Man`, `lose Pac-Man`, `Pac-Man eats power pellet`, `timer expires` / `eaten by Pac-Man`). Sin embargo, esa simplificación omite tres mecanismos esenciales del diseño real de *Pac-Man* (Namco, 1980; Hopcroft et al., 2007):
1. **Regeneración en la Casa de los Fantasmas (`q0_PenWait`) y llegada física a la base (`b`)**: En Gribkoff (2013), cuando un fantasma es comido y regresa como ojos (`Return`), vuelve directamente a `Wander`, sin distinguir el evento de cruzar la puerta de la casa central (`b`: *reach_base*) ni el tiempo de espera dentro de la jaula (`q0_PenWait`) antes de ser liberado al laberinto.
2. **Oleadas globales de Dispersión a las Esquinas (`q2_ScatterCorner` y evento `w`)**: En el juego real, los fantasmas no deambulan al azar indefinidamente; un reloj global de oleadas (*wave timer*, evento `w`) los obliga periódicamente a abandonar la persecución o el patrullaje para dirigirse a su esquina fija del mapa (*Scatter Mode*: Blinky arriba a la derecha, Pinky arriba a la izquierda, Inky abajo a la derecha, Clyde abajo a la izquierda).
3. **Modo Frenesí / Captura Crítica (*Cruise Elroy* / `q6_ElroyVictory` y evento `c`)**: En el diagrama de Gribkoff no existe ningún **estado de aceptación** ($F = \emptyset$), por lo que ninguna secuencia de eventos del juego es formalmente aceptada. Al incorporar el evento `c` (*critical_dots_capture*, cuando Blinky acelera en modo *Elroy* y atrapa a Pac-Man completando el objetivo del agente enemigo), dotamos al AFD de un estado de aceptación bien definido $F = \{\text{q6\_ElroyVictory}\}$ que caracteriza el lenguaje de todas las partidas o rondas en las que el fantasma logra culminar una persecución exitosa.

---

## 5.2. Definición formal del autómata como quíntupla $M = (Q, \Sigma, \delta, q_0, F)$

Los archivos implementados y verificados en los tres formatos se encuentran en:
* **JFLAP (`.jff`)**: [`automatas/aplicacion/ej5_pacman_ampliado.jff`](../automatas/aplicacion/ej5_pacman_ampliado.jff)
* **JSON (`.json`)**: [`automatas/aplicacion/ej5_pacman_ampliado.json`](../automatas/aplicacion/ej5_pacman_ampliado.json)
* **XML (`.xml`)**: [`automatas/aplicacion/ej5_pacman_ampliado.xml`](../automatas/aplicacion/ej5_pacman_ampliado.xml)

### 1. Conjunto finito de estados ($Q$, con $|Q| = 7$) y qué representa cada estado:
* **`q0_PenWait`** *(Estado inicial $q_0$, **Ampliación 1**)*: El fantasma se encuentra dentro de la casa central (*Ghost Pen*) al iniciar la ronda o tras haber regresado como ojos, esperando la señal del temporizador de salida (`t`) o una oleada global (`w`) para salir al laberinto.
* **`q1_Wander`**: El fantasma patrulla los pasillos del laberinto sin tener a Pac-Man en su línea de visión directa.
* **`q2_ScatterCorner`** *(**Ampliación 2**)*: Ante la señal del reloj de oleada (`w`), el fantasma se repliega hacia su esquina asignada del mapa hasta que expira la oleada (`t`) o avista directamente a Pac-Man (`s`).
* **`q3_Chase`**: El fantasma tiene localizado a Pac-Man y ejecuta su heurística activa de persecución para interceptarlo.
* **`q4_Flee`**: Pac-Man ha consumido una superpíldora energética (`p`); el fantasma se vuelve azul, invierte su dirección y huye siendo vulnerable a ser comido (`e`).
* **`q5_ReturnEyes`**: El fantasma fue devorado por Pac-Man estando en `q4_Flee` y viaja rápidamente en forma de ojos inofensivos de regreso hacia la puerta de la casa central (esperando el evento `b`).
* **`q6_ElroyVictory`** *(Estado de aceptación $F$, **Ampliación 3**)*: Estado en el que el fantasma, estando en persecución activa (`q3_Chase`), ejecuta el sprint crítico *Cruise Elroy* y captura a Pac-Man (`c`) (solo revocable si se activa de emergencia una superpíldora `p` o se reinicia a la base `b`).

### 2. Alfabeto de eventos de entrada ($\Sigma$, con $|\Sigma| = 8$):
* `s` (*see_pacman*): El fantasma detecta a Pac-Man en su radio/línea de visión.
* `l` (*lose_pacman*): El fantasma pierde el rastro de Pac-Man.
* `p` (*power_pellet*): Pac-Man come una superpíldora energética.
* `t` (*timer_expire*): Expira el temporizador activo (salida de la casa, fin de oleada *Scatter* o fin del efecto de superpíldora).
* `e` (*eaten_by_pacman*): Pac-Man colisiona con el fantasma vulnerable y se lo come.
* `b` (*reach_base*, **Evento nuevo 1**): Los ojos del fantasma alcanzan la casa central para regenerar su cuerpo.
* `w` (*wave_scatter*, **Evento nuevo 2**): El temporizador global del nivel ordena cambiar a modo dispersión hacia las esquinas.
* `c` (*critical_dots_capture*, **Evento nuevo 3**): Activación de sprint *Cruise Elroy* / intercepción efectiva de Pac-Man durante la persecución.

### 3. Estado inicial ($q_0$) y Estados de aceptación ($F$):
* $q_0 = \text{q0\_PenWait}$
* $F = \{ \text{q6\_ElroyVictory} \}$

### 4. Tabla de la función de transición ($\delta: Q \times \Sigma \to Q$):

| Estado actual | `s` | `l` | `p` | `t` | `e` | `b` | `w` | `c` |
| :--- | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| $\to$ **`q0_PenWait`** | `q0_PenWait` | `q0_PenWait` | `q0_PenWait` | `q1_Wander` | `q0_PenWait` | `q0_PenWait` | `q2_ScatterCorner` | `q0_PenWait` |
| **`q1_Wander`** | `q3_Chase` | `q1_Wander` | `q4_Flee` | `q1_Wander` | `q1_Wander` | `q1_Wander` | `q2_ScatterCorner` | `q3_Chase` |
| **`q2_ScatterCorner`** | `q3_Chase` | `q2_ScatterCorner` | `q4_Flee` | `q1_Wander` | `q2_ScatterCorner` | `q2_ScatterCorner` | `q2_ScatterCorner` | `q3_Chase` |
| **`q3_Chase`** | `q3_Chase` | `q1_Wander` | `q4_Flee` | `q3_Chase` | `q3_Chase` | `q3_Chase` | `q2_ScatterCorner` | `q6_ElroyVictory` |
| **`q4_Flee`** | `q4_Flee` | `q4_Flee` | `q4_Flee` | `q1_Wander` | `q5_ReturnEyes` | `q4_Flee` | `q4_Flee` | `q4_Flee` |
| **`q5_ReturnEyes`** | `q5_ReturnEyes` | `q5_ReturnEyes` | `q5_ReturnEyes` | `q5_ReturnEyes` | `q5_ReturnEyes` | `q0_PenWait` | `q5_ReturnEyes` | `q5_ReturnEyes` |
| $*$ **`q6_ElroyVictory`** | `q6_ElroyVictory` | `q6_ElroyVictory` | `q4_Flee` | `q6_ElroyVictory` | `q6_ElroyVictory` | `q0_PenWait` | `q6_ElroyVictory` | `q6_ElroyVictory` |

---

## 5.3. Conjunto de 12 cadenas de prueba (Resultado esperado vs. obtenido en el simulador)

Todas las cadenas siguientes fueron evaluadas cargando [`automatas/aplicacion/ej5_pacman_ampliado.jff`](../automatas/aplicacion/ej5_pacman_ampliado.jff) en nuestro simulador ([`src/app.py`](../src/app.py)) y verificadas automáticamente con `pytest`:

| # | Cadena de entrada $w$ | Interpretación en el dominio de Pac-Man | Estado final alcanzado | Resultado Esperado | Resultado Obtenido |
| :-: | :--- | :--- | :--- | :---: | :---: |
| **1** | `tsc` | Sale de la casa (`t`), ve a Pac-Man (`s`) y lo captura en modo Elroy (`c`). | `q6_ElroyVictory` | **Aceptada** | **Aceptada** |
| **2** | `wsc` | Sale directo en oleada Scatter (`w`), avista a Pac-Man (`s`) y lo captura (`c`). | `q6_ElroyVictory` | **Aceptada** | **Aceptada** |
| **3** | `tslsc` | Sale (`t`), ve a Pac-Man (`s`), lo pierde (`l`), lo vuelve a ver (`s`) y captura (`c`). | `q6_ElroyVictory` | **Aceptada** | **Aceptada** |
| **4** | `tsptsc` | Persigue (`ts`), huye por superpíldora (`p`), expira el efecto (`t`), retoma persecución (`s`) y captura (`c`). | `q6_ElroyVictory` | **Aceptada** | **Aceptada** |
| **5** | `tspebtsc` | Ciclo completo: persigue (`ts`), huye (`p`), es comido (`e`), llega a la base como ojos (`b`), regenera y sale (`t`), persigue (`s`) y captura (`c`). | `q6_ElroyVictory` | **Aceptada** | **Aceptada** |
| **6** | `twtsc` | Sale a deambular (`t`), entra en oleada de esquina (`w`), termina oleada (`t`), ve a Pac-Man (`s`) y captura (`c`). | `q6_ElroyVictory` | **Aceptada** | **Aceptada** |
| **7** | `λ` (vacía) | Inicio de la ronda; el fantasma permanece dentro de la casa central. | `q0_PenWait` | **Rechazada** | **Rechazada** |
| **8** | `ts` | Sale de la casa y persigue a Pac-Man, pero aún no logra capturarlo. | `q3_Chase` | **Rechazada** | **Rechazada** |
| **9** | `tspe` | Es comido durante la huida y queda viajando como ojos sin llegar aún a la base. | `q5_ReturnEyes` | **Rechazada** | **Rechazada** |
| **10** | `tspeb` | Regresa como ojos a la casa central (`b`), quedando en espera de regeneración. | `q0_PenWait` | **Rechazada** | **Rechazada** |
| **11** | `tscp` | Logra la captura (`tsc`), pero una superpíldora de emergencia (`p`) lo devuelve a huida (`q4_Flee`). | `q4_Flee` | **Rechazada** | **Rechazada** |
| **12** | `sc` | Intenta perseguir y capturar sin haber salido primero de la casa (`q0_PenWait` ignora `s` y `c`). | `q0_PenWait` | **Rechazada** | **Rechazada** |

---

## 5.4. Reflexión sobre la abstracción (Media cuartilla): ¿Qué captura el modelo y qué deja fuera?

Modelar el controlador de inteligencia artificial de los fantasmas de *Pac-Man* mediante el Autómata Finito Determinista $M = (Q, \Sigma, \delta, q_0, F)$ constituye un ejercicio ejemplar de **abstracción formal**.

**¿Qué comportamiento del sistema real captura nuestro modelo?**
El AFD captura de manera exacta y determinista la **lógica de control reactivo de alto nivel (la máquina de modos de comportamiento)** de un agente autónomo:
1. Garantiza invariantes de seguridad del diseño del videojuego: por ejemplo, es imposible que un fantasma sea comido por Pac-Man (`e`) mientras está en modo `q3_Chase` o `q1_Wander` (solo la transición $\delta(\text{q4\_Flee}, e) = \text{q5\_ReturnEyes}$ produce ese efecto), y es imposible que unos ojos (`q5_ReturnEyes`) pasen a perseguir sin haber tocado antes la base (`b` $\to$ `q0_PenWait`) y haber cumplido su tiempo de regeneración (`t` $\to$ `q1_Wander`).
2. Captura la **jerarquía de prioridades de interrupción**: la superpíldora (`p`) actúa como una interrupción de máxima prioridad que fuerza la transición hacia `q4_Flee` desde cualquier estado activo en el laberinto (`Wander`, `ScatterCorner`, `Chase` o `ElroyVictory`), mientras que los ojos en retorno (`q5_ReturnEyes`) son inmunes a nuevas superpíldoras hasta regenerarse.

**¿Qué aspectos del sistema real deja fuera la abstracción de un AFD?**
Dado que un AFD solo posee un número finito de estados discretos y carece de memoria auxiliar ilimitada o variables continuas, el modelo abstrae y deja fuera tres dimensiones físicas del videojuego real:
1. **La geometría espacial 2D del laberinto y las coordenadas $(x, y)$**: El AFD sabe *en qué modo* está el fantasma (`q3_Chase`), pero no calcula la ruta más corta en la cuadrícula de $28 \times 36$ celdas ni almacena la posición continua de Pac-Man; esos eventos geométricos llegan al autómata ya resumidos como símbolos discretos del alfabeto (`s`, `l`, `b`, `c`).
2. **Los contadores de tiempo continuo y el conteo exacto de los 240 puntos (*dots*) del mapa**: En vez de contar milisegundos en un reloj de hardware o decrementar un entero de $240$ a $0$, el AFD recibe la expiración del temporizador como el símbolo abstracto `t` y el umbral de pocos puntos restantes como el evento `c`.
3. **La coordinación multi-agente de los cuatro fantasmas simultáneos**: Nuestro AFD modela a un fantasma individual; modelar la posición e interacción simultánea de los cuatro fantasmas y Pac-Man sobre todas las casillas del tablero requeriría el producto cartesiano de sus espacios de estados, disparando la explosión combinatoria analizada en el Ejercicio 4.

<!-- Verificado en rama feature/automata-aplicacion para Pull Request #5 -->
