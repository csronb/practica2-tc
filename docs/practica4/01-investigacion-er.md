# Ejercicio 1: Investigación Formal sobre Lenguajes Regulares, Expresiones Regulares y el Teorema de Kleene

- **Unidad de Aprendizaje:** Teoría de la Computación (Plan 2020)
- **Institución:** Instituto Politécnico Nacional (IPN) — Escuela Superior de Cómputo (ESCOM)
- **Alumno:** César Octavio Navarro Bahena — **Boleta:** `2023630464` — **Grupo:** `4CM4`
- **Profesor:** M. en C. Gabriel Hurtado Avilés
- **Práctica 4:** Uso de las Expresiones Regulares y Extensión de Software para Convertir Expresiones Regulares

---

## 1. Definición Formal de Lenguaje Regular, Expresión Regular y Operaciones Regulares

Sea $\Sigma$ un alfabeto finito no vacío de símbolos y sea $\Sigma^*$ el monoide libre de todas las palabras finitas sobre $\Sigma$ con la palabra vacía $\lambda$ como elemento identidad ($|\lambda| = 0$). Cualquier subconjunto $L \subseteq \Sigma^*$ se denomina un **lenguaje formal** sobre $\Sigma$ (Hopcroft, Motwani & Ullman, 2007, §1.5).

### 1.1 Operaciones Regulares sobre Lenguajes

Dados dos lenguajes cualesquiera $L_1, L_2 \subseteq \Sigma^*$, las tres **operaciones regulares** fundamentales se definen conjuntistamente como sigue (Sipser, 2012, Definición 1.23, p. 44; Hopcroft et al., 2007, §3.1.1, p. 86):

1. **Unión ($L_1 \cup L_2$):** Es el conjunto de todas las cadenas que pertenecen a $L_1$, a $L_2$, o a ambos:
   $$L_1 \cup L_2 = \{ w \in \Sigma^* \mid w \in L_1 \lor w \in L_2 \}$$
2. **Concatenación ($L_1 \cdot L_2$ o simplemente $L_1 L_2$):** Es el conjunto de todas las cadenas que se obtienen al yuxtaponer un prefijo tomado de $L_1$ seguido de un sufijo tomado de $L_2$:
   $$L_1 L_2 = \{ xy \in \Sigma^* \mid x \in L_1 \land y \in L_2 \}$$
3. **Cerradura de Kleene o estrella ($L_1^*$):** Sea la potencia inductiva de un lenguaje $L_1^0 = \{\lambda\}$ y $L_1^{k} = L_1^{k-1} L_1$ para todo $k \ge 1$. La cerradura de Kleene de $L_1$ es la unión infinita numerable de todas sus potencias finitas:
   $$L_1^* = \bigcup_{k=0}^{\infty} L_1^k = L_1^0 \cup L_1^1 \cup L_1^2 \cup \cdots$$
   De forma complementaria, la **cerradura positiva** se define como $L_1^+ = \bigcup_{k=1}^{\infty} L_1^k = L_1 L_1^*$.

### 1.2 Definición Inductiva de Lenguaje Regular y de Expresión Regular

La familia de los **lenguajes regulares** sobre un alfabeto $\Sigma$, denotada $\mathcal{R}(\Sigma)$, es la colección más pequeña de subconjuntos de $\Sigma^*$ que contiene a los lenguajes básicos y es cerrada bajo unión, concatenación y cerradura de Kleene. Paralelamente, las **expresiones regulares** constituyen la notación algebraica finita que denota exactamente a los miembros de $\mathcal{R}(\Sigma)$ mediante una función de interpretación semántica $L(\cdot)$ (Hopcroft et al., 2007, §3.1.2, pp. 87–89; Linz, 2017, Definición 3.1, p. 73):

- **Casos base (expresiones atómicas):**
  1. $\emptyset$ es una expresión regular que denota al lenguaje vacío: $L(\emptyset) = \emptyset$.
  2. $\lambda$ es una expresión regular que denota al lenguaje unitario formado únicamente por la cadena vacía: $L(\lambda) = \{\lambda\}$.
  3. Para cada símbolo $a \in \Sigma$, el carácter $a$ es una expresión regular que denota al lenguaje unitario del símbolo: $L(a) = \{a\}$.
