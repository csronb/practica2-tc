# Instituto Politécnico Nacional
## Escuela Superior de Cómputo (ESCOM)

---

### Práctica 2: Autómatas Finitos No Deterministas (AFND) y Simulación de AFD con Interfaz Gráfica

| Campo | Información |
| :--- | :--- |
| **Alumno (Nombre completo)** | `[NOMBRE COMPLETO DEL ALUMNO]` |
| **Número de Boleta** | `[NÚMERO DE BOLETA]` |
| **Grupo** | `[GRUPO, EJ. 4CM1]` |
| **Carrera** | Ingeniería en Sistemas Computacionales (Plan 2020) |
| **Unidad de Aprendizaje** | Teoría de la Computación |
| **Profesor(a)** | `[NOMBRE DEL PROFESOR(A)]` |
| **Fecha de Entrega** | 6 de octubre de 2026 |
| **Versión de Flet utilizada** | `flet[web]==0.86.5` |

---

## Procedencia y Reutilización de la Práctica 1

De acuerdo con las instrucciones del **Ejercicio 1**, este repositorio reutiliza la configuración de contenedores (`entorno/Dockerfile`, `entorno/compose.yml`, `requirements.txt` y `pytest.ini`) así como el módulo puro de operaciones sobre cadenas y lenguajes ([`src/lenguajes.py`](src/lenguajes.py)) y sus pruebas unitarias desarrollados en la **Práctica 1**:

* **Enlace al repositorio de la Práctica 1**: [**https://github.com/csronb/practica1-tc**](https://github.com/csronb/practica1-tc)

---

## Convención sobre la Transición Lambda ($\lambda$) en los Archivos

Tal como se especifica en el **Anexo 3**, en los tres formatos de archivo soportados por el simulador (`.jff`, `.json` y `.xml`), **la transición $\lambda$ (transición espontánea sin consumo de entrada) se representa mediante la cadena vacía `""` como símbolo leído**:
* En **`.jff` (JFLAP)**: `<read/>` vacío dentro de `<transition>`.
* En **`.json`**: `"lee": ""` dentro de cada entrada de `"transiciones"`.
* En **`.xml`**: atributo `lee=""` dentro de `<transicion desde="..." lee="" hacia="..."/>`.

Esta convención garantiza que la exportación y la importación sean operaciones inversas exactas en los tres formatos.

---

## Índice de la Práctica

1. [**Ejercicio 1. Entorno de trabajo, flujo de ramas e integración continua**](docs/01-entorno.md)
   * Reutilización del entorno de la Práctica 1, flujo de 5 ramas funcionales fusionadas mediante Pull Request y configuración de GitHub Actions ([`.github/workflows/pruebas.yml`](.github/workflows/pruebas.yml)).
2. [**Ejercicio 2. AFND y AFND-$\lambda$ en JFLAP**](docs/02-jflap.md)
   * Clasificación justificada y cobertura del 100% de la Lista 2 (94–150) y Lista 3 (151–263) en [`automatas/lista2-afd/`](automatas/lista2-afd/), [`automatas/lista3-afnd/`](automatas/lista3-afnd/) y [`automatas/lista3-afnd-lambda/`](automatas/lista3-afnd-lambda/).
   * Diseño, validación con 5 cadenas válidas y 5 inválidas, recorridos con bifurcaciones, cálculo de $\lambda$-clausuras, conversiones completas en [`automatas/conversiones/`](automatas/conversiones/) y análisis de la cota $2^n$.
3. [**Ejercicio 3. Simulador de autómatas con interfaz gráfica**](docs/03-simulador.md)
   * Arquitectura desacoplada ([`src/automata.py`](src/automata.py), [`src/formatos.py`](src/formatos.py), [`src/lenguajes.py`](src/lenguajes.py) y [`src/app.py`](src/app.py)), justificación y coste computacional de la estrategia de simulación no determinista.
4. [**Ejercicio 4. Investigación y estado del arte**](docs/04-investigacion.md)
   * Investigación sustentada en fuentes verificables (libros con ISBN y artículos con DOI): AFN, AFN-$\lambda$, $\lambda$-clausura, construcción de subconjuntos, cota $2^n$, Teorema de Kleene, Teorema de Myhill-Nerode y algoritmo de Hopcroft.
   * Análisis del artículo clásico de **Rabin y Scott (1959)** (Premio Turing 1976) y dos fichas de artículos arbitrados recientes con implementación medida (Turonová et al., 2020; D'Antoni & Veanes, 2021).
5. [**Ejercicio 5. Del artículo al autómata (Fantasmas de Pac-Man Ampliado)**](docs/05-del-articulo-al-automata.md)
   * Definición formal como quíntupla de 7 estados y 8 eventos, archivos en [`.jff`](automatas/aplicacion/ej5_pacman_ampliado.jff), [`.json`](automatas/aplicacion/ej5_pacman_ampliado.json) y [`.xml`](automatas/aplicacion/ej5_pacman_ampliado.xml), tabla de 12 cadenas de prueba y reflexión de media cuartilla sobre la abstracción.
6. [**Propuesta de artículo de investigación (Apartado 5.3)**](docs/propuesta.md)
7. [**Bibliografía General (APA 7.ª Edición — Fuentes Verificables)**](docs/bibliografia.md)

---

## Estructura del Repositorio

```text
practica2-tc/
├── README.md
├── .gitignore
├── requirements.txt
├── pytest.ini
├── .github/workflows/
│   └── pruebas.yml
├── docs/
│   ├── 01-entorno.md
│   ├── 02-jflap.md
│   ├── 03-simulador.md
│   ├── 04-investigacion.md
│   ├── 05-del-articulo-al-automata.md
│   ├── propuesta.md
│   └── bibliografia.md
├── entorno/
│   ├── Dockerfile
│   └── compose.yml
├── automatas/
│   ├── lista2-afd/          # .jff, .json y .xml de cada ejercicio AFD
│   ├── lista3-afnd/         # .jff, .json y .xml de cada AFND estándar
│   ├── lista3-afnd-lambda/  # .jff, .json y .xml de cada AFND-lambda
│   ├── conversiones/        # AFND y AFD resultantes de cada conversión
│   └── aplicacion/          # Autómata ampliado del Ejercicio 5 (Pac-Man)
├── src/
│   ├── lenguajes.py
│   ├── automata.py
│   ├── formatos.py
│   └── app.py
├── tests/
│   └── test_practica2.py
└── evidencias/
    ├── git/
    ├── ci/
    ├── jflap/
    └── app/
```

---

## Instrucciones para Levantar el Entorno, Ejecutar las Pruebas y Usar el Simulador

Desde la carpeta [`entorno/`](entorno/):

```bash
cd entorno
```

1. **Construir las imágenes de los tres contenedores**:
   ```bash
   docker compose build
   ```
2. **Ejecutar la suite de pruebas automatizadas (`pytest`) en las tres versiones de Python**:
   ```bash
   docker compose run --rm py311 pytest -q
   docker compose run --rm py312 pytest -q
   docker compose run --rm py313 pytest -q
   ```
3. **Iniciar el simulador interactivo en Flet (servicio `py312`)**:
   ```bash
   docker compose up py312
   ```
   Abra en su navegador: **http://localhost:8550**
   * En la sección **1**, puede definir o editar estados, alfabeto y transiciones manualmente, o escribir la ruta de cualquier archivo (por ejemplo `automatas/aplicacion/ej5_pacman_ampliado.jff`, `.json` o `.xml`) y hacer clic en **Importar Archivo** o **Exportar (.jff, .json, .xml)**, así como convertir cualquier AFND/AFND-$\lambda$ a AFD.
   * En la sección **2**, ingrese cualquier cadena y use **Validar Cadena** o los botones **◀ Paso Anterior / Paso Siguiente ▶** para recorrer la traza paso a paso.
   * En la sección **3**, ejecute las operaciones sobre cadenas y lenguajes de la Práctica 1.
