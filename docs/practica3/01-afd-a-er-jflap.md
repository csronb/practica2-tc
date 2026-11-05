# Ejercicio 1. Conversión de AFD a Expresiones Regulares

En este documento se desarrolla el **Ejercicio 1** de la Práctica 3: la conversión de cinco Autómatas Finitos Deterministas (AFD) de las Listas 2 y 3 a expresiones regulares mediante **JFLAP 7.1** (*Convert FA to RE*), su verificación formal con *Convert to NFA* y *Compare Equivalence*, la simplificación algebraica paso a paso justificada con las leyes de **Hopcroft, Motwani y Ullman (2007, Sección 3.4)**, y la comparación detallada de los **tres métodos de conversión** (eliminación de estados, construcción inductiva $R_{ij}^{(k)}$ y sistema de ecuaciones con el Lema de Arden) aplicados a mano y contrastados con el módulo [`src/expresiones.py`](../../src/expresiones.py).

Los cinco archivos `.jff` y sus archivos de expresión regular se encuentran en [`automatas/practica3/afd-a-er/`](../../automatas/practica3/afd-a-er/).

![Evidencia JFLAP Ejercicio 1](../../evidencias/practica3/01_jflap_afd_a_er_y_equivalencia.svg)

---

## Tabla de Leyes Algebraicas de las Expresiones Regulares (Bibliografía Oficial)

Todas las simplificaciones algebraicas de las Secciones 1.1 y 1.2 se fundamentan exclusivamente en las fuentes admitidas en la Práctica 2, específicamente en **Hopcroft, Motwani y Ullman (2007, *Introducción a la teoría de autómatas, lenguajes y computación*, 3.ª ed., Capítulo 3, Sección 3.4 «Leyes algebraicas para las expresiones regulares», pp. 117–121)** y **Linz (2017, *An Introduction to Formal Languages and Automata*, 6.ª ed., Sección 3.1, pp. 75–82)**:

| Código | Ley algebraica | Ecuación formal | Referencia bibliográfica exacta |
| :--- | :--- | :--- | :--- |
| **L1** | Conmutatividad de la unión | $L + M = M + L$ | Hopcroft et al. (2007), Sección 3.4.1, p. 118 |
| **L2** | Asociatividad de la unión | $(L + M) + N = L + (M + N)$ | Hopcroft et al. (2007), Sección 3.4.1, p. 118 |
| **L3** | Asociatividad de la concatenación | $(LM)N = L(MN)$ | Hopcroft et al. (2007), Sección 3.4.1, p. 118 |
| **L4** | Identidad de la unión | $L + \emptyset = \emptyset + L = L$ | Hopcroft et al. (2007), Sección 3.4.2, p. 119 |
| **L5** | Identidad de la concatenación | $\lambda L = L \lambda = L$ | Hopcroft et al. (2007), Sección 3.4.2, p. 119 |
| **L6** | Aniquilador de la concatenación | $\emptyset L = L \emptyset = \emptyset$ | Hopcroft et al. (2007), Sección 3.4.2, p. 119 |
| **L7** | Idempotencia de la unión | $L + L = L$ | Hopcroft et al. (2007), Sección 3.4.2, p. 119 |
| **L8** | Distributividad izquierda | $L(M + N) = LM + LN$ | Hopcroft et al. (2007), Sección 3.4.3, p. 119 |
| **L9** | Distributividad derecha | $(M + N)L = ML + NL$ | Hopcroft et al. (2007), Sección 3.4.3, p. 119 |
| **L10** | Clausura del vacío y de $\lambda$ | $\emptyset^* = \lambda, \quad \lambda^* = \lambda$ | Hopcroft et al. (2007), Sección 3.4.4, p. 120 |
| **L11** | Expansión de Kleene | $L^* = \lambda + LL^* = \lambda + L^*L$ | Hopcroft et al. (2007), Sección 3.4.4, p. 120 |
| **L12** | Absorción de $\lambda$ en clausura | $(\lambda + L)^* = L^*$ | Hopcroft et al. (2007), Sección 3.4.4, p. 120 |
| **L13** | Regla de deslizamiento / denesting | $(L^*M)^*L^* = (L + M)^*$ y $L^*(ML^*)^* = (L + M)^*$ | Linz (2017), Sección 3.1, Ejercicio 19; Hopcroft et al. (2007), Sección 3.4.4 |

---

## 1.1. Conversión de cinco AFD con JFLAP 7.1

### Autómata 1: Ejercicio 131 (Lista 2) / Ejercicio 254 (Lista 3) — [`ej254_termina_en_1.jff`](../../automatas/practica3/afd-a-er/ej254_termina_en_1.jff)

* **Definición formal:** $M_{254} = (\{A, B\}, \{0, 1\}, \delta, A, \{B\})$, con $\delta(A,0)=A$, $\delta(A,1)=B$, $\delta(B,0)=A$, $\delta(B,1)=B$.

#### a) Análisis estructural previo (ciclos y ramas)
* **Ciclo inicial en $A$:** El bucle $A \xrightarrow{0} A$ genera el prefijo iterativo $0^*$ mientras no aparezca el primer `1`.
* **Rama de avance $A \to B$:** La transición $A \xrightarrow{1} B$ lleva al único estado de aceptación $B$ al leer un `1`.
* **Ciclos de retorno a $B$:** Estando en $B$, el autómata puede permanecer en $B$ leyendo `1` (lazo directo $B \xrightarrow{1} B$) o regresar a $A$ con `0`, ciclar en $0^*$ y volver a $B$ con `1` (camino $B \xrightarrow{0} A \xrightarrow{0^*} A \xrightarrow{1} B$, es decir, $00^*1$). Por tanto, se anticipa una expresión con estructura $0^*1(1 + 00^*1)^*$, equivalente al lenguaje de todas las cadenas binarias que terminan en `1`: $(0+1)^*1$.