- **Paso inductivo (operadores compuestos):** Si $R$ y $S$ son expresiones regulares que denotan los lenguajes $L(R)$ y $L(S)$ respectivamente, entonces:
  1. $(R + S)$ es una expresión regular que representa la **unión**: $L(R + S) = L(R) \cup L(S)$.
  2. $(R \cdot S)$ o $(RS)$ es una expresión regular que representa la **concatenación**: $L(RS) = L(R) \cdot L(S)$.
  3. $(R^*)$ es una expresión regular que representa la **cerradura de Kleene**: $L(R^*) = (L(R))^*$.
- **Cláusula extremal:** Ninguna cadena de símbolos es una expresión regular sobre $\Sigma$ a menos que se obtenga mediante un número finito de aplicaciones de las reglas anteriores.

Para eliminar paréntesis superfluos sin introducir ambigüedad sintáctica, la convención universal del curso asigna la mayor precedencia a la cerradura de Kleene (`*`, operador unario postfijo), precedencia intermedia a la concatenación por yuxtaposición (asociativa), y la menor precedencia a la unión (`+`, asociativa). Así, la expresión $0 + 10^*$ se interpreta unívocamente como $(0 + (1(0^*)))$ (Hopcroft et al., 2007, §3.1.3, p. 90).

---

## 2. Ubicación de los Lenguajes Regulares dentro de la Jerarquía de Chomsky

En su artículo fundacional, Noam Chomsky (1956, pp. 113–124) clasificó las gramáticas formales $G = (V, \Sigma, P, S)$ —donde $V$ es el conjunto de variables no terminales, $\Sigma$ el alfabeto terminal disjunto de $V$, $P$ el conjunto finito de reglas de producción y $S \in V$ el símbolo inicial— en cuatro niveles anidados según las restricciones estructurales impuestas a sus producciones (Linz, 2017, §11.4, pp. 305–309; Brookshear, 1993, Cap. 3):

| Nivel | Nombre de la clase | Restricción en las producciones ($\alpha \to \beta$) | Modelo reconocedor equivalente |
| :---: | :--- | :--- | :--- |
| **Tipo 0** | Lenguajes recursivamente enumerables | Sin restricciones ($\alpha \in (V \cup \Sigma)^+$, $\beta \in (V \cup \Sigma)^*$) | Máquina de Turing determinista o no determinista |
| **Tipo 1** | Lenguajes sensibles al contexto | $\|\alpha\| \le \|\beta\|$ (gramáticas no contractivas, salvo $S \to \lambda$) | Autómata Linealmente Acotado (LBA) |
| **Tipo 2** | Lenguajes libres de contexto (GLC) | $A \to \gamma$ con $A \in V$ y $\gamma \in (V \cup \Sigma)^*$ | Autómata con Pila no determinista (AP / PDA) |
| **Tipo 3** | **Lenguajes regulares** | Lineales por la derecha ($A \to wB$ o $A \to w$) o por la izquierda ($A \to Bw$ o $A \to w$), con $A, B \in V$ y $w \in \Sigma^*$ | **Autómata Finito (AFD, AFN, AFN-$\lambda$) y Expresiones Regulares** |

Se cumple la cadena de inclusiones estrictas $\mathcal{L}_{\text{Tipo 3}} \subsetneq \mathcal{L}_{\text{Tipo 2}} \subsetneq \mathcal{L}_{\text{Tipo 1}} \subsetneq \mathcal{L}_{\text{Tipo 0}}$. Los lenguajes regulares ocupan la base (**Tipo 3**) de la jerarquía: son exactamente aquellos cuyo reconocimiento requiere una cantidad de memoria **estrictamente constante** $\mathcal{O}(1)$ independiente de la longitud $|w|$ de la cadena de entrada, codificada en el conjunto finito de estados $Q$ del autómata finito (Rabin & Scott, 1959, pp. 115–119). Esta restricción de memoria finita les confiere propiedades de clausura y decidibilidad excepcionales: son cerrados bajo unión, intersección, complemento, diferencia, concatenación, cerradura de Kleene, reverso y homomorfismo, y los problemas de pertenencia ($w \in L$), vacuidad ($L = \emptyset$), finitud ($|L| < \infty$) y equivalencia ($L(M_1) = L(M_2)$) son todos decidibles en tiempo polinomial (Hopcroft et al., 2007, Cap. 4).

---

## 3. Enunciado del Teorema de Kleene en Ambas Direcciones

