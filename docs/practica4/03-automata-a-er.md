# Ejercicio 3: De Autómata a Expresión Regular (Dirección II del Teorema de Kleene)

- **Unidad de Aprendizaje:** Teoría de la Computación (Plan 2020) — **IPN — ESCOM**
- **Alumno:** César Octavio Navarro Bahena — **Boleta:** `2023630464` — **Grupo:** `4CM4`
- **Profesor:** M. en C. Gabriel Hurtado Avilés
- **Módulos de implementación:** [`src/automata.py`](../../src/automata.py), [`src/expresiones.py`](../../src/expresiones.py), [`src/app.py`](../../src/app.py)
- **Directorio de autómatas `.jff`:** [`automatas/practica4/afd-a-er/`](../../automatas/practica4/afd-a-er/)

---

## 1. Importación desde `.jff` y Verificación Diagnóstica de Determinismo

Antes de iniciar la conversión de autómata a expresión regular, el método `AutomataFinito.verificar_determinismo()` en [`src/automata.py`](../../src/automata.py) inspecciona la quíntupla $M = (Q, \Sigma, \delta, q_0, F)$ importada desde `.jff` y verifica:
1. Que exista un estado inicial válido $q_0 \in Q$.
2. Que ningún estado $q \in Q$ posea transiciones espontáneas $\lambda$ ($\delta(q, \lambda) = \emptyset$).
3. Que para todo par $(q, a) \in Q \times \Sigma$ exista a lo sumo un estado destino ($|\delta(q, a)| \le 1$).

Si el autómata no es determinista, devuelve un objeto `ResultadoVerificacionAFD` con la lista de objetos `ViolacionDeterminismo(estado, simbolo, destinos, motivo)`, indicando explícitamente **qué estado y qué símbolo lo impiden**:

| Archivo `.jff` evaluado | ¿Determinista? | Primer estado y símbolo en conflicto | Diagnóstico reportado por `verificar_determinismo()` |
| :--- | :---: | :---: | :--- |
| `ej254` a `ej258`, `ej276`, `ej277` | **Sí (`True`)** | Ninguno | `El autómata es determinista (AFD completo sobre Q=..., Σ=...).` |
| `ej196_afnd_lambda.jff` | **No (`False`)** | Estado `'A'`, símbolo `'λ'` | `El estado 'A' con el símbolo 'λ' presenta transición espontánea hacia {B}; el estado 'B' con el símbolo '0' tiene múltiples transiciones: δ(B, 0) = {A, B}.` |
| `ej191_subconjuntos.jff` | **No (`False`)** | Estado `'A'`, símbolo `'0'` | `El estado 'A' con el símbolo '0' tiene múltiples transiciones (2 destinos): δ(A, 0) = {A, B}.` |

---

## 2. Método de Eliminación de Estados y Autómata Finito Generalizado (GNFA) Paso a Paso

La función `eliminacion_de_estados_detallada(afd, orden)` en [`src/expresiones.py`](../../src/expresiones.py) implementa el método de eliminación de estados (Hopcroft, Motwani & Ullman, 2007, §3.2.2, pp. 98–102; Sipser, 2012, Lema 1.60, pp. 70–76):

1. **Paso 0 (Construcción del GNFA inicial):** Se agregan dos estados especiales: un nuevo estado inicial $\vdash_{\text{ini}}$ (sin aristas entrantes) con transición $\vdash_{\text{ini}} \xrightarrow{\lambda} q_0$, y un nuevo estado único de aceptación $\text{fin}_{\dashv}$ (sin aristas salientes) con transiciones $f \xrightarrow{\lambda} \text{fin}_{\dashv}$ para cada $f \in F$. Para cada par $(p, q) \in Q \times Q$, la etiqueta inicial $R(p, q)$ es la unión $a_1 + a_2 + \cdots + a_m$ de los símbolos $a \in \Sigma$ tales que $\delta(p, a) = q$ (o $\emptyset$ si no hay transición).
2. **Paso $k$ (Eliminación del estado $q_{\text{elim}} \in Q$):** Para toda pareja de estados sobrevivientes $(p, r)$ con $p \neq q_{\text{elim}}$ y $r \neq q_{\text{elim}}$, se actualiza la arista generalizada mediante la regla fundamental:
   $$R'(p, r) = R(p, r) + R(p, q_{\text{elim}}) \cdot \bigl(R(q_{\text{elim}}, q_{\text{elim}})\bigr)^* \cdot R(q_{\text{elim}}, r)$$
   Tras registrar cada actualización y remover $q_{\text{elim}}$, se almacena una instantánea `PasoGNFA` con la tabla Markdown completa de las aristas vivas del GNFA.