#### b) Eliminación de estados en JFLAP (`Convert FA to RE`)
1. **Estado inicial generalizado (GNFA):** JFLAP añade transiciones $\lambda$ si es necesario y evalúa los pares de estados con expresiones regulares en las aristas:
   * $R(A,A) = 0$, $R(A,B) = 1$, $R(B,A) = 0$, $R(B,B) = 1$.
2. **Eliminación del estado $A$ (conservar $B$ respecto al inicio):**
   * El lazo sobre $A$ es $R(A,A)^* = 0^*$.
   * La ruta de entrada desde el inicio hacia $B$ pasando por $A$ queda con etiqueta $R(\text{ini}, B) = \lambda \cdot 0^* \cdot 1 = 0^*1$.
   * El camino de retorno $B \to A \to B$ se fusiona con el lazo de $B$:
     $$R'(B,B) = R(B,B) + R(B,A)R(A,A)^*R(A,B) = 1 + 00^*1$$
3. **Eliminación del estado $B$ hacia el estado final del GNFA:**
   * Al concatenar la entrada $0^*1$ con la estrella del lazo en $B$, JFLAP entrega:
     $$r_{\text{JFLAP}} = 0^*1(1+00^*1)^*$$

#### c) Simplificación algebraica justificada paso a paso
$$\begin{aligned}
r_0 &= 0^*1(1 + 00^*1)^* \\
&= 0^*1(\lambda 1 + 00^*1)^* && \text{por L5 (identidad de la concatenación: } 1 = \lambda 1\text{)} \\
&= 0^*1((\lambda + 00^*)1)^* && \text{por L9 (distributividad derecha respecto a } 1\text{)} \\
&= 0^*1(0^*1)^* && \text{por L11 (expansión de Kleene: } \lambda + 00^* = 0^*\text{)} \\
&= (0^*1)^*0^*1 && \text{por asociatividad L3 / conmutación de } L(L)^* = (L)^*L \\
&= (0 + 1)^*1 && \text{por L13 (identidad de denesting } (0^*1)^*0^* = (0+1)^*\text{)}
\end{aligned}$$

#### d) Verificación de equivalencia en JFLAP y prueba de 5 cadenas
Al aplicar **Convert → Convert to NFA** sobre $0^*1(1+00^*1)^*$, seguido de **Convert → Convert to DFA** y **Test → Compare Equivalence** contra `ej254_termina_en_1.jff`, JFLAP confirma: **`They are equivalent!`**.

| # | Cadena $w$ | Traza en AFD $M_{254}$ | ¿Acepta AFD? | ¿Coincide con $0^*1(1+00^*1)^*$ y $(0+1)^*1$? |
| :---: | :---: | :--- | :---: | :---: |
| 1 | $\lambda$ | $A$ (termina en $A \notin F$) | Rechaza | Rechaza (coincide) |
| 2 | `1` | $A \xrightarrow{1} B \in F$ | Acepta | Acepta ($0^* \to \lambda$, $1$, clausura $\lambda$) |
| 3 | `001` | $A \xrightarrow{0} A \xrightarrow{0} A \xrightarrow{1} B \in F$ | Acepta | Acepta ($0^* \to 00$, $1$, clausura $\lambda$) |
| 4 | `1010` | $A \xrightarrow{1} B \xrightarrow{0} A \xrightarrow{1} B \xrightarrow{0} A \notin F$ | Rechaza | Rechaza (coincide) |
| 5 | `010011` | $A \xrightarrow{0} A \xrightarrow{1} B \xrightarrow{0} A \xrightarrow{0} A \xrightarrow{1} B \xrightarrow{1} B \in F$ | Acepta | Acepta (coincide) |

---

### Autómata 2: Ejercicio 255 (Lista 3) — [`ej255_ciclo_par_b.jff`](../../automatas/practica3/afd-a-er/ej255_ciclo_par_b.jff)

* **Definición formal:** $M_{255} = (\{A, B\}, \{0, 1\}, \delta, A, \{A\})$, con $\delta(A,0)=B$, $\delta(A,1)=B$, $\delta(B,0)=A$, $\delta(B,1)=B$.

#### a) Análisis estructural previo (ciclos y ramas)
* Como $A$ es simultáneamente el estado inicial y el único estado de aceptación ($F=\{A\}$), la cadena vacía $\lambda$ es aceptada y toda palabra aceptada corresponde a cero o más excursiones desde $A$ que regresan a $A$.
* **Rama de salida $A \to B$:** Cualquier símbolo en $A$ (`0` o `1`) envía al estado $B$, por lo que la arista combinada es $(0+1)$.
* **Ciclo interno en $B$ y retorno $B \to A$:** En $B$, el símbolo `1` cicla arbitrariamente ($1^*$) y el símbolo `0` devuelve al estado $A$. Por tanto, cada excursión completa desde $A$ hasta $A$ tiene la forma $(0+1)1^*0$, anticipando directamente la expresión $((0+1)1^*0)^*$.

#### b) Eliminación de estados en JFLAP (`Convert FA to RE`)
1. **Unificación de transiciones paralelas:** $R(A,B) = 0+1$, $R(B,B) = 1$, $R(B,A) = 0$, $R(A,A) = \emptyset$.
2. **Eliminación del estado $B$:**
   * Lazo en $B$: $R(B,B)^* = 1^*$.
   * Nuevo lazo inducido sobre $A$:
     $$R'(A,A) = R(A,A) + R(A,B)R(B,B)^*R(B,A) = \emptyset + (0+1)1^*0 = (0+1)1^*0$$
3. **Eliminación del estado $A$ (inicial y de aceptación):**
   * El lenguaje entre el nodo inicial y final del GNFA es el lazo de $A$ clausurado:
     $$r_{\text{JFLAP}} = ((0+1)1^*0)^*$$
   *(Nota: Si se elimina primero $A$ y luego $B$, como muestra [`src/expresiones.py`](../../src/expresiones.py), se obtiene la variante equivalente $\lambda + (0+1)(0(0+1)+1)^*0$).*