El resultado central que vincula la descripción operativa (autómatas finitos) con la descripción algebraica (expresiones regulares) fue demostrado originalmente por Stephen Cole Kleene (1956, Teoremas 3 y 6, pp. 18–31) en su estudio sobre eventos regulares en redes nerviosas abstractas.

> **Teorema de Kleene (Kleene, 1956, pp. 18–31; Hopcroft, Motwani & Ullman, 2007, §3.2, pp. 93–108; Sipser, 2012, Teorema 1.54, p. 66):**
> *Un lenguaje $L \subseteq \Sigma^*$ es regular (es decir, existe una expresión regular $R$ tal que $L = L(R)$) si y sólo si es aceptado por algún autómata finito $M$ ($L = L(M)$).*

Al tratarse de una equivalencia lógica bicondicional ($\Longleftrightarrow$), su demostración constructiva se divide en dos direcciones complementarias:

1. **Dirección I — De Expresión Regular a Autómata Finito ($\text{ER} \Longrightarrow \text{AFN-}\lambda \Longrightarrow \text{AFN} \Longrightarrow \text{AFD}$):**
   - **Enunciado (Hopcroft et al., 2007, Teorema 3.7, §3.2.3, pp. 102–107; Sipser, 2012, Lema 1.55, pp. 67–70; Linz, 2017, Teorema 3.1, pp. 77–81; De Castro Korgi, 2004, §2.8):** *Para toda expresión regular $R$ sobre $\Sigma$, existe un autómata finito no determinista con transiciones espontáneas $\lambda$ ($\text{AFN-}\lambda$) $M = (Q, \Sigma, \delta, q_0, \{q_f\})$ tal que $L(M) = L(R)$.*
   - **Método constructivo (Construcción de Thompson, 1968, pp. 419–422):** Se procede por inducción estructural sobre el árbol sintáctico de $R$, manteniendo la **forma estándar** en cada autómata parcial $M_i$: un único estado inicial sin transiciones entrantes y un único estado de aceptación distinto del inicial sin transiciones salientes. Los casos base ($\emptyset$, $\lambda$ y $a \in \Sigma$) requieren exactamente 2 estados cada uno; la concatenación $R_1 R_2$ enlaza el estado final de $M_1$ con el estado inicial de $M_2$ mediante una transición $\lambda$ sin añadir estados nuevos; la unión $R_1 + R_2$ y la cerradura de Kleene $R_1^*$ introducen 2 estados nuevos ($q_i$ inicial y $q_f$ final) y 4 transiciones $\lambda$. Posteriormente, la eliminación de transiciones $\lambda$, la construcción de subconjuntos de Rabin y Scott (1959, Teorema 3, p. 119) y la minimización de Hopcroft (1971, pp. 189–196) transforman el $\text{AFN-}\lambda$ en el único AFD mínimo canónico equivalente.
2. **Dirección II — De Autómata Finito a Expresión Regular ($\text{AFD} \Longrightarrow \text{ER}$):**
   - **Enunciado (Hopcroft et al., 2007, Teoremas 3.4 y 3.5, §3.2.1–3.2.2, pp. 94–102; Sipser, 2012, Lema 1.60, pp. 70–76; Linz, 2017, Teorema 3.2, pp. 82–86; De Castro Korgi, 2004, §2.9–2.12):** *Si $L = L(A)$ para algún autómata finito determinista $A = (Q, \Sigma, \delta, q_0, F)$, entonces existe una expresión regular $R$ tal que $L(R) = L$.*
   - **Métodos constructivos:** En la literatura y en el curso se disponen tres procedimientos equivalentes: (a) la **inducción dinámica $R_{ij}^{(k)}$** de Kleene (1956) y McNaughton & Yamada (1960, pp. 39–47), donde $R_{ij}^{(k)} = R_{ij}^{(k-1)} + R_{ik}^{(k-1)}(R_{kk}^{(k-1)})^* R_{kj}^{(k-1)}$ representa las etiquetas de los caminos de $q_i$ a $q_j$ cuyos nodos internos pertenecen a $\{q_1, \dots, q_k\}$; (b) el **método de eliminación de estados sobre un Autómata Finito Generalizado (GNFA)** (Hopcroft et al., 2007, §3.2.2, pp. 98–102; Sipser, 2012, Definición 1.61, p. 71), que añade un estado inicial único $\vdash_{\text{ini}}$ y un estado final único $\text{fin}_{\dashv}$ y elimina uno por uno cada estado $q_{\text{elim}} \in Q$ actualizando toda arista entre $p$ y $r$ según $R'(p, r) = R(p, r) + R(p, q_{\text{elim}})R(q_{\text{elim}}, q_{\text{elim}})^* R(q_{\text{elim}}, r)$; y (c) el **sistema de ecuaciones características de lenguajes** resuelto mediante el **Lema de Arden** (Arden, 1961, pp. 133–151), el cual establece que si $\lambda \notin L(A)$, la ecuación lineal de lenguajes $X = AX + B$ posee la solución única $X = A^*B$.

