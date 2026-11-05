# Ejercicio 3. Documentación Formal de los Algoritmos

En este documento se presenta la documentación teórica, algorítmica y de complejidad de cada uno de los algoritmos programados en Python puro en [`src/automata.py`](../../src/automata.py) para el Ejercicio 2, sustentada exclusivamente en las obras admitidas en la Práctica 2 (**[`docs/bibliografia.md`](../bibliografia.md)**).

Sea $n = |Q|$ el número de estados del autómata y $m = |\Sigma|$ el tamaño del alfabeto de entrada.

---

## Algoritmo 1 (Sección 2.1): Cálculo de la Cerradura $\lambda$ y Simulación Directa de un AFN-$\lambda$

### 1.1. Enunciado del problema y resultado teórico que lo respalda
* **Problema que resuelve:** Dado un autómata finito no determinista con transiciones $\lambda$, $M = (Q, \Sigma, \delta, q_0, F)$, calcular para todo estado $q \in Q$ el conjunto $Cl_\lambda(\{q\})$ de estados alcanzables desde $q$ mediante cero o más transiciones espontáneas $\lambda$, y decidir si una cadena $w = a_1 a_2 \cdots a_k \in \Sigma^*$ pertenece a $L(M)$ manteniendo en cada paso $i$ el conjunto activo antes ($M_i$) y después ($S_i = Cl_\lambda(M_i)$) de aplicar la cerradura $\lambda$, sin convertir el autómata a AFD.
* **Resultado teórico y referencia bibliográfica exacta:**
  * **Hopcroft, Motwani y Ullman (2007)**, *Introducción a la teoría de autómatas, lenguajes y computación* (3.ª ed., ISBN 978-84-7829-088-8), **Capítulo 2, Sección 2.5.3 «Cerradura-$\epsilon$» (p. 73) y Sección 2.5.4 «Transiciones extendidas y lenguajes de los AFN-$\epsilon$» (pp. 74–75)**: Define recursivamente $\text{ECLOSE}(q)$ como el menor conjunto tal que $q \in \text{ECLOSE}(q)$ y si $p \in \text{ECLOSE}(q)$, entonces $\delta(p, \lambda) \subseteq \text{ECLOSE}(q)$, y define la función de transición extendida por inducción sobre la longitud de la cadena:
    $$\hat{\delta}(q_0, \lambda) = Cl_\lambda(\{q_0\}), \qquad \hat{\delta}(q_0, xa) = Cl_\lambda\!\left(\bigcup_{p \in \hat{\delta}(q_0, x)} \delta(p, a)\right)$$
    de modo que $w \in L(M) \iff \hat{\delta}(q_0, w) \cap F \neq \emptyset$.
  * **Aho, Lam, Sethi y Ullman (2006)**, *Compilers: Principles, Techniques, and Tools* (2.ª ed., ISBN 978-0-321-48681-3), **Capítulo 3, Sección 3.7.1, Figuras 3.31–3.33 (pp. 152–156)**: Algoritmo de simulación directa en línea de un AFN manteniendo el conjunto de estados activos tras cada símbolo leído.

### 1.2. Pseudocódigo y correspondencia con [`src/automata.py`](../../src/automata.py)

```text
ALGORITMO 1A: CLAUSURA_LAMBDA_ESTADO(M, q)
Entrada: Autómata M = (Q, Σ, δ, q0, F), estado q ∈ Q
Salida: Conjunto ordenado Cl_λ({q})
1. visitados ← {q}
2. cola ← [q]
3. MIENTRAS cola ≠ [] HACER:
4.     u ← DESENCOLAR(cola)
5.     PARA CADA v ∈ δ(u, λ) HACER:
6.         SI v ∉ visitados ENTONCES:
7.             visitados ← visitados ∪ {v}
8.             ENCOLAR(cola, v)
9. DEVOLVER ORDENAR_SEGUN_Q(visitados)

ALGORITMO 1B: SIMULAR_DIRECTO_AFND_LAMBDA(M, w = a_1 a_2 ... a_k)
Entrada: AFN-λ M = (Q, Σ, δ, q0, F), cadena w ∈ Σ*
Salida: (aceptada, trazas_antes_y_despues)
1. antes_0 ← {q0}
2. S_0 ← CLAUSURA_LAMBDA(M, antes_0)         // Después de Cl_λ en paso inicial
3. Registrar Paso 0: (antes = antes_0, despues = S_0)
4. PARA i ← 1 HASTA k HACER:
5.     antes_i ← ⋃_{u ∈ S_{i-1}} δ(u, a_i)  // Estados activos ANTES de Cl_λ
6.     S_i ← ⋃_{v ∈ antes_i} CLAUSURA_LAMBDA_ESTADO(M, v) // DESPUÉS de Cl_λ
7.     Registrar Paso i: (simbolo = a_i, antes = antes_i, despues = S_i)
8. finales_alcanzados ← S_k ∩ F
9. DEVOLVER (finales_alcanzados ≠ ∅, pasos)
```