#### c) Simplificación algebraica justificada paso a paso
Partiendo de la expresión con eliminación de $B$ antes que $A$:
$$\begin{aligned}
r_0 &= (\emptyset + (0+1)1^*0)^* \\
&= ((0+1)1^*0)^* && \text{por L4 (identidad de la unión: } \emptyset + L = L\text{)}
\end{aligned}$$
Y verificando que la variante al eliminar primero $A$, $\lambda + (0+1)(0(0+1)+1)^*0$, es algebraicamente idéntica:
$$\begin{aligned}
\lambda + (0+1)(0(0+1)+1)^*0 &= \lambda + (0+1)(1^*0(0+1))^*1^*0 && \text{por L13 (deslizamiento } (M+L)^* = L^*(ML^*)^*\text{ con } L=1, M=0(0+1)\text{)} \\
&= \lambda + (0+1)1^*0((0+1)1^*0)^* && \text{por L3 (asociatividad y desplazamiento en estrella } (XY)^*X = X(YX)^*\text{)} \\
&= ((0+1)1^*0)^* && \text{por L11 (expansión de Kleene } \lambda + LL^* = L^*\text{)}
\end{aligned}$$

#### d) Verificación de equivalencia en JFLAP y prueba de 5 cadenas
La comparación con **Compare Equivalence** en JFLAP entre `ej255_ciclo_par_b.jff` y el autómata de $((0+1)1^*0)^*$ arroja **`They are equivalent!`**.

| # | Cadena $w$ | Traza en AFD $M_{255}$ | ¿Acepta AFD? | ¿Coincide con $((0+1)1^*0)^*$? |
| :---: | :---: | :--- | :---: | :---: |
| 1 | $\lambda$ | $A \in F$ | Acepta | Acepta (0 repeticiones de la estrella exterior) |
| 2 | `00` | $A \xrightarrow{0} B \xrightarrow{0} A \in F$ | Acepta | Acepta ($0 \cdot \lambda \cdot 0$) |
| 3 | `1110` | $A \xrightarrow{1} B \xrightarrow{1} B \xrightarrow{1} B \xrightarrow{0} A \in F$ | Acepta | Acepta ($1 \cdot 11 \cdot 0$) |
| 4 | `01` | $A \xrightarrow{0} B \xrightarrow{1} B \notin F$ | Rechaza | Rechaza (coincide) |
| 5 | `00110` | $A \xrightarrow{0} B \xrightarrow{0} A \xrightarrow{1} B \xrightarrow{1} B \xrightarrow{0} A \in F$ | Acepta | Acepta (dos bloques: `00` y `110`) |

---

### Autómata 3: Ejercicio 256 (Lista 3) — [`ej256_ternario.jff`](../../automatas/practica3/afd-a-er/ej256_ternario.jff)

* **Definición formal:** $M_{256} = (\{A, B\}, \{0, 1, 2\}, \delta, A, \{B\})$, con $\delta(A,0)=B$, $\delta(A,1)=A$, $\delta(A,2)=A$, $\delta(B,0)=B$, $\delta(B,1)=B$, $\delta(B,2)=A$.

#### a) Análisis estructural previo (ciclos y ramas)
* **Ciclo en $A$:** Los símbolos `1` y `2` mantienen al autómata en $A$, formando el bucle $(1+2)^*$.
* **Rama $A \to B$:** Sólo el símbolo `0` permite transitar de $A$ a $B$.
* **Ciclo en $B$ y retorno desde $A$:** En $B$, los símbolos `0` y `1` mantienen el estado activo en $B$, mientras que `2` devuelve a $A$, desde donde se requiere $(1+2)^*0$ para regresar a $B$. Esto anticipa la expresión $(1+2)^*0(0+1+2(1+2)^*0)^*$.

#### b) Eliminación de estados en JFLAP (`Convert FA to RE`)
1. **Aristas iniciales agrupadas:** $R(A,A) = 1+2$, $R(A,B) = 0$, $R(B,A) = 2$, $R(B,B) = 0+1$.
2. **Eliminación del estado $A$:**
   * Lazo en $A$: $R(A,A)^* = (1+2)^*$.
   * Entrada desde el inicio hacia $B$: $R'(\text{ini}, B) = (1+2)^*0$.
   * Nuevo lazo sobre $B$:
     $$R'(B,B) = R(B,B) + R(B,A)R(A,A)^*R(A,B) = (0+1) + 2(1+2)^*0 = 0+1+2(1+2)^*0$$
3. **Eliminación del estado $B$:**
   $$r_{\text{JFLAP}} = (1+2)^*0(0+1+2(1+2)^*0)^*$$

#### c) Simplificación algebraica justificada paso a paso
$$\begin{aligned}
r_0 &= \lambda(1+2)^*0((0+1) + 2(1+2)^*0)^*\lambda \\
&= (1+2)^*0((0+1) + 2(1+2)^*0)^* && \text{por L5 (identidad de la concatenación con } \lambda\text{)} \\
&= (1+2)^*0(0+1+2(1+2)^*0)^* && \text{por L2 (asociatividad de la unión)}
\end{aligned}$$
Esta forma ya es minimal en longitud de literales (9 apariciones de símbolos de $\Sigma$).

#### d) Verificación de equivalencia en JFLAP y prueba de 5 cadenas
En JFLAP, **Compare Equivalence** confirma **`They are equivalent!`**.

| # | Cadena $w$ | Traza en AFD $M_{256}$ | ¿Acepta AFD? | ¿Coincide con $(1+2)^*0(0+1+2(1+2)^*0)^*$? |
| :---: | :---: | :--- | :---: | :---: |
| 1 | `0` | $A \xrightarrow{0} B \in F$ | Acepta | Acepta (coincide) |
| 2 | `1201` | $A \xrightarrow{1} A \xrightarrow{2} A \xrightarrow{0} B \xrightarrow{1} B \in F$ | Acepta | Acepta (coincide) |
| 3 | `02` | $A \xrightarrow{0} B \xrightarrow{2} A \notin F$ | Rechaza | Rechaza (coincide) |
| 4 | `212` | $A \xrightarrow{2} A \xrightarrow{1} A \xrightarrow{2} A \notin F$ | Rechaza | Rechaza (coincide) |
| 5 | `202100` | $A \xrightarrow{2} A \xrightarrow{0} B \xrightarrow{2} A \xrightarrow{1} A \xrightarrow{0} B \xrightarrow{0} B \in F$ | Acepta | Acepta (coincide) |

