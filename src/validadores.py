"""Módulo `validadores.py`: Aplicaciones prácticas de expresiones regulares — Validadores
(Práctica 4, Ejercicio 4).

Implementa cuatro validadores basados en expresiones regulares construidos íntegramente con el
motor del Ejercicio 2 (`er_a_automata_completo`):
1. `correo`: Dirección de correo electrónico (basado en IETF RFC 5322 §3.4.1 y RFC 5321 §4.1.2).
2. `telefono_nacional`: Número telefónico en formato nacional de 10 dígitos (Plan Técnico
   Fundamental de Numeración del IFT, México).
3. `url`: Localizador Uniforme de Recursos HTTP/HTTPS (basado en IETF RFC 3986 §3 y RFC 1738).
4. `fecha`: Fecha calendario en formatos ISO 8601 (`AAAA-MM-DD`), tradicional con diagonal
   (`DD/MM/AAAA`) y tradicional con guion (`DD-MM-AAAA`), distinguiendo meses de 31, 30 y 29 días.

Para cada validador provee:
- La declaración explícita de las clases de símbolos empleadas en la notación del curso.
- La expresión regular en la notación del curso y su traducción exacta a la sintaxis del módulo `re` de Python.
- La tubería completa del Ejercicio 2 (AFN-λ -> AFN -> AFD -> AFD mínimo), reportando el número
  de estados del AFD antes y después de minimizar.
- La justificación técnica de qué casos válidos o inválidos quedan fuera de la expresión y la
  norma o estándar consultado.
- Un generador determinista documentado (`generar_corpus_validador`) que produce al menos 500
  cadenas válidas e inválidas por validador para comprobar la congruencia exacta entre el autómata
  del Ejercicio 2 y `re.fullmatch`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import random
import re

try:
    from automata import AutomataFinito
    from expresiones import (
        CLASES_PREDEFINIDAS,
        ResultadoERaAutomata,
        er_a_automata_completo,
    )
except ImportError:  # pragma: no cover
    from src.automata import AutomataFinito
    from src.expresiones import (
        CLASES_PREDEFINIDAS,
        ResultadoERaAutomata,
        er_a_automata_completo,
    )


# =============================================================================
# DECLARACIÓN EXPLÍCITA DE CLASES DE SÍMBOLOS EN LA NOTACIÓN DEL CURSO
# =============================================================================

@dataclass(frozen=True)
class DeclaracionClaseSimbolos:
    """Documentación formal de una clase abreviada de símbolos en la notación del curso."""

    simbolo: str
    definicion_curso: str
    equivalente_regex_python: str
    cardinalidad: int
    descripcion: str


DECLARACION_CLASES_CURSO: dict[str, DeclaracionClaseSimbolos] = {
    "D": DeclaracionClaseSimbolos(
        simbolo="D",
        definicion_curso="0 + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9",
        equivalente_regex_python="[0-9]",
        cardinalidad=10,
        descripcion="Dígitos decimales del 0 al 9.",
    ),
    "N": DeclaracionClaseSimbolos(
        simbolo="N",
        definicion_curso="1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9",
        equivalente_regex_python="[1-9]",
        cardinalidad=9,
        descripcion="Dígitos decimales positivos sin el cero (1 al 9).",
    ),
    "P": DeclaracionClaseSimbolos(
        simbolo="P",
        definicion_curso="2 + 3 + 4 + 5 + 6 + 7 + 8 + 9",
        equivalente_regex_python="[2-9]",
        cardinalidad=8,
        descripcion="Primer dígito válido de un Número Identificador de Región (NIR) del IFT (2 al 9).",
    ),
    "L": DeclaracionClaseSimbolos(
        simbolo="L",
        definicion_curso="a + b + c + d + e + f + g + h + i + j + k + l + m + n + o + p + q + r + s + t + u + v + w + x + y + z",
        equivalente_regex_python="[a-z]",
        cardinalidad=26,
        descripcion="Letras minúsculas del alfabeto latino básico ASCII.",
    ),
    "A": DeclaracionClaseSimbolos(
        simbolo="A",
        definicion_curso="a + b + ··· + z + 0 + 1 + ··· + 9",
        equivalente_regex_python="[a-z0-9]",
        cardinalidad=36,
        descripcion="Símbolos alfanuméricos en minúscula (letras a–z y dígitos 0–9).",
    ),
    "U": DeclaracionClaseSimbolos(
        simbolo="U",
        definicion_curso="a + b + ··· + z + 0 + 1 + ··· + 9 + _",
        equivalente_regex_python="[a-z0-9_]",
        cardinalidad=37,
        descripcion="Símbolos atómicos de identificador local de correo (letras, dígitos y guion bajo).",
    ),
    "R": DeclaracionClaseSimbolos(
        simbolo="R",
        definicion_curso="a + b + ··· + z + 0 + 1 + ··· + 9 + _ + - + .",
        equivalente_regex_python="[a-z0-9_.-]",
        cardinalidad=39,
        descripcion="Símbolos no reservados para segmentos de ruta y parámetros de consulta en URL.",
    ),
    "T": DeclaracionClaseSimbolos(
        simbolo="T",
        definicion_curso="1 + 3 + 5 + 7 + 8",
        equivalente_regex_python="[13578]",
        cardinalidad=5,
        descripcion="Segundo dígito de los meses con 31 días que inician con 0 (01, 03, 05, 07, 08).",
    ),
    "C": DeclaracionClaseSimbolos(
        simbolo="C",
        definicion_curso="4 + 6 + 9",
        equivalente_regex_python="[469]",
        cardinalidad=3,
        descripcion="Segundo dígito de los meses con 30 días que inician con 0 (04, 06, 09).",
    ),
}


# =============================================================================
# ESPECIFICACIÓN DE LOS CUATRO VALIDADORES (EJERCICIO 4)
# =============================================================================

@dataclass(frozen=True)
class EspecificacionValidador:
    """Metadatos formales, expresión regular y justificación normativa de un validador."""

    clave: str
    titulo: str
    expresion_curso: str
    clases_empleadas: list[str]
    norma_consultada: str
    casos_validos_cubiertos: str
    casos_fuera_de_la_expresion: str
    ejemplos_validos: list[str]
    ejemplos_invalidos: list[str]


ESPECIFICACIONES_VALIDADORES: dict[str, EspecificacionValidador] = {
    "correo": EspecificacionValidador(
        clave="correo",
        titulo="1. Dirección de correo electrónico",
        expresion_curso="U(U)*((. + -)U(U)*)*@A(A + -)*(.A(A + -)*)*(.LL(L)*)",
        clases_empleadas=["U", "A", "L"],
        norma_consultada=(
            "IETF RFC 5322 (Internet Message Format, §3.4.1 Addr-Spec Specification, Resnick, 2008), "
            "IETF RFC 5321 (Simple Mail Transfer Protocol, §4.1.2 Command Argument Syntax, Klensin, 2008) "
            "e IETF RFC 1035 (§2.3.1 Preferred name syntax para etiquetas de dominio DNS)."
        ),
        casos_validos_cubiertos=(
            "Direcciones en formato addr-spec estándar 'local-part@domain' donde la parte local inicia y "
            "termina con uno o más caracteres alfanuméricos o guion bajo (U), admitiendo puntos '.' o "
            "guiones '-' intermedios no consecutivos (ej. 'cesar.navarro_23@alumno.ipn.mx'), seguidos de '@' "
            "y un nombre de dominio jerárquico con una o más etiquetas DNS y un dominio de nivel superior "
            "(TLD) alfabético de al menos dos letras (.mx, .com, .edu, .gob.mx)."
        ),
        casos_fuera_de_la_expresion=(
            "1) Casos válidos según RFC 5322 que quedan fuera deliberadamente: partes locales entrecomilladas "
            "(quoted-string como '\"juan perez\"@ejemplo.com'), símbolos especiales poco comunes de atext "
            "('+', '!', '#', '$', '%', '&', '*', '/'), literales de dirección IP entre corchetes "
            "('usuario@[192.0.2.1]' o '[IPv6:2001:db8::1]'), direcciones internacionalizadas UTF-8 (RFC 6531 "
            "SMTPUTF8) y comentarios CFWS anidados '(comentario)usuario@dominio.com' (estos últimos permiten "
            "anidamiento arbitrario de paréntesis y constituyen un lenguaje libre de contexto Tipo 2 no regular). "
            "2) Restricciones adicionales de RFC 5321/1035 no impuestas para evitar explosión de estados: "
            "el límite de longitud máxima de 64 octetos en la parte local, 63 octetos por etiqueta DNS y 254 "
            "octetos totales, así como la prohibición de que una etiqueta DNS termine en guion '-' "
            "(ej. 'a-@b.com' es aceptada por el submodelo simplificado `A(A + -)*`)."
        ),
        ejemplos_validos=[
            "cesar.navarro@alumno.ipn.mx",
            "contacto_2026@escom.ipn.mx",
            "gabriel-hurtado@ipn.edu.mx",
            "usuario123@dominio-prueba.org",
            "a_b.c-d@sub.servidor.net",
        ],
        ejemplos_invalidos=[
            ".inicio_punto@ipn.mx",
            "doble..punto@ipn.mx",
            "sin_arroba.ipn.mx",
            "usuario@dominio.c",
            "usuario@-dominio.com",
            "usuario@dominio..com",
        ],
    ),
    "telefono_nacional": EspecificacionValidador(
        clave="telefono_nacional",
        titulo="2. Número telefónico en formato nacional (México, 10 dígitos)",
        expresion_curso=(
            "PDDDDDDDDD + "
            "PD-DDDD-DDDD + PDD-DDD-DDDD + "
            "PD\\ DDDD\\ DDDD + PDD\\ DDD\\ DDDD + "
            "\\(PD\\)(\\  + λ)DDDD(- + \\  + λ)DDDD + "
            "\\(PDD\\)(\\  + λ)DDD(- + \\  + λ)DDDD"
        ),
        clases_empleadas=["P", "D"],
        norma_consultada=(
            "Instituto Federal de Telecomunicaciones (IFT) — Plan Técnico Fundamental de Numeración "
            "(PTFN, publicado en el Diario Oficial de la Federación el 11 de mayo de 2018 y en vigor "
            "con marcación uniforme a 10 dígitos desde el 3 de agosto de 2019) y recomendación ITU-T E.123 "
            "(Notation for national and international telephone numbers)."
        ),
        casos_validos_cubiertos=(
            "Números telefónicos nacionales mexicanos de exactamente 10 dígitos cuyo Número Identificador "
            "de Región (NIR) inicia con un dígito P ∈ {2, ..., 9}, escritos en cualquiera de las siete "
            "representaciones nacionales habituales: (a) 10 dígitos corridos ('5512345678'), "
            "(b) agrupamiento 2-4-4 con guiones o espacios para NIR de 2 dígitos como CDMX 55/56, "
            "Guadalajara 33 y Monterrey 81 ('55-1234-5678', '55 1234 5678'), (c) agrupamiento 3-3-4 con "
            "guiones o espacios para NIR de 3 dígitos del resto del país ('722-123-4567', '722 123 4567'), "
            "y (d) clave NIR entre paréntesis de 2 o 3 dígitos ('(55) 1234-5678', '(722)123-4567')."
        ),
        casos_fuera_de_la_expresion=(
            "1) Casos válidos en telecomunicaciones que quedan fuera de la expresión de formato nacional: "
            "números con prefijo internacional E.164 ('+52 55 1234 5678' o '0052...'), números de emergencia "
            "y servicios especiales de 3 dígitos ('911', '089', '072') y marcaciones históricas obsoletas "
            "anteriores a la reforma de 2019 ('01 800...', '044 55...', '045...'). "
            "2) Casos sintácticamente aceptados pero administrativamente inválidos ante el IFT: "
            "el formato con NIR de 2 dígitos `PD-DDDD-DDDD` acepta cualquier par `PD` con P ∈ {2..9} "
            "(como '44-1234-5678'), aunque el PTFN sólo asigna NIR de 2 dígitos a las regiones 33, 55, 56 y 81 "
            "(y reserva el prefijo 800/900 para servicios no geográficos de cobro revertido o tarifa especial)."
        ),
        ejemplos_validos=[
            "5512345678",
            "55-1234-5678",
            "722-987-6543",
            "33 4567 8901",
            "(55) 1234-5678",
            "(722)123-4567",
        ],
        ejemplos_invalidos=[
            "0512345678",
            "1512345678",
            "551234567",
            "55123456789",
            "55-1234 5678",
            "(551234-5678",
        ],
    ),
    "url": EspecificacionValidador(
        clave="url",
        titulo="3. Localizador Uniforme de Recursos (URL HTTP/HTTPS)",
        expresion_curso="http(s + λ)://A(A + -)*(.A(A + -)*)*(.LL(L)*)(:ND* + λ)(/R*)*(\\?R(R + = + &)* + λ)",
        clases_empleadas=["A", "L", "N", "D", "R"],
        norma_consultada=(
            "IETF RFC 3986 (Uniform Resource Identifier (URI): Generic Syntax, Berners-Lee, Fielding & "
            "Masinter, 2005, §3 Syntax Components) e IETF RFC 1738 (Uniform Resource Locators, §3.3 HTTP)."
        ),
        casos_validos_cubiertos=(
            "URLs web con esquema 'http://' o 'https://', autoridad formada por un nombre de dominio "
            "registrado con subdominios y TLD alfabético de al menos 2 letras, puerto TCP opcional sin "
            "ceros a la izquierda (':80', ':443', ':8080'), ruta jerárquica opcional de cero o más "
            "segmentos ('/', '/docs/practica4/index.html') y cadena de consulta opcional iniciada por '?' "
            "con pares clave/valor ('?tema=automatas&ejercicio=4')."
        ),
        casos_fuera_de_la_expresion=(
            "1) Casos válidos en RFC 3986 excluidos por acotación de alcance: otros esquemas de URI "
            "('ftp://', 'mailto:', 'ws://', 'file:///'), subcomponente de credenciales `userinfo@` "
            "('https://user:pass@sitio.com'), anfitriones expresados como direcciones IPv4 ('http://127.0.0.1:8000') "
            "o literales IPv6 ('http://[::1]/') o 'localhost' sin TLD, codificación porcentual `%HH` fuera de R, "
            "y fragmentos con identificador `#seccion`. "
            "2) Casos sintácticamente aceptados pero semánticamente inválidos en TCP/IP: números de puerto "
            "que exceden el límite de 16 bits (65535), como ':99999', dado que `:ND*` acepta cualquier entero "
            "positivo sin cero inicial."
        ),
        ejemplos_validos=[
            "https://www.escom.ipn.mx",
            "http://sae.ipn.mx:8080/login",
            "https://github.com/ipn/practica4-tc/blob/main/readme.md",
            "https://api.ejemplo-web.org:443/v1/buscar?q=kleene&pagina=1",
            "http://portal.gob.mx/",
        ],
        ejemplos_invalidos=[
            "ftp://archivos.ipn.mx",
            "http:/www.ipn.mx",
            "https://sitio_invalido.com",
            "https://dominio-sin-tld",
            "https://www.ipn.mx:080/ruta",
            "https://www.ipn.mx/?",
        ],
    ),
    "fecha": EspecificacionValidador(
        clave="fecha",
        titulo="4. Fecha calendario en múltiples formatos (AAAA-MM-DD, DD/MM/AAAA, DD-MM-AAAA)",
        expresion_curso=(
            "(19 + 20)DD-((0T + 10 + 12)-(0N + 1D + 2D + 30 + 31) + (0C + 11)-(0N + 1D + 2D + 30) + 02-(0N + 1D + 2D)) + "
            "((0N + 1D + 2D + 30 + 31)/(0T + 10 + 12) + (0N + 1D + 2D + 30)/(0C + 11) + (0N + 1D + 2D)/02)/(19 + 20)DD + "
            "((0N + 1D + 2D + 30 + 31)-(0T + 10 + 12) + (0N + 1D + 2D + 30)-(0C + 11) + (0N + 1D + 2D)-02)-(19 + 20)DD"
        ),
        clases_empleadas=["D", "N", "T", "C"],
        norma_consultada=(
            "ISO 8601-1:2019 (Date and time — Representations for information interchange — Part 1: Basic rules, "
            "§5.2.2.1 Calendar date extended format `YYYY-MM-DD`) y convención oficial hispanoamericana "
            "`DD/MM/AAAA` y `DD-MM-AAAA` para el calendario gregoriano en los siglos XX y XXI (1900–2099)."
        ),
        casos_validos_cubiertos=(
            "Fechas entre los años 1900 y 2099 en tres formatos: (1) ISO 8601 extendido `AAAA-MM-DD` "
            "(ej. '2026-11-06'), (2) formato civil con diagonal `DD/MM/AAAA` (ej. '06/11/2026') y "
            "(3) formato civil con guion `DD-MM-AAAA` (ej. '28-02-2026'). La expresión discrimina "
            "exactamente los días permitidos según el mes: de 01 a 31 para enero (01), marzo (03), "
            "mayo (05), julio (07), agosto (08), octubre (10) y diciembre (12); de 01 a 30 para "
            "abril (04), junio (06), septiembre (09) y noviembre (11); y de 01 a 29 para febrero (02)."
        ),
        casos_fuera_de_la_expresion=(
            "1) Casos válidos en ISO 8601 excluidos: años fuera del intervalo 1900–2099 (ej. '1810-09-16' "
            "o '2105-01-01'), el formato básico sin separadores `AAAAMMDD` ('20261106'), fechas ordinales "
            "`AAAA-DDD` y fechas con semana ISO `AAAA-Www-D`. "
            "2) Caso inválido del calendario gregoriano aceptado por la expresión: el día 29 de febrero "
            "en años no bisiestos (como '2023-02-29', '29/02/2025' o el año secular no divisible entre 400 "
            "'1900-02-29'). Aunque la condición de año bisiesto en 1900–2099 es un conjunto finito y por "
            "tanto regular, distinguirla obligaría a desglosar en la expresión todas las terminaciones de "
            "dos dígitos múltiplos de 4 (`04, 08, ..., 96` y `2000`), incrementando drásticamente la longitud "
            "de la fórmula; en cambio, los días imposibles universales como `30/02`, `31/02`, `31/04`, "
            "`31/06`, `31/09` y `31/11` sí son rechazados de manera exacta por el autómata."
        ),
        ejemplos_validos=[
            "2026-11-06",
            "06/11/2026",
            "31-12-2025",
            "29/02/2024",
            "30-04-1999",
        ],
        ejemplos_invalidos=[
            "2026-02-30",
            "31/04/2026",
            "31-11-2026",
            "2026-13-01",
            "00/05/2026",
            "1899-01-15",
        ],
    ),
}


# =============================================================================
# COMPILACIÓN Y EJECUCIÓN DE VALIDADORES CON EL MOTOR DEL EJERCICIO 2
# =============================================================================

@dataclass
class ResultadoValidacionTexto:
    """Resultado detallado de validar una cadena de entrada en un validador del Ejercicio 4."""

    clave_validador: str
    cadena: str
    aceptada_automata: bool
    aceptada_afd_sin_minimizar: bool
    aceptada_re_python: bool
    congruente: bool
    recorrido_afd_minimo: list[tuple[str, str, str]]
    estado_final_alcanzado: str | None
    detalle: str


@dataclass
class ValidadorCompilado:
    """Validador construido con el flujo completo del Ejercicio 2 (AFN-λ -> AFN -> AFD -> AFD mínimo)."""

    especificacion: EspecificacionValidador
    tuberia: ResultadoERaAutomata
    regex_python: str
    patron_re: re.Pattern[str]

    @property
    def clave(self) -> str:
        return self.especificacion.clave

    @property
    def titulo(self) -> str:
        return self.especificacion.titulo

    @property
    def expresion_curso(self) -> str:
        return self.especificacion.expresion_curso

    @property
    def afn_lambda(self) -> AutomataFinito:
        return self.tuberia.afn_lambda

    @property
    def afn(self) -> AutomataFinito:
        return self.tuberia.afn

    @property
    def afd(self) -> AutomataFinito:
        return self.tuberia.afd

    @property
    def afd_minimo(self) -> AutomataFinito:
        return self.tuberia.afd_minimo

    @property
    def estados_afd_antes_minimizar(self) -> int:
        return len(self.tuberia.afd.estados)

    @property
    def estados_afd_despues_minimizar(self) -> int:
        return len(self.tuberia.afd_minimo.estados)

    def validar(self, cadena: str) -> ResultadoValidacionTexto:
        """Valida `cadena` con el AFD mínimo del Ejercicio 2 y verifica su coincidencia con `re.fullmatch`."""
        ok_min = self.afd_minimo.acepta(cadena)
        ok_afd = self.afd.acepta(cadena)
        ok_re = bool(self.patron_re.fullmatch(cadena))
        congruente = (ok_min == ok_re) and (ok_afd == ok_re)

        # Reconstruir la traza paso a paso sobre el AFD mínimo
        recorrido: list[tuple[str, str, str]] = []
        actual: str | None = self.afd_minimo.inicial
        abortado_en: tuple[int, str] | None = None

        for idx, ch in enumerate(cadena, start=1):
            if actual is None:
                break
            destinos = self.afd_minimo.destinos(actual, ch)
            if not destinos:
                abortado_en = (idx, ch)
                actual = None
                break
            sig = destinos[0]
            recorrido.append((actual, ch, sig))
            actual = sig

        if ok_min:
            detalle = (
                f"VÁLIDA — La cadena fue aceptada por el AFD mínimo en el estado final '{actual}' "
                f"tras consumir {len(cadena)} símbolo(s) (coincide con re.fullmatch={ok_re})."
            )
        elif abortado_en is not None:
            pos_err, ch_err = abortado_en
            ult_estado = recorrido[-1][2] if recorrido else self.afd_minimo.inicial
            detalle = (
                f"INVÁLIDA — Rechazada en el carácter #{pos_err} ('{ch_err}'): desde el estado "
                f"'{ult_estado}' no existe transición válida (transición al estado pozo implícito; "
                f"re.fullmatch={ok_re})."
            )
        else:
            detalle = (
                f"INVÁLIDA — Se consumió toda la cadena pero el estado alcanzado '{actual}' "
                f"no es de aceptación (estados finales: {sorted(self.afd_minimo.aceptacion)}; "
                f"re.fullmatch={ok_re})."
            )

        return ResultadoValidacionTexto(
            clave_validador=self.clave,
            cadena=cadena,
            aceptada_automata=ok_min,
            aceptada_afd_sin_minimizar=ok_afd,
            aceptada_re_python=ok_re,
            congruente=congruente,
            recorrido_afd_minimo=recorrido,
            estado_final_alcanzado=actual,
            detalle=detalle,
        )


_CACHE_VALIDADORES: dict[str, ValidadorCompilado] = {}


def obtener_validador(clave: str) -> ValidadorCompilado:
    """Construye (o recupera de caché en memoria) el validador solicitado con el motor del Ejercicio 2."""
    if clave not in ESPECIFICACIONES_VALIDADORES:
        raise KeyError(
            f"Validador desconocido '{clave}'. Opciones válidas: {list(ESPECIFICACIONES_VALIDADORES)}"
        )
    if clave not in _CACHE_VALIDADORES:
        esp = ESPECIFICACIONES_VALIDADORES[clave]
        tuberia = er_a_automata_completo(
            esp.expresion_curso,
            clases=CLASES_PREDEFINIDAS,
            incluir_pozo=False,
        )
        regex_py = tuberia.kleene_uno.regex_python
        patron = re.compile(regex_py)
        _CACHE_VALIDADORES[clave] = ValidadorCompilado(
            especificacion=esp,
            tuberia=tuberia,
            regex_python=regex_py,
            patron_re=patron,
        )
    return _CACHE_VALIDADORES[clave]


def obtener_todos_los_validadores() -> dict[str, ValidadorCompilado]:
    """Devuelve el diccionario ordenado con los cuatro validadores compilados."""
    return {k: obtener_validador(k) for k in ESPECIFICACIONES_VALIDADORES}


# =============================================================================
# PROCEDIMIENTO DOCUMENTADO DE GENERACIÓN DE >= 500 CADENAS Y CONGRUENCIA
# =============================================================================

@dataclass(frozen=True)
class MuestraCorpusValidador:
    """Una cadena de prueba generada para evaluar la congruencia entre el autómata y `re.fullmatch`."""

    cadena: str
    categoria: str        # "valida_estructurada" | "invalida_mutacion" | "invalida_frontera" | "invalida_ruido"
    esperado_valido: bool
    descripcion: str


@dataclass
class ResultadoCongruenciaValidador:
    """Resumen de la prueba de congruencia sobre >= 500 cadenas entre el autómata y `re.fullmatch`."""

    clave_validador: str
    total_cadenas: int
    total_validas: int
    total_invalidas: int
    coincidencias_afd_minimo_vs_re: int
    coincidencias_afd_vs_re: int
    coincidencias_afn_vs_re: int
    discrepancias: list[tuple[str, bool, bool]] = field(default_factory=list)

    @property
    def congruente(self) -> bool:
        return (
            self.total_cadenas >= 500
            and self.coincidencias_afd_minimo_vs_re == self.total_cadenas
            and self.coincidencias_afd_vs_re == self.total_cadenas
            and len(self.discrepancias) == 0
        )


def _generar_corpus_correo(rng: random.Random, n_validas: int, n_invalidas: int) -> list[MuestraCorpusValidador]:
    """Genera `n_validas` direcciones de correo válidas y `n_invalidas` inválidas mediante reglas documentadas."""
    muestras: list[MuestraCorpusValidador] = []
    vistos: set[str] = set()

    chars_u = CLASES_PREDEFINIDAS["U"]
    chars_a = CLASES_PREDEFINIDAS["A"]
    chars_l = CLASES_PREDEFINIDAS["L"]
    tlds_comunes = ["mx", "com", "org", "net", "edu", "gob", "io", "info", "escom", "ipn"]

    def agregar(cad: str, cat: str, esp: bool, desc: str) -> bool:
        if cad in vistos:
            return False
        vistos.add(cad)
        muestras.append(MuestraCorpusValidador(cad, cat, esp, desc))
        return True

    # 1. Cadenas válidas estructuradas
    for ej in ESPECIFICACIONES_VALIDADORES["correo"].ejemplos_validos:
        agregar(ej, "valida_estructurada", True, "Ejemplo canónico de correo válido")

    while sum(1 for m in muestras if m.esperado_valido) < n_validas:
        num_bloques_local = rng.randint(1, 3)
        bloques_local = [
            "".join(rng.choice(chars_u) for _ in range(rng.randint(1, 6)))
            for _ in range(num_bloques_local)
        ]
        local = bloques_local[0]
        for b in bloques_local[1:]:
            local += rng.choice([".", "-"]) + b

        num_etiquetas_dom = rng.randint(1, 3)
        etiquetas_dom = []
        for _ in range(num_etiquetas_dom):
            ini = rng.choice(chars_a)
            resto = "".join(rng.choice(chars_a + ["-"]) for _ in range(rng.randint(0, 5)))
            etiquetas_dom.append(ini + resto)
        tld = rng.choice(tlds_comunes) if rng.random() < 0.6 else "".join(
            rng.choice(chars_l) for _ in range(rng.randint(2, 5))
        )
        correo = f"{local}@{'.'.join(etiquetas_dom)}.{tld}"
        agregar(correo, "valida_estructurada", True, "Correo generado por derivación gramatical de la ER")

    # 2. Cadenas inválidas por violación de frontera, mutación estructural y ruido léxico
    for ej in ESPECIFICACIONES_VALIDADORES["correo"].ejemplos_invalidos:
        agregar(ej, "invalida_frontera", False, "Ejemplo canónico de correo inválido")
    agregar("", "invalida_frontera", False, "Cadena vacía")

    patrones_invalidos = [
        lambda u, d, t: f"{u}.{d}.{t}",                     # Sin símbolo '@'
        lambda u, d, t: f"{u}@@{d}.{t}",                    # Doble '@@'
        lambda u, d, t: f".{u}@{d}.{t}",                    # Punto inicial en parte local
        lambda u, d, t: f"-{u}@{d}.{t}",                    # Guion inicial en parte local
        lambda u, d, t: f"{u}.@{d}.{t}",                    # Punto final antes de '@'
        lambda u, d, t: f"{u}-@{d}.{t}",                    # Guion final antes de '@'
        lambda u, d, t: f"{u}..{u}@{d}.{t}",                # Doble punto consecutivo en parte local
        lambda u, d, t: f"{u}.-{u}@{d}.{t}",                # Punto y guion consecutivos en parte local
        lambda u, d, t: f"{u}@{d}",                         # Dominio sin punto ni TLD
        lambda u, d, t: f"{u}@.{d}.{t}",                    # Punto inicial tras '@'
        lambda u, d, t: f"{u}@-{d}.{t}",                    # Guion al inicio de etiqueta de dominio
        lambda u, d, t: f"{u}@{d}..{t}",                    # Doble punto en dominio
        lambda u, d, t: f"{u}@{d}.{t[0]}",                  # TLD de 1 sola letra
        lambda u, d, t: f"{u}@{d}.{t}1",                    # Dígito en el TLD
        lambda u, d, t: f"{u}@{d}_{d}.{t}",                 # Guion bajo '_' en el dominio
        lambda u, d, t: f"@{d}.{t}",                        # Parte local vacía
        lambda u, d, t: f"{u}@",                            # Dominio vacío
        lambda u, d, t: f"{u} {u}@{d}.{t}",                 # Espacio en blanco en parte local
        lambda u, d, t: f"MAYUS_{u}@{d}.{t}",               # Letras mayúsculas fuera de U
    ]

    idx_pat = 0
    while sum(1 for m in muestras if not m.esperado_valido) < n_invalidas:
        u = "".join(rng.choice(chars_u) for _ in range(rng.randint(2, 6)))
        d = "".join(rng.choice(chars_a) for _ in range(rng.randint(2, 6)))
        t = "".join(rng.choice(chars_l) for _ in range(rng.randint(2, 4)))
        fn = patrones_invalidos[idx_pat % len(patrones_invalidos)]
        idx_pat += 1
        cand = fn(u, d, t)
        agregar(cand, "invalida_mutacion", False, f"Mutación estructural #{idx_pat}")

    return muestras


def _generar_corpus_telefono(rng: random.Random, n_validas: int, n_invalidas: int) -> list[MuestraCorpusValidador]:
    """Genera `n_validas` teléfonos nacionales válidos y `n_invalidas` inválidos."""
    muestras: list[MuestraCorpusValidador] = []
    vistos: set[str] = set()

    chars_p = CLASES_PREDEFINIDAS["P"]
    chars_d = CLASES_PREDEFINIDAS["D"]

    def agregar(cad: str, cat: str, esp: bool, desc: str) -> bool:
        if cad in vistos:
            return False
        vistos.add(cad)
        muestras.append(MuestraCorpusValidador(cad, cat, esp, desc))
        return True

    for ej in ESPECIFICACIONES_VALIDADORES["telefono_nacional"].ejemplos_validos:
        agregar(ej, "valida_estructurada", True, "Ejemplo canónico de teléfono nacional válido")

    formatos_validos = [
        lambda d: "".join(d),                                       # PDDDDDDDDD
        lambda d: f"{''.join(d[:2])}-{''.join(d[2:6])}-{''.join(d[6:])}",  # PD-DDDD-DDDD
        lambda d: f"{''.join(d[:3])}-{''.join(d[3:6])}-{''.join(d[6:])}",  # PDD-DDD-DDDD
        lambda d: f"{''.join(d[:2])} {''.join(d[2:6])} {''.join(d[6:])}",  # PD DDDD DDDD
        lambda d: f"{''.join(d[:3])} {''.join(d[3:6])} {''.join(d[6:])}",  # PDD DDD DDDD
        lambda d: f"({''.join(d[:2])}){''.join(d[2:6])}{''.join(d[6:])}",
        lambda d: f"({''.join(d[:2])}) {''.join(d[2:6])}-{''.join(d[6:])}",
        lambda d: f"({''.join(d[:2])}) {''.join(d[2:6])} {''.join(d[6:])}",
        lambda d: f"({''.join(d[:3])}){''.join(d[3:6])}-{''.join(d[6:])}",
        lambda d: f"({''.join(d[:3])}) {''.join(d[3:6])}-{''.join(d[6:])}",
        lambda d: f"({''.join(d[:3])}) {''.join(d[3:6])} {''.join(d[6:])}",
    ]

    idx_f = 0
    while sum(1 for m in muestras if m.esperado_valido) < n_validas:
        digs = [rng.choice(chars_p)] + [rng.choice(chars_d) for _ in range(9)]
        fn = formatos_validos[idx_f % len(formatos_validos)]
        idx_f += 1
        agregar(fn(digs), "valida_estructurada", True, f"Formato nacional válido #{idx_f}")

    for ej in ESPECIFICACIONES_VALIDADORES["telefono_nacional"].ejemplos_invalidos:
        agregar(ej, "invalida_frontera", False, "Ejemplo canónico de teléfono inválido")
    agregar("", "invalida_frontera", False, "Cadena vacía")

    formatos_invalidos = [
        lambda d: "0" + "".join(d[1:]),                             # Inicia con 0 (prohibido por IFT)
        lambda d: "1" + "".join(d[1:]),                             # Inicia con 1 (prohibido por IFT)
        lambda d: "".join(d[:9]),                                   # Sólo 9 dígitos
        lambda d: "".join(d) + rng.choice(chars_d),                 # 11 dígitos
        lambda d: "".join(d[:8]),                                   # 8 dígitos
        lambda d: f"{''.join(d[:2])}-{''.join(d[2:6])} {''.join(d[6:])}",  # Separadores mezclados guion/espacio
        lambda d: f"{''.join(d[:2])} {''.join(d[2:6])}-{''.join(d[6:])}",  # Separadores mezclados espacio/guion
        lambda d: f"{''.join(d[:4])}-{''.join(d[4:7])}-{''.join(d[7:])}",  # Agrupamiento 4-3-3 inválido
        lambda d: f"({''.join(d[:2])}{''.join(d[2:6])}-{''.join(d[6:])}",  # Paréntesis sin cerrar
        lambda d: f"{''.join(d[:2])}){''.join(d[2:6])}-{''.join(d[6:])}",  # Paréntesis sin abrir
        lambda d: f"({''.join(d[:4])}) {''.join(d[4:7])}-{''.join(d[7:])}", # LADA de 4 dígitos entre paréntesis
        lambda d: f"+52 {''.join(d[:2])} {''.join(d[2:6])} {''.join(d[6:])}", # Prefijo internacional +52
        lambda d: f"{''.join(d[:2])}.{''.join(d[2:6])}.{''.join(d[6:])}",  # Separador con puntos
        lambda d: f"({''.join(d[:2])})--{''.join(d[2:6])}-{''.join(d[6:])}", # Doble guion
        lambda d: f"{''.join(d[:5])}a{''.join(d[6:])}",             # Letra infiltrada
    ]

    idx_inv = 0
    while sum(1 for m in muestras if not m.esperado_valido) < n_invalidas:
        digs = [rng.choice(chars_p)] + [rng.choice(chars_d) for _ in range(9)]
        fn = formatos_invalidos[idx_inv % len(formatos_invalidos)]
        idx_inv += 1
        agregar(fn(digs), "invalida_mutacion", False, f"Mutación telefónica inválida #{idx_inv}")

    return muestras


def _generar_corpus_url(rng: random.Random, n_validas: int, n_invalidas: int) -> list[MuestraCorpusValidador]:
    """Genera `n_validas` URLs válidas y `n_invalidas` inválidas."""
    muestras: list[MuestraCorpusValidador] = []
    vistos: set[str] = set()

    chars_a = CLASES_PREDEFINIDAS["A"]
    chars_l = CLASES_PREDEFINIDAS["L"]
    chars_r = CLASES_PREDEFINIDAS["R"]

    def agregar(cad: str, cat: str, esp: bool, desc: str) -> bool:
        if cad in vistos:
            return False
        vistos.add(cad)
        muestras.append(MuestraCorpusValidador(cad, cat, esp, desc))
        return True

    for ej in ESPECIFICACIONES_VALIDADORES["url"].ejemplos_validos:
        agregar(ej, "valida_estructurada", True, "Ejemplo canónico de URL válida")

    while sum(1 for m in muestras if m.esperado_valido) < n_validas:
        esquema = rng.choice(["http", "https"])
        n_sub = rng.randint(1, 3)
        partes_host = [
            rng.choice(chars_a) + "".join(rng.choice(chars_a + ["-"]) for _ in range(rng.randint(0, 5)))
            for _ in range(n_sub)
        ]
        tld = "".join(rng.choice(chars_l) for _ in range(rng.randint(2, 4)))
        host = ".".join(partes_host) + "." + tld

        puerto = ""
        if rng.random() < 0.35:
            puerto = ":" + rng.choice(CLASES_PREDEFINIDAS["N"]) + "".join(
                rng.choice(CLASES_PREDEFINIDAS["D"]) for _ in range(rng.randint(1, 3))
            )

        ruta = ""
        n_seg = rng.randint(0, 3)
        for _ in range(n_seg):
            seg = "".join(rng.choice(chars_r) for _ in range(rng.randint(0, 6)))
            ruta += "/" + seg

        query = ""
        if rng.random() < 0.4:
            q_ini = rng.choice(chars_r)
            q_resto = "".join(rng.choice(chars_r + ["=", "&"]) for _ in range(rng.randint(1, 8)))
            query = "?" + q_ini + q_resto

        url = f"{esquema}://{host}{puerto}{ruta}{query}"
        agregar(url, "valida_estructurada", True, "URL generada por derivación de la ER")

    for ej in ESPECIFICACIONES_VALIDADORES["url"].ejemplos_invalidos:
        agregar(ej, "invalida_frontera", False, "Ejemplo canónico de URL inválida")
    agregar("", "invalida_frontera", False, "Cadena vacía")

    mutaciones_url = [
        lambda h, r: f"ftp://{h}/{r}",                      # Esquema ftp no soportado
        lambda h, r: f"htp://{h}/{r}",                      # Esquema mal escrito
        lambda h, r: f"http:/{h}/{r}",                      # Una sola diagonal tras ':'
        lambda h, r: f"http://{h}:080/{r}",                 # Puerto con cero inicial
        lambda h, r: f"http://{h}:/{r}",                    # Dos puntos de puerto sin dígitos
        lambda h, r: f"https://-{h}/{r}",                   # Host inicia con guion
        lambda h, r: f"https://.{h}/{r}",                   # Host inicia con punto
        lambda h, r: f"https://{h}..com/{r}",               # Doble punto en host
        lambda h, r: f"https://{h.split('.')[0]}.a/{r}",    # TLD de 1 sola letra
        lambda h, r: f"https://{h.split('.')[0]}.c9/{r}",   # Dígito en el TLD
        lambda h, r: f"https://{h}/?={r}",                  # Query inicia con '=' en vez de R
        lambda h, r: f"https://{h}/?&{r}",                  # Query inicia con '&' en vez de R
        lambda h, r: f"https://{h}/?",                      # '?' sin ningún carácter de consulta
        lambda h, r: f"https://{h}/{r}#seccion",            # Fragmento '#' fuera del lenguaje
        lambda h, r: f"https://{h}/ruta con espacio/{r}",   # Espacio en la ruta
    ]

    idx_u = 0
    while sum(1 for m in muestras if not m.esperado_valido) < n_invalidas:
        h = (
            "".join(rng.choice(chars_a) for _ in range(rng.randint(2, 5)))
            + "."
            + "".join(rng.choice(chars_l) for _ in range(rng.randint(2, 4)))
        )
        r = "".join(rng.choice(chars_r) for _ in range(rng.randint(2, 6)))
        fn = mutaciones_url[idx_u % len(mutaciones_url)]
        idx_u += 1
        agregar(fn(h, r), "invalida_mutacion", False, f"Mutación de URL inválida #{idx_u}")

    return muestras


def _generar_corpus_fecha(rng: random.Random, n_validas: int, n_invalidas: int) -> list[MuestraCorpusValidador]:
    """Genera `n_validas` fechas válidas y `n_invalidas` inválidas en los tres formatos."""
    muestras: list[MuestraCorpusValidador] = []
    vistos: set[str] = set()

    meses_max_dias = {
        1: 31, 2: 29, 3: 31, 4: 30, 5: 31, 6: 30,
        7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31,
    }

    def agregar(cad: str, cat: str, esp: bool, desc: str) -> bool:
        if cad in vistos:
            return False
        vistos.add(cad)
        muestras.append(MuestraCorpusValidador(cad, cat, esp, desc))
        return True

    for ej in ESPECIFICACIONES_VALIDADORES["fecha"].ejemplos_validos:
        agregar(ej, "valida_estructurada", True, "Ejemplo canónico de fecha válida")

    # Cubrir sistemáticamente todos los meses y los 3 formatos
    formatos_f = [
        lambda a, m, d: f"{a:04d}-{m:02d}-{d:02d}",
        lambda a, m, d: f"{d:02d}/{m:02d}/{a:04d}",
        lambda a, m, d: f"{d:02d}-{m:02d}-{a:04d}",
    ]

    idx_f = 0
    while sum(1 for m in muestras if m.esperado_valido) < n_validas:
        mes = (idx_f % 12) + 1
        max_d = meses_max_dias[mes]
        dia = rng.randint(1, max_d)
        anio = rng.randint(1900, 2099)
        fn = formatos_f[idx_f % 3]
        idx_f += 1
        agregar(fn(anio, mes, dia), "valida_estructurada", True, f"Fecha válida mes {mes:02d}")

    for ej in ESPECIFICACIONES_VALIDADORES["fecha"].ejemplos_invalidos:
        agregar(ej, "invalida_frontera", False, "Ejemplo canónico de fecha inválida")
    agregar("", "invalida_frontera", False, "Cadena vacía")

    # Casos inválidos de frontera de calendario y formato
    generadores_invalidos = [
        # Día 30 o 31 en febrero
        lambda a: f"{a:04d}-02-30",
        lambda a: f"{a:04d}-02-31",
        lambda a: f"30/02/{a:04d}",
        lambda a: f"31/02/{a:04d}",
        lambda a: f"30-02-{a:04d}",
        lambda a: f"31-02-{a:04d}",
        # Día 31 en meses de 30 días (04, 06, 09, 11)
        lambda a: f"{a:04d}-{rng.choice([4, 6, 9, 11]):02d}-31",
        lambda a: f"31/{rng.choice([4, 6, 9, 11]):02d}/{a:04d}",
        lambda a: f"31-{rng.choice([4, 6, 9, 11]):02d}-{a:04d}",
        # Día 00 o >= 32
        lambda a: f"{a:04d}-{rng.randint(1, 12):02d}-00",
        lambda a: f"00/{rng.randint(1, 12):02d}/{a:04d}",
        lambda a: f"{a:04d}-{rng.randint(1, 12):02d}-{rng.randint(32, 39):02d}",
        lambda a: f"{rng.randint(32, 39):02d}/{rng.randint(1, 12):02d}/{a:04d}",
        # Mes 00 o >= 13
        lambda a: f"{a:04d}-00-{rng.randint(1, 28):02d}",
        lambda a: f"{a:04d}-{rng.randint(13, 19):02d}-{rng.randint(1, 28):02d}",
        lambda a: f"{rng.randint(1, 28):02d}/{rng.randint(13, 19):02d}/{a:04d}",
        # Año fuera de 1900..2099
        lambda a: f"{rng.randint(1000, 1899):04d}-05-15",
        lambda a: f"{rng.randint(2100, 2999):04d}-05-15",
        lambda a: f"15/05/{rng.randint(2100, 2999):04d}",
        # Separadores mezclados o formato AAAA/MM/DD no incluido
        lambda a: f"{a:04d}/{rng.randint(1, 12):02d}/{rng.randint(1, 28):02d}",
        lambda a: f"{rng.randint(1, 28):02d}/{rng.randint(1, 12):02d}-{a:04d}",
        lambda a: f"{rng.randint(1, 28):02d}-{rng.randint(1, 12):02d}/{a:04d}",
        # Sin cero inicial en día o mes
        lambda a: f"{a:04d}-{rng.randint(1, 9)}-{rng.randint(10, 28)}",
        lambda a: f"{rng.randint(1, 9)}/{rng.randint(1, 9)}/{a:04d}",
    ]

    idx_inv = 0
    while sum(1 for m in muestras if not m.esperado_valido) < n_invalidas:
        anio = rng.randint(1900, 2099)
        fn = generadores_invalidos[idx_inv % len(generadores_invalidos)]
        idx_inv += 1
        agregar(fn(anio), "invalida_frontera", False, f"Fecha inválida #{idx_inv}")

    return muestras


def generar_corpus_validador(
    clave: str,
    total: int = 500,
    semilla: int = 2026,
) -> list[MuestraCorpusValidador]:
    """Genera un conjunto determinista de al menos `total` (>= 500) cadenas válidas e inválidas
    para el validador `clave`.

    Procedimiento documentado:
    - Mitad de cadenas válidas (`total // 2`, mínimo 250): generadas por derivación controlada sobre
      las subexpresiones de cada validador, garantizando cobertura de todas las ramas de unión (`+`)
      y longitudes 0, 1, 2, 3 en las cerraduras de Kleene (`*`).
    - Mitad de cadenas inválidas (`total - total // 2`, mínimo 250): generadas aplicando operadores
      de mutación sintáctica, violaciones de frontera numérica/calendario y símbolos externos al
      alfabeto.
    """
    if total < 500:
        total = 500
    n_val = total // 2
    n_inv = total - n_val
    rng = random.Random(semilla)

    if clave == "correo":
        return _generar_corpus_correo(rng, n_val, n_inv)
    if clave == "telefono_nacional":
        return _generar_corpus_telefono(rng, n_val, n_inv)
    if clave == "url":
        return _generar_corpus_url(rng, n_val, n_inv)
    if clave == "fecha":
        return _generar_corpus_fecha(rng, n_val, n_inv)
    raise KeyError(f"Validador desconocido: {clave}")


def verificar_congruencia_validador(
    clave: str,
    total: int = 500,
    semilla: int = 2026,
    evaluar_afn: bool = False,
) -> ResultadoCongruenciaValidador:
    """Evalúa el autómata del Ejercicio 2 frente a `re.fullmatch` sobre al menos 500 cadenas."""
    validador = obtener_validador(clave)
    corpus = generar_corpus_validador(clave, total=total, semilla=semilla)

    coinc_min = 0
    coinc_afd = 0
    coinc_afn = 0
    n_validas = 0
    n_invalidas = 0
    discrepancias: list[tuple[str, bool, bool]] = []

    for muestra in corpus:
        w = muestra.cadena
        res_min = validador.afd_minimo.acepta(w)
        res_afd = validador.afd.acepta(w)
        res_afn = validador.afn.acepta(w) if evaluar_afn else res_min
        res_re = bool(validador.patron_re.fullmatch(w))

        if res_re:
            n_validas += 1
        else:
            n_invalidas += 1

        if res_min == res_re and res_afd == res_re and res_re == muestra.esperado_valido:
            coinc_min += 1
        else:
            discrepancias.append((w, res_min, res_re))

        if res_afd == res_re:
            coinc_afd += 1
        if res_afn == res_re:
            coinc_afn += 1

    return ResultadoCongruenciaValidador(
        clave_validador=clave,
        total_cadenas=len(corpus),
        total_validas=n_validas,
        total_invalidas=n_invalidas,
        coincidencias_afd_minimo_vs_re=coinc_min,
        coincidencias_afd_vs_re=coinc_afd,
        coincidencias_afn_vs_re=coinc_afn,
        discrepancias=discrepancias,
    )