| Bloque del pseudocódigo | Función / Método en [`src/automata.py`](../../src/automata.py) | Líneas en código |
| :--- | :--- | :--- |
| `CLAUSURA_LAMBDA_ESTADO(M, q)` | [`AutomataFinito.lambda_clausura_estado`](../../src/automata.py#L226-L242) | Líneas 226–242 |
| `CLAUSURA_LAMBDA(M, Z)` | [`AutomataFinito.lambda_clausura`](../../src/automata.py#L243-L250) | Líneas 243–250 |
| Tabla completa $\{q: Cl_\lambda(\{q\})\}$ | [`AutomataFinito.tabla_lambda_clausuras`](../../src/automata.py#L251-L253) | Líneas 251–253 |
| `SIMULAR_DIRECTO_AFND_LAMBDA(M, w)` | [`AutomataFinito.simular`](../../src/automata.py#L271-L364) y [`AutomataFinito.simular_directo_afnd_lambda`](../../src/automata.py#L366-L368) | Líneas 271–368 |

### 1.3. Ejemplo de la Lista 3 resuelto a mano vs. Software (Ejercicio 199, `ej199_afnd_lambda.jff`)
Sea el AFN-$\lambda$ del **Ejercicio 199** ($Q=\{A,B,C,D,E\}$, $\Sigma=\{0,1\}$, $q_0=A$, $F=\{D,E\}$) y la cadena $w = \text{`011`}$ del inciso e):
* **Resolución a mano:**
  1. **Cerraduras $\lambda$ individuales:**
     * Desde $A$: $A \xrightarrow{\lambda} B$ y $A \xrightarrow{\lambda} C \xrightarrow{\lambda} E \implies Cl_\lambda(\{A\}) = \{A, B, C, E\}$.
     * Desde $B$: sin transiciones $\lambda \implies Cl_\lambda(\{B\}) = \{B\}$.
     * Desde $C$: $C \xrightarrow{\lambda} E \implies Cl_\lambda(\{C\}) = \{C, E\}$.
     * Desde $D$: $Cl_\lambda(\{D\}) = \{D\}$; desde $E$: $Cl_\lambda(\{E\}) = \{E\}$.
  2. **Simulación paso a paso de $w = \text{`011`}$:**
     * **Paso 0 ($\lambda$ inicial):** Antes de $Cl_\lambda$: $\{A\}$. Después de $Cl_\lambda$: $S_0 = \{A, B, C, E\}$.
     * **Paso 1 (símbolo `0`):** $\delta(A,0)=\{E\}, \delta(B,0)=\{E\}, \delta(C,0)=\emptyset, \delta(E,0)=\emptyset$.
       * Antes de $Cl_\lambda$: $M_1 = \{E\}$.
       * Después de $Cl_\lambda$: $S_1 = Cl_\lambda(\{E\}) = \{E\}$.
     * **Paso 2 (símbolo `1`):** $\delta(E,1)=\{D\}$.
       * Antes de $Cl_\lambda$: $M_2 = \{D\}$.
       * Después de $Cl_\lambda$: $S_2 = Cl_\lambda(\{D\}) = \{D\}$.
     * **Paso 3 (símbolo `1`):** $\delta(D,1)=\{D\}$.
       * Antes de $Cl_\lambda$: $M_3 = \{D\}$.
       * Después de $Cl_\lambda$: $S_3 = Cl_\lambda(\{D\}) = \{D\}$.
     * **Veredicto:** $S_3 \cap F = \{D\} \cap \{D, E\} = \{D\} \neq \emptyset \implies$ **Aceptada**.
* **Salida del software (`m199.simular_directo_afnd_lambda("011")`) y comparación:**
  * `Paso 0`: `estados_antes_de_lambda=['A']`, `estados_despues_de_lambda=['A', 'B', 'C', 'E']`
  * `Paso 1 ('0')`: `estados_antes_de_lambda=['E']`, `estados_despues_de_lambda=['E']`
  * `Paso 2 ('1')`: `estados_antes_de_lambda=['D']`, `estados_despues_de_lambda=['D']`
  * `Paso 3 ('1')`: `estados_antes_de_lambda=['D']`, `estados_despues_de_lambda=['D']`
  * **Comparación:** Los conjuntos antes y después de $Cl_\lambda$ en los 4 pasos y el estado final alcanzado `['D']` coinciden exactamente entre el cálculo a mano y el software.

### 1.4. Estimación del número de pasos en función de $n = |Q|$ y $m = |\Sigma|$
* **Cálculo de $Cl_\lambda(\{q\})$ para un estado:** el recorrido BFS visita a lo sumo $n$ vértices y explora a lo sumo $n^2$ aristas $\lambda$, por lo que requiere $\mathcal{O}(n^2)$ pasos por estado, y **$\mathcal{O}(n^3)$ pasos** para calcular la tabla de los $n$ estados (independiente de $m = |\Sigma|$).
* **Simulación directa de una cadena de longitud $|w| = L$:** en cada uno de los $L$ símbolos se consultan a lo sumo $n$ estados activos con a lo sumo $n$ destinos por el símbolo leído ($\mathcal{O}(n^2)$) y se aplica la cerradura $\lambda$ ($\mathcal{O}(n^2)$), dando **$\mathcal{O}(L \cdot n^2)$ pasos**.

---

## Algoritmo 2 (Sección 2.2): Eliminación de Transiciones $\lambda$ (AFN-$\lambda \to$ AFN)

### 2.1. Enunciado del problema y resultado teórico que lo respalda
* **Problema que resuelve:** Dado un AFN-$\lambda$ $M = (Q, \Sigma, \delta, q_0, F)$, construir un AFN sin transiciones $\lambda$, $M_N = (Q, \Sigma, \delta_N, q_0, F_N)$, tal que $L(M_N) = L(M)$, identificando explícitamente las transiciones añadidas y los estados que se incorporan al conjunto de aceptación.
* **Resultado teórico y referencia bibliográfica exacta:**
  * **Linz (2017)**, *An Introduction to Formal Languages and Automata* (6.ª ed., ISBN 978-1-284-07724-7), **Capítulo 2, Sección 2.2, Teorema 2.2 (pp. 52–56)** y **Hopcroft, Motwani y Ullman (2007)**, **Capítulo 2, Sección 2.5.5 (pp. 75–78)**: Para todo AFN-$\lambda$ $M$ existe un AFN sin transiciones $\lambda$ con el mismo conjunto de estados $Q$ definido por:
    $$\delta_N(q, a) = Cl_\lambda\!\left(\bigcup_{p \in Cl_\lambda(\{q\})} \delta(p, a)\right) \quad \forall q \in Q, a \in \Sigma, \qquad F_N = \{q \in Q \mid Cl_\lambda(\{q\}) \cap F \neq \emptyset\}$$
     el cual cumple $\hat{\delta}_N(q_0, w) = \hat{\delta}(q_0, w)$ para toda $w \in \Sigma^+$ y $q_0 \in F_N \iff \lambda \in L(M)$, por lo que $L(M_N) = L(M)$.

### 2.2. Pseudocódigo y correspondencia con [`src/automata.py`](../../src/automata.py)

```text
ALGORITMO 2: ELIMINAR_TRANSICIONES_LAMBDA(M)
Entrada: AFN-λ M = (Q, Σ, δ, q0, F)
Salida: AFN sin λ M_N = (Q, Σ, δ_N, q0, F_N), lista trans_añadidas, lista nuevos_finales
1. Para cada q ∈ Q: calcular Cl[q] ← CLAUSURA_LAMBDA_ESTADO(M, q)
2. F_N ← ∅; nuevos_finales ← []
3. PARA CADA q ∈ Q HACER:
4.     SI Cl[q] ∩ F ≠ ∅ ENTONCES:
5.         F_N ← F_N ∪ {q}
6.         SI q ∉ F ENTONCES: agregar (q, Cl[q] ∩ F) a nuevos_finales
7.     PARA CADA a ∈ Σ HACER:
8.         intermedios ← ⋃_{p ∈ Cl[q]} δ(p, a)
9.         δ_N(q, a) ← ⋃_{r ∈ intermedios} Cl[r]
10.        PARA CADA w ∈ δ_N(q, a) HACER:
11.            SI w ∉ δ(q, a) ENTONCES: registrar (q, a, w) en trans_añadidas
12. DEVOLVER (Q, Σ, δ_N, q0, F_N), trans_añadidas, nuevos_finales
```

| Bloque del pseudocódigo | Función / Método en [`src/automata.py`](../../src/automata.py) | Líneas en código |
| :--- | :--- | :--- |
| Algoritmo completo con bitácora | [`AutomataFinito.eliminar_transiciones_lambda_detallado`](../../src/automata.py#L378-L442) | Líneas 378–442 |
| Envoltura directa que devuelve $M_N$ | [`AutomataFinito.convertir_afnd_lambda_a_afnd`](../../src/automata.py#L444-L446) | Líneas 444–446 |

### 2.3. Ejemplo de la Lista 3 resuelto a mano vs. Software (Ejercicio 196, `ej196_afnd_lambda.jff`)
Sea el AFN-$\lambda$ del **Ejercicio 196** ($Q=\{A,B,C\}$, $\Sigma=\{0,1\}$, $q_0=A$, $F=\{C\}$, con $\delta(A,\lambda)=\{B\}$, $\delta(A,0)=\{A\}$, $\delta(B,0)=\{A,B\}$, $\delta(B,1)=\{C\}$):
* **Resolución a mano:**
  1. **Cerraduras $\lambda$:** $Cl_\lambda(\{A\}) = \{A,B\}$, $Cl_\lambda(\{B\}) = \{B\}$, $Cl_\lambda(\{C\}) = \{C\}$.
  2. **Nuevos estados de aceptación $F_N$:** Como $C$ sólo pertenece a $Cl_\lambda(\{C\})$, $F_N = \{C\}$ (ningún estado nuevo pasa a ser de aceptación).
  3. **Nuevas transiciones $\delta_N(q,a)$:**
     * Para $q = A$:
       * Con $a=0$: $\delta(A,0) \cup \delta(B,0) = \{A\} \cup \{A,B\} = \{A,B\} \implies Cl_\lambda(\{A,B\}) = \{A,B\}$. Se añade la transición **`(A, 0) -> B`** (vía $A \xrightarrow{\lambda} B \xrightarrow{0} B$).
       * Con $a=1$: $\delta(A,1) \cup \delta(B,1) = \emptyset \cup \{C\} = \{C\} \implies Cl_\lambda(\{C\}) = \{C\}$. Se añade la transición **`(A, 1) -> C`** (vía $A \xrightarrow{\lambda} B \xrightarrow{1} C$).
     * Para $q = B$:
       * Con $a=0$: $Cl_\lambda(\delta(B,0)) = Cl_\lambda(\{A,B\}) = \{A,B\}$ (ya existía).
       * Con $a=1$: $Cl_\lambda(\delta(B,1)) = Cl_\lambda(\{C\}) = \{C\}$ (ya existía).
     * Para $q = C$: $\delta_N(C,0) = \emptyset$, $\delta_N(C,1) = \emptyset$.
* **Salida del software (`m196.eliminar_transiciones_lambda_detallado()`) y comparación:**
  * `aceptacion`: `['C']` (`nuevos_estados_aceptacion = []`).
  * `transiciones_anadidas`: `[('A', '0', 'B', 'A --λ*--> B --0--> B --λ*--> B'), ('A', '1', 'C', 'A --λ*--> B --1--> C --λ*--> C')]`.
  * **Comparación:** Coincidencia exacta tanto en la tabla $\delta_N$ como en las 2 transiciones añadidas y en $F_N$.

### 2.4. Estimación del número de pasos en función de $n = |Q|$ y $m = |\Sigma|$
1. Precalcular $Cl_\lambda(\{q\})$ para los $n$ estados toma $\mathcal{O}(n^3)$ pasos.
2. Para cada uno de los $n$ estados y cada uno de los $m$ símbolos de $\Sigma$ ($n \cdot m$ iteraciones):
   * Se recorren a lo sumo $n$ estados $p \in Cl_\lambda(\{q\})$ y sus a lo sumo $n$ destinos $r \in \delta(p,a)$ ($\mathcal{O}(n^2)$ operaciones).
   * Se unen las cerraduras precalculadas $Cl_\lambda(\{r\})$ de los a lo sumo $n$ estados intermedios ($\mathcal{O}(n^2)$ operaciones).
* **Complejidad total:** **$\mathcal{O}(n^3 + m \cdot n^3) = \mathcal{O}(m \cdot n^3)$ pasos**.

---

## Algoritmo 3 (Sección 2.3): Construcción de Subconjuntos Alcanzables (AFN $\to$ AFD)

### 3.1. Enunciado del problema y resultado teórico que lo respalda
* **Problema que resuelve:** Dado un AFN (o AFN-$\lambda$) $M = (Q, \Sigma, \delta, q_0, F)$, construir un AFD equivalente $M_D = (Q_D, \Sigma, \delta_D, S_0, F_D)$ generando únicamente los subconjuntos $S \subseteq Q$ que son alcanzables desde el estado inicial $S_0 = Cl_\lambda(\{q_0\})$ y determinando cuáles resultan de aceptación.
* **Resultado teórico y referencia bibliográfica exacta:**
  * **Rabin y Scott (1959)**, *Finite automata and their decision problems* (*IBM Journal of Research and Development*, 3(2), 114–125), **Sección 2, Teorema 3 (pp. 117–118)**: Demostración original de que todo autómata no determinista es equivalente a un autómata determinista sobre el conjunto potencia $\mathcal{P}(Q)$.
  * **Hopcroft, Motwani y Ullman (2007)**, **Capítulo 2, Sección 2.3.5 «La construcción de subconjuntos», Teorema 2.11 (pp. 58–63)**: La construcción de subconjuntos (restringida a los subconjuntos alcanzables para evitar construir estados inaccesibles de entre los $2^n$ posibles) produce un AFD $M_D$ con $F_D = \{S \in Q_D \mid S \cap F \neq \emptyset\}$ tal que $L(M_D) = L(M)$.

### 3.2. Pseudocódigo y correspondencia con [`src/automata.py`](../../src/automata.py)

```text
ALGORITMO 3: CONSTRUCCION_SUBCONJUNTOS_ALCANZABLES(M)
Entrada: AFN / AFN-λ M = (Q, Σ, δ, q0, F)
Salida: AFD M_D = (Q_D, Σ, δ_D, S_0, F_D) y tabla detallada de filas
1. S_0 ← CLAUSURA_LAMBDA(M, {q0})
2. Q_D ← [S_0]; cola ← [S_0]; δ_D ← {}
3. MIENTRAS cola ≠ [] HACER:
4.     S ← DESENCOLAR(cola)
5.     PARA CADA a ∈ Σ HACER:
6.         mov ← ⋃_{q ∈ S} δ(q, a)
7.         T ← CLAUSURA_LAMBDA(M, mov)
8.         SI T ≠ ∅ ENTONCES:
9.             δ_D(S, a) ← T
10.            SI T ∉ Q_D ENTONCES:
11.                Agregar T a Q_D y ENCOLAR(cola, T)
12. F_D ← { S ∈ Q_D | S ∩ F ≠ ∅ }
13. Para cada S ∈ Q_D: registrar razón de aceptación (S ∩ F)
14. DEVOLVER (Q_D, Σ, δ_D, S_0, F_D)
```

| Bloque del pseudocódigo | Función / Método en [`src/automata.py`](../../src/automata.py) | Líneas en código |
| :--- | :--- | :--- |
| Construcción de subconjuntos alcanzables | [`AutomataFinito.construccion_subconjuntos_detallada`](../../src/automata.py#L452-L549) | Líneas 452–549 |
| Envoltura directa que devuelve el AFD | [`AutomataFinito.convertir_a_afd`](../../src/automata.py#L551-L553) | Líneas 551–553 |

### 3.3. Ejemplo de la Lista 3 resuelto a mano vs. Software (Ejercicio 260, `ej260_subconjuntos.jff`)
Sea el AFN del **Ejercicio 260** ($Q=\{A,B,C,D,E\}$, $\Sigma=\{0,1\}$, $q_0=A$, $F=\{D\}$):
* $\delta(A,0)=\emptyset, \delta(A,1)=\{B,C\}$
* $\delta(B,0)=\{A,B,D\}, \delta(B,1)=\{C,D\}$
* $\delta(C,0)=\{A,C\}, \delta(C,1)=\{A,E\}$
* $\delta(D,0)=\emptyset, \delta(D,1)=\{D,E\}$
* $\delta(E,0)=\{A,E\}, \delta(E,1)=\emptyset$

* **Resolución a mano (sólo subconjuntos alcanzables desde $S_0=\{A\}$):**

| Orden | Subconjunto $S$ | Con `0`: $\delta_D(S,0)$ | Con `1`: $\delta_D(S,1)$ | ¿Aceptación? ($S \cap \{D\} \neq \emptyset$) |
| :---: | :--- | :--- | :--- | :--- |
| 0 | $\to \{A\}$ | $\emptyset$ | $\{B,C\}$ (nuevo #1) | No ($\{A\} \cap \{D\} = \emptyset$) |
| 1 | $\{B,C\}$ | $\{A,B,D\} \cup \{A,C\} = \{A,B,C,D\}$ (nuevo #2) | $\{C,D\} \cup \{A,E\} = \{A,C,D,E\}$ (nuevo #3) | No ($\{B,C\} \cap \{D\} = \emptyset$) |
| 2 | $* \{A,B,C,D\}$ | $\{A,B,D\} \cup \{A,C\} = \{A,B,C,D\}$ | $\{B,C\} \cup \{C,D\} \cup \{A,E\} \cup \{D,E\} = \{A,B,C,D,E\}$ (nuevo #4) | **Sí** ($D \in \{A,B,C,D\}$) |
| 3 | $* \{A,C,D,E\}$ | $\{A,C\} \cup \{A,E\} = \{A,C,E\}$ (nuevo #5) | $\{B,C\} \cup \{A,E\} \cup \{D,E\} = \{A,B,C,D,E\}$ | **Sí** ($D \in \{A,C,D,E\}$) |
| 4 | $* \{A,B,C,D,E\}$ | $\{A,B,D\}\cup\{A,C\}\cup\{A,E\} = \{A,B,C,D,E\}$ | $\{B,C\}\cup\{C,D\}\cup\{A,E\}\cup\{D,E\} = \{A,B,C,D,E\}$ | **Sí** ($D \in \{A,B,C,D,E\}$) |
| 5 | $\{A,C,E\}$ | $\{A,C\} \cup \{A,E\} = \{A,C,E\}$ | $\{B,C\} \cup \{A,E\} = \{A,B,C,E\}$ (nuevo #6) | No ($\{A,C,E\} \cap \{D\} = \emptyset$) |
| 6 | $\{A,B,C,E\}$ | $\{A,B,D\}\cup\{A,C\}\cup\{A,E\} = \{A,B,C,D,E\}$ | $\{B,C\}\cup\{C,D\}\cup\{A,E\} = \{A,B,C,D,E\}$ | No ($\{A,B,C,E\} \cap \{D\} = \emptyset$) |

* **Comparación con la salida del software (`m260.construccion_subconjuntos_detallada()`):**
  El software descubre exactamente los mismos **7 subconjuntos alcanzables** (de $2^5 = 32$ posibles) en el mismo orden `#0` a `#6`, y marca exactamente a `{A,B,C,D}`, `{A,C,D,E}` y `{A,B,C,D,E}` como estados de aceptación con la razón `{...} ∩ F = {D} ≠ ∅`.

### 3.4. Estimación del número de pasos en función de $n = |Q|$ y $m = |\Sigma|$
* Sea $|Q_D| \le 2^n$ el número de subconjuntos alcanzables desde $S_0$.
* Para cada uno de los $|Q_D|$ subconjuntos alcanzables y cada uno de los $m$ símbolos de $\Sigma$:
  * Se unen los conjuntos $\delta(q,a)$ de los $|S| \le n$ elementos del subconjunto, tomando $\mathcal{O}(n^2)$ operaciones (o $\mathcal{O}(n^2)$ adicionales si hay $\lambda$-clausura).
* **Complejidad parametrizada por subconjuntos alcanzables:** **$\mathcal{O}(|Q_D| \cdot m \cdot n^2)$ pasos**.
* **Cota en el peor caso (cuando $|Q_D| = 2^n$):** **$\mathcal{O}(2^n \cdot m \cdot n^2)$ pasos**.

---

## Algoritmo 4 (Sección 2.4): Minimización de AFD y Equivalencia de dos AFD

### 4.1. Enunciado del problema y resultado teórico que lo respalda
* **Problema que resuelve:** Dado un AFD $M = (Q, \Sigma, \delta, q_0, F)$, eliminar primero todos los estados inaccesibles desde $q_0$, construir el AFD mínimo equivalente $M_{\min}$ tanto por refinamiento de particiones como por la tabla de pares distinguibles mostrando cada ronda, y decidir si dos AFD $M_1, M_2$ reconocen el mismo lenguaje comparando si sus AFD mínimos son isomorfos.
* **Resultado teórico y referencia bibliográfica exacta:**
  * **Hopcroft, Motwani y Ullman (2007)**, **Capítulo 4, Sección 4.4.1 «Equivalencia de estados» (p. 155), Sección 4.4.2 «Prueba de la equivalencia de estados y de autómatas» (Teorema 4.8, pp. 156–161) y Sección 4.4.3 «Minimización de AFD» (Teorema 4.26, pp. 163–168)**:
    1. Dos estados $p, q$ son distinguibles si existe $w \in \Sigma^*$ tal que $\hat{\delta}(p,w) \in F \iff \hat{\delta}(q,w) \notin F$. El algoritmo de llenado de tabla marca exactamente los pares distinguibles en a lo sumo $n-1$ rondas (Teorema 4.8).
    2. El cociente del AFD accesible respecto a la relación de indistinguibilidad $\equiv$ produce el **único AFD de número mínimo de estados** salvo isomorfismo (renombramiento de estados, Teorema 4.26 / Teorema de Myhill-Nerode).
    3. Por consiguiente, dos AFD $M_1$ y $M_2$ sobre $\Sigma$ son equivalentes ($L(M_1)=L(M_2)$) si y sólo si sus autómatas mínimos son isomorfos.
  * **Linz (2017)**, **Capítulo 2, Sección 2.4 «Reduction of the Number of States in Finite Automata», Teorema 2.4 (pp. 62–69)** y **Hopcroft (1971, pp. 189–196)**: Algoritmo de refinamiento de particiones $\Pi_0, \Pi_1, \dots, \Pi_k$.

### 4.2. Pseudocódigo y correspondencia con [`src/automata.py`](../../src/automata.py)

```text
ALGORITMO 4A: MINIMIZAR_AFD(M)
Entrada: AFD M = (Q, Σ, δ, q0, F)
Salida: AFD mínimo M_min, rondas de partición Π_k y rondas de tabla de pares
1. // Fase 1: Eliminar estados inaccesibles mediante BFS desde q0
2. Q_acc ← BFS_ALCANZABLES(M, q0)
3. Restringir M a Q_acc (y completar con estado pozo si δ es parcial)
4. // Fase 2A: Refinamiento de particiones (Moore)
5. Π_0 ← { Q_acc \ F, F } (omitiendo conjuntos vacíos); k ← 0
6. REPETIR:
7.     k ← k + 1; Π_k ← ∅
8.     PARA CADA grupo G ∈ Π_{k-1} HACER:
9.         Particionar G en subgrupos según la tupla de bloques (bloque(δ(q,a)) : a ∈ Σ)
10.        Agregar los subgrupos a Π_k
11. HASTA QUE |Π_k| = |Π_{k-1}|
12. // Fase 2B: Tabla de pares distinguibles
13. Para todo par {p, q}: marcar en Ronda 0 si (p ∈ F) ≠ (q ∈ F)
14. r ← 1
15. MIENTRAS se marque algún par nuevo HACER:
16.     Para cada par {p, q} no marcado:
17.         SI existe a ∈ Σ tal que {δ(p,a), δ(q,a)} está marcado ENTONCES:
18.             Marcar {p, q} en Ronda r
19.     r ← r + 1
20. Construir M_min tomando cada clase C ∈ Π_k como un estado, C_0 ∋ q0, F_min = {C | C ⊆ F}
21. DEVOLVER M_min, rondas_Π, rondas_tabla

ALGORITMO 4B: SON_AFD_EQUIVALENTES(M_1, M_2)
1. A_1 ← MINIMIZAR_AFD(M_1).afd_minimo; A_2 ← MINIMIZAR_AFD(M_2).afd_minimo
2. Recorrer en anchura (BFS) simultáneamente (q0_1, q0_2) con biyección φ(q0_1) = q0_2:
3.     Si en algún par (u_1, u_2) difiere la pertenencia a F o la existencia de transición con 'a',
       devolver FALSO con la cadena testigo w.
       Si φ(u_1) ya estaba asignado a otro estado distinto de u_2, devolver FALSO.
4. DEVOLVER VERDADERO y la biyección φ entre los estados de A_1 y A_2.
```

| Bloque del pseudocódigo | Función / Método en [`src/automata.py`](../../src/automata.py) | Líneas en código |
| :--- | :--- | :--- |
| Eliminación de estados inaccesibles | [`obtener_estados_accesibles`](../../src/automata.py#L559-L574) y [`eliminar_estados_inaccesibles`](../../src/automata.py#L576-L594) | Líneas 559–594 |
| Refinamiento de particiones y tabla de pares | [`AutomataFinito.minimizar_afd_detallado`](../../src/automata.py#L642-L865) | Líneas 642–865 |
| Equivalencia de dos AFD por isomorfismo | [`AutomataFinito.son_afd_equivalentes`](../../src/automata.py#L871-L978) | Líneas 871–978 |

### 4.3. Ejemplo de la Lista 3 resuelto a mano vs. Software (Ejercicio 154, `ej154_minimizacion.jff`)
Sea el AFD del **Ejercicio 154** ($Q=\{A,B,C,D,E,F,G,H,I,J,K\}$, $\Sigma=\{0,1\}$, $q_0=A$, $F=\{E,G,H,J\}$):
* **Resolución a mano:**
  1. **Eliminación de estados inaccesibles:**
     Recorriendo desde $A$: $A \to \{D,K\} \to \{C,G,F\} \to \{I,E,B\} \to \{H\}$. Ninguna transición desde $\{A,B,C,D,E,F,G,H,I,K\}$ llega al estado **`J`**. Por tanto, **`J` es inaccesible** y se elimina. Quedan 10 estados accesibles con $F_{\text{acc}} = \{E, G, H\}$.
  2. **Refinamiento de particiones ronda por ronda:**
     * **Ronda $\Pi_0$:** Separación inicial entre $Q_{\text{acc}} \setminus F$ y $F_{\text{acc}}$:
       $$\Pi_0 = \big\{\underbrace{\{A, B, C, D, F, I, K\}}_{G_0}, \underbrace{\{E, G, H\}}_{G_1}\big\}$$
     * **Ronda $\Pi_1$:** Evaluamos a qué bloque de $\Pi_0$ van con `0` y con `1`:
       * En $G_0$: $C \xrightarrow{1} E \in G_1$ y $F \xrightarrow{1} E \in G_1$ (firma $(G_0, G_1)$); mientras que $D \xrightarrow{1} G \in G_1$ (también firma $(G_0, G_1)$); y $A, B, I, K$ van con `1` a $G_0$, salvo $B \xrightarrow{0} H \in G_1$ e $I \xrightarrow{0} G \in G_1$ (firma $(G_1, G_0)$), mientras $A, K$ tienen firma $(G_0, G_0)$.
         * $G_0$ se divide en $\{A, K\}$ (firma $(G_0,G_0)$), $\{D, C, F\}$ (firma $(G_0,G_1)$) y $\{B, I\}$ (firma $(G_1,G_0)$).
       * En $G_1 = \{E, G, H\}$: todos van a $G_0$ con `0` y `1` ($\delta(E)=(K,I), \delta(G)=(C,I), \delta(H)=(C,B)$), por lo que en $\Pi_1$ permanecen juntos:
       $$\Pi_1 = \big\{\{A, K\}, \{B, I\}, \{C, D, F\}, \{E, G, H\}\big\}$$
     * **Ronda $\Pi_2$:**
       * En $\{A, K\}$: $A \xrightarrow{0} D \in \{C,D,F\}$, $K \xrightarrow{0} C \in \{C,D,F\}$, pero $A \xrightarrow{1} K \in \{A,K\}$ mientras $K \xrightarrow{1} F \in \{C,D,F\}$. Se separan en $\{A\}$ y $\{K\}$.
       * En $\{B, I\}$: $B \to (H \in \{E,G,H\}, K \in \{A,K\})$ e $I \to (G \in \{E,G,H\}, K \in \{A,K\})$. ¡Tienen la misma firma! Permanecen juntos $\{B, I\}$.
       * En $\{C, D, F\}$: $C \to (I \in \{B,I\}, E \in \{E,G,H\})$ y $F \to (B \in \{B,I\}, E \in \{E,G,H\})$ tienen la misma firma, pero $D \to (C \in \{C,D,F\}, G \in \{E,G,H\})$. Se divide en $\{C, F\}$ y $\{D\}$.
       * En $\{E, G, H\}$: $E \to (K \in \{A,K\}, I \in \{B,I\})$ mientras $G \to (C \in \{C,D,F\}, I \in \{B,I\})$ y $H \to (C \in \{C,D,F\}, B \in \{B,I\})$. Se divide en $\{E\}$ y $\{G, H\}$.
       $$\Pi_2 = \big\{\{A\}, \{K\}, \{B, I\}, \{C, F\}, \{D\}, \{E\}, \{G, H\}\big\}$$
     * **Ronda $\Pi_3$:**
       * En $\{B, I\}$: $B \to (H \in \{G,H\}, K \in \{K\})$ e $I \to (G \in \{G,H\}, K \in \{K\}) \implies$ siguen juntos.
       * En $\{C, F\}$: $C \to (I \in \{B,I\}, E \in \{E\})$ y $F \to (B \in \{B,I\}, E \in \{E\}) \implies$ siguen juntos.
       * En $\{G, H\}$: $G \to (C \in \{C,F\}, I \in \{B,I\})$ y $H \to (C \in \{C,F\}, B \in \{B,I\}) \implies$ siguen juntos.
       * $\Pi_3 = \Pi_2$ (estabilización en **7 clases de equivalencia**).
* **Salida del software (`m154.minimizar_afd_detallado()`) y comparación:**
  * `estados_inaccesibles_eliminados`: `['J']`
  * `clases_equivalencia`: `[['A'], ['B', 'I'], ['C', 'F'], ['D'], ['E'], ['G', 'H'], ['K']]`
  * `pares_equivalentes`: `[('B', 'I'), ('C', 'F'), ('G', 'H')]`
  * **Comparación:** Los estados inaccesibles (`J`), las rondas de partición y las 7 clases de equivalencia finales coinciden al 100 % entre el cálculo manual y el software.

### 4.4. Estimación del número de pasos en función de $n = |Q|$ y $m = |\Sigma|$
1. **Eliminación de estados inaccesibles (BFS):** visita a lo sumo $n$ estados y recorre $m$ aristas salientes por estado: **$\mathcal{O}(n + m \cdot n) = \mathcal{O}(m \cdot n)$ pasos**.
2. **Refinamiento de particiones (Moore):** como cada ronda que no termina divide al menos un grupo y a lo sumo hay $n$ grupos posibles, se ejecutan a lo sumo $n$ rondas. En cada ronda se calcula la firma de $m$ transiciones para los $n$ estados ($\mathcal{O}(m \cdot n)$): **$\mathcal{O}(m \cdot n^2)$ pasos**.
3. **Tabla de pares distinguibles:** existen $\binom{n}{2} = \frac{n(n-1)}{2} = \mathcal{O}(n^2)$ pares de estados. En cada ronda se inspeccionan los pares aún no marcados en $m$ símbolos ($\mathcal{O}(m \cdot n^2)$ por ronda), y como en cada ronda activa se marca al menos un par (o a lo sumo $n-1$ rondas por la cota de longitud de cadena distinguible), toma **$\mathcal{O}(m \cdot n^3)$ pasos** en el peor caso (y $\mathcal{O}(m \cdot n^2)$ cuando termina en un número acotado de rondas).
4. **Decisión de equivalencia de dos AFD ya minimizados:** el recorrido BFS simultáneo visita a lo sumo $n$ pares de estados y verifica $m$ transiciones por estado: **$\mathcal{O}(m \cdot n)$ pasos**.

---

## Algoritmo 5 (Sección 2.5): Validación de Lote de Cadenas desde Archivo (`.txt`)

* **Problema que resuelve:** Dado un archivo de texto con $N$ líneas (una cadena $w_i$ por línea) y un autómata finito $M$, determinar la aceptación de cada $w_i$ y generar un archivo de informe estructurado.
* **Correspondencia en código:** [`AutomataFinito.validar_archivo_cadenas`](../../src/automata.py#L984-L1044) (líneas 984–1044 de `src/automata.py`).
* **Estimación del número de pasos:** Para un lote de $N$ cadenas de longitud media $\bar{L}$, invoca la simulación directa en cada línea, requiriendo **$\mathcal{O}(N \cdot \bar{L} \cdot n^2)$ pasos** en un AFN/AFN-$\lambda$ (y **$\mathcal{O}(N \cdot \bar{L})$ pasos** en un AFD).
