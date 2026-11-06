# Ejercicio 2: De Expresión Regular a Autómata (Dirección I del Teorema de Kleene)

- **Unidad de Aprendizaje:** Teoría de la Computación (Plan 2020) — **IPN — ESCOM**
- **Alumno:** César Octavio Navarro Bahena — **Boleta:** `2023630464` — **Grupo:** `4CM4`
- **Profesor:** M. en C. Gabriel Hurtado Avilés
- **Módulos de implementación:** [`src/expresiones.py`](../../src/expresiones.py), [`src/automata.py`](../../src/automata.py), [`src/app.py`](../../src/app.py)
- **Directorio de autómatas `.jff`:** [`automatas/practica4/er-a-automata/`](../../automatas/practica4/er-a-automata/)

---

## 1. Analizador Sintáctico por Descenso Recursivo y Precedencia de Operadores

En [`src/expresiones.py`](../../src/expresiones.py) (`tokenizar_expresion` y `analizar_expresion`) se implementó en Python puro un analizador léxico y sintáctico por descenso recursivo que reconoce la notación del curso sin evaluar expresiones con bibliotecas externas:
- `+` para la **unión** (menor precedencia, asociativa por la izquierda),
- **yuxtaposición** (y opcionalmente el punto medio `·`) para la **concatenación** (precedencia intermedia, asociativa por la izquierda),
- `*` para la **cerradura de Kleene** (mayor precedencia, operador unario postfijo),
- `λ` para la palabra vacía, `∅` para el lenguaje vacío, y paréntesis `(` y `)`.

La jerarquía de precedencias se codifica directamente en los niveles de la gramática libre de contexto no ambigua:

$$\begin{aligned}
\text{Expresion} &\to \text{Termino} \; (\; \text{'+'} \; \text{Termino} \; )^* \\
\text{Termino}   &\to \text{Factor} \; (\; [\text{'·'}] \; \text{Factor} \; )^* \\
\text{Factor}    &\to \text{Primario} \; (\; \text{'*'} \; )^* \\
\text{Primario}  &\to \text{SIMBOLO} \;\mid\; \text{CLASE} \;\mid\; \text{'}\lambda\text{'} \;\mid\; \text{'}\emptyset\text{'} \;\mid\; \text{'('} \; \text{Expresion} \; \text{')'}
\end{aligned}$$

### 1.1 Detección de Expresiones Mal Formadas con Posición Exacta del Error

Cada token léxico conserva su posición `1-based` en la cadena original (`TokenER.posicion`). Cuando una expresión viola la gramática, `analizar_expresion` lanza `ErrorSintaxisER` indicando la posición exacta del carácter erróneo y un puntero visual `^`:

| Expresión mal formada | Posición reportada | Diagnóstico generado por `ErrorSintaxisER` |
| :--- | :---: | :--- |
| `""` (vacía) | `1` | `Error de sintaxis en la posición 1: La expresión regular está vacía.` |
| `"+a"` | `1` | `Error de sintaxis en la posición 1: Se esperaba un símbolo, 'λ', '∅' o '(', pero se encontró '+'.` |
| `"a+b+"` | `4` | `Error de sintaxis en la posición 4: Operador de unión '+' al final de la expresión sin operando derecho.` |
| `"a++b"` | `3` | `Error de sintaxis en la posición 3: Se esperaba un operando después de '+', pero se encontró '+'.` |
| `"*a"` | `1` | `Error de sintaxis en la posición 1: El operador '*' requiere un operando previo; apareció '*' sin expresión a su izquierda.` |
| `"(*a)"` | `2` | `Error de sintaxis en la posición 2: El operador '*' requiere un operando previo; apareció '*' sin expresión a su izquierda.` |
| `"()"` | `2` | `Error de sintaxis en la posición 2: Paréntesis vacíos '()' no permitidos; use 'λ' para la palabra vacía o '∅' para el lenguaje vacío.` |
| `"((a+b)"` | `1` | `Error de sintaxis en la posición 1: Paréntesis '(' abierto en la posición 1 no tiene su ')' de cierre correspondiente.` |
| `"a+b)"` | `4` | `Error de sintaxis en la posición 4: Paréntesis de cierre ')' sin su correspondiente '(' de apertura.` |
| `"a?b"` | `2` | `Error de sintaxis en la posición 2: Carácter '?' no válido en la notación del curso (antemponga '\' si desea el carácter literal).` |

