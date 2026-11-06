# Ejercicio 4: Aplicaciones de Expresiones Regulares — Validadores y Congruencia entre Modelos

- **Unidad de Aprendizaje:** Teoría de la Computación (Plan 2020) — **IPN — ESCOM**
- **Alumno:** César Octavio Navarro Bahena — **Boleta:** `2023630464` — **Grupo:** `4CM4`
- **Profesor:** M. en C. Gabriel Hurtado Avilés
- **Módulos de implementación:** [`src/validadores.py`](../../src/validadores.py), [`src/expresiones.py`](../../src/expresiones.py), [`tests/test_practica4.py`](../../tests/test_practica4.py)
- **Directorio de autómatas `.jff`:** [`automatas/practica4/validadores/`](../../automatas/practica4/validadores/)

---

## 1. Declaración Explícita de Clases de Símbolos en la Notación del Curso

Siguiendo la nota sobre la notación de la práctica, en [`src/validadores.py`](../../src/validadores.py) (`DECLARACION_CLASES_CURSO`) y [`src/expresiones.py`](../../src/expresiones.py) (`CLASES_PREDEFINIDAS`) se declaran explícitamente las siguientes abreviaturas de uniones finitas de símbolos:

| Símbolo | Definición explícita en la notación del curso | Sintaxis `re` Python | $\|\Sigma_C\|$ | Significado semántico |
| :---: | :--- | :---: | :---: | :--- |
| **`D`** | `0 + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9` | `[0-9]` | 10 | Dígitos decimales del 0 al 9 |
| **`N`** | `1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9` | `[1-9]` | 9 | Dígitos positivos sin el cero (1 al 9) |
| **`P`** | `2 + 3 + 4 + 5 + 6 + 7 + 8 + 9` | `[2-9]` | 8 | Primer dígito válido de un NIR telefónico nacional (IFT) |
| **`L`** | `a + b + c + ··· + x + y + z` | `[a-z]` | 26 | Letras minúsculas del alfabeto latino ASCII |
| **`A`** | `a + b + ··· + z + 0 + 1 + ··· + 9` | `[a-z0-9]` | 36 | Símbolos alfanuméricos en minúscula |
| **`U`** | `a + b + ··· + z + 0 + 1 + ··· + 9 + _` | `[a-z0-9_]` | 37 | Caracteres atómicos de identificador de usuario local |
| **`R`** | `a + b + ··· + z + 0 + 1 + ··· + 9 + _ + - + .` | `[a-z0-9_.-]` | 39 | Caracteres no reservados de segmento de ruta / consulta URL |
| **`T`** | `1 + 3 + 5 + 7 + 8` | `[13578]` | 5 | Segundo dígito de meses de 31 días con cero inicial (`01,03,05,07,08`) |
| **`C`** | `4 + 6 + 9` | `[469]` | 3 | Segundo dígito de meses de 30 días con cero inicial (`04,06,09`) |

---

## 2. Resumen Comparativo de los Cuatro Validadores Implementados

Cada validador se construye íntegramente mediante `er_a_automata_completo` (Ejercicio 2):

| Validador (`clave`) | Norma o estándar consultado | $\|Q_{\text{AFN-}\lambda}\|$ | **Estados AFD antes de minimizar** | **Estados AFD después de minimizar** | Reducción de estados | Archivos `.jff` |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **1. Correo electrónico (`correo`)** | IETF RFC 5322 (§3.4.1), RFC 5321 (§4.1.2) y RFC 1035 | 56 | **18** | **7** | $-61.1\%$ | `correo_afd.jff` / `correo_afd_minimo.jff` |
| **2. Teléfono nacional (`telefono_nacional`)** | Plan Técnico Fundamental de Numeración del IFT (DOF, 2018) e ITU-T E.123 | 208 | **76** | **32** | $-57.9\%$ | `telefono_nacional_afd.jff` / `telefono_nacional_afd_minimo.jff` |
| **3. URL HTTP/HTTPS (`url`)** | IETF RFC 3986 (§3) y RFC 1738 (§3.3) | 94 | **29** | **18** | $-37.9\%$ | `url_afd.jff` / `url_afd_minimo.jff` |
| **4. Fecha en distintos formatos (`fecha`)** | ISO 8601-1:2019 (§5.2.2.1) y formato civil `DD/MM/AAAA`, `DD-MM-AAAA` | 370 | **91** | **47** | $-48.4\%$ | `fecha_afd.jff` / `fecha_afd_minimo.jff` |