3. **Terminación:** Cuando se han eliminado los $|Q|$ estados originales, los únicos estados sobrevivientes son $\vdash_{\text{ini}}$ y $\text{fin}_{\dashv}$, y la expresión regular resultante es $R(\vdash_{\text{ini}}, \text{fin}_{\dashv})$.

---

## 3. Comparación con JFLAP (Práctica 3) y Prueba Formal de Equivalencia vía AFD Mínimos

Para demostrar algorítmicamente que la expresión regular $E_{\text{propia}}$ obtenida por eliminación de estados y la expresión $E_{\text{JFLAP}}$ obtenida con JFLAP en la Práctica 3 (así como la expresión simplificada $E_{\text{simp}}$) describen exactamente el mismo lenguaje, la función `comparar_expresiones_por_afd_minimo(E_1, E_2)` ejecuta el ciclo completo:
1. Convierte $E_1$ en su AFD mínimo $M_{\min}(E_1)$ usando el Ejercicio 2 (`er_a_automata_completo`).
2. Convierte $E_2$ en su AFD mínimo $M_{\min}(E_2)$ usando el Ejercicio 2 (`er_a_automata_completo`).
3. Aplica la prueba de equivalencia formal de la Práctica 3 (`M_min(E_1).son_afd_equivalentes(M_min(E_2))`), la cual verifica por el Teorema de Myhill-Nerode el isomorfismo canónico entre ambos AFD mínimos.

### 3.1 Resultados en la Lista 3 (Ejercicios 254 al 258 — Cinco Autómatas del Ejercicio 1 de la Práctica 3)

| Caso (`.jff`) | Expresión obtenida (`eliminacion_de_estados_detallada`) | Expresión JFLAP (Práctica 3) | Expresión Simplificada (Práctica 3) | $\|Q_{\text{AFD mín}}\|$ | ¿Equivalentes (`son_afd_equivalentes`)? |
| :--- | :--- | :--- | :--- | :---: | :---: |
| **`ej254_termina_en_1.jff`** | `0*1(00*1+1)*` | `0*1(1+00*1)*` | `(0+1)*1` | 2 | **Sí (`A ↔ q0`, `B ↔ q1`)** |
| **`ej255_ciclo_par_b.jff`** | `λ+(0+1)(0(0+1)+1)*0` | `((0+1)1*0)*` | `((0+1)1*0)*` | 2 | **Sí (`A ↔ q0`, `B ↔ q1`)** |
| **`ej256_ternario.jff`** | `(1+2)*0(0+1+2(1+2)*0)*` | `(1+2)*0(0+1+2(1+2)*0)*` | `(1+2)*0(0+1+2(1+2)*0)*` | 2 | **Sí (`A ↔ q0`, `B ↔ q1`)** |
| **`ej257_tres_estados_bc.jff`** | `(01*0+1)((0+1)01*0+(0+1)1)*(λ+(0+1)01*)+01*` | `((1+01*0)(0+1))*01*+((1+01*0)(0+1))*(1+01*0)` | `((1+01*0)(0+1))*(01*+1+01*0)` | 3 | **Sí (`A ↔ q0`, `B ↔ q1`, `C ↔ q2`)** |
| **`ej258_tres_estados_c.jff`** | `(0+1)(0(0(0+1)+1)+1(0+1))*` | `(0+1)(01+(1+00)(0+1))*` | `(0+1)(01+(1+00)(0+1))*` | 3 | **Sí (`A ↔ q0`, `B ↔ q1`, `C ↔ q2`)** |

---

## 4. Casos de Prueba de la Lista 4 (Ejercicios 276 y 277)

### 4.1 Ejercicio 276 (`ej276_multiplo_3_a.jff`): Número de letras `a` múltiplo de 3 sobre $\Sigma = \{a, b\}$