---

### Autómata 4: Ejercicio 257 (Lista 3) — [`ej257_tres_estados_bc.jff`](../../automatas/practica3/afd-a-er/ej257_tres_estados_bc.jff)

* **Definición formal:** $M_{257} = (\{A, B, C\}, \{0, 1\}, \delta, A, \{B, C\})$, con $\delta(A,0)=B$, $\delta(A,1)=C$, $\delta(B,0)=C$, $\delta(B,1)=B$, $\delta(C,0)=A$, $\delta(C,1)=A$.

#### a) Análisis estructural previo (ciclos y ramas)
* **Dos ramas desde $A$ hacia $C$:** Desde $A$, el autómata puede ir directamente a $C$ con `1` ($A \xrightarrow{1} C$) o pasar por $B$ leyendo `0`, ciclar en $B$ con `1^*` y saltar a $C$ con `0` ($A \xrightarrow{0} B \xrightarrow{1^*} B \xrightarrow{0} C$, es decir, $01^*0$). Por tanto, llegar de $A$ a $C$ consume $(1 + 01^*0)$.
* **Ciclo global $A \to C \to A$:** Desde $C$, cualquier símbolo $(0+1)$ regresa a $A$. Así, el ciclo fundamental alrededor de $A$ es $((1 + 01^*0)(0+1))^*$.
* **Aceptación en $F=\{B, C\}$:** Tras repetir el ciclo en $A$, la cadena es aceptada si termina en $B$ (leyendo $01^*$) o en $C$ (leyendo $1 + 01^*0$).

#### b) Eliminación de estados en JFLAP (`Convert FA to RE`)
1. **GNFA inicial:** Se conectan $B \xrightarrow{\lambda} \text{fin}$ y $C \xrightarrow{\lambda} \text{fin}$ porque $F=\{B,C\}$.
2. **Eliminación del estado $B$:**
   * Lazo en $B$: $R(B,B)^* = 1^*$.
   * La transición $A \to B \to C$ se suma a $R(A,C)=1$:
     $$R'(A,C) = 1 + 01^*0$$
   * La transición $A \to B \to \text{fin}$ produce:
     $$R'(A, \text{fin}) = 01^*\lambda = 01^*$$
3. **Eliminación del estado $C$:**
   * $C$ no tiene lazo propio ($R(C,C)=\emptyset \implies \emptyset^* = \lambda$).
   * El camino $A \to C \to A$ induce un lazo sobre $A$:
     $$R'(A,A) = (1 + 01^*0)(0+1)$$
   * El camino $A \to C \to \text{fin}$ se une con $R'(A, \text{fin})$:
     $$R''(A, \text{fin}) = 01^* + (1 + 01^*0)\lambda = 01^* + 1 + 01^*0$$
4. **Eliminación del estado $A$:**
   * Al clausurar el lazo $R'(A,A)$, JFLAP obtiene:
     $$r_{\text{JFLAP}} = ((1+01^*0)(0+1))^*01^* + ((1+01^*0)(0+1))^*(1+01^*0)$$

#### c) Simplificación algebraica justificada paso a paso
$$\begin{aligned}
r_0 &= ((1+01^*0)(0+1))^*01^* + ((1+01^*0)(0+1))^*(1+01^*0) \\
&= ((1+01^*0)(0+1))^*(01^* + 1 + 01^*0) && \text{por L8 (distributividad izquierda de } ((1+01^*0)(0+1))^*\text{)} \\
&= ((1+01^*0)(0+1))^*(01^*(\lambda + 0) + 1) && \text{por L5 y L8 (factorizando } 01^*\text{ en } 01^*\lambda + 01^*0\text{)}
\end{aligned}$$

#### d) Verificación de equivalencia en JFLAP y prueba de 5 cadenas
La verificación en JFLAP mediante **Compare Equivalence** arroja **`They are equivalent!`**.

| # | Cadena $w$ | Traza en AFD $M_{257}$ | ¿Acepta AFD? | ¿Coincide con la ER? |
| :---: | :---: | :--- | :---: | :---: |
| 1 | $\lambda$ | $A \notin F$ | Rechaza | Rechaza (coincide) |
| 2 | `0` | $A \xrightarrow{0} B \in F$ | Acepta | Acepta ($01^*$ con 0 repeticiones de `1`) |
| 3 | `0110` | $A \xrightarrow{0} B \xrightarrow{1} B \xrightarrow{1} B \xrightarrow{0} C \in F$ | Acepta | Acepta (rama $01^*0$) |
| 4 | `10` | $A \xrightarrow{1} C \xrightarrow{0} A \notin F$ | Rechaza | Rechaza (regresa a $A$) |
| 5 | `1001` | $A \xrightarrow{1} C \xrightarrow{0} A \xrightarrow{0} B \xrightarrow{1} B \in F$ | Acepta | Acepta (un ciclo $1\cdot 0$ y sufijo $01$) |

---

### Autómata 5: Ejercicio 258 (Lista 3) — [`ej258_tres_estados_c.jff`](../../automatas/practica3/afd-a-er/ej258_tres_estados_c.jff)

* **Definición formal:** $M_{258} = (\{A, B, C\}, \{0, 1\}, \delta, A, \{C\})$, con $\delta(A,0)=C$, $\delta(A,1)=C$, $\delta(B,0)=A$, $\delta(B,1)=C$, $\delta(C,0)=B$, $\delta(C,1)=A$.