---

## 3. Especificación Técnica y Justificación Normativa de Cada Validador

### 3.1 Validador 1: Dirección de Correo Electrónico (`correo`)

- **Expresión en la notación del curso:**
  ```text
  U(U)*((. + -)U(U)*)*@A(A + -)*(.A(A + -)*)*(.LL(L)*)
  ```
- **Traducción a la sintaxis del módulo `re` de Python:**
  ```regex
  [a-z0-9_][a-z0-9_]*(?:(?:\.|\-)[a-z0-9_][a-z0-9_]*)*@[a-z0-9](?:[a-z0-9]|\-)*(?:\.[a-z0-9](?:[a-z0-9]|\-)*)*\.[a-z][a-z][a-z]*
  ```
- **Conteo de estados del AFD:** Antes de minimizar: **18 estados** $\longrightarrow$ Después de minimizar: **7 estados**.
- **Norma consultada:** **IETF RFC 5322** (*Internet Message Format*, §3.4.1 *Addr-Spec Specification*, Resnick, 2008), **IETF RFC 5321** (*Simple Mail Transfer Protocol*, §4.1.2, Klensin, 2008) e **IETF RFC 1035** (§2.3.1 *Preferred name syntax*).
- **Justificación de casos válidos o inválidos que quedan fuera de la expresión:**
  1. *Casos válidos en RFC 5322 que quedan fuera:* partes locales entrecomilladas (`"juan perez"@dominio.com`), caracteres especiales de `atext` poco frecuentes (`+`, `!`, `#`, `$`, `%`, `/`), literales de dirección IP entre corchetes (`usuario@[192.0.2.1]`), direcciones internacionalizadas UTF-8 (RFC 6531 `SMTPUTF8`) y comentarios con paréntesis anidados `(comentario)usuario@dominio.com` (estos últimos permiten anidamiento arbitrario y constituyen un lenguaje libre de contexto Tipo 2 imposible de describir con una expresión regular).
  2. *Casos inválidos aceptados o cotas no impuestas:* las cotas numéricas de longitud de RFC 5321 (máximo 64 octetos en la parte local, 63 octetos por etiqueta DNS y 254 octetos totales) no se codifican en la expresión para evitar multiplicar por cientos el número de estados del AFD; asimismo, la subexpresión de etiqueta de dominio `A(A + -)*` impide que una etiqueta inicie con guion `-`, pero permite que termine con guion (ej. `a-@b.com`).

---

### 3.2 Validador 2: Número Telefónico en Formato Nacional (`telefono_nacional`)

- **Expresión en la notación del curso:**
  ```text
  PDDDDDDDDD + PD-DDDD-DDDD + PDD-DDD-DDDD + PD\ DDDD\ DDDD + PDD\ DDD\ DDDD + \(PD\)(\  + λ)DDDD(- + \  + λ)DDDD + \(PDD\)(\  + λ)DDD(- + \  + λ)DDDD
  ```
- **Traducción a la sintaxis del módulo `re` de Python:**
  ```regex
  (?:[2-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]|[2-9][0-9]\-[0-9][0-9][0-9][0-9]\-[0-9][0-9][0-9][0-9]|[2-9][0-9][0-9]\-[0-9][0-9][0-9]\-[0-9][0-9][0-9][0-9]|[2-9][0-9]\ [0-9][0-9][0-9][0-9]\ [0-9][0-9][0-9][0-9]|[2-9][0-9][0-9]\ [0-9][0-9][0-9]\ [0-9][0-9][0-9][0-9]|\([2-9][0-9]\)(?:\ |)[0-9][0-9][0-9][0-9](?:\-|\ |)[0-9][0-9][0-9][0-9]|\([2-9][0-9][0-9]\)(?:\ |)[0-9][0-9][0-9](?:\-|\ |)[0-9][0-9][0-9][0-9])
  ```
