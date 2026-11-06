"""Módulo `expresiones.py`: Expresiones regulares y las dos direcciones del Teorema de Kleene
(Práctica 3, Ejercicio 1 y Práctica 4, Ejercicios 2, 3 y 4).

Implementa en Python puro (sin bibliotecas externas de autómatas):
1. Analizador léxico y sintáctico por descenso recursivo (`analizar_expresion`, `ErrorSintaxisER`)
   para expresiones regulares con la notación del curso:
   - `+` para la unión (menor precedencia, asociativa por la izquierda),
   - yuxtaposición (y opcionalmente `·`) para la concatenación (precedencia intermedia),
   - `*` para la cerradura de Kleene (mayor precedencia, unario postfijo),
   - `λ` para la palabra vacía y `∅` para el lenguaje vacío,
   - paréntesis `(` y `)` y soporte para clases de símbolos abreviadas declaradas (ej. `D`, `L`).
   Rechaza cualquier expresión mal formada indicando la posición exacta del error.
2. Dirección 1 del Teorema de Kleene — De expresión regular a autómata (`er_a_afn_lambda_detallado`,
   `er_a_automata_completo`):
   - Construye el AFN-λ en forma estándar mediante los casos básicos (∅, λ, a ∈ Σ) y las
     construcciones inductivas de unión, concatenación y cerradura de Kleene (Thompson, 1968;
     Hopcroft, Motwani & Ullman, 2007, §3.2.3), registrando paso a paso cada autómata parcial.
   - Aplica al AFN-λ resultante los algoritmos de la Práctica 3: eliminación de transiciones λ,
     construcción de subconjuntos alcanzables y minimización de AFD.
3. Dirección 2 del Teorema de Kleene — De autómata a expresión regular (`eliminacion_de_estados_detallada`,
   `comparar_expresiones_por_afd_minimo`, `tres_metodos`):
   - Verifica previamente que el autómata importado sea determinista indicando, en caso contrario,
     qué estado y qué símbolo lo impiden (`verificar_determinismo`).
   - Obtiene la expresión regular por el método de eliminación de estados registrando el
     Autómata Finito Generalizado (GNFA) completo después de cada estado eliminado.
   - Compara dos expresiones regulares convirtiendo ambas en AFD mínimos con el Ejercicio 2 y
     aplicando la prueba de equivalencia formal de la Práctica 3 (`son_afd_equivalentes`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Union

try:
    from automata import (
        AutomataFinito,
        ResultadoEliminacionLambda,
        ResultadoEquivalenciaAFD,
        ResultadoMinimizacion,
        ResultadoSubconjuntos,
        ResultadoVerificacionAFD,
    )
except ImportError:  # pragma: no cover
    from src.automata import (
        AutomataFinito,
        ResultadoEliminacionLambda,
        ResultadoEquivalenciaAFD,
        ResultadoMinimizacion,
        ResultadoSubconjuntos,
        ResultadoVerificacionAFD,
    )

# -----------------------------------------------------------------------------
# Árbol sintáctico simplificado de expresiones regulares (Práctica 3 / Kleene II)
#   VACIO (∅) -> None ; LAMBDA (λ) -> "" ; símbolo -> ("s", a)
#   unión -> ("u", (e1, e2, ...)) ; concatenación -> ("c", (e1, e2, ...)) ; estrella -> ("*", e)
# -----------------------------------------------------------------------------
ER = Union[None, str, tuple]
VACIO: ER = None
LAMBDA: ER = ""


def simbolo(a: str) -> ER:
    return ("s", a)


def _necesita_escape_texto(ch: str) -> bool:
    return ch in {"+", "*", "(", ")", "λ", "∅", "\\", " "}


def _formatear_simbolo_curso(ch: str) -> str:
    if _necesita_escape_texto(ch):
        return "\\" + ch
    return ch


def a_texto(e: ER) -> str:
    """Convierte el árbol a la notación del curso: '+' para unión, yuxtaposición y '*'."""
    if e is None:
        return "∅"
    if e == "":
        return "λ"
    tipo = e[0]
    if tipo == "s":
        return _formatear_simbolo_curso(e[1])
    if tipo == "u":
        return "+".join(a_texto(x) for x in e[1])
    if tipo == "c":
        partes = []
        for x in e[1]:
            t = a_texto(x)
            partes.append(f"({t})" if isinstance(x, tuple) and x[0] == "u" else t)
        return "".join(partes)
    if tipo == "*":
        x = e[1]
        t = a_texto(x)
        atomico = isinstance(x, tuple) and x[0] == "s" and len(x[1]) == 1
        return f"{t}*" if atomico else f"({t})*"
    raise ValueError(e)


def union(*args: ER) -> ER:
    terminos: list[ER] = []
    for a in args:
        if a is None:
            continue
        if isinstance(a, tuple) and a[0] == "u":
            candidatos = list(a[1])
        else:
            candidatos = [a]
        for c in candidatos:
            if c not in terminos:
                terminos.append(c)
    # λ es redundante si algún término es una estrella (λ ∈ L(r*))
    if "" in terminos and any(isinstance(t, tuple) and t[0] == "*" for t in terminos):
        terminos.remove("")
    if not terminos:
        return None
    if len(terminos) == 1:
        return terminos[0]
    terminos.sort(key=lambda t: (t != "", a_texto(t)))
    return ("u", tuple(terminos))


def concat(*args: ER) -> ER:
    factores: list[ER] = []
    for a in args:
        if a is None:
            return None
        if a == "":
            continue
        if isinstance(a, tuple) and a[0] == "c":
            factores.extend(a[1])
        else:
            factores.append(a)
    # r* r* = r*
    compactos: list[ER] = []
    for f in factores:
        if compactos and f == compactos[-1] and isinstance(f, tuple) and f[0] == "*":
            continue
        compactos.append(f)
    if not compactos:
        return ""
    if len(compactos) == 1:
        return compactos[0]
    return ("c", tuple(compactos))


def estrella(a: ER) -> ER:
    if a is None or a == "":
        return ""
    if isinstance(a, tuple) and a[0] == "*":
        return a
    if isinstance(a, tuple) and a[0] == "u" and "" in a[1]:
        sin_lambda = union(*[t for t in a[1] if t != ""])
        return estrella(sin_lambda)
    return ("*", a)


def a_regex_python(e: ER) -> str:
    """Traduce el árbol simplificado `ER` a sintaxis de `re` de Python."""
    if e is None:
        return "(?!)"
    if e == "":
        return ""
    tipo = e[0]
    if tipo == "s":
        return re.escape(e[1])
    if tipo == "u":
        return "(?:" + "|".join(a_regex_python(x) for x in e[1]) + ")"
    if tipo == "c":
        return "".join(a_regex_python(x) for x in e[1])
    if tipo == "*":
        return "(?:" + a_regex_python(e[1]) + ")*"
    raise ValueError(e)


def compilar(e: ER) -> re.Pattern[str]:
    return re.compile("^(?:" + a_regex_python(e) + ")$")


def longitud(e: ER) -> int:
    """Número de símbolos de Σ que aparecen en la expresión."""
    if e is None or e == "":
        return 0
    if e[0] == "s":
        return 1
    if e[0] == "*":
        return longitud(e[1])
    return sum(longitud(x) for x in e[1])


def _etiqueta(afd: AutomataFinito, p: str, q: str) -> ER:
    """Unión de los símbolos a tales que δ(p, a) = q."""
    return union(*[simbolo(a) for a in afd.alfabeto if q in afd.destinos(p, a)])


# =============================================================================
# PRÁCTICA 4 — EJERCICIO 2: ANALIZADOR SINTÁCTICO Y CONSTRUCCIÓN DE KLEENE I
# =============================================================================

# Clases de símbolos abreviadas disponibles cuando el usuario activa abreviaturas
CLASES_PREDEFINIDAS: dict[str, list[str]] = {
    "D": [str(d) for d in range(10)],                         # Dígitos decimales: 0 + 1 + ... + 9
    "N": [str(d) for d in range(1, 10)],                      # Dígitos sin cero: 1 + 2 + ... + 9
    "P": [str(d) for d in range(2, 10)],                      # Primer dígito NIR telefónico IFT: 2 + 3 + ... + 9
    "L": [chr(c) for c in range(ord("a"), ord("z") + 1)],     # Letras minúsculas ASCII: a + b + ... + z
    "M": [chr(c) for c in range(ord("A"), ord("Z") + 1)],     # Letras mayúsculas ASCII: A + B + ... + Z
    "A": (
        [chr(c) for c in range(ord("a"), ord("z") + 1)]
        + [str(d) for d in range(10)]
    ),                                                        # Alfanuméricos en minúscula: a..z + 0..9
    "X": (
        [chr(c) for c in range(ord("a"), ord("z") + 1)]
        + [chr(c) for c in range(ord("A"), ord("Z") + 1)]
        + [str(d) for d in range(10)]
    ),                                                        # Alfanuméricos completos: a..z + A..Z + 0..9
    "U": (
        [chr(c) for c in range(ord("a"), ord("z") + 1)]
        + [str(d) for d in range(10)]
        + ["_"]
    ),                                                        # Identificador local de usuario: a..z + 0..9 + _
    "R": (
        [chr(c) for c in range(ord("a"), ord("z") + 1)]
        + [str(d) for d in range(10)]
        + ["_", "-", "."]
    ),                                                        # Segmento de ruta URL: a..z + 0..9 + _ + - + .
    "T": ["1", "3", "5", "7", "8"],                           # Meses de 31 días (01,03,05,07,08): 1 + 3 + 5 + 7 + 8
    "C": ["4", "6", "9"],                                     # Meses de 30 días (04,06,09): 4 + 6 + 9
}


class ErrorSintaxisER(ValueError):
    """Excepción lanzada cuando una expresión regular está mal formada, indicando la posición exacta."""

    def __init__(self, detalle: str, posicion: int, expresion: str = "") -> None:
        self.detalle = detalle
        self.posicion = max(1, posicion)  # Posición 1-based del carácter donde ocurrió el error
        self.indice = self.posicion - 1   # Índice 0-based correspondiente
        self.expresion = expresion
        indicador = ""
        if expresion:
            caret_pos = max(0, min(self.indice, len(expresion)))
            indicador = f"\n  {expresion}\n  {' ' * caret_pos}^"
        mensaje = f"Error de sintaxis en la posición {self.posicion}: {detalle}{indicador}"
        super().__init__(mensaje)


@dataclass(frozen=True)
class TokenER:
    """Token léxico de una expresión regular con su posición exacta (1-based) en la cadena original."""

    tipo: str   # "SIMBOLO", "CLASE", "LAMBDA", "VACIO", "UNION", "CONCAT", "ESTRELLA", "PAR_IZQ", "PAR_DER"
    valor: str
    posicion: int  # Posición 1-based


@dataclass(frozen=True)
class NodoER:
    """Nodo del árbol sintáctico abstracto (AST) que preserva la estructura exacta para Thompson."""

    tipo: str  # "vacio", "lambda", "simbolo", "clase", "union", "concat", "estrella"
    valor: str = ""
    hijos: tuple[NodoER, ...] = ()
    simbolos_clase: tuple[str, ...] = ()

    def a_er_simplificada(self) -> ER:
        """Convierte el nodo AST al tipo `ER` con simplificaciones algebraicas básicas."""
        if self.tipo == "vacio":
            return VACIO
        if self.tipo == "lambda":
            return LAMBDA
        if self.tipo == "simbolo":
            return simbolo(self.valor)
        if self.tipo == "clase":
            return union(*[simbolo(s) for s in self.simbolos_clase])
        if self.tipo == "union":
            return union(*(h.a_er_simplificada() for h in self.hijos))
        if self.tipo == "concat":
            return concat(*(h.a_er_simplificada() for h in self.hijos))
        if self.tipo == "estrella":
            return estrella(self.hijos[0].a_er_simplificada())
        raise ValueError(f"Tipo de nodo desconocido: {self.tipo}")

    def a_texto_curso(self, expandir_clases: bool = False) -> str:
        """Devuelve la expresión escrita en la notación del curso respetando precedencias."""
        if self.tipo == "vacio":
            return "∅"
        if self.tipo == "lambda":
            return "λ"
        if self.tipo == "simbolo":
            return _formatear_simbolo_curso(self.valor)
        if self.tipo == "clase":
            if expandir_clases:
                return "(" + "+".join(_formatear_simbolo_curso(s) for s in self.simbolos_clase) + ")"
            return self.valor
        if self.tipo == "union":
            return "+".join(h.a_texto_curso(expandir_clases) for h in self.hijos)
        if self.tipo == "concat":
            partes: list[str] = []
            for h in self.hijos:
                t = h.a_texto_curso(expandir_clases)
                if h.tipo == "union":
                    partes.append(f"({t})")
                else:
                    partes.append(t)
            return "".join(partes)
        if self.tipo == "estrella":
            h = self.hijos[0]
            t = h.a_texto_curso(expandir_clases)
            if h.tipo in ("simbolo", "lambda", "vacio") or (h.tipo == "clase" and not expandir_clases):
                return f"{t}*"
            return f"({t})*"
        raise ValueError(f"Tipo de nodo desconocido: {self.tipo}")

    def a_regex_python(self) -> str:
        """Traduce el árbol sintáctico directamente a una expresión regular compatible con `re`."""
        if self.tipo == "vacio":
            return "(?!)"
        if self.tipo == "lambda":
            return ""
        if self.tipo == "simbolo":
            return re.escape(self.valor)
        if self.tipo == "clase":
            if not self.simbolos_clase:
                return "(?!)"
            # Optimización legible para clases estándar
            if list(self.simbolos_clase) == CLASES_PREDEFINIDAS.get("D"):
                return "[0-9]"
            if list(self.simbolos_clase) == CLASES_PREDEFINIDAS.get("N"):
                return "[1-9]"
            if list(self.simbolos_clase) == CLASES_PREDEFINIDAS.get("P"):
                return "[2-9]"
            if list(self.simbolos_clase) == CLASES_PREDEFINIDAS.get("L"):
                return "[a-z]"
            if list(self.simbolos_clase) == CLASES_PREDEFINIDAS.get("M"):
                return "[A-Z]"
            if list(self.simbolos_clase) == CLASES_PREDEFINIDAS.get("A"):
                return "[a-z0-9]"
            if list(self.simbolos_clase) == CLASES_PREDEFINIDAS.get("X"):
                return "[a-zA-Z0-9]"
            if list(self.simbolos_clase) == CLASES_PREDEFINIDAS.get("U"):
                return "[a-z0-9_]"
            if list(self.simbolos_clase) == CLASES_PREDEFINIDAS.get("R"):
                return "[a-z0-9_.-]"
            if list(self.simbolos_clase) == CLASES_PREDEFINIDAS.get("T"):
                return "[13578]"
            if list(self.simbolos_clase) == CLASES_PREDEFINIDAS.get("C"):
                return "[469]"
            return "(?:" + "|".join(re.escape(s) for s in self.simbolos_clase) + ")"
        if self.tipo == "union":
            ramas: list[NodoER] = []

            def recolectar_union(n: NodoER) -> None:
                if n.tipo == "union":
                    for h in n.hijos:
                        recolectar_union(h)
                else:
                    ramas.append(n)

            recolectar_union(self)
            return "(?:" + "|".join(h.a_regex_python() for h in ramas) + ")"
        if self.tipo == "concat":
            return "".join(h.a_regex_python() for h in self.hijos)
        if self.tipo == "estrella":
            h = self.hijos[0]
            sub = h.a_regex_python()
            if h.tipo in ("simbolo", "clase") and (sub.startswith("[") or len(sub) == 1 or (len(sub) == 2 and sub.startswith("\\"))):
                return f"{sub}*"
            return f"(?:{sub})*"
        raise ValueError(f"Tipo de nodo desconocido: {self.tipo}")

    def extraer_alfabeto(self) -> list[str]:
        """Devuelve la lista ordenada por aparición de todos los símbolos de Σ en el árbol."""
        vistos: list[str] = []

        def recorrer(n: NodoER) -> None:
            if n.tipo == "simbolo":
                if n.valor not in vistos:
                    vistos.append(n.valor)
            elif n.tipo == "clase":
                for s in n.simbolos_clase:
                    if s not in vistos:
                        vistos.append(s)
            else:
                for h in n.hijos:
                    recorrer(h)

        recorrer(self)
        return vistos


def tokenizar_expresion(
    texto: str,
    clases: dict[str, list[str]] | None = None,
    alfabeto_permitido: set[str] | None = None,
) -> list[TokenER]:
    """Convierte una cadena con la notación del curso en una lista de `TokenER` con posiciones 1-based."""
    if not texto or not texto.strip():
        raise ErrorSintaxisER(
            "La expresión regular está vacía; debe contener al menos un símbolo, 'λ' o '∅'.",
            posicion=1,
            expresion=texto,
        )

    mapa_clases = dict(clases) if clases else {}
    tokens: list[TokenER] = []
    i = 0
    n = len(texto)

    while i < n:
        ch = texto[i]
        pos_1 = i + 1

        if ch in (" ", "\t", "\r", "\n"):
            i += 1
            continue

        if ch == "\\":
            if i + 1 >= n:
                raise ErrorSintaxisER(
                    "Secuencia de escape '\\' incompleta al final de la expresión.",
                    posicion=pos_1,
                    expresion=texto,
                )
            lit = texto[i + 1]
            if alfabeto_permitido is not None and lit not in alfabeto_permitido:
                raise ErrorSintaxisER(
                    f"El símbolo escapado '\\{lit}' no pertenece al alfabeto permitido.",
                    posicion=pos_1,
                    expresion=texto,
                )
            tokens.append(TokenER("SIMBOLO", lit, pos_1))
            i += 2
            continue

        if ch == "+":
            tokens.append(TokenER("UNION", "+", pos_1))
        elif ch == "*":
            tokens.append(TokenER("ESTRELLA", "*", pos_1))
        elif ch in ("·", "\u22c5"):
            tokens.append(TokenER("CONCAT", ch, pos_1))
        elif ch == "(":
            tokens.append(TokenER("PAR_IZQ", "(", pos_1))
        elif ch == ")":
            tokens.append(TokenER("PAR_DER", ")", pos_1))
        elif ch in ("λ", "ε"):
            tokens.append(TokenER("LAMBDA", "λ", pos_1))
        elif ch in ("∅", "ø"):
            tokens.append(TokenER("VACIO", "∅", pos_1))
        elif ch in mapa_clases:
            tokens.append(TokenER("CLASE", ch, pos_1))
        else:
            # Detectar metacaracteres de otros lenguajes (como '|', '?', '[', ']', '{', '}', '^', '$')
            # no escapados con '\' para dar un mensaje claro de notación del curso
            if ch in ("|", "?", "[", "]", "{", "}", "^", "$"):
                sugerencia = " (use '+' para la unión)" if ch == "|" else " (antemponga '\\' si desea el carácter literal)"
                raise ErrorSintaxisER(
                    f"Carácter '{ch}' no válido en la notación del curso{sugerencia}.",
                    posicion=pos_1,
                    expresion=texto,
                )
            if alfabeto_permitido is not None and ch not in alfabeto_permitido:
                raise ErrorSintaxisER(
                    f"El símbolo '{ch}' no pertenece al alfabeto declarado.",
                    posicion=pos_1,
                    expresion=texto,
                )
            tokens.append(TokenER("SIMBOLO", ch, pos_1))

        i += 1

    return tokens


def analizar_expresion(
    texto: str,
    clases: dict[str, list[str]] | None = None,
    alfabeto_permitido: set[str] | None = None,
) -> NodoER:
    """Analiza una expresión regular en la notación del curso respetando precedencias (* > concat > +).

    Gramática libre de contexto (descenso recursivo):
        Expresion -> Termino ( '+' Termino )*
        Termino   -> Factor ( ['·'] Factor )*
        Factor    -> Primario ( '*' )*
        Primario  -> SIMBOLO | CLASE | 'λ' | '∅' | '(' Expresion ')'

    Si la expresión está mal formada, lanza `ErrorSintaxisER` indicando la posición (1-based) del error.
    """
    mapa_clases = dict(clases) if clases else {}
    tokens = tokenizar_expresion(texto, clases=mapa_clases, alfabeto_permitido=alfabeto_permitido)
    idx = 0
    total = len(tokens)

    def actual() -> TokenER | None:
        return tokens[idx] if idx < total else None

    def consumir() -> TokenER:
        nonlocal idx
        tok = tokens[idx]
        idx += 1
        return tok

    def inicio_de_factor(tok: TokenER | None) -> bool:
        return tok is not None and tok.tipo in ("SIMBOLO", "CLASE", "LAMBDA", "VACIO", "PAR_IZQ")

    def parse_expresion() -> NodoER:
        nodo = parse_termino()
        while (tok := actual()) is not None and tok.tipo == "UNION":
            tok_mas = consumir()
            sig = actual()
            if sig is None:
                raise ErrorSintaxisER(
                    "Operador de unión '+' al final de la expresión sin operando derecho.",
                    posicion=tok_mas.posicion,
                    expresion=texto,
                )
            if not inicio_de_factor(sig):
                raise ErrorSintaxisER(
                    f"Se esperaba un operando después del operador '+' pero se encontró '{sig.valor}'.",
                    posicion=sig.posicion,
                    expresion=texto,
                )
            der = parse_termino()
            nodo = NodoER("union", "+", (nodo, der))
        return nodo

    def parse_termino() -> NodoER:
        nodo = parse_factor()
        while (tok := actual()) is not None:
            if tok.tipo == "CONCAT":
                tok_punto = consumir()
                sig = actual()
                if sig is None:
                    raise ErrorSintaxisER(
                        f"Operador de concatenación '{tok_punto.valor}' al final sin operando derecho.",
                        posicion=tok_punto.posicion,
                        expresion=texto,
                    )
                if not inicio_de_factor(sig):
                    raise ErrorSintaxisER(
                        f"Se esperaba un operando después de '{tok_punto.valor}' pero se encontró '{sig.valor}'.",
                        posicion=sig.posicion,
                        expresion=texto,
                    )
                der = parse_factor()
                nodo = NodoER("concat", "", (nodo, der))
            elif inicio_de_factor(tok):
                der = parse_factor()
                nodo = NodoER("concat", "", (nodo, der))
            else:
                break
        return nodo

    def parse_factor() -> NodoER:
        nodo = parse_primario()
        while (tok := actual()) is not None and tok.tipo == "ESTRELLA":
            consumir()
            nodo = NodoER("estrella", "*", (nodo,))
        return nodo

    def parse_primario() -> NodoER:
        tok = actual()
        if tok is None:
            pos_fin = len(texto) if texto else 1
            raise ErrorSintaxisER(
                "Fin inesperado de la expresión regular; faltaba un operando.",
                posicion=pos_fin,
                expresion=texto,
            )

        if tok.tipo == "SIMBOLO":
            consumir()
            return NodoER("simbolo", tok.valor)

        if tok.tipo == "CLASE":
            consumir()
            simbolos_c = tuple(mapa_clases[tok.valor])
            return NodoER("clase", tok.valor, simbolos_clase=simbolos_c)

        if tok.tipo == "LAMBDA":
            consumir()
            return NodoER("lambda", "λ")

        if tok.tipo == "VACIO":
            consumir()
            return NodoER("vacio", "∅")

        if tok.tipo == "PAR_IZQ":
            tok_abierto = consumir()
            sig = actual()
            if sig is not None and sig.tipo == "PAR_DER":
                raise ErrorSintaxisER(
                    "Paréntesis vacíos '()' no representan una expresión válida.",
                    posicion=sig.posicion,
                    expresion=texto,
                )
            sub = parse_expresion()
            cierre = actual()
            if cierre is None:
                raise ErrorSintaxisER(
                    "Paréntesis '(' sin cerrar.",
                    posicion=tok_abierto.posicion,
                    expresion=texto,
                )
            if cierre.tipo != "PAR_DER":
                raise ErrorSintaxisER(
                    f"Se esperaba ')' para cerrar el paréntesis de la posición {tok_abierto.posicion}, "
                    f"pero se encontró '{cierre.valor}'.",
                    posicion=cierre.posicion,
                    expresion=texto,
                )
            consumir()
            return sub

        if tok.tipo == "UNION":
            raise ErrorSintaxisER(
                "Operador de unión '+' sin operando izquierdo.",
                posicion=tok.posicion,
                expresion=texto,
            )
        if tok.tipo == "ESTRELLA":
            raise ErrorSintaxisER(
                "Operador de cerradura '*' sin operando previo al cual aplicarse.",
                posicion=tok.posicion,
                expresion=texto,
            )
        if tok.tipo == "CONCAT":
            raise ErrorSintaxisER(
                f"Operador de concatenación '{tok.valor}' sin operando izquierdo.",
                posicion=tok.posicion,
                expresion=texto,
            )
        if tok.tipo == "PAR_DER":
            raise ErrorSintaxisER(
                "Paréntesis de cierre ')' sin paréntesis de apertura correspondiente.",
                posicion=tok.posicion,
                expresion=texto,
            )

        raise ErrorSintaxisER(
            f"Token inesperado '{tok.valor}'.",
            posicion=tok.posicion,
            expresion=texto,
        )

    arbol = parse_expresion()
    restante = actual()
    if restante is not None:
        if restante.tipo == "PAR_DER":
            raise ErrorSintaxisER(
                "Paréntesis de cierre ')' sin paréntesis de apertura correspondiente.",
                posicion=restante.posicion,
                expresion=texto,
            )
        raise ErrorSintaxisER(
            f"Símbolo u operador inesperado '{restante.valor}'.",
            posicion=restante.posicion,
            expresion=texto,
        )
    return arbol


# =============================================================================
# CONSTRUCCIÓN PASO A PASO DE LA PRIMERA PARTE DEL TEOREMA DE KLEENE (THOMPSON)
# =============================================================================

@dataclass
class PasoKleeneUno:
    """Representa un paso inductivo en la construcción de la Parte I del Teorema de Kleene."""

    numero_paso: int
    operacion: str
    subexpresion: str
    estado_inicial: str
    estado_final: str
    estados_nuevos: list[str]
    transiciones_nuevas: list[tuple[str, str, str]]  # (origen, simbolo_mostrado, destino)
    automata_parcial: AutomataFinito
    descripcion: str


@dataclass
class ResultadoKleeneUno:
    """Resultado de construir el AFN-λ a partir de una expresión regular (Teorema de Kleene, Parte I)."""

    expresion_original: str
    arbol: NodoER
    expresion_normalizada: str
    regex_python: str
    afn_lambda: AutomataFinito
    pasos: list[PasoKleeneUno]


@dataclass
class ResultadoERaAutomata:
    """Tubería completa del Ejercicio 2: ER -> AFN-λ (Kleene I) -> AFN -> AFD -> AFD mínimo."""

    kleene_uno: ResultadoKleeneUno
    eliminacion_lambda: ResultadoEliminacionLambda
    subconjuntos: ResultadoSubconjuntos
    minimizacion: ResultadoMinimizacion

    @property
    def afn_lambda(self) -> AutomataFinito:
        return self.kleene_uno.afn_lambda

    @property
    def afn_sin_lambda(self) -> AutomataFinito:
        return self.eliminacion_lambda.automata_sin_lambda

    @property
    def afn(self) -> AutomataFinito:
        return self.eliminacion_lambda.automata_sin_lambda

    @property
    def afd(self) -> AutomataFinito:
        return self.subconjuntos.afd

    @property
    def afd_minimo(self) -> AutomataFinito:
        return self.minimizacion.afd_minimo


@dataclass
class _PiezaThompson:
    """Estructura interna en forma estándar: un estado inicial (sin entradas) y un final (sin salidas)."""

    inicial: str
    final: str
    estados: list[str]
    alfabeto: list[str]
    transiciones: dict[tuple[str, str], list[str]]

    def a_automata(self, alfabeto_global: list[str] | None = None) -> AutomataFinito:
        alf = list(dict.fromkeys((alfabeto_global or []) + self.alfabeto))
        return AutomataFinito(
            alfabeto=alf,
            estados=list(self.estados),
            inicial=self.inicial,
            aceptacion=[self.final],
            transiciones={k: list(v) for k, v in self.transiciones.items()},
            tipo_declarado="AFND-lambda",
        )


def er_a_afn_lambda_detallado(
    expresion: str | NodoER,
    alfabeto_forzado: list[str] | None = None,
    clases: dict[str, list[str]] | None = None,
    expandir_clases_en_thompson: bool = False,
    alfabeto: list[str] | None = None,
) -> ResultadoKleeneUno:
    """Construye el AFN-λ equivalente mediante la Parte I del Teorema de Kleene mostrando cada pieza parcial.

    Forma estándar de cada pieza M_i (Hopcroft, Motwani & Ullman, 2007, §3.2.3; De Castro, 2004, §2.8):
    1. Tiene un único estado inicial `ini` sin transiciones entrantes.
    2. Tiene un único estado de aceptación `fin` sin transiciones salientes (`ini != fin`).
    3. Casos básicos:
       - `∅`: estados `q_i`, `q_f` sin transiciones (2 estados).
       - `λ`: estados `q_i`, `q_f` con `q_i --λ--> q_f` (2 estados).
       - `a ∈ Σ`: estados `q_i`, `q_f` con `q_i --a--> q_f` (2 estados).
    4. Pasos inductivos:
       - Unión `E1 + E2`: nuevos estados `q_i`, `q_f` y 4 transiciones λ (`q_i -> ini1, ini2`; `fin1, fin2 -> q_f`).
       - Concatenación `E1 E2`: une `fin1 --λ--> ini2`, conservando `ini1` como inicial y `fin2` como final.
       - Cerradura `E1*`: nuevos estados `q_i`, `q_f` y 4 transiciones λ (`q_i -> ini1, q_f`; `fin1 -> ini1, q_f`).
    """
    alfabeto_forzado = alfabeto_forzado or alfabeto
    if isinstance(expresion, str):
        arbol = analizar_expresion(expresion, clases=clases)
        exp_orig = expresion
    else:
        arbol = expresion
        exp_orig = arbol.a_texto_curso()

    alf_base = list(dict.fromkeys((alfabeto_forzado or []) + arbol.extraer_alfabeto()))
    contador_estados = 0
    pasos: list[PasoKleeneUno] = []

    def nuevo_estado() -> str:
        nonlocal contador_estados
        nombre = f"q{contador_estados}"
        contador_estados += 1
        return nombre

    def agregar_tr(
        mapa: dict[tuple[str, str], list[str]],
        u: str,
        sym: str,
        v: str,
    ) -> None:
        dest = mapa.setdefault((u, sym), [])
        if v not in dest:
            dest.append(v)

    def construir(nodo: NodoER) -> _PiezaThompson:
        # Si se pide expandir una clase de símbolos en uniones binarias puras de casos básicos
        if nodo.tipo == "clase" and expandir_clases_en_thompson and len(nodo.simbolos_clase) > 1:
            nodo_exp = NodoER("simbolo", nodo.simbolos_clase[0])
            for s_extra in nodo.simbolos_clase[1:]:
                nodo_exp = NodoER("union", "+", (nodo_exp, NodoER("simbolo", s_extra)))
            return construir(nodo_exp)

        if nodo.tipo == "vacio":
            qi, qf = nuevo_estado(), nuevo_estado()
            pieza = _PiezaThompson(
                inicial=qi,
                final=qf,
                estados=[qi, qf],
                alfabeto=[],
                transiciones={},
            )
            pasos.append(
                PasoKleeneUno(
                    numero_paso=len(pasos) + 1,
                    operacion="Caso básico (∅)",
                    subexpresion="∅",
                    estado_inicial=qi,
                    estado_final=qf,
                    estados_nuevos=[qi, qf],
                    transiciones_nuevas=[],
                    automata_parcial=pieza.a_automata(),
                    descripcion=f"Pieza básica para ∅: estados {qi} (inicial) y {qf} (final) sin transiciones.",
                )
            )
            return pieza

        if nodo.tipo == "lambda":
            qi, qf = nuevo_estado(), nuevo_estado()
            tr: dict[tuple[str, str], list[str]] = {(qi, ""): [qf]}
            pieza = _PiezaThompson(
                inicial=qi,
                final=qf,
                estados=[qi, qf],
                alfabeto=[],
                transiciones=tr,
            )
            pasos.append(
                PasoKleeneUno(
                    numero_paso=len(pasos) + 1,
                    operacion="Caso básico (λ)",
                    subexpresion="λ",
                    estado_inicial=qi,
                    estado_final=qf,
                    estados_nuevos=[qi, qf],
                    transiciones_nuevas=[(qi, "λ", qf)],
                    automata_parcial=pieza.a_automata(),
                    descripcion=f"Pieza básica para λ: transición espontánea {qi} --λ--> {qf}.",
                )
            )
            return pieza

        if nodo.tipo == "simbolo":
            a = nodo.valor
            qi, qf = nuevo_estado(), nuevo_estado()
            tr = {(qi, a): [qf]}
            pieza = _PiezaThompson(
                inicial=qi,
                final=qf,
                estados=[qi, qf],
                alfabeto=[a],
                transiciones=tr,
            )
            pasos.append(
                PasoKleeneUno(
                    numero_paso=len(pasos) + 1,
                    operacion=f"Caso básico ('{a}')",
                    subexpresion=nodo.a_texto_curso(),
                    estado_inicial=qi,
                    estado_final=qf,
                    estados_nuevos=[qi, qf],
                    transiciones_nuevas=[(qi, a, qf)],
                    automata_parcial=pieza.a_automata(),
                    descripcion=f"Pieza básica para el símbolo '{a}': transición {qi} --{a}--> {qf}.",
                )
            )
            return pieza

        if nodo.tipo == "clase":
            qi, qf = nuevo_estado(), nuevo_estado()
            tr = {}
            tr_nuevas: list[tuple[str, str, str]] = []
            for s in nodo.simbolos_clase:
                agregar_tr(tr, qi, s, qf)
                tr_nuevas.append((qi, s, qf))
            pieza = _PiezaThompson(
                inicial=qi,
                final=qf,
                estados=[qi, qf],
                alfabeto=list(nodo.simbolos_clase),
                transiciones=tr,
            )
            rango_txt = f"{nodo.simbolos_clase[0]}..{nodo.simbolos_clase[-1]}" if len(nodo.simbolos_clase) > 3 else "+".join(nodo.simbolos_clase)
            pasos.append(
                PasoKleeneUno(
                    numero_paso=len(pasos) + 1,
                    operacion=f"Clase de símbolos {nodo.valor}",
                    subexpresion=nodo.valor,
                    estado_inicial=qi,
                    estado_final=qf,
                    estados_nuevos=[qi, qf],
                    transiciones_nuevas=[(qi, f"{nodo.valor}=({rango_txt})", qf)],
                    automata_parcial=pieza.a_automata(),
                    descripcion=(
                        f"Pieza abreviada para la clase {nodo.valor} ({len(nodo.simbolos_clase)} símbolos: {rango_txt}): "
                        f"estados {qi} y {qf} unidos por cada símbolo de la clase."
                    ),
                )
            )
            return pieza

        if nodo.tipo == "concat":
            p1 = construir(nodo.hijos[0])
            p2 = construir(nodo.hijos[1])
            tr_comb: dict[tuple[str, str], list[str]] = {
                k: list(v) for k, v in p1.transiciones.items()
            }
            for k, v in p2.transiciones.items():
                for dest in v:
                    agregar_tr(tr_comb, k[0], k[1], dest)
            agregar_tr(tr_comb, p1.final, "", p2.inicial)

            pieza = _PiezaThompson(
                inicial=p1.inicial,
                final=p2.final,
                estados=p1.estados + p2.estados,
                alfabeto=list(dict.fromkeys(p1.alfabeto + p2.alfabeto)),
                transiciones=tr_comb,
            )
            sub_txt = nodo.a_texto_curso()
            pasos.append(
                PasoKleeneUno(
                    numero_paso=len(pasos) + 1,
                    operacion="Concatenación",
                    subexpresion=sub_txt,
                    estado_inicial=pieza.inicial,
                    estado_final=pieza.final,
                    estados_nuevos=[],
                    transiciones_nuevas=[(p1.final, "λ", p2.inicial)],
                    automata_parcial=pieza.a_automata(),
                    descripcion=(
                        f"Concatenación '{sub_txt}': se une la salida {p1.final} de '{nodo.hijos[0].a_texto_curso()}' "
                        f"con la entrada {p2.inicial} de '{nodo.hijos[1].a_texto_curso()}' mediante λ "
                        f"(inicial={pieza.inicial}, final={pieza.final}, |Q|={len(pieza.estados)})."
                    ),
                )
            )
            return pieza

        if nodo.tipo == "union":
            p1 = construir(nodo.hijos[0])
            p2 = construir(nodo.hijos[1])
            qi, qf = nuevo_estado(), nuevo_estado()
            tr_comb = {k: list(v) for k, v in p1.transiciones.items()}
            for k, v in p2.transiciones.items():
                for dest in v:
                    agregar_tr(tr_comb, k[0], k[1], dest)

            agregar_tr(tr_comb, qi, "", p1.inicial)
            agregar_tr(tr_comb, qi, "", p2.inicial)
            agregar_tr(tr_comb, p1.final, "", qf)
            agregar_tr(tr_comb, p2.final, "", qf)

            pieza = _PiezaThompson(
                inicial=qi,
                final=qf,
                estados=p1.estados + p2.estados + [qi, qf],
                alfabeto=list(dict.fromkeys(p1.alfabeto + p2.alfabeto)),
                transiciones=tr_comb,
            )
            sub_txt = nodo.a_texto_curso()
            pasos.append(
                PasoKleeneUno(
                    numero_paso=len(pasos) + 1,
                    operacion="Unión (+)",
                    subexpresion=sub_txt,
                    estado_inicial=qi,
                    estado_final=qf,
                    estados_nuevos=[qi, qf],
                    transiciones_nuevas=[
                        (qi, "λ", p1.inicial),
                        (qi, "λ", p2.inicial),
                        (p1.final, "λ", qf),
                        (p2.final, "λ", qf),
                    ],
                    automata_parcial=pieza.a_automata(),
                    descripcion=(
                        f"Unión '{sub_txt}': nuevos estados {qi} (inicial) y {qf} (final) con 4 transiciones λ "
                        f"({qi} -> {p1.inicial}, {p2.inicial}; {p1.final}, {p2.final} -> {qf}; |Q|={len(pieza.estados)})."
                    ),
                )
            )
            return pieza

        if nodo.tipo == "estrella":
            p1 = construir(nodo.hijos[0])
            qi, qf = nuevo_estado(), nuevo_estado()
            tr_comb = {k: list(v) for k, v in p1.transiciones.items()}

            agregar_tr(tr_comb, qi, "", p1.inicial)
            agregar_tr(tr_comb, qi, "", qf)
            agregar_tr(tr_comb, p1.final, "", p1.inicial)
            agregar_tr(tr_comb, p1.final, "", qf)

            pieza = _PiezaThompson(
                inicial=qi,
                final=qf,
                estados=p1.estados + [qi, qf],
                alfabeto=list(p1.alfabeto),
                transiciones=tr_comb,
            )
            sub_txt = nodo.a_texto_curso()
            pasos.append(
                PasoKleeneUno(
                    numero_paso=len(pasos) + 1,
                    operacion="Cerradura de Kleene (*)",
                    subexpresion=sub_txt,
                    estado_inicial=qi,
                    estado_final=qf,
                    estados_nuevos=[qi, qf],
                    transiciones_nuevas=[
                        (qi, "λ", p1.inicial),
                        (qi, "λ", qf),
                        (p1.final, "λ", p1.inicial),
                        (p1.final, "λ", qf),
                    ],
                    automata_parcial=pieza.a_automata(),
                    descripcion=(
                        f"Cerradura de Kleene '{sub_txt}': nuevos estados {qi} (inicial) y {qf} (final) con "
                        f"entrada {qi}->({p1.inicial},{qf}) y retorno/salida {p1.final}->({p1.inicial},{qf}) (|Q|={len(pieza.estados)})."
                    ),
                )
            )
            return pieza

        raise ValueError(f"Tipo de nodo no soportado: {nodo.tipo}")

    pieza_final = construir(arbol)
    afn_lambda_final = pieza_final.a_automata(alfabeto_global=alf_base)

    return ResultadoKleeneUno(
        expresion_original=exp_orig,
        arbol=arbol,
        expresion_normalizada=arbol.a_texto_curso(),
        regex_python=arbol.a_regex_python(),
        afn_lambda=afn_lambda_final,
        pasos=pasos,
    )


def er_a_automata_completo(
    expresion: str | NodoER,
    alfabeto_forzado: list[str] | None = None,
    clases: dict[str, list[str]] | None = None,
    incluir_pozo: bool = False,
    alfabeto: list[str] | None = None,
) -> ResultadoERaAutomata:
    """Ejecuta el flujo completo del Ejercicio 2:
    1. Analiza la expresión regular y construye el AFN-λ paso a paso (Kleene Parte I).
    2. Elimina las transiciones λ para obtener el AFN equivalente (Práctica 3, 2.2).
    3. Aplica la construcción de subconjuntos alcanzables para obtener el AFD (Práctica 3, 2.3).
    4. Minimiza el AFD para obtener el AFD mínimo (Práctica 3, 2.4).
    """
    alfabeto_forzado = alfabeto_forzado or alfabeto
    res_kleene = er_a_afn_lambda_detallado(
        expresion,
        alfabeto_forzado=alfabeto_forzado,
        clases=clases,
    )
    res_sin_lambda = res_kleene.afn_lambda.eliminar_transiciones_lambda_detallado()
    res_subconjuntos = res_sin_lambda.automata_sin_lambda.construccion_subconjuntos_detallada(
        incluir_pozo=incluir_pozo
    )
    res_minimo = res_subconjuntos.afd.minimizar_afd_detallado()
    return ResultadoERaAutomata(
        kleene_uno=res_kleene,
        eliminacion_lambda=res_sin_lambda,
        subconjuntos=res_subconjuntos,
        minimizacion=res_minimo,
    )


# =============================================================================
# PRÁCTICA 4 — EJERCICIO 3: ELIMINACIÓN DE ESTADOS PASO A PASO (GNFA) Y COMPARACIÓN
# =============================================================================

@dataclass
class PasoGNFA:
    """Instantánea del Autómata Finito Generalizado (GNFA) tras eliminar un estado (Ejercicio 3)."""

    numero_paso: int
    estado_eliminado: str | None
    expresion_bucle: str
    estados_vivos: list[str]
    aristas: dict[tuple[str, str], str]   # (origen, destino) -> expresión regular (sólo != ∅)
    actualizaciones: list[str]
    resumen_paso: str
    tabla_markdown: str


@dataclass
class ResultadoEliminacionEstados:
    """Resultado detallado de convertir un AFD a expresión regular por eliminación de estados."""

    afd_origen: AutomataFinito
    verificacion_afd: ResultadoVerificacionAFD
    orden_eliminacion: list[str]
    pasos_gnfa: list[PasoGNFA]
    expresion_arbol: ER
    expresion_texto: str


@dataclass
class ResultadoComparacionExpresiones:
    """Resultado de comprobar que dos expresiones regulares son equivalentes vía sus AFD mínimos (Ejercicio 3)."""

    expresion_1: str
    expresion_2: str
    tuberia_1: ResultadoERaAutomata
    tuberia_2: ResultadoERaAutomata
    equivalencia_afd: ResultadoEquivalenciaAFD

    @property
    def equivalentes(self) -> bool:
        return self.equivalencia_afd.equivalentes


def _renderizar_tabla_gnfa(
    vivos: list[str],
    R: dict[tuple[str, str], ER],
    ini: str,
    fin: str,
) -> tuple[dict[tuple[str, str], str], str]:
    """Construye el diccionario de aristas activas y la tabla Markdown del GNFA en el paso actual."""
    aristas_activas: dict[tuple[str, str], str] = {}
    for u in vivos:
        for v in vivos:
            val = R.get((u, v))
            if val is not None:
                aristas_activas[(u, v)] = a_texto(val)

    origenes = [u for u in vivos if u != fin]
    destinos = [v for v in vivos if v != ini]

    enc = "| Origen \\ Destino | " + " | ".join(f"**`{v}`**" for v in destinos) + " |\n"
    sep = "| :--- | " + " | ".join(":---:" for _ in destinos) + " |\n"
    filas: list[str] = []
    for u in origenes:
        celdas: list[str] = []
        for v in destinos:
            txt = aristas_activas.get((u, v), "∅")
            celdas.append(f"`{txt}`" if txt != "∅" else "∅")
        filas.append(f"| **`{u}`** | " + " | ".join(celdas) + " |")

    lista_aristas = [
        f"`{u} --({etq})--> {v}`"
        for (u, v), etq in aristas_activas.items()
    ]
    md = (
        enc
        + sep
        + "\n".join(filas)
        + "\n\n**Aristas activas en el GNFA:** "
        + (", ".join(lista_aristas) if lista_aristas else "Ninguna (`∅`)")
    )
    return aristas_activas, md


def eliminacion_de_estados_detallada(
    afd: AutomataFinito,
    orden: list[str] | None = None,
    exigir_determinista: bool = True,
) -> ResultadoEliminacionEstados:
    """Convierte un AFD a expresión regular por eliminación de estados registrando el GNFA en cada paso.

    Si `exigir_determinista=True` y el autómata no es determinista, lanza `ValueError` detallando
    qué estado y qué símbolo lo impiden.
    """
    verif = afd.verificar_determinismo()
    if exigir_determinista and not verif.es_determinista:
        raise ValueError(verif.mensaje)

    ini, fin = "⊢ini", "fin⊣"
    estados = list(afd.estados)
    orden_elim = list(orden) if orden else list(estados)

    R: dict[tuple[str, str], ER] = {}
    for p in estados:
        for q in estados:
            R[(p, q)] = _etiqueta(afd, p, q)
    if afd.inicial:
        R[(ini, afd.inicial)] = LAMBDA
    for f in afd.aceptacion:
        R[(f, fin)] = LAMBDA

    vivos = [ini] + estados + [fin]
    pasos_gnfa: list[PasoGNFA] = []

    aristas_0, md_0 = _renderizar_tabla_gnfa(vivos, R, ini, fin)
    resumen_0 = (
        f"GNFA inicial (Paso 0): se agrega el estado inicial '{ini}' con transición λ hacia '{afd.inicial}' "
        f"y el estado final único '{fin}' con transiciones λ desde F = {{{', '.join(afd.aceptacion)}}}."
    )
    pasos_gnfa.append(
        PasoGNFA(
            numero_paso=0,
            estado_eliminado=None,
            expresion_bucle="λ",
            estados_vivos=list(vivos),
            aristas=aristas_0,
            actualizaciones=[resumen_0],
            resumen_paso=resumen_0,
            tabla_markdown=md_0,
        )
    )

    for idx_paso, q in enumerate(orden_elim, start=1):
        bucle = estrella(R.get((q, q)))
        bucle_txt = a_texto(bucle)
        entradas = [p for p in vivos if p != q and R.get((p, q)) is not None]
        salidas = [r for r in vivos if r != q and R.get((q, r)) is not None]
        actualizaciones: list[str] = []

        for p in entradas:
            for r in salidas:
                anterior = R.get((p, r))
                ant_txt = a_texto(anterior)
                pq_txt = a_texto(R[(p, q)])
                qr_txt = a_texto(R[(q, r)])
                nuevo_val = union(anterior, concat(R[(p, q)], bucle, R[(q, r)]))
                R[(p, r)] = nuevo_val
                actualizaciones.append(
                    f"R'({p}, {r}) = R({p}, {r}) + R({p}, {q})·R({q}, {q})*·R({q}, {r}) "
                    f"= {ant_txt} + ({pq_txt})·({bucle_txt})·({qr_txt}) = {a_texto(nuevo_val)}"
                )

        vivos.remove(q)
        for k in [k for k in list(R.keys()) if q in k]:
            del R[k]

        aristas_k, md_k = _renderizar_tabla_gnfa(vivos, R, ini, fin)
        resumen_k = (
            f"Paso {idx_paso} — Se elimina el estado '{q}' (bucle R({q},{q})* = {bucle_txt}): "
            + ("; ".join(actualizaciones) if actualizaciones else "sin pares (p, r) conectados a través de este estado.")
        )
        pasos_gnfa.append(
            PasoGNFA(
                numero_paso=idx_paso,
                estado_eliminado=q,
                expresion_bucle=bucle_txt,
                estados_vivos=list(vivos),
                aristas=aristas_k,
                actualizaciones=actualizaciones,
                resumen_paso=resumen_k,
                tabla_markdown=md_k,
            )
        )

    resultado_er = R.get((ini, fin))
    return ResultadoEliminacionEstados(
        afd_origen=afd,
        verificacion_afd=verif,
        orden_eliminacion=orden_elim,
        pasos_gnfa=pasos_gnfa,
        expresion_arbol=resultado_er,
        expresion_texto=a_texto(resultado_er),
    )


def comparar_expresiones_por_afd_minimo(
    expresion_1: str,
    expresion_2: str,
    alfabeto_forzado: list[str] | None = None,
    clases: dict[str, list[str]] | None = None,
    alfabeto: list[str] | None = None,
) -> ResultadoComparacionExpresiones:
    """Comprueba si dos expresiones regulares son equivalentes convirtiendo ambas en AFD mínimos
    con el Ejercicio 2 y comparándolos con la prueba de equivalencia de la Práctica 3 (Ejercicio 3).
    """
    alfabeto_forzado = alfabeto_forzado or alfabeto
    n1 = analizar_expresion(expresion_1, clases=clases)
    n2 = analizar_expresion(expresion_2, clases=clases)
    alf_comun = list(
        dict.fromkeys(
            (alfabeto_forzado or []) + n1.extraer_alfabeto() + n2.extraer_alfabeto()
        )
    )
    tub1 = er_a_automata_completo(n1, alfabeto_forzado=alf_comun, clases=clases)
    tub2 = er_a_automata_completo(n2, alfabeto_forzado=alf_comun, clases=clases)
    eq = tub1.afd_minimo.son_afd_equivalentes(tub2.afd_minimo)
    return ResultadoComparacionExpresiones(
        expresion_1=expresion_1,
        expresion_2=expresion_2,
        tuberia_1=tub1,
        tuberia_2=tub2,
        equivalencia_afd=eq,
    )


# =============================================================================
# MÉTODOS DE LA PRÁCTICA 3 CONSERVADOS ÍNTEGRAMENTE (ELIMINACIÓN, R_ij^(k), ARDEN)
# =============================================================================

@dataclass
class ResultadoMetodo:
    """Expresión obtenida por un método y su bitácora de pasos."""

    metodo: str
    expresion: ER
    pasos: list[str] = field(default_factory=list)

    @property
    def texto(self) -> str:
        return a_texto(self.expresion)


def eliminacion_de_estados(afd: AutomataFinito, orden: list[str] | None = None) -> ResultadoMetodo:
    """Convierte el AFD en un GNFA con estados nuevos `ini` y `fin` y elimina los estados originales.

    Regla al eliminar q: R'(p, r) = R(p, r) + R(p, q) R(q, q)* R(q, r).
    """
    ini, fin = "⊢ini", "fin⊣"
    estados = list(afd.estados)
    orden = list(orden) if orden else list(estados)
    R: dict[tuple[str, str], ER] = {}
    for p in estados:
        for q in estados:
            R[(p, q)] = _etiqueta(afd, p, q)
    R[(ini, afd.inicial)] = LAMBDA
    for f in afd.aceptacion:
        R[(f, fin)] = LAMBDA

    pasos = [
        f"GNFA inicial: nuevo inicial {ini} --λ--> {afd.inicial}; "
        + ", ".join(f"{f} --λ--> {fin}" for f in afd.aceptacion)
    ]
    vivos = [ini] + estados + [fin]
    for q in orden:
        bucle = estrella(R.get((q, q)))
        entradas = [p for p in vivos if p != q and R.get((p, q)) is not None]
        salidas = [r for r in vivos if r != q and R.get((q, r)) is not None]
        nuevas: list[str] = []
        for p in entradas:
            for r in salidas:
                anterior = R.get((p, r))
                R[(p, r)] = union(anterior, concat(R[(p, q)], bucle, R[(q, r)]))
                nuevas.append(f"R({p},{r}) = {a_texto(R[(p, r)])}")
        vivos.remove(q)
        for k in [k for k in R if q in k]:
            del R[k]
        pasos.append(f"Se elimina {q} (bucle R({q},{q})* = {a_texto(bucle)}): " + ("; ".join(nuevas) or "sin aristas nuevas"))
    resultado = R.get((ini, fin))
    pasos.append(f"Expresión final R({ini},{fin}) = {a_texto(resultado)}")
    return ResultadoMetodo("Eliminación de estados", resultado, pasos)


def construccion_rijk(afd: AutomataFinito) -> ResultadoMetodo:
    """R_ij^(k) = R_ij^(k-1) + R_ik^(k-1) (R_kk^(k-1))* R_kj^(k-1), numerando los estados 1..n."""
    estados = list(afd.estados)
    n = len(estados)
    R: dict[tuple[int, int], ER] = {}
    for i, p in enumerate(estados, start=1):
        for j, q in enumerate(estados, start=1):
            e = _etiqueta(afd, p, q)
            R[(i, j)] = union(LAMBDA, e) if i == j else e
    numeracion = ", ".join(f"{i}={q}" for i, q in enumerate(estados, start=1))
    pasos = [f"Numeración: {numeracion}", "k=0: " + "; ".join(f"R{i}{j}={a_texto(R[(i, j)])}" for (i, j) in sorted(R))]
    for k in range(1, n + 1):
        kk = estrella(R[(k, k)])
        nuevo = {
            (i, j): union(R[(i, j)], concat(R[(i, k)], kk, R[(k, j)]))
            for i in range(1, n + 1)
            for j in range(1, n + 1)
        }
        R = nuevo
        pasos.append(f"k={k}: " + "; ".join(f"R{i}{j}={a_texto(R[(i, j)])}" for (i, j) in sorted(R)))
    i0 = estados.index(afd.inicial) + 1
    finales = [estados.index(f) + 1 for f in afd.aceptacion]
    resultado = union(*[R[(i0, j)] for j in finales])
    pasos.append(
        "L(M) = " + " + ".join(f"R{i0}{j}^({n})" for j in finales) + f" = {a_texto(resultado)}"
    )
    return ResultadoMetodo("Construcción R_ij^(k)", resultado, pasos)


def ecuaciones_arden(afd: AutomataFinito, orden: list[str] | None = None) -> ResultadoMetodo:
    """Resuelve X_q = Σ_a a·X_δ(q,a) + [q ∈ F]λ eliminando variables con el Lema de Arden.

    X_q denota el lenguaje aceptado desde q; la solución pedida es X_{q0}.
    """
    estados = list(afd.estados)
    coef: dict[str, dict[str, ER]] = {q: {r: _etiqueta(afd, q, r) for r in estados} for q in estados}
    ind: dict[str, ER] = {q: (LAMBDA if q in afd.aceptacion else VACIO) for q in estados}

    def ecuacion(q: str) -> str:
        terminos = [
            (f"({a_texto(c)})" if isinstance(c, tuple) and c[0] == "u" else a_texto(c)) + f"X{r}"
            for r, c in coef[q].items()
            if c is not None
        ]
        if ind[q] is not None:
            terminos.append(a_texto(ind[q]))
        return f"X{q} = " + (" + ".join(terminos) if terminos else "∅")

    pasos = ["Sistema inicial: " + " ; ".join(ecuacion(q) for q in estados)]
    orden = list(orden) if orden else [q for q in reversed(estados) if q != afd.inicial] + [afd.inicial]
    pendientes = list(estados)
    for q in orden:
        a_qq = coef[q].get(q)
        if a_qq is not None:
            bucle = estrella(a_qq)
            coef[q] = {r: concat(bucle, c) for r, c in coef[q].items() if r != q}
            coef[q][q] = VACIO
            ind[q] = concat(bucle, ind[q])
            pasos.append(f"Arden en X{q} (A = {a_texto(a_qq)}): {ecuacion(q)}")
        pendientes.remove(q)
        for p in pendientes:
            c_pq = coef[p].get(q)
            if c_pq is None:
                continue
            for r, c in coef[q].items():
                if c is not None:
                    coef[p][r] = union(coef[p].get(r), concat(c_pq, c))
            ind[p] = union(ind[p], concat(c_pq, ind[q]))
            coef[p][q] = VACIO
        if pendientes:
            pasos.append(f"Sustituyendo X{q}: " + " ; ".join(ecuacion(p) for p in pendientes))
    resultado = ind[afd.inicial]
    pasos.append(f"Solución X{afd.inicial} = {a_texto(resultado)}")
    return ResultadoMetodo("Ecuaciones + Lema de Arden", resultado, pasos)


def tres_metodos(afd: AutomataFinito) -> list[ResultadoMetodo]:
    """Aplica los tres métodos del Ejercicio 1.2 al mismo AFD."""
    return [eliminacion_de_estados(afd), construccion_rijk(afd), ecuaciones_arden(afd)]