---

## 2. Construcción de la Parte I del Teorema de Kleene (Forma Estándar de Thompson)

La función `er_a_afn_lambda_detallado` recorre en postorden el árbol sintáctico binario construyendo para cada subexpresión una pieza parcial $\text{AFN-}\lambda$ $M_i = (Q_i, \Sigma, \delta_i, q_{\text{ini}}, \{q_{\text{fin}}\})$ en **forma estándar** (Hopcroft, Motwani & Ullman, 2007, §3.2.3; Thompson, 1968; notas del curso *Teorema de Kleene: De ER a AFN-$\lambda$*):
1. El estado inicial $q_{\text{ini}}$ no tiene transiciones entrantes.
2. El único estado de aceptación $q_{\text{fin}}$ ($q_{\text{fin}} \neq q_{\text{ini}}$) no tiene transiciones salientes.
3. **Casos básicos** (2 estados nuevos $q_k, q_{k+1}$ cada uno):
   - $\emptyset$: sin transiciones ($\delta = \emptyset$).
   - $\lambda$: una transición espontánea $q_k \xrightarrow{\lambda} q_{k+1}$.
   - $a \in \Sigma$: una transición $q_k \xrightarrow{a} q_{k+1}$.
4. **Reglas inductivas**:
   - **Concatenación $R_1 R_2$**: añade la transición puente $\text{fin}_1 \xrightarrow{\lambda} \text{ini}_2$ (0 estados nuevos; inicial $\text{ini}_1$, final $\text{fin}_2$).
   - **Unión $R_1 + R_2$**: crea 2 estados nuevos $q_i$ (inicial) y $q_f$ (final) y 4 transiciones $\lambda$: $q_i \xrightarrow{\lambda} \text{ini}_1, \text{ini}_2$ y $\text{fin}_1, \text{fin}_2 \xrightarrow{\lambda} q_f$.
   - **Cerradura de Kleene $R_1^*$**: crea 2 estados nuevos $q_i$ (inicial) y $q_f$ (final) y 4 transiciones $\lambda$: $q_i \xrightarrow{\lambda} \text{ini}_1, q_f$ y $\text{fin}_1 \xrightarrow{\lambda} \text{ini}_1, q_f$.

A continuación, `er_a_automata_completo` encadena automáticamente los tres algoritmos de la Práctica 3:
$$\text{ER} \xrightarrow{\text{Kleene I}} \text{AFN-}\lambda \xrightarrow{\text{Ej. 2.2 (Prác. 3)}} \text{AFN sin }\lambda \xrightarrow{\text{Ej. 2.3 (Subconjuntos)}} \text{AFD alcanzable} \xrightarrow{\text{Ej. 2.4 (Hopcroft/Moore)}} \text{AFD mínimo}$$

---

## 3. Casos de Prueba de la Lista 3 (Ejercicios 241 al 253, $\Sigma = \{0, 1\}$)

Todos los autómatas exportados en formato `.jff` se encuentran en [`automatas/practica4/er-a-automata/`](../../automatas/practica4/er-a-automata/):