---

## 4. Leyes Algebraicas de las Expresiones Regulares Empleadas para Simplificar

Dado que los algoritmos de eliminación de estados y de recurrencia $R_{ij}^{(k)}$ generan fórmulas con términos redundantes, en la Práctica 3 se aplicaron las leyes del **álgebra de Kleene** (Hopcroft et al., 2007, §3.4, Teorema 3.13, pp. 114–119; De Castro Korgi, 2004, §2.7) para reducir las expresiones obtenidas sin alterar el lenguaje denotado ($L(E_1) = L(E_2) \iff E_1 \equiv E_2$):

1. **Asociatividad y conmutatividad:** $(L + M) + N \equiv L + (M + N)$, $(LM)N \equiv L(MN)$, y $L + M \equiv M + L$ (la concatenación **no** es conmutativa: $ab \not\equiv ba$).
2. **Elementos identidad y elemento absorbente (aniquilador):**
   - $\emptyset + L \equiv L + \emptyset \equiv L$ ($\emptyset$ es el neutro de la unión).
   - $\lambda L \equiv L \lambda \equiv L$ ($\lambda$ es el neutro de la concatenación).
   - $\emptyset L \equiv L \emptyset \equiv \emptyset$ ($\emptyset$ es el aniquilador de la concatenación).
3. **Idempotencia de la unión:** $L + L \equiv L$.
4. **Distributividad de la concatenación respecto a la unión:**
   - Distributividad por la izquierda: $L(M + N) \equiv LM + LN$.
   - Distributividad por la derecha: $(M + N)L \equiv ML + NL$.
5. **Leyes de la cerradura de Kleene:**
   - $(L^*)^* \equiv L^*$, $\emptyset^* \equiv \lambda$, y $\lambda^* \equiv \lambda$.
   - Despliegue inductivo de la estrella: $L^* \equiv \lambda + LL^* \equiv \lambda + L^*L$.
   - Absorción de $\lambda$: $(L + \lambda)^* \equiv L^*$ y $\lambda + L^* \equiv L^*$.
6. **Identidades de Arden, deslizamiento y denesting (usadas en los ejercicios 254–258 y 276–278):**
   - Regla de desplazamiento (shifting): $L(ML)^* \equiv (LM)^*L$.
   - Regla de desanidamiento (denesting): $(L + M)^* \equiv (L^*M)^*L^* \equiv L^*(ML^*)^*$. En particular, en los ejercicios 254, 277 y 278 permite simplificar $0^*1(1 + 00^*1)^* = 0^*1(\lambda + 00^*)^*1^* \equiv (0 + 1)^*1$ y $(a + b^*a)^*b(a^*b)^* \equiv (a + b)^*b$.

---

## 5. Diferencia entre las Expresiones Regulares Teóricas y las de los Lenguajes de Programación

En la teoría de la computación, una expresión regular se restringe estrictamente a los operadores regulares ($+$, concatenación y $*$) y a azúcares sintácticos que se expanden en ellos sin incrementar el poder expresivo (como clases de caracteres `[0-9]` $= 0+1+\cdots+9$, el cuantificador opcional `R?` $= R + \lambda$, la cerradura positiva `R+` $= RR^*$ o la repetición acotada `R{m,n}`). Toda expresión regular teórica de longitud $m$ puede convertirse en un AFN de $\mathcal{O}(m)$ estados y simularse sobre una cadena $w$ en tiempo lineal $\mathcal{O}(m \cdot |w|)$ o en $\mathcal{O}(|w|)$ tras compilarse a un AFD (Thompson, 1968; Cox, 2007).