- **Conteo de estados del AFD:** Antes de minimizar: **76 estados** $\longrightarrow$ Después de minimizar: **32 estados**.
- **Norma consultada:** **Plan Técnico Fundamental de Numeración (PTFN)** emitido por el **Instituto Federal de Telecomunicaciones (IFT)** (Diario Oficial de la Federación, 11 de mayo de 2018; marcación nacional uniforme a 10 dígitos vigente desde el 3 de agosto de 2019) y recomendación **ITU-T E.123**.
- **Justificación de casos válidos o inválidos que quedan fuera de la expresión:**
  1. *Casos válidos fuera de la expresión:* números con código de país internacional E.164 (`+52 55 1234 5678`), códigos cortos de servicios de emergencia y atención ciudadana de 3 dígitos (`911`, `089`, `072`), y prefijos históricos derogados en 2019 (`01`, `044`, `045`).
  2. *Casos sintácticamente aceptados pero administrativamente no asignados:* las ramas de agrupamiento `2-4-4` (`PD-DDDD-DDDD` y `(PD)...`) aceptan cualquier clave de 2 dígitos que inicie con $P \in \{2, \dots, 9\}$ (como `44-1234-5678`), aunque en el PTFN del IFT únicamente las zonas metropolitanas de Guadalajara (`33`), Ciudad de México (`55`/`56`) y Monterrey (`81`) tienen NIR de 2 dígitos y el resto de la República utiliza NIR de 3 dígitos.

---

### 3.3 Validador 3: Localizador Uniforme de Recursos (`url`)

- **Expresión en la notación del curso:**
  ```text
  http(s + λ)://A(A + -)*(.A(A + -)*)*(.LL(L)*)(:ND* + λ)(/R*)*(\?R(R + = + &)* + λ)
  ```
- **Traducción a la sintaxis del módulo `re` de Python:**
  ```regex
  http(?:s|)://[a-z0-9](?:[a-z0-9]|\-)*(?:\.[a-z0-9](?:[a-z0-9]|\-)*)*\.[a-z][a-z][a-z]*(?::[1-9][0-9]*|)(?:/[a-z0-9_.-]*)*(?:\?[a-z0-9_.-](?:[a-z0-9_.-]|=|\&)*|)
  ```
- **Conteo de estados del AFD:** Antes de minimizar: **29 estados** $\longrightarrow$ Después de minimizar: **18 estados**.
- **Norma consultada:** **IETF RFC 3986** (*Uniform Resource Identifier (URI): Generic Syntax*, Berners-Lee, Fielding & Masinter, 2005, §3) e **IETF RFC 1738** (*Uniform Resource Locators*, §3.3 HTTP).
- **Justificación de casos válidos o inválidos que quedan fuera de la expresión:**
  1. *Casos válidos en RFC 3986 excluidos:* esquemas distintos de HTTP/HTTPS (`ftp://`, `ws://`, `mailto:`, `file://`), subcomponente de usuario `userinfo@`, anfitriones expresados mediante direcciones IPv4 (`http://192.168.1.1`), literales IPv6 (`http://[::1]/`) o nombres locales sin TLD (`http://localhost:8000`), secuencias de escape porcentual `%HH` y fragmentos `#seccion`.
  2. *Casos inválidos en TCP/IP aceptados por la expresión:* el subpatrón de puerto opcional `(:ND* + λ)` impide ceros a la izquierda (`:080` es rechazado), pero acepta enteros positivos arbitrariamente largos que superan el límite de 16 bits (`65535`) del encabezado TCP (por ejemplo `:99999`).

---

### 3.4 Validador 4: Fecha Calendario en Múltiples Formatos (`fecha`)

- **Expresión en la notación del curso:**
  ```text
  (19 + 20)DD-((0T + 10 + 12)-(0N + 1D + 2D + 30 + 31) + (0C + 11)-(0N + 1D + 2D + 30) + 02-(0N + 1D + 2D)) + ((0N + 1D + 2D + 30 + 31)/(0T + 10 + 12) + (0N + 1D + 2D + 30)/(0C + 11) + (0N + 1D + 2D)/02)/(19 + 20)DD + ((0N + 1D + 2D + 30 + 31)-(0T + 10 + 12) + (0N + 1D + 2D + 30)-(0C + 11) + (0N + 1D + 2D)-02)-(19 + 20)DD
  ```
- **Traducción a la sintaxis del módulo `re` de Python:**
  ```regex
  (?:(?:19|20)[0-9][0-9]\-(?:(?:0[13578]|10|12)\-(?:0[1-9]|1[0-9]|2[0-9]|30|31)|(?:0[469]|11)\-(?:0[1-9]|1[0-9]|2[0-9]|30)|02\-(?:0[1-9]|1[0-9]|2[0-9]))|(?:(?:0[1-9]|1[0-9]|2[0-9]|30|31)/(?:0[13578]|10|12)|(?:0[1-9]|1[0-9]|2[0-9]|30)/(?:0[469]|11)|(?:0[1-9]|1[0-9]|2[0-9])/02)/(?:19|20)[0-9][0-9]|(?:(?:0[1-9]|1[0-9]|2[0-9]|30|31)\-(?:0[13578]|10|12)|(?:0[1-9]|1[0-9]|2[0-9]|30)\-(?:0[469]|11)|(?:0[1-9]|1[0-9]|2[0-9])\-02)\-(?:19|20)[0-9][0-9])
  ```
