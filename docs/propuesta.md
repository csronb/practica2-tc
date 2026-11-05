# Ejercicio 5.3. Propuesta de artículo de investigación

## Título tentativo de la propuesta
**Verificación formal híbrida de vulnerabilidades de Denegación de Servicio por Expresiones Regulares (ReDoS) en validadores de entrada mediante Autómatas Finitos Simbólicos y de Conteo**

---

## 1. El problema de interés y por qué admite un modelo de lenguajes formales

En el desarrollo moderno de aplicaciones web, APIs REST y cortafuegos de aplicaciones (WAF), las expresiones regulares se emplean de forma ubicua para validar entradas de usuario (correos electrónicos, URLs, tokens JWT y rutas). Sin embargo, los motores de expresiones regulares incluidos por defecto en lenguajes como Python (`re`), JavaScript (`RegExp`), Java y PHP no implementan la construcción de subconjuntos de Rabin y Scott (1959), sino algoritmos de búsqueda en profundidad con retroceso (*recursive backtracking*). Cuando un desarrollador escribe una expresión regular que induce **ambigüedad no determinista** en su AFN equivalente —por ejemplo, una estrella de Kleene anidada como `(a+)+b` o repeticiones solapadas como `([a-z0-9]+)*@`—, una cadena maliciosa de apenas 30 o 40 caracteres que falle en el último símbolo obliga al motor a explorar $O(2^{|w|})$ caminos del árbol no determinista, congelando el hilo del servidor al 100% de CPU. Este vector de ataque se conoce como **Denegación de Servicio por Expresiones Regulares (*Regular Expression Denial of Service*, ReDoS)** (Turonová et al., 2020).

Este problema admite de manera natural y exacta un **modelo de lenguajes formales** porque:
1. Toda expresión regular pura $R$ define un lenguaje regular $L(R) \subseteq \Sigma^*$ y se traduce constructivamente mediante el **Teorema de Kleene y la construcción de Thompson/Glushkov** a un Autómata Finito No Determinista $N(R) = (Q, \Sigma, \delta, q_0, F)$ (Kleene, 1956; Hopcroft et al., 2007).
2. La existencia de vulnerabilidad exponencial o polinomial ante ReDoS equivale a una **propiedad estructural decidible sobre el grafo de transiciones del AFN $N(R)$**: un motor de *backtracking* sufre explosión exponencial si y solo si en el autómata producto $N(R) \times N(R)$ existe un estado accesible y co-accesible (capaz de llegar a un bloqueo tras un sufijo de fallo $z$) que pertenece a **dos ciclos distintos etiquetados con la misma subcadena bombeable $v \in \Sigma^+$** (ambigüedad exponencial o *EDA: Exponential Degree of Ambiguity*).

---

## 2. Clase de máquina necesaria con lo visto hasta ahora y proyección hacia Autómatas de Pila y Máquinas de Turing