| Ejercicio | Expresión regular (notación del curso) | Piezas parciales | $\|Q_{\text{AFN-}\lambda}\|$ | $\|Q_{\text{AFN}}\|$ | $\|Q_{\text{AFD}}\|$ | $\|Q_{\text{AFD mín}}\|$ | Archivo `.jff` exportado |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **241** | `0 + 1` | 3 | 6 | 6 | 3 | 2 | `ej241_afn_lambda.jff` / `ej241_afd_minimo.jff` |
| **242** | `0* + 1` | 4 | 8 | 8 | 4 | 3 | `ej242_afn_lambda.jff` / `ej242_afd_minimo.jff` |
| **243** | `(0 + 1)*` | 4 | 8 | 8 | 3 | 1 | `ej243_afn_lambda.jff` / `ej243_afd_minimo.jff` |
| **244** | `0(0 + 1)` | 5 | 8 | 8 | 4 | 3 | `ej244_afn_lambda.jff` / `ej244_afd_minimo.jff` |
| **245** | `0(0 + 1)*` | 6 | 10 | 10 | 4 | 2 | `ej245_afn_lambda.jff` / `ej245_afd_minimo.jff` |
| **246** | `0*(0 + 1)` | 6 | 10 | 10 | 4 | 3 | `ej246_afn_lambda.jff` / `ej246_afd_minimo.jff` |
| **247** | `(01)* + 1*` | 7 | 12 | 12 | 5 | 4 | `ej247_afn_lambda.jff` / `ej247_afd_minimo.jff` |
| **248** | `(0* + 1)0` | 6 | 10 | 10 | 5 | 4 | `ej248_afn_lambda.jff` / `ej248_afd_minimo.jff` |
| **249** | `(0* + 1)0*` | 7 | 12 | 12 | 5 | 2 | `ej249_afn_lambda.jff` / `ej249_afd_minimo.jff` |
| **250** | `0*1* + 1*0` | 9 | 16 | 16 | 6 | 4 | `ej250_afn_lambda.jff` / `ej250_afd_minimo.jff` |
| **251** | `(0 + 1*)0 + 1*1` | 10 | 16 | 16 | 7 | 4 | `ej251_afn_lambda.jff` / `ej251_afd_minimo.jff` |
| **252** | `(0 + 1)*(00 + 11) + (00 + 11)(0 + 1)*` | 23 | 34 | 34 | 13 | 6 | `ej252_afn_lambda.jff` / `ej252_afd_minimo.jff` |
| **253** | `(0 + (11 + 00)*)(11 + 10 + 01)*(λ + 110)` | 26 | 38 | 38 | 11 | 9 | `ej253_afn_lambda.jff` / `ej253_afd_minimo.jff` |

---

## 4. Casos de Prueba de la Lista 4 (Ejercicios 272, 273 y 278, $\Sigma = \{a, b\}$)

### 4.1 Ejercicio 272: Construcción de $\text{AFN-}\lambda$ para los incisos (a) a (e)

| Inciso | Expresión regular | Piezas parciales | $\|Q_{\text{AFN-}\lambda}\|$ | Estado inicial / final | $\|Q_{\text{AFD}}\|$ | $\|Q_{\text{AFD mín}}\|$ | Archivo `.jff` |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **272(a)** | `a + b*` | 4 | **8** | `q6` / `{q7}` | 3 | 3 | `272a_a_mas_b_estrella.jff` |
| **272(b)** | `(ab)*a` | 6 | **8** | `q4` / `{q7}` | 3 | 2 | `272b_ab_estrella_a.jff` |
| **272(c)** | `(a + b)*abb` | 10 | **14** | `q6` / `{q13}` | 5 | 4 | `272c_a_mas_b_estrella_abb.jff` |
| **272(d)** | `a(ba)* + b` | 8 | **12** | `q10` / `{q11}` | 5 | 4 | `272d_a_ba_estrella_mas_b.jff` |
| **272(e)** | `(a + λ)(b + ∅)` | 7 | **12** | `q4` / `{q11}` | 3 | 3 | `272e_a_mas_lambda_por_b_mas_vacio.jff` |

### 4.2 Ejercicio 273: Verificación de Cadenas con Clausuras $\lambda$ sobre `272(b)` y `272(c)`

Se evaluaron las cuatro cadenas $w \in \{\texttt{aba}, \texttt{ab}, \texttt{babb}, \texttt{abab}\}$ directamente sobre los $\text{AFN-}\lambda$ de `272(b)` y `272(c)` calculando $\hat{\delta}(q_0, w) = \text{Cl}_\lambda(\delta(\dots))$ en cada paso:

1. **Autómata de `272(b)` para $R = (ab)^*a$ ($q_0 = q_4$, $F = \{q_7\}$):**
   - $\text{Cl}_\lambda(\{q_4\}) = \{q_0, q_4, q_5, q_6\}$.
   - **`aba` $\to$ ACEPTADA:** $\text{Cl}_\lambda(\{q_4\}) \xrightarrow{a} \{q_1, q_2, q_7\} \xrightarrow{b} \{q_0, q_3, q_5, q_6\} \xrightarrow{a} \{q_1, q_2, q_7\}$. Como $q_7 \in F$, la cadena `aba` es **aceptada**.
   - **`ab` $\to$ RECHAZADA:** termina en $\{q_0, q_3, q_5, q_6\} \cap \{q_7\} = \emptyset$.
   - **`babb` $\to$ RECHAZADA:** desde $\{q_0, q_4, q_5, q_6\}$ con `b` el conjunto activo se vacía ($\emptyset$).
   - **`abab` $\to$ RECHAZADA:** termina en $\{q_0, q_3, q_5, q_6\} \cap \{q_7\} = \emptyset$.

