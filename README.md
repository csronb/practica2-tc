# Instituto Politécnico Nacional
## Escuela Superior de Cómputo (ESCOM)

---

### Práctica 3: Uso de la Herramienta JFLAP para Convertir Autómatas Finitos Deterministas a Expresiones Regulares y Extensión de Software para Simular Autómatas No Deterministas, AFN con Transiciones Lambda y Minimización de AFD

| Campo | Información |
| :--- | :--- |
| **Alumno (Nombre completo)** | `[NOMBRE COMPLETO DEL ALUMNO]` |
| **Número de Boleta** | `[NÚMERO DE BOLETA]` |
| **Grupo** | `[GRUPO, EJ. 4CM1]` |
| **Carrera** | Ingeniería en Sistemas Computacionales (Plan 2020) |
| **Unidad de Aprendizaje** | Teoría de la Computación |
| **Profesor(a)** | `[NOMBRE DEL PROFESOR(A)]` |
| **Fecha de Entrega (Práctica 3)** | **Miércoles 4 de noviembre de 2026** (Etiqueta de Git: `practica3`) |
| **Fecha de Entrega (Práctica 2)** | 6 de octubre de 2026 |
| **Versión de Flet y pytest en contenedor** | `flet[web]==0.86.5`, `pytest==8.3.4` (`python:3.12-slim-trixie`) |

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

### 2. Instrucciones de Uso del Contenedor Oficial y de las Funciones Nuevas (Práctica 3)

#### A) Levantar el contenedor del curso (`ContenedorV1`: [`Dockerfile`](Dockerfile) y [`compose.yaml`](compose.yaml))

Desde la raíz del repositorio:

```bash
docker compose up -d --build          # 1. Construir la imagen y prender el contenedor
docker compose exec teoria bash       # 2. Entrar al contenedor en /trabajo
```

Una vez dentro del contenedor, puede comprobar el entorno del curso y todos los algoritmos de la Práctica 3 ejecutando:

```bash
bash extras/comprobar.sh              # Comprobación oficial del entorno (M1, pytest, volumen y Flet)
bash extras/comprobar_practica3.sh    # Comprobación completa de la Práctica 3 y casos de la Lista 3
pytest -v                             # Ejecutar toda la suite de pruebas (Prácticas 1, 2 y 3)
```

Para ejecutar las pruebas en las tres versiones de Python (3.11, 3.12 y 3.13) tal como en la Integración Continua:

```bash
docker compose -f entorno/compose.yml run --rm py311 pytest -q
docker compose -f entorno/compose.yml run --rm py312 pytest -q
docker compose -f entorno/compose.yml run --rm py313 pytest -q
```

#### B) Uso de las funciones nuevas desde la Interfaz Gráfica Web (`http://localhost:8550`)

Dentro del contenedor (`docker compose exec teoria bash`), inicie la interfaz interactiva:

```bash
python src/app.py
```

Abra **`http://localhost:8550`** en el navegador de su computadora:
1. **Importar cualquier caso `.jff` y consultar la cerradura $\lambda$ (2.1):**
   * Seleccione cualquier caso de prueba en el menú desplegable **`Cargar caso de prueba de la Práctica 3`** (ej. `Ej. 196` a `Ej. 200`, `Ej. 191` a `Ej. 194`, `Ej. 260` a `Ej. 263` o `Ej. 151` a `Ej. 157`) o escriba la ruta de cualquier archivo `.jff` y pulse **Importar Archivo**.
   * Elija un estado en **`Estado q para consultar Cl_λ({q})`** para visualizar su cerradura $\lambda$ individual, además de la columna `Cl_λ({q})` en la tabla general.
2. **Simulación directa paso a paso de un AFN-$\lambda$ (2.1):**
   * En la sección 3, ingrese la cadena a evaluar y pulse **Simular Directamente (Traza Completa)** o recorra con **◀ Paso Anterior / Paso Siguiente ▶** para inspeccionar en cada paso el conjunto de estados activos **antes de aplicar la $\lambda$-clausura** y **después de aplicar la $\lambda$-clausura**.
3. **Transformaciones paso a paso (2.2, 2.3 y 2.4):**
   * Pulse **`2.2 Eliminar Transiciones λ (AFN-λ → AFN)`** para ver los estados que pasan a ser de aceptación y las transiciones añadidas con su camino justificado.
   * Pulse **`2.3 Construcción de Subconjuntos (AFN → AFD)`** para generar únicamente los subconjuntos alcanzables desde el estado inicial y consultar la tabla de transiciones y por qué cada subconjunto es o no de aceptación ($S \cap F \neq \emptyset$).
   * Pulse **`2.4 Minimizar AFD (Particiones y Tabla de Pares)`** para eliminar estados inaccesibles y visualizar cada ronda de refinamiento de particiones ($\Pi_0, \Pi_1, \dots$) y cada ronda de la tabla de pares distinguibles.
   * Ingrese la ruta de un segundo autómata y pulse **`2.4 Comparar Equivalencia con 2º AFD`** para decidir si ambos AFD son equivalentes a partir de sus AFD mínimos.
4. **Validación de lote de cadenas desde archivo `.txt` (2.5):**
   * En la sección 4, indique el archivo de entrada (por defecto `automatas/practica3/casos-de-prueba/lote_cadenas_prueba.txt`) y la ruta de salida (`salidas/reporte_validacion_lote.txt`), y pulse **Validar Archivo de Cadenas y Guardar Reporte**.

#### C) Uso directo del núcleo en Python puro sin abrir la interfaz

```python
import sys
sys.path.insert(0, "src")
from formatos import cargar_automata
from expresiones import tres_metodos

# Cargar un AFN-λ desde archivo .jff de JFLAP
m = cargar_automata("automatas/practica3/casos-de-prueba/ej199_afnd_lambda.jff")
print("Cl_λ(A) =", m.lambda_clausura_estado("A"))
traza = m.simular_directo_afnd_lambda("011")
res_sin_lambda = m.eliminar_transiciones_lambda_detallado()
res_subconjuntos = m.construccion_subconjuntos_detallada()
res_minimo = res_subconjuntos.afd.minimizar_afd_detallado()
```

---

## Procedencia y Reutilización de las Prácticas 1 y 2

De acuerdo con las condiciones generales del curso, este repositorio continúa sobre el software interactivo de las prácticas anteriores:

* **Enlace al repositorio de la Práctica 1**: [**https://github.com/csronb/practica1-tc**](https://github.com/csronb/practica1-tc)
* **Etiqueta de entrega de la Práctica 3**: `practica3` (`git tag -a practica3 -m "Entrega de la Practica 3"`)

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
practica2-tc/
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
│   └── ejemplos/
│       ├── afd.py
│       ├── m1_par_de_ceros.jff
│       └── test_afd.py
├── src/
│   ├── lenguajes.py
│   ├── automata.py
│   ├── expresiones.py
│   ├── formatos.py
│   └── app.py
├── tests/
│   ├── test_practica2.py
│   └── test_practica3.py
└── evidencias/
    ├── practica3/                    # Capturas SVG de JFLAP y del simulador (Práctica 3)
    ├── git/
    ├── ci/
    ├── jflap/
    └── app/
```