#### a) Análisis estructural previo (ciclos y ramas)
* **Avance inicial $A \to C$:** Desde el estado inicial $A$, tanto `0` como `1` llevan directamente al único estado de aceptación $C$. Así, toda palabra aceptada comienza con el factor $(0+1)$ que coloca al autómata en $C$.
* **Tres ciclos de retorno desde $C$ hacia $C$:** Una vez en $C$, existen tres rutas elementales para volver a $C$:
  1. $C \xrightarrow{0} B \xrightarrow{1} C$: etiqueta `01`.
  2. $C \xrightarrow{1} A \xrightarrow{0+1} C$: etiqueta $1(0+1)$.
  3. $C \xrightarrow{0} B \xrightarrow{0} A \xrightarrow{0+1} C$: etiqueta $00(0+1)$.
* Agrupando las dos rutas que pasan por $A$, se obtiene $(1+00)(0+1)$, por lo que el ciclo general en $C$ es $(01 + (1+00)(0+1))^*$.

#### b) Eliminación de estados en JFLAP (`Convert FA to RE`)
1. **Unificación inicial:** $R(A,C) = 0+1$, $R(B,A) = 0$, $R(B,C) = 1$, $R(C,B) = 0$, $R(C,A) = 1$.
2. **Eliminación del estado $B$:**
   * $B$ no tiene lazo ($R(B,B) = \emptyset \implies \emptyset^* = \lambda$).
   * El camino $C \to B \to A$ se une a $R(C,A)=1$:
     $$R'(C,A) = 1 + 0\lambda 0 = 1 + 00$$
   * El camino $C \to B \to C$ crea un lazo en $C$:
     $$R'(C,C) = 0\lambda 1 = 01$$
3. **Eliminación del estado $A$:**
   * $A$ no tiene lazo ($R(A,A) = \emptyset$).
   * Entrada desde el inicio hacia $C$: $R'(\text{ini}, C) = \lambda \cdot \lambda \cdot (0+1) = 0+1$.
   * El ciclo $C \to A \to C$ se suma al lazo de $C$:
     $$R''(C,C) = R'(C,C) + R'(C,A)R(A,A)^*R(A,C) = 01 + (1+00)(0+1)$$
4. **Eliminación del estado $C$:**
   $$r_{\text{JFLAP}} = (0+1)(01+(1+00)(0+1))^*$$

#### c) Simplificación algebraica justificada paso a paso
$$\begin{aligned}
r_0 &= (0+1)(01 + (1+00)(0+1))^* \\
&= (0+1)(01 + 1(0+1) + 00(0+1))^* && \text{por L9 (distributividad derecha sobre } 1+00\text{)} \\
&= (0+1)(0(1 + 0(0+1)) + 1(0+1))^* && \text{por L8 y L1 (factorizando } 0\text{ por la izquierda)}
\end{aligned}$$
Ambas formas, $(0+1)(01+(1+00)(0+1))^*$ y $(0+1)(0(0(0+1)+1)+1(0+1))^*$, tienen longitud mínima de literales y describen de forma transparente los ciclos desde $C$.

#### d) Verificación de equivalencia en JFLAP y prueba de 5 cadenas
En JFLAP, **Compare Equivalence** confirma **`They are equivalent!`**.

| # | Cadena $w$ | Traza en AFD $M_{258}$ | ¿Acepta AFD? | ¿Coincide con $(0+1)(01+(1+00)(0+1))^*$? |
| :---: | :---: | :--- | :---: | :---: |
| 1 | `0` | $A \xrightarrow{0} C \in F$ | Acepta | Acepta (prefijo `0`, 0 ciclos) |
| 2 | `101` | $A \xrightarrow{1} C \xrightarrow{0} B \xrightarrow{1} C \in F$ | Acepta | Acepta (prefijo `1`, ciclo `01`) |
| 3 | `0001` | $A \xrightarrow{0} C \xrightarrow{0} B \xrightarrow{0} A \xrightarrow{1} C \in F$ | Acepta | Acepta (prefijo `0`, ciclo `001`) |
| 4 | `10` | $A \xrightarrow{1} C \xrightarrow{0} B \notin F$ | Rechaza | Rechaza (coincide) |
| 5 | `11` | $A \xrightarrow{1} C \xrightarrow{1} A \notin F$ | Rechaza | Rechaza (coincide) |

---

## 1.2. Comparación de los Tres Métodos de Conversión a Mano

Seleccionamos dos autómatas de distinta complejidad estructural —el **Autómata 1 (`ej254_termina_en_1.jff`, de 2 estados)** y el **Autómata 5 (`ej258_tres_estados_c.jff`, de 3 estados con ciclos entrelazados)**— y obtenemos a mano su expresión regular mediante los tres métodos del curso:

1. **Método 1: Eliminación de estados (GNFA)** — Sustentado en **Hopcroft, Motwani y Ullman (2007, Capítulo 3, Sección 3.2.2 «Conversión de autómatas finitos deterministas en expresiones regulares mediante la eliminación de estados», pp. 103–108)** y **Sipser (2012, Sección 1.3, Lema 1.60, pp. 66–76)**.
2. **Método 2: Construcción inductiva de las expresiones $R_{ij}^{(k)}$** — Sustentado en **Hopcroft, Motwani y Ullman (2007, Capítulo 3, Sección 3.2.1 «De autómatas finitos deterministas a expresiones regulares», Teorema 3.4, pp. 98–103)** y el artículo original de **Kleene (1956, pp. 3–41)**:
   $$R_{ij}^{(0)} = \begin{cases} \{a \in \Sigma \mid \delta(q_i,a)=q_j\} & \text{si } i \neq j \\ \lambda + \{a \in \Sigma \mid \delta(q_i,a)=q_i\} & \text{si } i = j \end{cases}, \qquad R_{ij}^{(k)} = R_{ij}^{(k-1)} + R_{ik}^{(k-1)}\left(R_{kk}^{(k-1)}\right)^* R_{kj}^{(k-1)}$$