En contraste, las bibliotecas de expresiones regulares de los lenguajes de programación modernos —como el módulo `re` de Python, PCRE (Perl Compatible Regular Expressions), Java, JavaScript o .NET— incorporan extensiones no regulares tales como **referencias hacia atrás (*backreferences*)** `\1, \2`, aserciones de búsqueda anticipada (*lookahead/lookbehind*) y subrutinas recursivas (Friedl, 2006, Cap. 4; Python Software Foundation, 2025b).

### 5.1 Caso de Estudio: El Patrón con Referencia hacia Atrás `(a*)b\1` y Demostración de No Regularidad

Considérese el patrón `(a*)b\1` en la sintaxis de `re` de Python sobre el alfabeto $\Sigma = \{a, b\}$. El primer grupo de captura `(a*)` consume una secuencia arbitraria $a^n$ ($n \ge 0$), a continuación se exige el símbolo literal `b`, y la retorreferencia `\1` obliga a que el sufijo restante sea **idéntico carácter por carácter** a la subcadena capturada por el primer grupo. Por consiguiente, el lenguaje descrito por `(a*)b\1` es:
$$L = \{ a^n b a^n \mid n \ge 0 \}$$

> **Proposición:** *El lenguaje $L = \{a^n b a^n \mid n \ge 0\}$ descrito por `(a*)b\1` **no es regular**.*
>
> **Demostración formal mediante el Lema del Bombeo (Hopcroft et al., 2007, Teorema 4.1, p. 128; Sipser, 2012, Teorema 1.70, p. 78):**
> Supóngase por reducción al absurdo que $L$ es un lenguaje regular. Entonces existe una constante de bombeo $p \ge 1$ (correspondiente al número de estados de algún AFD que reconoce $L$) tal que toda cadena $w \in L$ con $|w| \ge p$ puede descomponerse en tres partes $w = xyz$ satisfaciendo simultáneamente:
> 1. $|xy| \le p$,
> 2. $|y| \ge 1$ ($y \neq \lambda$), y
> 3. Para todo entero $k \ge 0$, la cadena bombeada $xy^kz$ pertenece a $L$.
>
> Elíjase la cadena testigo $w = a^p b a^p$. Claramente $w \in L$ (tomando $n = p$) y su longitud es $|w| = 2p + 1 \ge p$. Sea $w = xyz$ cualquier partición que cumpla las condiciones (1) y (2):
> - Como $|xy| \le p$ y los primeros $p$ símbolos de $w = a^p b a^p$ son exclusivamente letras $a$, tanto $x$ como $y$ constan únicamente de símbolos $a$; es decir, $x = a^r$ e $y = a^s$ con $r + s \le p$.
> - Por la condición (2), $|y| \ge 1 \implies s \ge 1$. El resto de la cadena es $z = a^{p - r - s} b a^p$.
> - Tomando $k = 2$ (o bien $k = 0$) en la condición (3), se obtiene la cadena bombeada:
>   $$xy^2z = a^r (a^s)^2 a^{p - r - s} b a^p = a^{p + s} b a^p$$
> - Puesto que $s \ge 1$, el número de símbolos $a$ antes de la $b$ es $p + s > p$, mientras que el número de símbolos $a$ después de la $b$ es $p$. Por lo tanto, $xy^2z \notin L$, lo que contradice la condición (3) del Lema del Bombeo.
>
> En consecuencia, ningún autómata finito puede reconocer $L = \{a^n b a^n \mid n \ge 0\}$. Intuitivamente, para verificar la igualdad entre el prefijo $a^n$ y el sufijo $a^n$ tras leer la $b$, una máquina necesita recordar el valor arbitrariamente grande de $n$, lo cual exige memoria ilimitada $\Omega(\log n)$ o una pila (de hecho, $L$ es libre de contexto Tipo 2, generado por $S \to aSa \mid b$). Es más, el patrón `(a*)\1` o `(.*)\1` ($L = \{ww \mid w \in \Sigma^*\}$) ni siquiera es libre de contexto, sino sensible al contexto (Tipo 1), y el problema de emparejamiento con retorreferencias es **NP-completo**, obligando a motores como `re` de Python a emplear búsqueda con retroceso (*backtracking*) exponencial en el peor caso (Cox, 2007).

---

## 6. Cinco Aplicaciones Reales de las Expresiones Regulares en Computación

