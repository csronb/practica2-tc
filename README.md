# Instituto Politécnico Nacional
## Escuela Superior de Cómputo (ESCOM)

---

### Práctica 4: Uso de las Expresiones Regulares y Extensión de Software para Convertir Expresiones Regulares

| Campo | Información |
| :--- | :--- |
| **Alumno (Nombre completo)** | `César Octavio Navarro Bahena` |
| **Número de Boleta** | `2023630464` |
| **Grupo** | `4CM4` |
| **Carrera** | Ingeniería en Sistemas Computacionales (Plan 2020) |
| **Unidad de Aprendizaje** | Teoría de la Computación |
| **Profesor(a)** | `M. en C. Gabriel Hurtado Avilés` |
| **Entrega actual (Práctica 4)** | Etiqueta de Git: `practica4` |
| **Entrega previa (Práctica 3)** | Miércoles 4 de noviembre de 2026 (Etiqueta de Git: `practica3`) |
| **Entrega previa (Práctica 2)** | 6 de octubre de 2026 |
| **Versión de Flet y pytest en contenedor** | `flet[web]==0.86.5`, `pytest==8.3.4` (`python:3.12-slim-trixie`) |

---

## Sección de la Práctica 4 (Entrega con etiqueta `practica4`)

### 1. Índice de Documentos y Recursos de la Práctica 4

1. [**Ejercicio 1. Investigación sobre expresiones regulares (`docs/practica4/01-investigacion-er.md`)**](docs/practica4/01-investigacion-er.md)
   * Definición formal de lenguaje regular, expresión regular y operaciones de unión, concatenación y cerradura de Kleene.
   * Ubicación de los lenguajes regulares dentro de la jerarquía de Chomsky (Tipo 3).
   * Enunciado del Teorema de Kleene en ambas direcciones con referencias exactas a la bibliografía oficial ([`docs/bibliografia.md`](docs/bibliografia.md)).
   * Leyes algebraicas de las expresiones regulares empleadas en la Práctica 3 para simplificar.
   * Diferencia entre expresiones regulares teóricas y las de los lenguajes de programación (`re`), demostrando mediante el Lema del Bombeo por qué `(a*)b\1` ($L = \{a^n b a^n \mid n \ge 0\}$) no es regular.
   * Cinco aplicaciones reales en computación (análisis léxico en compiladores, búsqueda de patrones en texto, validación de datos, filtrado de bitácoras y automatización en el sistema operativo), cada una con una expresión regular concreta y la explicación de su funcionamiento.
2. [**Ejercicio 2. De expresión regular a autómata (`docs/practica4/02-er-a-automata.md`)**](docs/practica4/02-er-a-automata.md)
   * Analizador sintáctico por descenso recursivo (`analizar_expresion`, `ErrorSintaxisER`) que respeta la precedencia (`*` > concatenación > `+`) y los paréntesis, e indica la posición exacta del error ante expresiones mal formadas.
   * Construcción del $\text{AFN-}\lambda$ equivalente mediante la Parte I del Teorema de Kleene (forma estándar de Thompson) mostrando los autómatas parciales paso a paso (`er_a_afn_lambda_detallado`), encadenado con eliminación de transiciones $\lambda$, construcción de subconjuntos y minimización hasta obtener el AFD mínimo (`er_a_automata_completo`), exportación a `.jff` y validación de cadenas.
   * **Casos de prueba:** Lista 3 (ejercicios 241 a 253) y Lista 4 (ejercicios 272, 273 y 278) en [`automatas/practica4/er-a-automata/`](automatas/practica4/er-a-automata/).
3. [**Ejercicio 3. De autómata a expresión regular (`docs/practica4/03-automata-a-er.md`)**](docs/practica4/03-automata-a-er.md)
   * Importación de un AFD desde `.jff` verificando que sea determinista e indicando, en caso contrario, qué estado y qué símbolo lo impiden (`verificar_determinismo`).
   * Obtención de la expresión regular por el método de eliminación de estados mostrando el autómata finito generalizado (GNFA) después de cada estado eliminado (`eliminacion_de_estados_detallada`).
   * Comparación con la expresión obtenida con JFLAP en la Práctica 3 demostrando su equivalencia al convertir ambas expresiones en AFD mínimos con el Ejercicio 2 y compararlos con la prueba de equivalencia de la Práctica 3 (`comparar_expresiones_por_afd_minimo`).
   * **Casos de prueba:** Lista 3 (ejercicios 254 a 258 / los cinco autómatas del Ejercicio 1 de la Práctica 3) y Lista 4 (ejercicios 276 y 277) en [`automatas/practica4/afd-a-er/`](automatas/practica4/afd-a-er/).