3. **Método 3: Sistema de ecuaciones lineales por la derecha y Lema de Arden** — Sustentado en el apunte del curso y en **Linz (2017, Capítulo 3, Sección 3.2, pp. 82–90)** / **Brookshear (1993, Capítulo 1)**: si $X = A X + B$ y $\lambda \notin L(A)$, entonces $X = A^* B$ es la solución única.

---

### Caso A: Desarrollo completo por los tres métodos para $M_{254}$ (`ej254_termina_en_1.jff`)

Recordemos la tabla de transición de $M_{254}$ ($q_1 = A$ inicial, $q_2 = B$ de aceptación):
* $\delta(A,0)=A$, $\delta(A,1)=B$
* $\delta(B,0)=A$, $\delta(B,1)=B$

#### Método 1: Eliminación de estados (a mano)
1. **Construcción del GNFA:** Se agregan $\vdash_{\text{ini}} \xrightarrow{\lambda} A$ y $B \xrightarrow{\lambda} \dashv_{\text{fin}}$.
   * Aristas: $R(A,A)=0$, $R(A,B)=1$, $R(B,A)=0$, $R(B,B)=1$.
2. **Paso 1 — Eliminar el estado $A$:**
   * Lazo sobre $A$: $R(A,A)^* = 0^*$.
   * Nueva arista $\vdash_{\text{ini}} \to B$: $R'(\vdash_{\text{ini}}, B) = \lambda \cdot 0^* \cdot 1 = 0^*1$.
   * Nuevo lazo sobre $B$: $R'(B,B) = R(B,B) + R(B,A)R(A,A)^*R(A,B) = 1 + 00^*1$.
3. **Paso 2 — Eliminar el estado $B$:**
   * Lazo sobre $B$: $R'(B,B)^* = (1 + 00^*1)^*$.
   * Arista final $\vdash_{\text{ini}} \to \dashv_{\text{fin}}$:
     $$r_{\text{elim}} = 0^*1(1 + 00^*1)^* \equiv (0+1)^*1$$

#### Método 2: Construcción de las expresiones $R_{ij}^{(k)}$ (a mano)
Numeramos los estados como $1 = A$ y $2 = B$. Como $F = \{B\} = \{2\}$ e inicial es $1$, el lenguaje es $L(M_{254}) = R_{12}^{(2)}$.

* **Base ($k = 0$):**
  $$\begin{aligned}
  R_{11}^{(0)} &= \lambda + 0, & R_{12}^{(0)} &= 1, \\
  R_{21}^{(0)} &= 0, & R_{22}^{(0)} &= \lambda + 1.
  \end{aligned}$$

* **Paso inductivo $k = 1$ (permitiendo a $1=A$ como estado intermedio, con $(R_{11}^{(0)})^* = (\lambda+0)^* = 0^*$ por L12):**
  $$\begin{aligned}
  R_{11}^{(1)} &= R_{11}^{(0)} + R_{11}^{(0)}(R_{11}^{(0)})^*R_{11}^{(0)} = (\lambda+0) + (\lambda+0)0^*(\lambda+0) = 0^* && \text{(por L11 y L12)} \\
  R_{12}^{(1)} &= R_{12}^{(0)} + R_{11}^{(0)}(R_{11}^{(0)})^*R_{12}^{(0)} = 1 + (\lambda+0)0^*1 = 0^*1 && \text{(por L11: } \lambda + 0^*1 = 0^*1\text{)} \\
  R_{21}^{(1)} &= R_{21}^{(0)} + R_{21}^{(0)}(R_{11}^{(0)})^*R_{11}^{(0)} = 0 + 00^*(\lambda+0) = 00^* && \text{(por L11)} \\
  R_{22}^{(1)} &= R_{22}^{(0)} + R_{21}^{(0)}(R_{11}^{(0)})^*R_{12}^{(0)} = \lambda + 1 + 00^*1.
  \end{aligned}$$
  *(Nota: Sin simplificar en $k=1$, como registra [`src/expresiones.py`](../../src/expresiones.py), quedan $R_{12}^{(1)} = (\lambda+0)0^*1+1$ y $R_{22}^{(1)} = \lambda+00^*1+1$).*

* **Paso inductivo $k = 2$ (permitiendo a $2=B$ como estado intermedio, con $(R_{22}^{(1)})^* = (\lambda + 1 + 00^*1)^* = (1 + 00^*1)^*$ por L12):**
  $$\begin{aligned}
  R_{12}^{(2)} &= R_{12}^{(1)} + R_{12}^{(1)}\left(R_{22}^{(1)}\right)^* R_{22}^{(1)} \\
  &= ((\lambda+0)0^*1+1)(00^*1+1)^*(\lambda+00^*1+1) + (\lambda+0)0^*1+1 && \text{(forma cruda de } R_{12}^{(2)}\text{)} \\
  &= 0^*1\left(\lambda + (1+00^*1)^*(\lambda + 1 + 00^*1)\right) && \text{(aplicando } R_{12}^{(1)}=0^*1 \text{ y L8)} \\
  &= 0^*1(1+00^*1)^* \equiv (0+1)^*1 && \text{(por L11 y L13).}
  \end{aligned}$$

#### Método 3: Sistema de ecuaciones y Lema de Arden (a mano)
Asociamos a cada estado una incógnita que representa el lenguaje aceptado partiendo de dicho estado ($X_A, X_B$). Como $B \in F$, su ecuación incluye $\lambda$:
$$\begin{cases}
X_A = 0 X_A + 1 X_B & (1) \\
X_B = 0 X_A + 1 X_B + \lambda & (2)
\end{cases}$$

1. **Aplicamos el Lema de Arden a la ecuación (2) para despejar $X_B$:**
   Reescribimos (2) como $X_B = 1 X_B + (0 X_A + \lambda)$. Puesto que $\lambda \notin L(1)$, el Lema de Arden garantiza:
   $$X_B = 1^*(0 X_A + \lambda) = 1^*0 X_A + 1^* \qquad (3)$$