- **Conteo de estados del AFD:** Antes de minimizar: **91 estados** $\longrightarrow$ Después de minimizar: **47 estados**.
- **Norma consultada:** **ISO 8601-1:2019** (*Date and time — Representations for information interchange — Part 1: Basic rules*, §5.2.2.1 `YYYY-MM-DD`) y convención oficial hispanoamericana `DD/MM/AAAA` y `DD-MM-AAAA`.
- **Justificación de casos válidos o inválidos que quedan fuera de la expresión:**
  1. *Casos válidos en ISO 8601 excluidos:* años anteriores a `1900` o posteriores a `2099`, formato básico compacto sin guiones `AAAAMMDD`, fechas ordinales `AAAA-DDD` y fechas por semana `AAAA-Www-D`.
  2. *Caso inválido del calendario gregoriano aceptado por la expresión:* el día `29` de febrero en años no bisiestos (como `2023-02-29`, `29/02/2025` o el año secular no divisible entre 400 `1900-02-29`). En cambio, la expresión **sí rechaza exactamente** fechas inexistentes en cualquier año como `30/02`, `31/02`, `31/04`, `31/06`, `31/09` y `31/11`.

---

## 4. Procedimiento Documentado de Generación de $\ge 500$ Cadenas y Congruencia entre Modelos

En [`src/validadores.py`](../../src/validadores.py) (`generar_corpus_validador` y `verificar_congruencia_validador`) se implementó un procedimiento determinista (con semilla fija `semilla=2026` en `random.Random(2026)`) que genera exactamente **500 cadenas distintas por validador** (**250 cadenas válidas** y **250 cadenas inválidas**, sumando **2,000 cadenas** en los cuatro validadores):

1. **Generación de las 250 cadenas válidas (`valida_estructurada`):**
   - Incluye primero los ejemplos canónicos declarados en `ESPECIFICACIONES_VALIDADORES`.
   - Genera el resto por **derivación gramatical controlada** recorriendo todas las ramas de unión (`+`) de la expresión (los 11 patrones de formato telefónico nacional, los esquemas `http`/`https` con y sin puerto/ruta/query, y los 12 meses del año en los 3 formatos `AAAA-MM-DD`, `DD/MM/AAAA` y `DD-MM-AAAA`) y muestreando longitudes $k \in \{0, 1, 2, 3\}$ en cada cerradura de Kleene (`*`).
2. **Generación de las 250 cadenas inválidas (`invalida_frontera` e `invalida_mutacion`):**
   - Aplica rotativamente entre 15 y 24 **operadores de mutación estructural y violación de frontera** específicos de cada dominio: cadena vacía `""`, omisión o duplicación de delimitadores (`@`, `://`, `:`, `/`, `-`), puntos consecutivos `..`, TLDs de 1 sola letra o con dígitos, números telefónicos que inician con `0` o `1` o de 9/11 dígitos, separadores mezclados (`55-1234 5678`), puertos con cero inicial (`:080`), días `30`/`31` en febrero, día `31` en abril/junio/septiembre/noviembre, meses `00` o `13`–`19`, y años fuera de `1900–2099`.

### 4.1 Resultados de la Prueba Automatizada en `pytest` (`tests/test_practica4.py`)

| Validador | Cadenas generadas | Válidas | Inválidas | Coincidencias `AFD_min.acepta(w) == bool(re.fullmatch(pat, w))` | Coincidencias `AFD.acepta(w) == bool(re.fullmatch(pat, w))` | Discrepancias |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`correo`** | 500 | 250 | 250 | **500 / 500 (100%)** | **500 / 500 (100%)** | 0 |
| **`telefono_nacional`** | 500 | 250 | 250 | **500 / 500 (100%)** | **500 / 500 (100%)** | 0 |
| **`url`** | 500 | 250 | 250 | **500 / 500 (100%)** | **500 / 500 (100%)** | 0 |
| **`fecha`** | 500 | 250 | 250 | **500 / 500 (100%)** | **500 / 500 (100%)** | 0 |
| **Total global** | **2,000** | **1,000** | **1,000** | **2,000 / 2,000 (100%)** | **2,000 / 2,000 (100%)** | **0** |