4. [**Ejercicio 4. Aplicaciones: validadores (`docs/practica4/04-validadores.md`)**](docs/practica4/04-validadores.md)
   * Cuatro validadores implementados en [`src/validadores.py`](src/validadores.py): **correo electrónico** (`correo`), **número telefónico en formato nacional** (`telefono_nacional`), **URL** (`url`) y **fecha en distintos formatos** (`fecha`), con sus archivos `.jff` en [`automatas/practica4/validadores/`](automatas/practica4/validadores/).
   * Presentación de cada expresión en la notación del curso y su traducción a `re` de Python, conteo de estados del AFD antes y después de minimizar, justificación de casos fuera de la expresión, norma consultada (RFC 5322/5321, Plan IFT, RFC 3986, ISO 8601-1:2019) y prueba de **congruencia entre modelos** en [`tests/test_practica4.py`](tests/test_practica4.py) sobre **500 cadenas válidas e inválidas por validador** (2,000 cadenas en total).
5. [**Capturas y evidencias de la Práctica 4 (`evidencias/practica4/`)**](evidencias/practica4/) y [**Bibliografía General APA 7.ª Edición (`docs/bibliografia.md`)**](docs/bibliografia.md).

---

### 2. Notación Aceptada por el Analizador Sintáctico (`src/expresiones.py`)

El analizador sintáctico (`analizar_expresion`) acepta exclusivamente la notación formal del curso:

| Elemento | Símbolo(s) aceptado(s) | Precedencia y asociatividad | Descripción |
| :--- | :---: | :--- | :--- |
| **Cerradura de Kleene** | `*` | **1.ª (mayor)** — unario postfijo | Cero o más repeticiones del factor inmediato anterior (`R*`). |
| **Concatenación** | Yuxtaposición implícita (o `·`) | **2.ª (intermedia)** — asociativa por la izquierda | Concatenación de factores consecutivos (`ab` o `a·b`). |
| **Unión** | `+` | **3.ª (menor)** — asociativa por la izquierda | Unión de alternativas (`R + S`). |
| **Agrupación** | `(` y `)` | Máxima (altera el orden de evaluación) | Paréntesis balanceados no vacíos `(R)`. |
| **Palabra vacía** | `λ` (también `epsilon` o `ε`) | Constante atómica | Lenguaje unitario $\{\lambda\}$. |
| **Lenguaje vacío** | `∅` | Constante atómica | Lenguaje vacío $\emptyset$. |
| **Escape literal** | `\c` | Constante atómica | Interpreta literalmente el carácter `c` (ej. `\+`, `\*`, `\(`, `\)`, `\?`, `\ ` para espacio). |

#### Clases de Símbolos Declaradas Explícitamente para el Ejercicio 4 (`CLASES_PREDEFINIDAS`)

Cuando se activa el soporte de clases declaradas (`clases=CLASES_PREDEFINIDAS`), el analizador expande las siguientes abreviaturas documentadas en [`src/validadores.py`](src/validadores.py):
- `D = 0 + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9` (`[0-9]`, dígitos decimales)
- `N = 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9` (`[1-9]`, dígitos sin el cero)
- `P = 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9` (`[2-9]`, primer dígito de NIR telefónico nacional IFT)
- `L = a + b + c + ··· + z` (`[a-z]`, letras minúsculas ASCII)
- `A = a + b + ··· + z + 0 + 1 + ··· + 9` (`[a-z0-9]`, alfanuméricos en minúscula)
- `U = a + b + ··· + z + 0 + 1 + ··· + 9 + _` (`[a-z0-9_]`, carácter de usuario local de correo)
- `R = a + b + ··· + z + 0 + 1 + ··· + 9 + _ + - + .` (`[a-z0-9_.-]`, carácter de segmento de ruta/consulta URL)
- `T = 1 + 3 + 5 + 7 + 8` (`[13578]`, meses de 31 días con prefijo `0`)
- `C = 4 + 6 + 9` (`[469]`, meses de 30 días con prefijo `0`)

---

### 3. Instrucciones de Uso de las Nuevas Funciones (Práctica 4)

#### A) Comprobación en el Contenedor Oficial (`ContenedorV1`) y Pruebas Automatizadas (`pytest`)