### 6.1 Análisis Léxico en Compiladores (*Scanners / Lexers*)
En la primera fase de un compilador (Aho, Lam, Sethi & Ullman, 2006, Cap. 3, pp. 109–188), el analizador léxico agrupa el flujo de caracteres del código fuente en componentes léxicos (*tokens*) eliminando espacios y comentarios. Herramientas como **Flex/Lex** o el tokenizador de Python compilan las expresiones regulares de cada categoría léxica en un único AFD mínimo que opera bajo la regla de coincidencia más larga (*maximal munch*):
- **Expresión regular concreta (identificadores y literales flotantes en C/Python):**
  - En notación del curso (con $L = a+\cdots+z+A+\cdots+Z$ y $D = 0+\cdots+9$):
    $$\text{Identificador: } (L + \_) (L + D + \_)^* \qquad \text{Flotante: } DD^* . DD^* ((e + E)(+ + - + \lambda)DD^* + \lambda)$$
  - En sintaxis de Flex / `re`: `[a-zA-Z_][a-zA-Z0-9_]*` y `[0-9]+\.[0-9]+([eE][+-]?[0-9]+)?`.
- **Funcionamiento:** El estado inicial bifurca según si el primer carácter pertenece a $L \cup \{\_\}$ (entrando al sub-AFD de identificadores, que permanece en aceptación mientras lea letras, dígitos o guiones bajos) o a $D$ (consumiendo la parte entera, exigiendo el punto decimal `.`, la mantisa fraccionaria y opcionalmente el exponente científico `e`/`E`).

### 6.2 Búsqueda de Patrones en Texto y Refactorización de Código
Editores e IDEs modernos, así como motores de indexación de código a gran escala (como `ripgrep`, Google Code Search o Hyperscan de Wang et al., 2019), utilizan expresiones regulares compiladas en autómatas deterministas vectorizados para localizar declaraciones o llamadas en millones de líneas en milisegundos.
- **Expresión regular concreta (localizar llamadas a `print` o `printf` en código fuente):**
  - En notación del curso: `\text{print}(f + \lambda)\ (A + \  + " + ' + ,)*\)`
  - En sintaxis POSIX ERE / `grep -E`: `\bprintf?\([^)]*\)`
- **Funcionamiento:** El autómata reconoce el prefijo literal `print`, permite opcionalmente el carácter `f` mediante la unión $(f + \lambda)$ (cubriendo tanto `print(...)` como `printf(...)`), exige el paréntesis de apertura `(`, consume en un bucle de cerradura de Kleene todos los caracteres del argumento hasta encontrar el paréntesis de cierre `)`.

### 6.3 Validación Estructural de Datos en Sistemas de Información
Los formularios web, APIs REST y esquemas JSON Schema validan en la frontera del sistema identificadores fiscales, correos electrónicos, URLs y fechas calendario antes de consultar bases de datos (Gribkoff, 2013; Resnick, 2008).
- **Expresión regular concreta (fecha calendario ISO 8601 `AAAA-MM-DD`, Norma ISO 8601-1:2019):**
  - En notación del curso (con $D = 0+\cdots+9$ y $N = 1+\cdots+9$):
    $$(19 + 20)DD - (0N + 1(0 + 1 + 2)) - (0N + (1 + 2)D + 3(0 + 1))$$
  - En sintaxis de `re`: `(19|20)[0-9]{2}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])`
- **Funcionamiento:** El primer bloque $(19 + 20)DD$ restringe el siglo a `19xx` o `20xx`; tras el primer guion `-`, la unión $(0N + 1(0+1+2))$ acepta únicamente meses de `01` a `09` o de `10` a `12` (rechazando `00` y `13`–`99`); tras el segundo guion, la unión de tres ramas valida días de `01`–`09`, `10`–`29` o `30`–`31`.

### 6.4 Filtrado Forense de Bitácoras (*Logs*) y Detección de Intrusiones (SIEM / WAF)
En administración de servidores web (Nginx, Apache) y sistemas de detección de intrusiones (Snort, Suricata), las expresiones regulares filtran millones de líneas de bitácoras para aislar errores HTTP `4xx`/`5xx` o intentos de ataque (Wang et al., 2019).
- **Expresión regular concreta (filtrar respuestas de error de servidor `500`, `502`, `503`, `504` en bitácoras HTTP):**
  - En notación del curso: `(GET + POST + PUT + DELETE)\ /R*\ HTTP/1.(0 + 1)"\ 50(0 + 2 + 3 + 4)\ DD*`
  - En sintaxis ERE: `"(GET|POST|PUT|DELETE) /[a-z0-9_./-]* HTTP/1\.[01]" 50[0234] [0-9]+`
