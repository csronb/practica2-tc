#!/usr/bin/env python3
"""afd.py — un AFD guardado por JFLAP, leído y simulado con Python puro.

El autómata es M₁, el Ejemplo 1 de la sección 1.2.3:

    M₁ = ({s₁, s₂}, {0, 1}, δ, s₁, {s₁})
    L(M₁) = { w ∈ {0,1}* : w tiene un número par de ceros }

Está en m1_par_de_ceros.jff, en el formato de JFLAP 7.1. JFLAP se usa en su
computadora; este programa lee el mismo archivo desde dentro del contenedor,
porque la carpeta es la misma. Sólo usa la biblioteca estándar de Python.

    python extras/ejemplos/afd.py                 las cadenas del ejemplo
    python extras/ejemplos/afd.py 0110 000        las que usted indique

Teoría de la Computación · 2027-1 · ESCOM-IPN
"""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

JFF = Path(__file__).with_name("m1_par_de_ceros.jff")


def leer_jff(ruta):
    """Devuelve la quíntupla (Q, Σ, δ, q₀, F) de un autómata finito guardado en .jff."""
    automata = ET.parse(ruta).getroot().find("automaton")
    nombre, inicial, finales = {}, None, set()
    for e in automata.iter("state"):
        nombre[e.get("id")] = e.get("name")
        if e.find("initial") is not None:
            inicial = e.get("name")
        if e.find("final") is not None:
            finales.add(e.get("name"))
    delta = {}
    for t in automata.iter("transition"):
        q = nombre[t.findtext("from")]
        a = t.findtext("read") or ""        # <read/> vacío es una transición λ
        delta[q, a] = nombre[t.findtext("to")]
    alfabeto = {a for (_, a) in delta if a}
    return set(nombre.values()), alfabeto, delta, inicial, finales


def acepta(m, w):
    """Calcula δ̂(q₀, w) símbolo a símbolo y dice si el estado final está en F."""
    _, _, delta, q, finales = m
    for a in w:
        if (q, a) not in delta:             # sin transición definida: se rechaza
            return False
        q = delta[q, a]
    return q in finales


if __name__ == "__main__":
    m1 = leer_jff(JFF)
    cadenas = sys.argv[1:] if len(sys.argv) > 1 else ["", "111", "10", "100", "1001"]
    for w in cadenas:
        print(f"{w or 'λ':>8}   {'se acepta' if acepta(m1, w) else 'se rechaza'}")