```bash
docker compose up -d --build          # 1. Construir y levantar el contenedor
docker compose exec teoria bash       # 2. Abrir una terminal dentro del contenedor
bash extras/comprobar_practica4.sh    # 3. Ejecutar la comprobación integral de la Práctica 4
pytest -v                             # 4. Ejecutar las 83 pruebas (Prácticas 2, 3 y 4)
```

#### B) Uso desde la Interfaz Gráfica Flet (`python src/app.py` $\to$ `http://localhost:8550`)

1. **Sección 6 — Ejercicio 2 (De expresión regular a autómata):**
   * Elija cualquiera de los casos de prueba de la Lista 3 (`241`–`253`) o de la Lista 4 (`272a`–`272e`, `273`, `278`), o escriba cualquier expresión regular en la notación del curso y pulse **`Construir AFN-λ, AFN, AFD y AFD Mínimo`**.
   * Si la expresión está mal formada, se mostrará el mensaje de error indicando la **posición exacta** del carácter problemático.
   * Recorra cada pieza parcial con **`◀ Pieza Parcial Anterior`** / **`Pieza Parcial Siguiente ▶`**, exporte los autómatas a `.jff` con **`Exportar Autómatas a .jff`** y valide cadenas en **`Validar Cadena(s) con el Autómata`**.
2. **Sección 7 — Ejercicio 3 (De autómata a expresión regular):**
   * Seleccione un archivo `.jff` (`ej254` a `ej258`, `ej276`, `ej277`, o un caso no determinista de prueba) y pulse **`Importar .jff, Verificar Determinismo y Eliminar Estados`**.
   * Si el autómata no es determinista, el software indica explícitamente **qué estado y qué símbolo lo impiden**.
   * Si es un AFD, navegue por el GNFA después de cada estado eliminado con **`◀ Estado GNFA Anterior`** / **`Estado GNFA Siguiente ▶`** y consulte la demostración de equivalencia con la expresión de JFLAP mediante sus AFD mínimos.
3. **Sección 8 — Ejercicio 4 (Aplicaciones: validadores):**
   * Seleccione uno de los cuatro validadores (`correo`, `telefono_nacional`, `url`, `fecha`), consulte su expresión en la notación del curso, su traducción a `re` de Python, el número de estados del AFD antes y después de minimizar, y la justificación normativa.
   * Escriba cualquier texto (o seleccione un ejemplo válido/inválido) y pulse **`Validar Texto con el Autómata (Ejercicio 2)`** o **`Comprobar Congruencia en 500 Cadenas vs re.fullmatch`**.

#### C) Uso Programático desde Python Puro

```python
import sys
sys.path.insert(0, "src")
from expresiones import (
    analizar_expresion,
    er_a_automata_completo,
    eliminacion_de_estados_detallada,
    comparar_expresiones_por_afd_minimo,
)
from formatos import cargar_automata, guardar_automata
from validadores import obtener_validador, verificar_congruencia_validador

# Ejercicio 2: De expresión regular a AFN-λ, AFN, AFD y AFD mínimo
res = er_a_automata_completo("(a + b)*b", alfabeto=["a", "b"])
print("Piezas Kleene I:", len(res.kleene_uno.pasos), "| Estados AFN-λ:", len(res.afn_lambda.estados))
print("Estados AFD:", len(res.afd.estados), "-> AFD mínimo:", len(res.afd_minimo.estados))
guardar_automata(res.afd_minimo, "salidas/afd_minimo_278.jff")

# Ejercicio 3: De AFD (.jff) a expresión regular por eliminación de estados (GNFA)
afd = cargar_automata("automatas/practica4/afd-a-er/ej276_multiplo_3_a.jff")
gnfa = eliminacion_de_estados_detallada(afd)
comp = comparar_expresiones_por_afd_minimo(gnfa.expresion_texto, "(b + ab*ab*a)*", alfabeto=["a", "b"])
print("ER obtenida:", gnfa.expresion_texto, "| Equivalente con (b+ab*ab*a)*:", comp.equivalentes)

# Ejercicio 4: Validadores y congruencia sobre 500 cadenas frente a re.fullmatch
val_correo = obtener_validador("correo")
print(val_correo.validar("cesar.navarro@alumno.ipn.mx").detalle)
cong = verificar_congruencia_validador("correo", total=500, semilla=2026)
print("Congruencia 500 cadenas:", cong.coincidencias_afd_minimo_vs_re, "/", cong.total_cadenas)
```

---

## Sección de la Práctica 3 (Entrega con etiqueta `practica3`)

### 1. Índice de Documentos y Recursos de la Práctica 3

