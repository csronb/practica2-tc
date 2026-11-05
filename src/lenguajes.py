"""Módulo de funciones puras para operaciones básicas sobre cadenas y lenguajes.

Este módulo carece de dependencias de interfaz gráfica (Flet) para permitir
su verificación automatizada mediante pytest en múltiples versiones del
intérprete de Python (3.11, 3.12 y 3.13).

Convención adoptada sobre la cadena vacía (λ):
    Por definición formal, para cualquier cadena w ∈ Σ*, la cadena vacía λ es
    simultáneamente prefijo, sufijo y subcadena de w, dado que w = λ·w = w·λ = λ·w·λ.
    En Python, la cadena vacía se representa mediante `""` (y se formatea como `"λ"`
    en la capa de presentación cuando resulta pertinente).
"""

from __future__ import annotations

from itertools import product

LIMITE_CADENAS: int = 200_000


def prefijos(cadena: str) -> list[str]:
    """Calcula todos los prefijos de una cadena dada, incluyendo la cadena vacía.

    Una cadena u es prefijo de w si existe v ∈ Σ* tal que w = uv.
    Para una cadena de longitud n, existen exactamente n + 1 prefijos (siendo
    el primero la cadena vacía "" de longitud 0 y el último la propia cadena w).

    Args:
        cadena: Cadena de entrada w.

    Returns:
        Lista ordenada por longitud ascendente con todos los prefijos de `cadena`,
        comenzando por `""`.
    """
    return [cadena[:i] for i in range(len(cadena) + 1)]


def sufijos(cadena: str) -> list[str]:
    """Calcula todos los sufijos de una cadena dada, incluyendo la cadena vacía.

    Una cadena v es sufijo de w si existe u ∈ Σ* tal que w = uv.
    Para una cadena de longitud n, existen exactamente n + 1 sufijos.

    Args:
        cadena: Cadena de entrada w.

    Returns:
        Lista ordenada por longitud ascendente con todos los sufijos de `cadena`,
        comenzando por `""` y terminando con `cadena`.
    """
    n = len(cadena)
    return [cadena[n - i :] for i in range(n + 1)]


def subcadenas(cadena: str) -> list[str]:
    """Calcula todas las subcadenas distintas de una cadena dada, incluyendo "".

    Una cadena y es subcadena de w si existen x, z ∈ Σ* tales que w = xyz.
    El número máximo de subcadenas distintas para una cadena de longitud n es
    n(n + 1)/2 + 1 (cota alcanzada cuando todos los símbolos de la cadena son
    distintos).

    Args:
        cadena: Cadena de entrada w.

    Returns:
        Lista de subcadenas únicas (sin duplicados), preservando el orden por
        longitud ascendente y posición de aparición, comenzando por `""`.
    """
    vistas: set[str] = {""}
    resultado: list[str] = [""]
    n = len(cadena)
    for longitud in range(1, n + 1):
        for inicio in range(n - longitud + 1):
            sub = cadena[inicio : inicio + longitud]
            if sub not in vistas:
                vistas.add(sub)
                resultado.append(sub)
    return resultado


def contar_cadenas_cerradura(
    cardinalidad_alfabeto: int,
    longitud_max: int,
    incluir_vacia: bool = True,
) -> int:
    """Calcula la cantidad total de cadenas en Σ* o Σ+ hasta `longitud_max`.

    Dado que |Σ^k| = |Σ|^k, el total de cadenas de longitud 0 (o 1) hasta n es:
        - Para |Σ| = 0: 1 si se incluye λ, 0 en caso contrario.
        - Para |Σ| = 1: n + 1 (para Σ*) o n (para Σ+).
        - Para |Σ| > 1: suma geométrica (|Σ|^(n+1) - 1) / (|Σ| - 1) para Σ*,
          y ese valor menos 1 para Σ+.

    Args:
        cardinalidad_alfabeto: Número de símbolos distintos |Σ|.
        longitud_max: Longitud máxima n >= 0.
        incluir_vacia: True para Σ* (incluye k=0), False para Σ+ (desde k=1).

    Returns:
        Número entero de cadenas que se generarían.
    """
    if longitud_max < 0:
        raise ValueError("La longitud máxima no puede ser negativa.")
    if cardinalidad_alfabeto < 0:
        raise ValueError("La cardinalidad del alfabeto no puede ser negativa.")

    k_inicio = 0 if incluir_vacia else 1
    if longitud_max < k_inicio:
        return 0

    if cardinalidad_alfabeto == 0:
        return 1 if incluir_vacia else 0
    if cardinalidad_alfabeto == 1:
        return (longitud_max + 1) if incluir_vacia else longitud_max

    total_con_vacia = (cardinalidad_alfabeto ** (longitud_max + 1) - 1) // (
        cardinalidad_alfabeto - 1
    )
    return total_con_vacia if incluir_vacia else (total_con_vacia - 1)