- **Quíntupla del AFD:** $Q = \{A, B, C\}$, $\Sigma = \{a, b\}$, estado inicial $q_0 = A$, estados de aceptación $F = \{A\}$, con transiciones $\delta(A, a) = B$, $\delta(B, a) = C$, $\delta(C, a) = A$ y bucles $\delta(q, b) = q$ para todo $q \in \{A, B, C\}$.
- **Evolución del GNFA paso a paso:**
  1. **Paso 0 (GNFA inicial):** Estados vivos $\{\vdash_{\text{ini}}, A, B, C, \text{fin}_{\dashv}\}$ con $\vdash_{\text{ini}} \xrightarrow{\lambda} A$, $A \xrightarrow{\lambda} \text{fin}_{\dashv}$, $R(A,A)=b, R(A,B)=a, R(B,B)=b, R(B,C)=a, R(C,C)=b, R(C,A)=a$.
  2. **Paso 1 (Se elimina $A$, bucle $R(A,A)^* = b^*$):**
     - $R'(\vdash_{\text{ini}}, B) = \lambda \cdot b^* \cdot a = b^*a$
     - $R'(\vdash_{\text{ini}}, \text{fin}_{\dashv}) = \lambda \cdot b^* \cdot \lambda = b^*$
     - $R'(C, B) = a \cdot b^* \cdot a = ab^*a$
     - $R'(C, \text{fin}_{\dashv}) = a \cdot b^* \cdot \lambda = ab^*$
  3. **Paso 2 (Se elimina $B$, bucle $R(B,B)^* = b^*$):**
     - $R'(\vdash_{\text{ini}}, C) = b^*a \cdot b^* \cdot a = b^*ab^*a$
     - $R'(C, C) = b + ab^*a \cdot b^* \cdot a = b + ab^*ab^*a$
  4. **Paso 3 (Se elimina $C$, bucle $R(C,C)^* = (b + ab^*ab^*a)^*$):**
     - $R'(\vdash_{\text{ini}}, \text{fin}_{\dashv}) = b^* + b^*ab^*a(b + ab^*ab^*a)^*ab^*$
- **Comparación con la solución por Lema de Arden `(b + ab*ab*a)*`:** Al ejecutar `comparar_expresiones_por_afd_minimo("b*+b*ab*a(b+ab*ab*a)*ab*", "(b+ab*ab*a)*", alfabeto=["a", "b"])`, ambas expresiones se compilan en AFD mínimos de **3 estados** isomorfos (`equivalentes=True`).

### 4.2 Ejercicio 277 (`ej277_termina_en_1.jff`): Cadenas sobre $\Sigma = \{0, 1\}$ que terminan en `1`

- **Quíntupla del AFD:** $Q = \{A, B\}$, $\Sigma = \{0, 1\}$, estado inicial $q_0 = A$, aceptación $F = \{B\}$, con $\delta(A, 0) = A$, $\delta(A, 1) = B$, $\delta(B, 0) = A$, $\delta(B, 1) = B$.
- **Evolución del GNFA paso a paso:**
  1. **Paso 0 (GNFA inicial):** $\vdash_{\text{ini}} \xrightarrow{\lambda} A$, $B \xrightarrow{\lambda} \text{fin}_{\dashv}$, $R(A,A)=0, R(A,B)=1, R(B,A)=0, R(B,B)=1$.
  2. **Paso 1 (Se elimina $A$, bucle $R(A,A)^* = 0^*$):**
     - $R'(\vdash_{\text{ini}}, B) = \lambda \cdot 0^* \cdot 1 = 0^*1$
     - $R'(B, B) = 1 + 0 \cdot 0^* \cdot 1 = 00^*1 + 1$
  3. **Paso 2 (Se elimina $B$, bucle $R(B,B)^* = (00^*1 + 1)^*$):**
     - $R'(\vdash_{\text{ini}}, \text{fin}_{\dashv}) = 0^*1(00^*1 + 1)^*$
- **Comparación de equivalencia:** `comparar_expresiones_por_afd_minimo("0*1(00*1+1)*", "(0+1)*1", alfabeto=["0", "1"])` convierte ambas expresiones en AFD mínimos de **2 estados** y comprueba su isomorfismo exacto (`equivalentes=True`).