2. **Sustituimos (3) en la ecuación (1):**
   $$X_A = 0 X_A + 1(1^*0 X_A + 1^*) = (0 + 11^*0) X_A + 11^* \qquad (4)$$
3. **Aplicamos el Lema de Arden a (4) para despejar $X_A$:**
   Como $\lambda \notin L(0 + 11^*0)$, obtenemos la solución para el estado inicial $X_A$:
   $$X_A = (0 + 11^*0)^* 11^*$$
   *(Y aplicando L13 con $L=1, M=0$: $(0+1^*10)^*11^* = (1^*(0)1^*)^* \dots \equiv (0+1)^*1$).*

---

### Caso B: Desarrollo completo por los tres métodos para $M_{258}$ (`ej258_tres_estados_c.jff`)

Recordemos la tabla de transición de $M_{258}$ ($q_1 = A$ inicial, $q_2 = B$, $q_3 = C$ único estado de aceptación):
* $\delta(A,0)=C$, $\delta(A,1)=C \implies R(A,C) = 0+1$
* $\delta(B,0)=A$, $\delta(B,1)=C$
* $\delta(C,0)=B$, $\delta(C,1)=A$

#### Método 1: Eliminación de estados (a mano)
1. **GNFA inicial:** $\vdash_{\text{ini}} \xrightarrow{\lambda} A$ y $C \xrightarrow{\lambda} \dashv_{\text{fin}}$.
2. **Paso 1 — Eliminar el estado $A$ ($R(A,A)=\emptyset \implies R(A,A)^*=\lambda$):**
   * Arista $\vdash_{\text{ini}} \to C$: $R'(\vdash_{\text{ini}}, C) = \lambda \cdot \lambda \cdot (0+1) = 0+1$.
   * Arista $B \to C$ pasando por $A$: $R'(B,C) = R(B,C) + R(B,A)\lambda R(A,C) = 1 + 0(0+1)$.
   * Lazo en $C$ pasando por $A$: $R'(C,C) = \emptyset + R(C,A)\lambda R(A,C) = 1(0+1)$.
3. **Paso 2 — Eliminar el estado $B$ ($R'(B,B)=\emptyset \implies R'(B,B)^*=\lambda$):**
   * El camino $C \xrightarrow{0} B \xrightarrow{1+0(0+1)} C$ se suma al lazo de $C$:
     $$R''(C,C) = R'(C,C) + R(C,B)\lambda R'(B,C) = 1(0+1) + 0(1 + 0(0+1)) = 01 + (1+00)(0+1)$$
4. **Paso 3 — Eliminar el estado $C$:**
   $$r_{\text{elim}} = (0+1)\big(0(0(0+1)+1) + 1(0+1)\big)^* = (0+1)(01 + (1+00)(0+1))^*$$

#### Método 2: Construcción de las expresiones $R_{ij}^{(k)}$ (a mano)
Numeramos $1 = A$, $2 = B$, $3 = C$. Buscamos $L(M_{258}) = R_{13}^{(3)}$.

* **Base ($k = 0$):**
  $$R^{(0)} = \begin{pmatrix}
  \lambda & \emptyset & 0+1 \\
  0 & \lambda & 1 \\
  1 & 0 & \lambda
  \end{pmatrix}$$

* **Paso $k = 1$ (intermedio $1=A$, con $(R_{11}^{(0)})^* = \lambda^* = \lambda$):**
  $$\begin{aligned}
  R_{11}^{(1)} &= \lambda, \quad R_{12}^{(1)} = \emptyset, \quad R_{13}^{(1)} = 0+1, \\
  R_{21}^{(1)} &= 0, \quad R_{22}^{(1)} = \lambda, \quad R_{23}^{(1)} = 1 + 0\lambda(0+1) = 0(0+1)+1, \\
  R_{31}^{(1)} &= 1, \quad R_{32}^{(1)} = 0, \quad R_{33}^{(1)} = \lambda + 1\lambda(0+1) = \lambda + 1(0+1).
  \end{aligned}$$

* **Paso $k = 2$ (intermedio $2=B$, con $(R_{22}^{(1)})^* = \lambda^* = \lambda$):**
  $$\begin{aligned}
  R_{13}^{(2)} &= R_{13}^{(1)} + R_{12}^{(1)}\lambda R_{23}^{(1)} = (0+1) + \emptyset = 0+1, \\
  R_{31}^{(2)} &= R_{31}^{(1)} + R_{32}^{(1)}\lambda R_{21}^{(1)} = 1 + 00 = 00+1, \\
  R_{33}^{(2)} &= R_{33}^{(1)} + R_{32}^{(1)}\lambda R_{23}^{(1)} = \lambda + 1(0+1) + 0(0(0+1)+1).
  \end{aligned}$$

* **Paso $k = 3$ (intermedio $3=C$, con $(R_{33}^{(2)})^* = \big(0(0(0+1)+1) + 1(0+1)\big)^*$ por L12):**
  $$\begin{aligned}
  R_{13}^{(3)} &= R_{13}^{(2)} + R_{13}^{(2)}\left(R_{33}^{(2)}\right)^* R_{33}^{(2)} \\
  &= (0+1)\big(0(0(0+1)+1)+1(0+1)\big)^*\big(\lambda + 0(0(0+1)+1)+1(0+1)\big) + (0+1) && \text{(forma directa de } R_{13}^{(3)}\text{)} \\
  &= (0+1)\big(0(0(0+1)+1)+1(0+1)\big)^* && \text{(por L8 y L11: } L + L M^*(\lambda+M) = L M^*\text{).}
  \end{aligned}$$

#### Método 3: Sistema de ecuaciones y Lema de Arden (a mano)
Planteamos el sistema lineal por la derecha ($C \in F$ aporta $\lambda$):
$$\begin{cases}
X_A = (0+1) X_C & (1) \\
X_B = 0 X_A + 1 X_C & (2) \\
X_C = 1 X_A + 0 X_B + \lambda & (3)
\end{cases}$$

