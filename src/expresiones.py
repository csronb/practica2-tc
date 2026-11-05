"""Módulo `expresiones.py`: Conversión de AFD a Expresión Regular en Python puro (Práctica 3, Ejercicio 1).

Implementa los tres métodos del Ejercicio 1.2, registrando cada paso para poder compararlos
con el desarrollo a mano y con la salida de JFLAP (*Convert FA to RE*):

1. Eliminación de estados (autómata finito generalizado, GNFA).
2. Construcción de las expresiones R_ij^(k) (algoritmo de McNaughton-Yamada / Kleene).
3. Sistema de ecuaciones lineales por la derecha resuelto con el Lema de Arden
   (X = A X + B, con λ ∉ L(A)  ⇒  X = A* B).

Las expresiones se representan como árboles sintácticos sencillos y se aplican sólo
simplificaciones algebraicas seguras (identidades de ∅ y λ, idempotencia de la unión y
propiedades de la estrella), de modo que el resultado es siempre equivalente al AFD.
También se ofrece la traducción a una expresión regular de Python (`re`) para verificar
automáticamente la equivalencia sobre todas las cadenas de Σ^{≤k}.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Union

from automata import AutomataFinito

# -----------------------------------------------------------------------------
# Árbol sintáctico de expresiones regulares
#   VACIO (∅) -> None ; LAMBDA (λ) -> "" ; símbolo -> ("s", a)
#   unión -> ("u", (e1, e2, ...)) ; concatenación -> ("c", (e1, e2, ...)) ; estrella -> ("*", e)
# -----------------------------------------------------------------------------
ER = Union[None, str, tuple]
VACIO: ER = None
LAMBDA: ER = ""


def simbolo(a: str) -> ER:
    return ("s", a)


def a_texto(e: ER) -> str:
    """Convierte el árbol a la notación del curso: '+' para unión, yuxtaposición y '*'."""
    if e is None:
        return "∅"
    if e == "":
        return "λ"
    tipo = e[0]
    if tipo == "s":
        return e[1]
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
    """Traduce el árbol a sintaxis de `re` de Python."""
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
    """Número de símbolos de Σ que aparecen en la expresión (medida de tamaño usada en la comparación)."""
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
# 1. ELIMINACIÓN DE ESTADOS
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


# =============================================================================
# 2. CONSTRUCCIÓN R_ij^(k)
# =============================================================================

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


# =============================================================================
# 3. SISTEMA DE ECUACIONES Y LEMA DE ARDEN
# =============================================================================

def ecuaciones_arden(afd: AutomataFinito, orden: list[str] | None = None) -> ResultadoMetodo:
    """Resuelve X_q = Σ_a a·X_δ(q,a) + [q ∈ F]λ eliminando variables con el Lema de Arden.

    X_q denota el lenguaje aceptado desde q; la solución pedida es X_{q0}.
    """
    estados = list(afd.estados)
    # coef[q][r] = expresión que multiplica a X_r en la ecuación de X_q; ind[q] = término independiente
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
    # Sustitución hacia atrás no es necesaria: X_{q0} queda sin variables al final.
    resultado = ind[afd.inicial]
    pasos.append(f"Solución X{afd.inicial} = {a_texto(resultado)}")
    return ResultadoMetodo("Ecuaciones + Lema de Arden", resultado, pasos)


def tres_metodos(afd: AutomataFinito) -> list[ResultadoMetodo]:
    """Aplica los tres métodos del Ejercicio 1.2 al mismo AFD."""
    return [eliminacion_de_estados(afd), construccion_rijk(afd), ecuaciones_arden(afd)]