Con los conceptos cubiertos hasta la Unidad Temática I y la Práctica 2, la base del sistema se modela dentro del **Nivel 3 de la Jerarquía de Chomsky (Lenguajes Regulares)**:
* Se requiere un **AFN-$\lambda$ / AFN de Glushkov** para representar fielmente las bifurcaciones no deterministas tal como las recorre el motor de *backtracking*, combinado con **Autómatas Finitos Simbólicos (SFA)** (D'Antoni & Veanes, 2021) para manejar eficientemente clases de caracteres Unicode (`\w`, `[a-zA-Z0-9_]`, `[^/]+`) sin expandir miles de aristas individuales, y **Autómatas de Conjuntos de Conteo (CsA)** (Turonová et al., 2020) para expresiones con cuantificadores acotados `{m,n}`.
* Asimismo, para sintetizar automáticamente la "cadena de ataque" más corta $w_{\text{ataque}} = u v^k z$ que demuestra la vulnerabilidad y para ofrecer una versión segura en tiempo lineal, se emplea la **construcción de subconjuntos (AFN $\to$ AFD)** y la **minimización de Hopcroft** (Hopcroft et al., 2007).

### ¿Se prevé requerir Autómatas de Pila o Máquinas de Turing conforme avance el curso?
**Sí, de manera fundamental en dos extensiones del proyecto**:
1. **Autómatas de Pila (Nivel 2 — Lenguajes Libres de Contexto)**: Muchas expresiones utilizadas en validadores reales emplean grupos anidados recursivos o emparejamiento de delimitadores balanceados (por ejemplo, validar etiquetas HTML/XML o paréntesis en filtros de consulta), los cuales exceden la capacidad de un AFD por el Lema de Bombeo y requieren un **Autómata de Pila (PDA)** para analizar su ambigüedad.
2. **Máquinas de Turing / Autómatas Linealmente Acotados (Niveles 1 y 0)**: Cuando una expresión "regular" de tipo PCRE incluye **referencias hacia atrás (*backreferences*, como `(.*)\1`)**, el lenguaje reconocido $\{ ww \mid w \in \Sigma^* \}$ deja de ser regular e incluso libre de contexto, pasando a ser **Sensible al Contexto (Nivel 1)**, cuyo problema de pertenencia es $\text{NP-completo}$ y cuya equivalencia general es indecidible en el marco de las **Máquinas de Turing** (Sipser, 2012).

---

## 3. Dos artículos arbitrados con DOI que sustentan la propuesta

1. **Turonová, L., Lukáš, H., Lengál, O., & Vojnar, T. (2020)**. Regex matching with counting-set automata. *Proceedings of the ACM on Programming Languages*, *4*(OOPSLA), Artículo 218, 1–30. https://doi.org/10.1145/3428286
   * *Sustento*: Proporciona el modelo formal de los *Counting-Set Automata (CsA)* y demuestra cómo determinizar expresiones regulares con cuantificadores numéricos `{m,n}` evitando tanto la explosión exponencial $2^n$ de los AFD tradicionales como la vulnerabilidad ReDoS de los motores con *backtracking*.
2. **D'Antoni, L., & Veanes, M. (2021)**. Automata modulo theories. *Communications of the ACM*, *64*(5), 86–95. https://doi.org/10.1145/3419404
   * *Sustento*: Introduce los *Symbolic Finite Automata (SFA)* donde las transiciones llevan predicados sobre alfabetos grandes (Unicode), permitiendo construir el autómata producto $N \times N$ y minimizar AFD sin sufrir explosión por el tamaño del alfabeto $|\Sigma|$.

---

## 4. Qué se construiría y de qué manera se comprobaría que funciona

### ¿Qué se construiría?
Se construiría una herramienta y biblioteca en Python llamada **`SafeRegex-TC`** (integrada sobre el núcleo [`src/automata.py`](../src/automata.py) y con interfaz interactiva en Flet) compuesta por tres módulos:
1. **Analizador y Compilador a AFN-$\lambda$ / AFN**: Recibe una expresión regular, la convierte a un AFN mediante construcción de Thompson y elimina las transiciones $\lambda$.
2. **Detector Estático de Ambigüedad (Producto $N \times N$)**: Construye el grafo producto de caminos paralelos del AFN para detectar si existen dos rutas distintas desde $q_0$ que consuman la misma subcadena bombeable $v$ y luego fallen al leer un sufijo $z \notin L(R)$. En caso afirmativo, genera automáticamente la cadena testigo $u v^k z$ que provoca el comportamiento exponencial.
3. **Motor de Mitigación por Conversión a AFD Mínimo**: Convierte el AFN vulnerable a su AFD mínimo equivalente (o CsA si tiene cuantificadores) y lo exporta en `.jff`, `.json` y `.xml`, garantizando evaluación en tiempo estrictamente lineal $O(|w|)$.

### ¿De qué manera se comprobaría experimentalmente que funciona?
1. **Conjunto de pruebas (*Benchmark*)**: Se evaluaría contra un banco de 100 expresiones regulares reales (50 vulnerables a ReDoS documentadas en CVE/OWASP y 50 benignas).
2. **Métricas cuantitativas**:
   * **Precisión y Exhaustividad (*Precision & Recall*)** en la detección de expresiones con grado de ambigüedad exponencial.
   * **Comparación empírica de tiempos de ejecución**: Se mediría en los tres contenedores (`py311`, `py312`, `py313`) el tiempo que tarda el módulo estándar `re` de Python frente al AFD generado por `SafeRegex-TC` al evaluar la cadena testigo $u v^k z$ para longitudes $k \in \{10, 20, 30, 40\}$, comprobando gráficamente la diferencia entre la curva exponencial $\Theta(2^k)$ del *backtracking* y la recta lineal $\Theta(k)$ de nuestro AFD.