* **Vía 3a (Sustitución en orden inverso $X_C \to X_B \to X_A$, tal como ejecuta [`src/expresiones.py`](../../src/expresiones.py)):**
  1. Sustituimos $X_C = 1 X_A + 0 X_B + \lambda$ en (1) y (2):
     $$\begin{aligned}
     X_A &= (0+1)1 X_A + (0+1)0 X_B + (0+1) \\
     X_B &= 0 X_A + 1(1 X_A + 0 X_B + \lambda) = (0+11) X_A + 10 X_B + 1
     \end{aligned}$$
  2. Aplicamos el Lema de Arden en $X_B$ ($\lambda \notin L(10)$):
     $$X_B = (10)^*(0+11) X_A + (10)^*1$$
  3. Sustituimos $X_B$ en $X_A$:
     $$X_A = \big((0+1)0(10)^*(0+11) + (0+1)1\big) X_A + (0+1)0(10)^*1 + (0+1)$$
  4. Aplicamos el Lema de Arden en $X_A$:
     $$X_A = \big((0+1)0(10)^*(0+11) + (0+1)1\big)^*\big((0+1)0(10)^*1 + 0 + 1\big)$$

* **Vía 3b (Sustituyendo primero las variables sin recursión propia $X_A$ y $X_B$ en $X_C$):**
  1. Sustituimos (1) $X_A = (0+1)X_C$ dentro de (2):
     $$X_B = 0(0+1)X_C + 1X_C = (0(0+1)+1)X_C$$
  2. Sustituimos $X_A$ y $X_B$ dentro de (3):
     $$X_C = 1(0+1)X_C + 0(0(0+1)+1)X_C + \lambda = \big(01 + (1+00)(0+1)\big)X_C + \lambda$$
  3. Aplicamos el Lema de Arden una sola vez en $X_C$:
     $$X_C = \big(01 + (1+00)(0+1)\big)^*$$
  4. Regresamos a (1):
     $$X_A = (0+1)X_C = (0+1)\big(01 + (1+00)(0+1)\big)^*$$

---

### Tabla Comparativa de los Tres Métodos

| Criterio de evaluación | 1. Eliminación de estados (GNFA) | 2. Construcción inductiva $R_{ij}^{(k)}$ | 3. Sistema de ecuaciones + Lema de Arden |
| :--- | :--- | :--- | :--- |
| **Sección de la bibliografía oficial** | **Hopcroft, Motwani & Ullman (2007)**, Cap. 3, **Sección 3.2.2** (pp. 103–108); **Sipser (2012)**, **Sección 1.3**, Lema 1.60 (pp. 66–76). | **Hopcroft, Motwani & Ullman (2007)**, Cap. 3, **Sección 3.2.1**, Teorema 3.4 (pp. 98–103); **Kleene (1956)** (pp. 3–41). | **Linz (2017)**, Cap. 3, **Sección 3.2** (pp. 82–90); **Brookshear (1993)**, Cap. 1; Apunte del curso. |
| **Expresión obtenida en $M_{254}$ ($n=2$)** | $0^*1(00^*1+1)^*$ | $((\lambda+0)0^*1+1)(00^*1+1)^*(\lambda+00^*1+1)+(\lambda+0)0^*1+1$ | $(0+11^*0)^*11^*$ |
| **Longitud en $M_{254}$ (núm. de símbolos de $\Sigma$)** | **6** literales (simplifica a 3 en $(0+1)^*1$) | **16** literales sin simplificar en cada ronda (6 si se simplifica en cada $k$) | **6** literales (simplifica a 3 en $(0+1)^*1$) |
| **Expresión obtenida en $M_{258}$ ($n=3$)** | $(0+1)(0(0(0+1)+1)+1(0+1))^*$ | $(0+1)(0(0(0+1)+1)+1(0+1))^*(\lambda+0(0(0+1)+1)+1(0+1))+0+1$ | $((0+1)0(10)^*(0+11)+(0+1)1)^*((0+1)0(10)^*1+0+1)$ (o **10** literales si se despeja $X_C$ primero) |
| **Longitud en $M_{258}$ (núm. de símbolos de $\Sigma$)** | **10** literales | **20** literales | **19** literales en orden fijo $C \to B \to A$; **10** literales en orden óptimo $A, B \to C$ |
| **Número de pasos para un AFD de $n$ estados** | Se eliminan $n$ estados; al eliminar el estado $k$ se actualizan a lo sumo $(k-1)^2$ pares con entradas y salidas activas ($\mathcal{O}(n^3)$ en el peor caso, pero muy disperso en la práctica: **2 pasos** en $M_{254}$ y **3 pasos** en $M_{258}$). | Calcula obligatoriamente las $n^2$ entradas de la matriz en cada uno de los $n+1$ niveles ($k=0,1,\dots,n$): **$4 \times 3 = 12$ entradas** en $M_{254}$ y **$9 \times 4 = 36$ entradas** en $M_{258}$ ($\Theta(n^3)$ estricto). | $n$ pasos de despeje y sustitución gaussiana con aplicaciones del Lema de Arden (**2 despejes** en $M_{254}$ y **3 despejes** en $M_{258}$, o 1 solo Arden eligiendo $X_C$ como pivote). |
| **Facilidad de aplicación a mano** | **Alta y visual:** opera directamente sobre el digrafo del autómata y sólo actualiza los pares $(p,r)$ conectados a través del estado eliminado. Es el método implementado en JFLAP. | **Baja a mano (alta en programación matricial):** exige calcular muchos términos $R_{ij}^{(k)}$ que no llegan a usarse en la unión final y duplica subexpresiones por el factor $R_{ik}(R_{kk})^*R_{kj}$. | **Muy alta a mano si se elige bien el orden de sustitución:** permite despejar primero estados sin lazo propio ($X_A, X_B$ en $M_{258}$) sin introducir estrellas innecesarias. |