2. **Autómata de `272(c)` para $R = (a + b)^*abb$ ($q_0 = q_6$, $F = \{q_{13}\}$):**
   - $\text{Cl}_\lambda(\{q_6\}) = \{q_0, q_2, q_4, q_6, q_7, q_8\}$.
   - **`aba` $\to$ RECHAZADA:** termina en $\{q_0, q_1, q_2, q_4, q_5, q_7, q_8, q_9, q_{10}\} \cap \{q_{13}\} = \emptyset$.
   - **`ab` $\to$ RECHAZADA:** termina en $\{q_0, q_2, q_3, q_4, q_5, q_7, q_8, q_{11}, q_{12}\} \cap \{q_{13}\} = \emptyset$.
   - **`babb` $\to$ ACEPTADA:** tras consumir `b`, `a`, `b`, `b`, el conjunto activo final es $\{q_0, q_2, q_3, q_4, q_5, q_7, q_8, q_{13}\}$, el cual contiene a $q_{13} \in F$.
   - **`abab` $\to$ RECHAZADA:** termina en $\{q_0, q_2, q_3, q_4, q_5, q_7, q_8, q_{11}, q_{12}\} \cap \{q_{13}\} = \emptyset$.

### 4.3 Ejercicio 278: Desarrollo Paso a Paso para $R = (a + b)^*b$

Las 6 piezas parciales generadas por `er_a_afn_lambda_detallado("(a + b)*b")` son:
1. **Paso 1 — Caso básico `'a'`**: estados $q_0 \xrightarrow{a} q_1$ ($|Q|=2$).
2. **Paso 2 — Caso básico `'b'`**: estados $q_2 \xrightarrow{b} q_3$ ($|Q|=2$).
3. **Paso 3 — Unión `'a+b'`**: nuevos estados $q_4$ (inicial) y $q_5$ (final) con $q_4 \xrightarrow{\lambda} q_0, q_2$ y $q_1, q_3 \xrightarrow{\lambda} q_5$ ($|Q|=6$).
4. **Paso 4 — Cerradura de Kleene `'(a+b)*'`**: nuevos estados $q_6$ (inicial) y $q_7$ (final) con $q_6 \xrightarrow{\lambda} q_4, q_7$ y $q_5 \xrightarrow{\lambda} q_4, q_7$ ($|Q|=8$).
5. **Paso 5 — Caso básico `'b'`**: estados $q_8 \xrightarrow{b} q_9$ ($|Q|=2$).
6. **Paso 6 — Concatenación `'(a+b)*b'`**: añade $q_7 \xrightarrow{\lambda} q_8$, conservando $q_6$ como estado inicial y $q_9$ como único estado final ($|Q|=10$, exportado en `278a_afn_lambda_thompson.jff`).

Al aplicar la tubería de la Práctica 3:
- **Inciso (b) — Eliminación de transiciones $\lambda$ (`278b_afn_sin_lambda.jff`)**: se obtiene un AFN de 10 estados con $q_0 = q_6$ y $F = \{q_9\}$.
- **Inciso (c) — Construcción de subconjuntos (`278c_afd_subconjuntos.jff`) y minimización (`278d_afd_minimo.jff`)**: la construcción de subconjuntos genera 3 estados alcanzables:
  - $S_0 = \{q_0, q_2, q_4, q_6, q_7, q_8\}$ (inicial, no final),
  - $S_1 = \{q_0, q_1, q_2, q_4, q_5, q_7, q_8\}$ (no final),
  - $S_2 = \{q_0, q_2, q_3, q_4, q_5, q_7, q_8, q_9\}$ (aceptación, contiene a $q_9$).
  Al minimizar, $S_0 \equiv S_1$ se fusionan en la clase $\{S_0, S_1\}$ y $S_2$ permanece en $\{S_2\}$, produciendo el **AFD mínimo de 2 estados**.
- **Inciso (d) — Retorno a expresión regular y equivalencia**: al aplicar eliminación de estados al AFD mínimo se obtiene $a^*b(a^*b + b)^*$, y `comparar_expresiones_por_afd_minimo("(a + b)*b", "a*b(a*b + b)*")` demuestra formalmente que sus AFD mínimos son isomorfos (`equivalentes=True`).