def normalizar_alfabeto(alfabeto: list[str] | set[str] | tuple[str, ...]) -> list[str]:
    """Limpia, valida y elimina duplicados de un alfabeto preservando el orden."""
    simbolos: list[str] = []
    vistos: set[str] = set()
    for s in alfabeto:
        limpio = s.strip()
        if limpio and limpio not in vistos:
            vistos.add(limpio)
            simbolos.append(limpio)
    return simbolos


def cerradura_kleene(
    alfabeto: list[str] | set[str] | tuple[str, ...],
    longitud_max: int,
    limite: int = LIMITE_CADENAS,
) -> list[str]:
    """Calcula Σ* truncado hasta `longitud_max` (∪_{i=0}^{n} Σ^i).

    Rechaza con `ValueError` si la combinación de |Σ| y `longitud_max` generaría
    más de `limite` cadenas (por defecto 200,000), previniendo el agotamiento
    de memoria por la explosión combinatoria |Σ|^n.

    Args:
        alfabeto: Colección de símbolos del alfabeto Σ.
        longitud_max: Longitud máxima n >= 0 de las cadenas a generar.
        limite: Cota máxima permitida de cadenas (por defecto 200,000).

    Returns:
        Lista de cadenas en Σ* de longitud <= `longitud_max`, empezando por `""`.

    Raises:
        ValueError: Si `longitud_max < 0`, si el alfabeto está vacío o si el
            número total de cadenas a generar excede `limite`.
    """
    if longitud_max < 0:
        raise ValueError("La longitud máxima debe ser un entero mayor o igual a 0.")

    simbolos = normalizar_alfabeto(alfabeto)
    if not simbolos and longitud_max > 0:
        raise ValueError("El alfabeto Σ no puede estar vacío.")

    total = contar_cadenas_cerradura(len(simbolos), longitud_max, incluir_vacia=True)
    if total > limite:
        raise ValueError(
            f"Límite excedido: la combinación |Σ|={len(simbolos)} y n={longitud_max} "
            f"generaría {total:,} cadenas en Σ*, superando el máximo permitido de "
            f"{limite:,} cadenas (crecimiento exponencial |Σ|^n)."
        )

    resultado: list[str] = [""]
    for k in range(1, longitud_max + 1):
        for tupla in product(simbolos, repeat=k):
            resultado.append("".join(tupla))
    return resultado


def cerradura_positiva(
    alfabeto: list[str] | set[str] | tuple[str, ...],
    longitud_max: int,
    limite: int = LIMITE_CADENAS,
) -> list[str]:
    """Calcula Σ+ truncado hasta `longitud_max` (∪_{i=1}^{n} Σ^i).

    A diferencia de Σ*, la cerradura positiva Σ+ no incluye Σ^0 = {λ}, por lo
    que para `longitud_max == 0` devuelve la lista vacía `[]`.

    Args:
        alfabeto: Colección de símbolos del alfabeto Σ.
        longitud_max: Longitud máxima n >= 0 de las cadenas a generar.
        limite: Cota máxima permitida de cadenas (por defecto 200,000).

    Returns:
        Lista de cadenas en Σ+ de longitud 1 <= |w| <= `longitud_max`.

    Raises:
        ValueError: Si `longitud_max < 0`, si el alfabeto está vacío (cuando n > 0)
            o si el número total de cadenas a generar excede `limite`.
    """
    if longitud_max < 0:
        raise ValueError("La longitud máxima debe ser un entero mayor o igual a 0.")

    simbolos = normalizar_alfabeto(alfabeto)
    if longitud_max == 0:
        return []
    if not simbolos:
        raise ValueError("El alfabeto Σ no puede estar vacío.")

    total = contar_cadenas_cerradura(len(simbolos), longitud_max, incluir_vacia=False)
    if total > limite:
        raise ValueError(
            f"Límite excedido: la combinación |Σ|={len(simbolos)} y n={longitud_max} "
            f"generaría {total:,} cadenas en Σ+, superando el máximo permitido de "
            f"{limite:,} cadenas (crecimiento exponencial |Σ|^n)."
        )

    resultado: list[str] = []
    for k in range(1, longitud_max + 1):
        for tupla in product(simbolos, repeat=k):
            resultado.append("".join(tupla))
    return resultado


def formatear_cadena(w: str) -> str:
    """Devuelve 'λ' si la cadena es vacía, o la propia cadena en caso contrario."""
    return "λ" if w == "" else w