- **Funcionamiento:** El autómata selecciona primero el método HTTP mediante una unión de cuatro ramas, consume la ruta del recurso `/R*` y la versión del protocolo `HTTP/1.0` o `HTTP/1.1`, y filtra específicamente el código de estado que inicia con `50` seguido de un símbolo en $\{0, 2, 3, 4\}$ y el tamaño de respuesta en bytes $DD^*$.

### 6.5 Automatización de Tareas y Procesamiento por Lotes en el Sistema Operativo
En entornos Unix/Linux y contenedores Docker (Merkel, 2014), los intérpretes de comandos (`bash`), `find`, `sed` y `awk` emplean expresiones regulares para seleccionar archivos por extensión, transformar configuraciones y automatizar canalizaciones de integración continua.
- **Expresión regular concreta (seleccionar archivos de pruebas o módulos de las prácticas 1 a 4 en el repositorio):**
  - En notación del curso (con $A = a+\cdots+z+0+\cdots+9$):
    `((src/ + tests/)(test_ + \lambda)practica(1 + 2 + 3 + 4) + automatas/practica(3 + 4)/A(A + -)*).(py + jff)`
  - En sintaxis ERE (`find . -regextype posix-extended`): `((src/|tests/)(test_)?practica[1-4]|automatas/practica[34]/[a-z0-9-]+)\.(py|jff)`
- **Funcionamiento:** La primera rama de unión reconoce rutas en `src/` o `tests/` con el prefijo opcional `test_` seguido de `practica` y el número de práctica en $\{1, 2, 3, 4\}$; la segunda rama reconoce rutas bajo `automatas/practica3/` o `automatas/practica4/`; finalmente, la concatenación con `.(py + jff)` exige que el archivo termine exactamente en extensión `.py` o `.jff`.

---

## 7. Referencias Bibliográficas Consultadas

Todas las referencias citadas en esta investigación se encuentran registradas en formato APA 7.ª edición en [`docs/bibliografia.md`](../bibliografia.md):
- Aho, A. V., Lam, M. S., Sethi, R., & Ullman, J. D. (2006). *Compilers: Principles, techniques, and tools* (2.ª ed., Cap. 3). Addison-Wesley.
- Arden, D. N. (1961). Delayed-logic and finite-state machines. *Proceedings of SWCT 1961*, 133–151.
- Chomsky, N. (1956). Three models for the description of language. *IRE Transactions on Information Theory*, *2*(3), 113–124.
- Cox, R. (2007). Regular expression matching can be simple and fast. https://swtch.com/~rsc/regexp/regexp1.html
- De Castro Korgi, R. (2004). *Teoría de la computación: Lenguajes, autómatas, gramáticas* (§2.7–2.12). Universidad Nacional de Colombia.
- Friedl, J. E. F. (2006). *Mastering regular expressions* (3.ª ed.). O'Reilly Media.
- Hopcroft, J. E., Motwani, R., & Ullman, J. D. (2007). *Introducción a la teoría de autómatas, lenguajes y computación* (3.ª ed., Caps. 3 y 4). Pearson Educación.
- Kleene, S. C. (1956). Representation of events in nerve nets and finite automata. En *Automata studies* (pp. 3–41). Princeton University Press.
- Linz, P. (2017). *An introduction to formal languages and automata* (6.ª ed., Cap. 3 y §11.4). Jones & Bartlett Learning.
- McNaughton, R., & Yamada, H. (1960). Regular expressions and state graphs for automata. *IRE Transactions on Electronic Computers*, *EC-9*(1), 39–47.
- Rabin, M. O., & Scott, D. (1959). Finite automata and their decision problems. *IBM Journal of Research and Development*, *3*(2), 114–125.
- Sipser, M. (2012). *Introduction to the theory of computation* (3.ª ed., §1.3–1.4). Cengage Learning.
- Thompson, K. (1968). Programming techniques: Regular expression search algorithm. *Communications of the ACM*, *11*(6), 419–422.
