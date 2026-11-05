"""Pruebas del ejemplo: el autómata M₁ contra la definición de su lenguaje.

En lugar de probar unas cuantas cadenas a mano, la última prueba compara TODAS
las cadenas de {0,1}* de longitud 0 a 10 —2047 en total— contra la definición:

    w ∈ L(M₁)   si y sólo si   w tiene un número par de ceros

    pytest extras/ejemplos
"""
from itertools import product

from afd import JFF, acepta, leer_jff

M1 = leer_jff(JFF)


def test_lee_la_quintupla():
    estados, alfabeto, delta, inicial, finales = M1
    assert estados == {"s1", "s2"}
    assert alfabeto == {"0", "1"}
    assert inicial == "s1"
    assert finales == {"s1"}
    assert len(delta) == 4          # completo: una transición por (estado, símbolo)


def test_cadenas_del_ejemplo():
    assert acepta(M1, "")           # λ: cero ceros es un número par
    assert acepta(M1, "111")        # ningún cero
    assert not acepta(M1, "10")     # un cero
    assert acepta(M1, "100")        # dos ceros
    assert acepta(M1, "1001")       # la traza de la sección 1.2.3


def test_contra_la_definicion():
    for n in range(11):
        for w in map("".join, product("01", repeat=n)):
            assert acepta(M1, w) == (w.count("0") % 2 == 0), w