1. [**Ejercicio 1. Conversión de AFD a expresiones regulares (`docs/practica3/01-afd-a-er-jflap.md`)**](docs/practica3/01-afd-a-er-jflap.md)
   * **1.1 Conversión con JFLAP 7.1:** Análisis estructural previo de ciclos y ramas, eliminación paso a paso con *Convert FA to RE*, verificación con *Convert to NFA* y *Compare Equivalence*, prueba de 5 cadenas por autómata y simplificación algebraica justificada con las leyes de Hopcroft, Motwani y Ullman (2007, Sección 3.4).
   * **1.2 Comparación de métodos:** Resolución a mano y en software ([`src/expresiones.py`](src/expresiones.py)) por los tres métodos del curso: **Eliminación de estados (GNFA)**, **Construcción recursiva de expresiones $R_{ij}^{(k)}$** y **Sistema de ecuaciones con el Lema de Arden**.
   * **Archivos `.jff` y expresiones:** [`automatas/practica3/afd-a-er/`](automatas/practica3/afd-a-er/).
2. [**Ejercicio 2. Extensión del software interactivo (`docs/practica3/02-software.md`)**](docs/practica3/02-software.md)
   * **2.1 Cerradura $\lambda$ y simulación directa:** Cálculo de $Cl_\lambda(q)$ por estado, selector individual en la interfaz y simulación directa mostrando en cada paso el conjunto de estados activos **antes y después** de aplicar la cerradura $\lambda$ (Casos de prueba: Lista 3, ejercicios 196 a 200).
   * **2.2 Eliminación de transiciones $\lambda$:** Transformación AFN-$\lambda \to$ AFN mostrando explícitamente las transiciones añadidas y los estados que pasan a ser de aceptación.
   * **2.3 Construcción de subconjuntos:** Transformación AFN $\to$ AFD construyendo únicamente los subconjuntos alcanzables desde el estado inicial y justificando cuáles resultan de aceptación ($S \cap F \neq \emptyset$) (Casos de prueba: Lista 3, ejercicios 191 a 194 y 260 a 263).
   * **2.4 Minimización de AFD y equivalencia:** Eliminación de estados inaccesibles, obtención del AFD mínimo mostrando cada ronda de **refinamiento de particiones ($\Pi_k$)** y de la **tabla de pares distinguibles**, y decisión de equivalencia de dos AFD a partir de sus autómatas mínimos (Casos de prueba: Lista 3, ejercicios 151 a 157).
   * **2.5 Validación de varias cadenas:** Carga de un archivo `.txt` con una cadena por línea, validación completa y guardado del informe en disco.
   * **2.6 Pruebas automatizadas (`pytest`):** Suite [`tests/test_practica3.py`](tests/test_practica3.py) ejecutada en integración continua con las tres versiones de Python (3.11, 3.12 y 3.13).
   * **Casos de prueba `.jff` de la Lista 3:** [`automatas/practica3/casos-de-prueba/`](automatas/practica3/casos-de-prueba/).
   * **Capturas y evidencias de la Práctica 3:** [`evidencias/practica3/`](evidencias/practica3/).
3. [**Ejercicio 3. Documentación de los algoritmos (`docs/practica3/03-algoritmos.md`)**](docs/practica3/03-algoritmos.md)
   * Enunciado formal y resultado teórico con referencia exacta al libro y sección de la bibliografía oficial ([`docs/bibliografia.md`](docs/bibliografia.md)), pseudocódigo y correspondencia línea por línea con [`src/automata.py`](src/automata.py), ejemplos de la Lista 3 resueltos a mano vs. software, y estimación del número de pasos en función de $|Q|$ y $|\Sigma|$.

---

## Procedencia y Reutilización de las Prácticas 1, 2 y 3

De acuerdo con las condiciones generales del curso, este repositorio continúa sobre el software interactivo de las prácticas anteriores:

* **Enlace al repositorio de la Práctica 1**: [**https://github.com/csronb/practica1-tc**](https://github.com/csronb/practica1-tc)
* **Etiqueta de entrega de la Práctica 3**: `practica3` (`git tag -a practica3 -m "Entrega de la Practica 3"`)
* **Etiqueta de entrega de la Práctica 4**: `practica4` (`git tag -a practica4 -m "Entrega de la Practica 4"`)

---

## Convención sobre la Transición Lambda ($\lambda$) en los Archivos

Tal como se especifica en el **Anexo 3**, en los tres formatos de archivo soportados por el simulador (`.jff`, `.json` y `.xml`), **la transición $\lambda$ (transición espontánea sin consumo de entrada) se representa mediante la cadena vacía `""` como símbolo leído**:
* En **`.jff` (JFLAP)**: `<read/>` vacío dentro de `<transition>`.
* En **`.json`**: `"lee": ""` dentro de cada entrada de `"transiciones"`.
* En **`.xml`**: atributo `lee=""` dentro de `<transicion desde="..." lee="" hacia="..."/>`.

---

## Índice de la Práctica 2 (Conservado en el Repositorio)

1. [**Ejercicio 1. Entorno de trabajo, flujo de ramas e integración continua**](docs/01-entorno.md)
2. [**Ejercicio 2. AFND y AFND-$\lambda$ en JFLAP**](docs/02-jflap.md)
3. [**Ejercicio 3. Simulador de autómatas con interfaz gráfica**](docs/03-simulador.md)
4. [**Ejercicio 4. Investigación y estado del arte**](docs/04-investigacion.md)
5. [**Ejercicio 5. Del artículo al autómata (Fantasmas de Pac-Man Ampliado)**](docs/05-del-articulo-al-automata.md)
6. [**Propuesta de artículo de investigación (Apartado 5.3)**](docs/propuesta.md)
7. [**Bibliografía General (APA 7.ª Edición — Fuentes Verificables)**](docs/bibliografia.md)

---

## Estructura General del Repositorio

```text
practica4-tc/
├── README.md
├── Dockerfile
├── compose.yaml
├── .gitattributes
├── .gitignore
├── requirements.txt
├── pytest.ini
├── .github/workflows/
│   └── pruebas.yml
├── docs/
│   ├── practica4/
│   │   ├── 01-investigacion-er.md    # Ejercicio 1 (Práctica 4: 3–4 cuartillas)
│   │   ├── 02-er-a-automata.md       # Ejercicio 2 (Práctica 4: ER -> AFN-λ -> AFD_min)
│   │   ├── 03-automata-a-er.md       # Ejercicio 3 (Práctica 4: AFD -> ER por GNFA)
│   │   └── 04-validadores.md         # Ejercicio 4 (Práctica 4: Validadores y 500 cadenas)
│   ├── practica3/
│   │   ├── 01-afd-a-er-jflap.md      # Ejercicio 1 (Práctica 3)
│   │   ├── 02-software.md            # Ejercicio 2, con capturas (Práctica 3)
│   │   └── 03-algoritmos.md          # Ejercicio 3 (Práctica 3)
│   ├── 01-entorno.md
│   ├── 02-jflap.md
│   ├── 03-simulador.md
│   ├── 04-investigacion.md
│   ├── 05-del-articulo-al-automata.md
│   ├── propuesta.md
│   └── bibliografia.md
├── automatas/
│   ├── practica4/
│   │   ├── er-a-automata/            # 40 .jff de Lista 3 (241–253) y Lista 4 (272a–e, 278)
│   │   ├── afd-a-er/                 # 7 .jff y expresiones de Lista 3 (254–258) y Lista 4 (276, 277)
│   │   └── validadores/              # 8 .jff (AFD y AFD mínimo de los 4 validadores)
│   ├── practica3/
│   │   ├── afd-a-er/                 # Los cinco .jff y sus expresiones regulares
│   │   └── casos-de-prueba/          # Los 20 .jff de la Lista 3 usados en las pruebas
│   ├── lista2-afd/
│   ├── lista3-afnd/
│   ├── lista3-afnd-lambda/
│   ├── conversiones/
│   └── aplicacion/
├── extras/
│   ├── comprobar.sh                  # Script oficial de comprobación (ContenedorV1)
│   ├── comprobar_practica3.sh        # Script de comprobación de la Práctica 3
│   ├── comprobar_practica4.sh        # Script de comprobación de la Práctica 4
│   └── ejemplos/
│       ├── afd.py
│       ├── m1_par_de_ceros.jff
│       └── test_afd.py
├── src/
│   ├── lenguajes.py
│   ├── automata.py
│   ├── expresiones.py
│   ├── validadores.py
│   ├── formatos.py
│   └── app.py
├── tests/
│   ├── test_practica2.py
│   ├── test_practica3.py
│   └── test_practica4.py
└── evidencias/
    ├── practica4/                    # Capturas SVG del simulador y pruebas (Práctica 4)
    ├── practica3/                    # Capturas SVG de JFLAP y del simulador (Práctica 3)
    ├── git/
    ├── ci/
    ├── jflap/
    └── app/
```
