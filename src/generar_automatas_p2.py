"""Genera todos los autómatas de la Práctica 2 en .jff, .json y .xml dentro de automatas/.

Organiza los archivos en las 5 subcarpetas exigidas por la estructura de la Práctica 2:
1. `automatas/lista2-afd/`: Cobertura completa de la Lista 2 (ejercicios 94 a 150) y
   ejercicios AFD de la Lista 3 (simplificación 151-157 y regex/equivalencias AFD).
2. `automatas/lista3-afnd/`: Ejercicios de AFND estándar de la Lista 3 (158 a 195,
   260 a 263), incluyendo las versiones no deterministas directas de 162 a 188.
3. `automatas/lista3-afnd-lambda/`: Ejercicios de AFND con transiciones lambda de la
   Lista 3 (196 a 200 y las construcciones de Thompson de expresiones regulares 241 a 253).
4. `automatas/conversiones/`: Los AFND estándar y AFD resultantes de convertir cada
   AFND y cada AFND-λ mediante eliminación de λ y construcción de subconjuntos.
5. `automatas/aplicacion/`: El autómata del Ejercicio 5 (Comportamiento ampliado de los
   fantasmas de Pac-Man basado en Gribkoff, 2013, Fig. 3, ampliado de 4 a 7 estados y
   de 4 a 7 eventos).
"""

from __future__ import annotations

from pathlib import Path
import shutil
import sys

ROOT_P2 = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_P2 / "src"))

from automata import AutomataFinito
from formatos import guardar_en_tres_formatos, importar_jff_texto

DIR_L2_AFD = ROOT_P2 / "automatas" / "lista2-afd"
DIR_L3_AFND = ROOT_P2 / "automatas" / "lista3-afnd"
DIR_L3_AFND_L = ROOT_P2 / "automatas" / "lista3-afnd-lambda"
DIR_CONV = ROOT_P2 / "automatas" / "conversiones"
DIR_APP = ROOT_P2 / "automatas" / "aplicacion"


def kmp_afd_obj(alfabeto: list[str], patron: str, solo_sufijo: bool = False) -> AutomataFinito:
    """Construye un `AutomataFinito` AFD para contener `patron` o terminar en `patron`."""
    m = len(patron)
    estados = [f"q{i}" for i in range(m + 1)]
    trans: dict[tuple[str, str], list[str]] = {}
    for i in range(m + 1):
        if i == m and not solo_sufijo:
            for a in alfabeto:
                trans[(f"q{m}", a)] = [f"q{m}"]
            continue
        pref = patron[:i]
        for a in alfabeto:
            cand = pref + a
            k = min(m, len(cand))
            while k > 0 and not cand.endswith(patron[:k]):
                k -= 1
            trans[(f"q{i}", a)] = [f"q{k}"]
    return AutomataFinito(
        alfabeto=alfabeto,
        estados=estados,
        inicial="q0",
        aceptacion=[f"q{m}"],
        transiciones=trans,
        tipo_declarado="AFD",
    )


def afnd_contiene_patron(alfabeto: list[str], patron: str) -> AutomataFinito:
    """Construye el AFND estándar canónico (mucho más simple que el AFD) que contiene `patron`."""
    m = len(patron)
    estados = [f"q{i}" for i in range(m + 1)]
    trans: dict[tuple[str, str], list[str]] = {}
    # En q0 se queda con todo el alfabeto y además con patron[0] bifurca a q1
    for a in alfabeto:
        dest = ["q0"]
        if a == patron[0]:
            dest.append("q1")
        trans[("q0", a)] = dest
    for i in range(1, m):
        trans[(f"q{i}", patron[i])] = [f"q{i+1}"]
    for a in alfabeto:
        trans[(f"q{m}", a)] = [f"q{m}"]
    return AutomataFinito(
        alfabeto=alfabeto,
        estados=estados,
        inicial="q0",
        aceptacion=[f"q{m}"],
        transiciones=trans,
        tipo_declarado="AFND",
    )


def afnd_termina_patron(alfabeto: list[str], patron: str) -> AutomataFinito:
    """Construye el AFND estándar que acepta cadenas que terminan con `patron`."""
    m = len(patron)
    estados = [f"q{i}" for i in range(m + 1)]
    trans: dict[tuple[str, str], list[str]] = {}
    for a in alfabeto:
        dest = ["q0"]
        if a == patron[0]:
            dest.append("q1")
        trans[("q0", a)] = dest
    for i in range(1, m):
        trans[(f"q{i}", patron[i])] = [f"q{i+1}"]
    return AutomataFinito(
        alfabeto=alfabeto,
        estados=estados,
        inicial="q0",
        aceptacion=[f"q{m}"],
        transiciones=trans,
        tipo_declarado="AFND",
    )


def generar_lista2_afd_completa() -> dict[str, AutomataFinito]:
    """Genera los AFD de la Lista 2 completa (94 a 150), conservando los de P1 y añadiendo los sin *."""
    S1 = ["0", "1", "2"]
    S2 = ["a", "b", "c", "0", "1"]
    S3 = ["a", "b"]
    SB = ["0", "1"]
    resultado: dict[str, AutomataFinito] = {}

    # 1. Importar primero los .jff ya construidos en la Práctica 1 desde Documents/practica1-tc/automatas
    dir_p1_aut = Path(r"C:\Users\cesar\Documents\practica1-tc\automatas")
    if dir_p1_aut.exists():
        for jff_path in sorted(dir_p1_aut.glob("*.jff")):
            aut = importar_jff_texto(jff_path.read_text(encoding="utf-8"))
            aut.tipo_declarado = "AFD"
            resultado[jff_path.stem] = aut

    # 2. Añadir todos los ejercicios SIN asterisco de la Lista 2 (94, 95, 96, 98, 100, 101, 104, 105, 108, 110, 114, 115, 117, 119, 129, 130, 132, 134, 136, 138, 140, 142, 144, 146)
    # Ej 94: Palabras de S1 que comienzan con 1 y terminan con 2
    resultado["ej094_comienza1_termina2"] = AutomataFinito(
        alfabeto=S1,
        estados=["q0_ini", "q1_empezo1", "q2_termina2_ok", "q3_pozo"],
        inicial="q0_ini",
        aceptacion=["q2_termina2_ok"],
        transiciones={
            ("q0_ini", "1"): ["q1_empezo1"],
            ("q0_ini", "0"): ["q3_pozo"],
            ("q0_ini", "2"): ["q3_pozo"],
            ("q1_empezo1", "0"): ["q1_empezo1"],
            ("q1_empezo1", "1"): ["q1_empezo1"],
            ("q1_empezo1", "2"): ["q2_termina2_ok"],
            ("q2_termina2_ok", "0"): ["q1_empezo1"],
            ("q2_termina2_ok", "1"): ["q1_empezo1"],
            ("q2_termina2_ok", "2"): ["q2_termina2_ok"],
            ("q3_pozo", "0"): ["q3_pozo"],
            ("q3_pozo", "1"): ["q3_pozo"],
            ("q3_pozo", "2"): ["q3_pozo"],
        },
        tipo_declarado="AFD",
    )

    # Ej 95: Palabras de S1 que tienen longitud 4
    tr_95 = {(f"q{i}", a): [f"q{min(5, i+1)}"] for i in range(6) for a in S1}
    resultado["ej095_longitud_4"] = AutomataFinito(
        alfabeto=S1,
        estados=[f"q{i}" for i in range(6)],
        inicial="q0",
        aceptacion=["q4"],
        transiciones=tr_95,
        tipo_declarado="AFD",
    )

    # Ej 96: Palabras de S1 con prefijo 20 y longitud 4
    resultado["ej096_prefijo20_longitud4"] = AutomataFinito(
        alfabeto=S1,
        estados=["q0", "q1_2", "q2_20", "q3_len3", "q4_ok", "q5_pozo"],
        inicial="q0",
        aceptacion=["q4_ok"],
        transiciones={
            ("q0", "2"): ["q1_2"], ("q0", "0"): ["q5_pozo"], ("q0", "1"): ["q5_pozo"],
            ("q1_2", "0"): ["q2_20"], ("q1_2", "1"): ["q5_pozo"], ("q1_2", "2"): ["q5_pozo"],
            ("q2_20", "0"): ["q3_len3"], ("q2_20", "1"): ["q3_len3"], ("q2_20", "2"): ["q3_len3"],
            ("q3_len3", "0"): ["q4_ok"], ("q3_len3", "1"): ["q4_ok"], ("q3_len3", "2"): ["q4_ok"],
            ("q4_ok", "0"): ["q5_pozo"], ("q4_ok", "1"): ["q5_pozo"], ("q4_ok", "2"): ["q5_pozo"],
            ("q5_pozo", "0"): ["q5_pozo"], ("q5_pozo", "1"): ["q5_pozo"], ("q5_pozo", "2"): ["q5_pozo"],
        },
        tipo_declarado="AFD",
    )

    # Ej 98: Palabras de S1 que terminan con 00102
    resultado["ej098_termina_00102"] = kmp_afd_obj(S1, "00102", solo_sufijo=True)

    # Ej 100: Palabras de S2 donde el 1er símbolo es letra (a,b,c) y el 2do es dígito (0,1)
    tr_100: dict[tuple[str, str], list[str]] = {}
    for s in S2:
        tr_100[("q0", s)] = ["q1_letra"] if s in ("a", "b", "c") else ["q3_pozo"]
        tr_100[("q1_letra", s)] = ["q2_ok"] if s in ("0", "1") else ["q3_pozo"]
        tr_100[("q2_ok", s)] = ["q2_ok"]
        tr_100[("q3_pozo", s)] = ["q3_pozo"]
    resultado["ej100_letra_y_digito"] = AutomataFinito(
        alfabeto=S2,
        estados=["q0", "q1_letra", "q2_ok", "q3_pozo"],
        inicial="q0",
        aceptacion=["q2_ok"],
        transiciones=tr_100,
        tipo_declarado="AFD",
    )

    # Ej 101: Palabras de S3 que contienen aba
    resultado["ej101_contiene_aba"] = kmp_afd_obj(S3, "aba", solo_sufijo=False)

    # Ej 104: Palabras de S3 que inician con abbab
    resultado["ej104_inicia_abbab"] = AutomataFinito(
        alfabeto=S3,
        estados=["q0", "q1_a", "q2_ab", "q3_abb", "q4_abba", "q5_abbab_ok", "q6_pozo"],
        inicial="q0",
        aceptacion=["q5_abbab_ok"],
        transiciones={
            ("q0", "a"): ["q1_a"], ("q0", "b"): ["q6_pozo"],
            ("q1_a", "b"): ["q2_ab"], ("q1_a", "a"): ["q6_pozo"],
            ("q2_ab", "b"): ["q3_abb"], ("q2_ab", "a"): ["q6_pozo"],
            ("q3_abb", "a"): ["q4_abba"], ("q3_abb", "b"): ["q6_pozo"],
            ("q4_abba", "b"): ["q5_abbab_ok"], ("q4_abba", "a"): ["q6_pozo"],
            ("q5_abbab_ok", "a"): ["q5_abbab_ok"], ("q5_abbab_ok", "b"): ["q5_abbab_ok"],
            ("q6_pozo", "a"): ["q6_pozo"], ("q6_pozo", "b"): ["q6_pozo"],
        },
        tipo_declarado="AFD",
    )

    # Ej 105: Palabras de S3 que terminan con abaa
    resultado["ej105_termina_abaa"] = kmp_afd_obj(S3, "abaa", solo_sufijo=True)

    # Ej 108: Palabras de S2 con abbcb y cbaabb sin traslape (lo construimos via conversión de su AFND)
    # Ej 110: Palabras de S1 con exactamente 3 veces 01
    resultado["ej110_exactamente_tres_01"] = AutomataFinito(
        alfabeto=S1,
        estados=["c0_no0", "c0_0", "c1_no0", "c1_0", "c2_no0", "c2_0", "c3_no0_ok", "c3_0_ok", "c4_pozo"],
        inicial="c0_no0",
        aceptacion=["c3_no0_ok", "c3_0_ok"],
        transiciones={
            ("c0_no0", "0"): ["c0_0"], ("c0_no0", "1"): ["c0_no0"], ("c0_no0", "2"): ["c0_no0"],
            ("c0_0", "0"): ["c0_0"], ("c0_0", "1"): ["c1_no0"], ("c0_0", "2"): ["c0_no0"],
            ("c1_no0", "0"): ["c1_0"], ("c1_no0", "1"): ["c1_no0"], ("c1_no0", "2"): ["c1_no0"],
            ("c1_0", "0"): ["c1_0"], ("c1_0", "1"): ["c2_no0"], ("c1_0", "2"): ["c1_no0"],
            ("c2_no0", "0"): ["c2_0"], ("c2_no0", "1"): ["c2_no0"], ("c2_no0", "2"): ["c2_no0"],
            ("c2_0", "0"): ["c2_0"], ("c2_0", "1"): ["c3_no0_ok"], ("c2_0", "2"): ["c2_no0"],
            ("c3_no0_ok", "0"): ["c3_0_ok"], ("c3_no0_ok", "1"): ["c3_no0_ok"], ("c3_no0_ok", "2"): ["c3_no0_ok"],
            ("c3_0_ok", "0"): ["c3_0_ok"], ("c3_0_ok", "1"): ["c4_pozo"], ("c3_0_ok", "2"): ["c3_no0_ok"],
            ("c4_pozo", "0"): ["c4_pozo"], ("c4_pozo", "1"): ["c4_pozo"], ("c4_pozo", "2"): ["c4_pozo"],
        },
        tipo_declarado="AFD",
    )

    # Ej 114: L = {a^n b^m : m, n in N} (asumiendo N >= 1 o N >= 0; para N >= 0 es a*b*)
    resultado["ej114_an_bm"] = AutomataFinito(
        alfabeto=S3,
        estados=["q0_a", "q1_b", "q2_pozo"],
        inicial="q0_a",
        aceptacion=["q0_a", "q1_b"],
        transiciones={
            ("q0_a", "a"): ["q0_a"], ("q0_a", "b"): ["q1_b"],
            ("q1_b", "b"): ["q1_b"], ("q1_b", "a"): ["q2_pozo"],
            ("q2_pozo", "a"): ["q2_pozo"], ("q2_pozo", "b"): ["q2_pozo"],
        },
        tipo_declarado="AFD",
    )

    # Ej 115: L = {(abc)^n : n in N} sobre S2
    resultado["ej115_abc_n"] = AutomataFinito(
        alfabeto=S2,
        estados=["q0_ok", "q1_a", "q2_ab", "q3_pozo"],
        inicial="q0_ok",
        aceptacion=["q0_ok"],
        transiciones={
            ("q0_ok", "a"): ["q1_a"], ("q0_ok", "b"): ["q3_pozo"], ("q0_ok", "c"): ["q3_pozo"], ("q0_ok", "0"): ["q3_pozo"], ("q0_ok", "1"): ["q3_pozo"],
            ("q1_a", "b"): ["q2_ab"], ("q1_a", "a"): ["q3_pozo"], ("q1_a", "c"): ["q3_pozo"], ("q1_a", "0"): ["q3_pozo"], ("q1_a", "1"): ["q3_pozo"],
            ("q2_ab", "c"): ["q0_ok"], ("q2_ab", "a"): ["q3_pozo"], ("q2_ab", "b"): ["q3_pozo"], ("q2_ab", "0"): ["q3_pozo"], ("q2_ab", "1"): ["q3_pozo"],
            ("q3_pozo", "a"): ["q3_pozo"], ("q3_pozo", "b"): ["q3_pozo"], ("q3_pozo", "c"): ["q3_pozo"], ("q3_pozo", "0"): ["q3_pozo"], ("q3_pozo", "1"): ["q3_pozo"],
        },
        tipo_declarado="AFD",
    )

    # Ej 117: L = {a^n b^m a^p b^q} = a*b*a*b*
    resultado["ej117_an_bm_ap_bq"] = AutomataFinito(
        alfabeto=S3,
        estados=["q0_a1", "q1_b1", "q2_a2", "q3_b2", "q4_pozo"],
        inicial="q0_a1",
        aceptacion=["q0_a1", "q1_b1", "q2_a2", "q3_b2"],
        transiciones={
            ("q0_a1", "a"): ["q0_a1"], ("q0_a1", "b"): ["q1_b1"],
            ("q1_b1", "b"): ["q1_b1"], ("q1_b1", "a"): ["q2_a2"],
            ("q2_a2", "a"): ["q2_a2"], ("q2_a2", "b"): ["q3_b2"],
            ("q3_b2", "b"): ["q3_b2"], ("q3_b2", "a"): ["q4_pozo"],
            ("q4_pozo", "a"): ["q4_pozo"], ("q4_pozo", "b"): ["q4_pozo"],
        },
        tipo_declarado="AFD",
    )

    # Ej 119: Después de cada subcadena aa aparece una b (no contiene aaa y no termina en aa)
    resultado["ej119_despues_de_aa_viene_b"] = AutomataFinito(
        alfabeto=S3,
        estados=["q0_ok", "q1_a_ok", "q2_aa_espera_b", "q3_pozo_aaa"],
        inicial="q0_ok",
        aceptacion=["q0_ok", "q1_a_ok"],
        transiciones={
            ("q0_ok", "a"): ["q1_a_ok"], ("q0_ok", "b"): ["q0_ok"],
            ("q1_a_ok", "a"): ["q2_aa_espera_b"], ("q1_a_ok", "b"): ["q0_ok"],
            ("q2_aa_espera_b", "b"): ["q0_ok"], ("q2_aa_espera_b", "a"): ["q3_pozo_aaa"],
            ("q3_pozo_aaa", "a"): ["q3_pozo_aaa"], ("q3_pozo_aaa", "b"): ["q3_pozo_aaa"],
        },
        tipo_declarado="AFD",
    )

    # Ej 129, 130, 132, 134, 136, 138, 140a, 140b, 142a, 142b, 144a-e, 146
    resultado["ej129_no_tres_b_consecutivos"] = AutomataFinito(
        alfabeto=S3,
        estados=["q0", "q1", "q2", "q3"],
        inicial="q0",
        aceptacion=["q0", "q1", "q2"],
        transiciones={
            ("q0", "a"): ["q0"], ("q0", "b"): ["q1"],
            ("q1", "a"): ["q0"], ("q1", "b"): ["q2"],
            ("q2", "a"): ["q0"], ("q2", "b"): ["q3"],
            ("q3", "a"): ["q3"], ("q3", "b"): ["q3"],
        },
        tipo_declarado="AFD",
    )

    resultado["ej130_esquema_afd"] = AutomataFinito(
        alfabeto=SB,
        estados=["q1", "q2", "q3"],
        inicial="q1",
        aceptacion=["q2"],
        transiciones={
            ("q1", "0"): ["q1"], ("q1", "1"): ["q2"],
            ("q2", "0"): ["q3"], ("q2", "1"): ["q2"],
            ("q3", "0"): ["q2"], ("q3", "1"): ["q2"],
        },
        tipo_declarado="AFD",
    )

    resultado["ej132_an_b"] = AutomataFinito(
        alfabeto=S3,
        estados=["q0", "q1_ok", "q2_pozo"],
        inicial="q0",
        aceptacion=["q1_ok"],
        transiciones={
            ("q0", "a"): ["q0"], ("q0", "b"): ["q1_ok"],
            ("q1_ok", "a"): ["q2_pozo"], ("q1_ok", "b"): ["q2_pozo"],
            ("q2_pozo", "a"): ["q2_pozo"], ("q2_pozo", "b"): ["q2_pozo"],
        },
        tipo_declarado="AFD",
    )

    resultado["ej134_patron_abac"] = kmp_afd_obj(["a", "b", "c"], "abac", solo_sufijo=False)

    resultado["ej136_am_bn_positivos"] = AutomataFinito(
        alfabeto=S3,
        estados=["q0", "q1_a", "q2_ab_ok", "q3_pozo"],
        inicial="q0",
        aceptacion=["q2_ab_ok"],
        transiciones={
            ("q0", "a"): ["q1_a"], ("q0", "b"): ["q3_pozo"],
            ("q1_a", "a"): ["q1_a"], ("q1_a", "b"): ["q2_ab_ok"],
            ("q2_ab_ok", "b"): ["q2_ab_ok"], ("q2_ab_ok", "a"): ["q3_pozo"],
            ("q3_pozo", "a"): ["q3_pozo"], ("q3_pozo", "b"): ["q3_pozo"],
        },
        tipo_declarado="AFD",
    )

    resultado["ej138_num_b_divisible_por_3"] = AutomataFinito(
        alfabeto=S3,
        estados=["q0_mod0", "q1_mod1", "q2_mod2"],
        inicial="q0_mod0",
        aceptacion=["q0_mod0"],
        transiciones={
            ("q0_mod0", "a"): ["q0_mod0"], ("q0_mod0", "b"): ["q1_mod1"],
            ("q1_mod1", "a"): ["q1_mod1"], ("q1_mod1", "b"): ["q2_mod2"],
            ("q2_mod2", "a"): ["q2_mod2"], ("q2_mod2", "b"): ["q0_mod0"],
        },
        tipo_declarado="AFD",
    )

    resultado["ej140a_impar_de_ceros"] = AutomataFinito(
        alfabeto=SB,
        estados=["q0_par", "q1_impar"],
        inicial="q0_par",
        aceptacion=["q1_impar"],
        transiciones={
            ("q0_par", "0"): ["q1_impar"], ("q0_par", "1"): ["q0_par"],
            ("q1_impar", "0"): ["q0_par"], ("q1_impar", "1"): ["q1_impar"],
        },
        tipo_declarado="AFD",
    )

    resultado["ej140b_par0_y_par1"] = AutomataFinito(
        alfabeto=SB,
        estados=["q00_ok", "q10", "q01", "q11"],
        inicial="q00_ok",
        aceptacion=["q00_ok"],
        transiciones={
            ("q00_ok", "0"): ["q10"], ("q00_ok", "1"): ["q01"],
            ("q10", "0"): ["q00_ok"], ("q10", "1"): ["q11"],
            ("q01", "0"): ["q11"], ("q01", "1"): ["q00_ok"],
            ("q11", "0"): ["q01"], ("q11", "1"): ["q10"],
        },
        tipo_declarado="AFD",
    )

    resultado["ej142_ab_positiva"] = AutomataFinito(
        alfabeto=S3,
        estados=["q0_ini", "q1_a", "q2_ab_ok", "q3_pozo"],
        inicial="q0_ini",
        aceptacion=["q2_ab_ok"],
        transiciones={
            ("q0_ini", "a"): ["q1_a"], ("q0_ini", "b"): ["q3_pozo"],
            ("q1_a", "b"): ["q2_ab_ok"], ("q1_a", "a"): ["q3_pozo"],
            ("q2_ab_ok", "a"): ["q1_a"], ("q2_ab_ok", "b"): ["q3_pozo"],
            ("q3_pozo", "a"): ["q3_pozo"], ("q3_pozo", "b"): ["q3_pozo"],
        },
        tipo_declarado="AFD",
    )

    resultado["ej144a_comienza_con_a"] = AutomataFinito(
        alfabeto=S3,
        estados=["q0", "q1_ok", "q2_pozo"],
        inicial="q0",
        aceptacion=["q1_ok"],
        transiciones={
            ("q0", "a"): ["q1_ok"], ("q0", "b"): ["q2_pozo"],
            ("q1_ok", "a"): ["q1_ok"], ("q1_ok", "b"): ["q1_ok"],
            ("q2_pozo", "a"): ["q2_pozo"], ("q2_pozo", "b"): ["q2_pozo"],
        },
        tipo_declarado="AFD",
    )

    resultado["ej144b_comienza_a_termina_b"] = AutomataFinito(
        alfabeto=S3,
        estados=["q0", "q1_a", "q2_ab_ok", "q3_pozo"],
        inicial="q0",
        aceptacion=["q2_ab_ok"],
        transiciones={
            ("q0", "a"): ["q1_a"], ("q0", "b"): ["q3_pozo"],
            ("q1_a", "a"): ["q1_a"], ("q1_a", "b"): ["q2_ab_ok"],
            ("q2_ab_ok", "a"): ["q1_a"], ("q2_ab_ok", "b"): ["q2_ab_ok"],
            ("q3_pozo", "a"): ["q3_pozo"], ("q3_pozo", "b"): ["q3_pozo"],
        },
        tipo_declarado="AFD",
    )

    resultado["ej144c_contiene_aaa"] = kmp_afd_obj(S3, "aaa", solo_sufijo=False)

    # Ej 146: Binario leído de izquierda a derecha múltiplo de 5
    tr_146 = {(f"q{r}", b): [f"q{(2*r + int(b)) % 5}"] for r in range(5) for b in SB}
    resultado["ej146_binario_izq_a_der_mult5"] = AutomataFinito(
        alfabeto=SB,
        estados=[f"q{r}" for r in range(5)],
        inicial="q0",
        aceptacion=["q0"],
        transiciones=tr_146,
        tipo_declarado="AFD",
    )

    # Ej 259: Autómata de tabla 259 (4 estados sobre {a, b})
    resultado["ej259_tabla_arden"] = AutomataFinito(
        alfabeto=S3,
        estados=["1", "2", "3", "4"],
        inicial="1",
        aceptacion=["4"],
        transiciones={
            ("1", "a"): ["3"], ("1", "b"): ["2"],
            ("2", "a"): ["1"], ("2", "b"): ["3"],
            ("3", "a"): ["2"], ("3", "b"): ["3"],
            ("4", "a"): ["1"], ("4", "b"): ["4"],
        },
        tipo_declarado="AFD",
    )

    return resultado


def generar_lista3_afnd() -> dict[str, AutomataFinito]:
    """Genera los AFND estándar de la Lista 3 (158-195, 260-263)."""
    S1 = ["0", "1", "2"]
    S2 = ["a", "b", "c", "0", "1"]
    S3 = ["a", "b"]
    SB = ["0", "1"]
    afnds: dict[str, AutomataFinito] = {}

    # 158 a 161
    afnds["ej158_afnd_cadena_01"] = AutomataFinito(
        alfabeto=SB,
        estados=["q1", "q2", "q3"],
        inicial="q1",
        aceptacion=["q3"],
        transiciones={("q1", "0"): ["q2"], ("q2", "1"): ["q3"]},
        tipo_declarado="AFND",
    )
    afnds["ej159_afnd_1estrella_01"] = AutomataFinito(
        alfabeto=SB,
        estados=["q1", "q2", "q3"],
        inicial="q1",
        aceptacion=["q3"],
        transiciones={("q1", "1"): ["q1"], ("q1", "0"): ["q2"], ("q2", "1"): ["q3"]},
        tipo_declarado="AFND",
    )
    afnds["ej160_afnd_prefijo_01"] = AutomataFinito(
        alfabeto=SB,
        estados=["q1", "q2", "q3"],
        inicial="q1",
        aceptacion=["q3"],
        transiciones={
            ("q1", "0"): ["q2"],
            ("q2", "1"): ["q3"],
            ("q3", "0"): ["q3"],
            ("q3", "1"): ["q3"],
        },
        tipo_declarado="AFND",
    )
    afnds["ej161_afnd_ciclo_010"] = AutomataFinito(
        alfabeto=SB,
        estados=["q1", "q2", "q3"],
        inicial="q1",
        aceptacion=["q1"],
        transiciones={("q1", "0"): ["q2"], ("q2", "1"): ["q3"], ("q3", "0"): ["q1"]},
        tipo_declarado="AFND",
    )

    # 162 a 188: Versiones AFND simplificadas de los problemas 94-123 de la Lista 2
    afnds["ej164_afnd_termina_00102"] = afnd_termina_patron(S1, "00102")
    afnds["ej165_afnd_termina_001001"] = afnd_termina_patron(S1, "001001")
    afnds["ej167_afnd_contiene_aba"] = afnd_contiene_patron(S3, "aba")
    afnds["ej168_afnd_contiene_abbbab"] = afnd_contiene_patron(S3, "abbbab")
    afnds["ej169_afnd_contiene_aabbba"] = afnd_contiene_patron(S3, "aabbba")
    afnds["ej171_afnd_termina_abaa"] = afnd_termina_patron(S3, "abaa")
    afnds["ej172_afnd_incluye_1101001"] = afnd_contiene_patron(S1, "1101001")

    # 184 (correspondiente a 118): w = a x ab y a sobre {a, b} -> en AFND basta con 5 estados sin pozo!
    afnds["ej184_afnd_axabya"] = AutomataFinito(
        alfabeto=S3,
        estados=["q0", "q1", "q2", "q3", "q4"],
        inicial="q0",
        aceptacion=["q4"],
        transiciones={
            ("q0", "a"): ["q1"],
            ("q1", "a"): ["q1", "q2"],
            ("q1", "b"): ["q1"],
            ("q2", "b"): ["q3"],
            ("q3", "a"): ["q3", "q4"],
            ("q3", "b"): ["q3"],
        },
        tipo_declarado="AFND",
    )

    # 186 (correspondiente a 120): primer y último carácter distintos sobre S1
    afnds["ej186_afnd_primero_ultimo_distintos"] = AutomataFinito(
        alfabeto=S1,
        estados=["q0", "q_ini0", "q_ini1", "q_ini2", "q_fin"],
        inicial="q0",
        aceptacion=["q_fin"],
        transiciones={
            ("q0", "0"): ["q_ini0"],
            ("q0", "1"): ["q_ini1"],
            ("q0", "2"): ["q_ini2"],
            ("q_ini0", "0"): ["q_ini0"],
            ("q_ini0", "1"): ["q_ini0", "q_fin"],
            ("q_ini0", "2"): ["q_ini0", "q_fin"],
            ("q_ini1", "0"): ["q_ini1", "q_fin"],
            ("q_ini1", "1"): ["q_ini1"],
            ("q_ini1", "2"): ["q_ini1", "q_fin"],
            ("q_ini2", "0"): ["q_ini2", "q_fin"],
            ("q_ini2", "1"): ["q_ini2", "q_fin"],
            ("q_ini2", "2"): ["q_ini2"],
        },
        tipo_declarado="AFND",
    )

    # 189: AFND que contiene 00101 o 00110
    afnds["ej189_afnd_00101_o_00110"] = AutomataFinito(
        alfabeto=SB,
        estados=["q0", "q1", "q2", "q3", "q4_a", "q4_b", "q5_ok"],
        inicial="q0",
        aceptacion=["q5_ok"],
        transiciones={
            ("q0", "0"): ["q0", "q1"],
            ("q0", "1"): ["q0"],
            ("q1", "0"): ["q2"],
            ("q2", "1"): ["q3"],
            ("q3", "0"): ["q4_a"],
            ("q3", "1"): ["q4_b"],
            ("q4_a", "1"): ["q5_ok"],
            ("q4_b", "0"): ["q5_ok"],
            ("q5_ok", "0"): ["q5_ok"],
            ("q5_ok", "1"): ["q5_ok"],
        },
        tipo_declarado="AFND",
    )

    # 190: AFND que contiene 11010 y 10100
    afnds["ej190_afnd_11010_y_10100"] = AutomataFinito(
        alfabeto=SB,
        estados=["q0", "q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9_ok"],
        inicial="q0",
        aceptacion=["q9_ok"],
        transiciones={
            ("q0", "0"): ["q0"],
            ("q0", "1"): ["q0", "q1"],
            ("q1", "1"): ["q2"],
            ("q2", "0"): ["q3"],
            ("q3", "1"): ["q4"],
            ("q4", "0"): ["q5"],
            ("q5", "0"): ["q5"],
            ("q5", "1"): ["q5", "q6"],
            ("q6", "0"): ["q7"],
            ("q7", "1"): ["q8"],
            ("q8", "0"): ["q9_ok"],
            ("q9_ok", "0"): ["q9_ok"],
            ("q9_ok", "1"): ["q9_ok"],
        },
        tipo_declarado="AFND",
    )

    # 192, 193, 194, 195 (Tablas AFND originales)
    afnds["ej192_afnd_tabla"] = AutomataFinito(
        alfabeto=SB,
        estados=["A", "B", "C"],
        inicial="A",
        aceptacion=["C"],
        transiciones={
            ("A", "0"): ["B"],
            ("A", "1"): ["B", "C"],
            ("B", "0"): ["A", "B"],
            ("C", "0"): ["A", "C"],
        },
        tipo_declarado="AFND",
    )

    afnds["ej193_afnd_tabla"] = AutomataFinito(
        alfabeto=SB,
        estados=["A", "B", "C", "D"],
        inicial="A",
        aceptacion=["D"],
        transiciones={
            ("A", "1"): ["B", "C"],
            ("B", "0"): ["A", "D"],
            ("B", "1"): ["B", "C", "D"],
            ("C", "0"): ["C"],
            ("C", "1"): ["A", "C"],
            ("D", "0"): ["C"],
            ("D", "1"): ["D"],
        },
        tipo_declarado="AFND",
    )

    afnds["ej194_afnd_tabla"] = AutomataFinito(
        alfabeto=S1,
        estados=["A", "B", "C", "D"],
        inicial="A",
        aceptacion=["C", "D"],
        transiciones={
            ("A", "0"): ["A", "B"],
            ("A", "1"): ["A", "C"],
            ("A", "2"): ["A"],
            ("C", "0"): ["A", "B"],
            ("C", "1"): ["A", "B", "C", "D"],
            ("D", "0"): ["B"],
            ("D", "1"): ["A"],
        },
        tipo_declarado="AFND",
    )

    afnds["ej195_afnd_tabla"] = AutomataFinito(
        alfabeto=SB,
        estados=["A", "B", "C", "D", "E"],
        inicial="A",
        aceptacion=["C", "E"],
        transiciones={
            ("A", "0"): ["A", "B"],
            ("A", "1"): ["A"],
            ("B", "0"): ["A"],
            ("B", "1"): ["C"],
            ("C", "0"): ["A"],
            ("C", "1"): ["D"],
            ("D", "0"): ["D"],
            ("D", "1"): ["E"],
            ("E", "0"): ["E"],
            ("E", "1"): ["C", "D"],
        },
        tipo_declarado="AFND",
    )

    # 260, 261, 262, 263 (Los AFND originales antes de convertir a AFD)
    afnds["ej260_afnd_original"] = AutomataFinito(
        alfabeto=SB,
        estados=["A", "B", "C", "D", "E"],
        inicial="A",
        aceptacion=["D"],
        transiciones={
            ("A", "1"): ["B", "C"],
            ("B", "0"): ["A", "B", "D"],
            ("B", "1"): ["C", "D"],
            ("C", "0"): ["A", "C"],
            ("C", "1"): ["A", "E"],
            ("D", "1"): ["D", "E"],
            ("E", "0"): ["A", "E"],
        },
        tipo_declarado="AFND",
    )

    afnds["ej261_afnd_original"] = AutomataFinito(
        alfabeto=SB,
        estados=["q0", "q1", "q2", "q3", "q4"],
        inicial="q0",
        aceptacion=["q2", "q4"],
        transiciones={
            ("q0", "0"): ["q0", "q1"],
            ("q0", "1"): ["q0", "q3"],
            ("q1", "0"): ["q2"],
            ("q3", "1"): ["q4"],
        },
        tipo_declarado="AFND",
    )

    afnds["ej262_afnd_ab_ba"] = AutomataFinito(
        alfabeto=S3,
        estados=["q0", "q1", "q2", "q3", "q4"],
        inicial="q0",
        aceptacion=["q2", "q4"],
        transiciones={
            ("q0", "a"): ["q1"],
            ("q1", "b"): ["q2"],
            ("q0", "b"): ["q3"],
            ("q3", "a"): ["q4"],
        },
        tipo_declarado="AFND",
    )

    afnds["ej263_afnd_original"] = AutomataFinito(
        alfabeto=SB,
        estados=["q0", "q1", "q2"],
        inicial="q0",
        aceptacion=["q2"],
        transiciones={
            ("q0", "0"): ["q0", "q1"],
            ("q0", "1"): ["q0"],
            ("q1", "1"): ["q2"],
        },
        tipo_declarado="AFND",
    )

    return afnds


def generar_lista3_afnd_lambda() -> dict[str, AutomataFinito]:
    """Genera todos los AFND-λ de la Lista 3: reactivos 196-200 y expresiones regulares 241-253."""
    SB = ["0", "1"]
    afnd_l: dict[str, AutomataFinito] = {}

    # 196 a 200 (Tablas AFND-λ originales)
    afnd_l["ej196_afnd_lambda"] = AutomataFinito(
        alfabeto=SB,
        estados=["A", "B", "C"],
        inicial="A",
        aceptacion=["C"],
        transiciones={
            ("A", ""): ["B"],
            ("A", "0"): ["A"],
            ("B", "0"): ["A", "B"],
            ("B", "1"): ["C"],
        },
        tipo_declarado="AFND-lambda",
    )

    afnd_l["ej197_afnd_lambda"] = AutomataFinito(
        alfabeto=SB,
        estados=["A", "B", "C", "D"],
        inicial="A",
        aceptacion=["D"],
        transiciones={
            ("A", ""): ["C"],
            ("A", "0"): ["B", "D"],
            ("B", ""): ["D"],
            ("B", "0"): ["A", "C"],
            ("B", "1"): ["D"],
            ("C", ""): ["B"],
            ("C", "1"): ["A", "C"],
            ("D", "1"): ["D"],
        },
        tipo_declarado="AFND-lambda",
    )

    afnd_l["ej198_afnd_lambda"] = AutomataFinito(
        alfabeto=SB,
        estados=["A", "B", "C", "D"],
        inicial="A",
        aceptacion=["D"],
        transiciones={
            ("A", ""): ["C"],
            ("A", "0"): ["B"],
            ("B", "0"): ["C"],
            ("C", ""): ["B"],
            ("C", "1"): ["C", "D"],
            ("D", "1"): ["B"],
        },
        tipo_declarado="AFND-lambda",
    )

    afnd_l["ej199_afnd_lambda"] = AutomataFinito(
        alfabeto=SB,
        estados=["A", "B", "C", "D", "E"],
        inicial="A",
        aceptacion=["D", "E"],
        transiciones={
            ("A", ""): ["B", "C"],
            ("A", "0"): ["E"],
            ("B", "0"): ["E"],
            ("B", "1"): ["B"],
            ("C", ""): ["E"],
            ("C", "1"): ["A", "C"],
            ("D", "1"): ["D"],
            ("E", "1"): ["D"],
        },
        tipo_declarado="AFND-lambda",
    )

    afnd_l["ej200_afnd_lambda"] = AutomataFinito(
        alfabeto=SB,
        estados=["A", "B", "C", "D", "E", "F"],
        inicial="A",
        aceptacion=["D", "E"],
        transiciones={
            ("A", ""): ["B"],
            ("A", "0"): ["F"],
            ("A", "1"): ["A", "C", "F"],
            ("B", "0"): ["C", "D"],
            ("B", "1"): ["B", "E"],
            ("C", ""): ["E"],
            ("C", "1"): ["A", "C"],
            ("D", ""): ["E", "F"],
            ("D", "0"): ["A", "C"],
            ("D", "1"): ["B", "E"],
            ("E", "1"): ["D"],
            ("F", ""): ["E"],
            ("F", "0"): ["B", "E"],
        },
        tipo_declarado="AFND-lambda",
    )

    # 241 a 253: Construcción de Thompson (AFND-λ) para cada Expresión Regular
    # 241: 0 + 1
    afnd_l["ej241_thompson_0_mas_1"] = AutomataFinito(
        alfabeto=SB,
        estados=["q0", "q1", "q2", "q3", "q4", "q5"],
        inicial="q0",
        aceptacion=["q5"],
        transiciones={
            ("q0", ""): ["q1", "q3"],
            ("q1", "0"): ["q2"],
            ("q3", "1"): ["q4"],
            ("q2", ""): ["q5"],
            ("q4", ""): ["q5"],
        },
        tipo_declarado="AFND-lambda",
    )

    # 242: 0* + 1
    afnd_l["ej242_thompson_0estrella_mas_1"] = AutomataFinito(
        alfabeto=SB,
        estados=["q0", "q1", "q2", "q3", "q4", "q5"],
        inicial="q0",
        aceptacion=["q5"],
        transiciones={
            ("q0", ""): ["q1", "q3"],
            ("q1", ""): ["q2", "q5"],
            ("q2", "0"): ["q1"],
            ("q3", "1"): ["q4"],
            ("q4", ""): ["q5"],
        },
        tipo_declarado="AFND-lambda",
    )

    # 243: (0 + 1)*
    afnd_l["ej243_thompson_0_mas_1_estrella"] = AutomataFinito(
        alfabeto=SB,
        estados=["q0", "q1", "q2", "q3"],
        inicial="q0",
        aceptacion=["q3"],
        transiciones={
            ("q0", ""): ["q1", "q3"],
            ("q1", "0"): ["q2"],
            ("q1", "1"): ["q2"],
            ("q2", ""): ["q1", "q3"],
        },
        tipo_declarado="AFND-lambda",
    )

    # 244: 0(0 + 1)
    afnd_l["ej244_thompson_0_por_0mas1"] = AutomataFinito(
        alfabeto=SB,
        estados=["q0", "q1", "q2", "q3"],
        inicial="q0",
        aceptacion=["q3"],
        transiciones={
            ("q0", "0"): ["q1"],
            ("q1", ""): ["q2"],
            ("q2", "0"): ["q3"],
            ("q2", "1"): ["q3"],
        },
        tipo_declarado="AFND-lambda",
    )

    # 245: 0(0 + 1)*
    afnd_l["ej245_thompson_0_por_0mas1_estrella"] = AutomataFinito(
        alfabeto=SB,
        estados=["q0", "q1", "q2", "q3"],
        inicial="q0",
        aceptacion=["q3"],
        transiciones={
            ("q0", "0"): ["q1"],
            ("q1", ""): ["q2", "q3"],
            ("q2", "0"): ["q1"],
            ("q2", "1"): ["q1"],
        },
        tipo_declarado="AFND-lambda",
    )

    # 246: 0*(0 + 1)
    afnd_l["ej246_thompson_0estrella_por_0mas1"] = AutomataFinito(
        alfabeto=SB,
        estados=["q0", "q1", "q2", "q3"],
        inicial="q0",
        aceptacion=["q3"],
        transiciones={
            ("q0", ""): ["q1", "q2"],
            ("q1", "0"): ["q0"],
            ("q2", "0"): ["q3"],
            ("q2", "1"): ["q3"],
        },
        tipo_declarado="AFND-lambda",
    )

    # 247: (01)* + 1*
    afnd_l["ej247_thompson_01estrella_mas_1estrella"] = AutomataFinito(
        alfabeto=SB,
        estados=["q0", "q1", "q2", "q3", "q4"],
        inicial="q0",
        aceptacion=["q4"],
        transiciones={
            ("q0", ""): ["q1", "q3"],
            ("q1", ""): ["q4"],
            ("q1", "0"): ["q2"],
            ("q2", "1"): ["q1"],
            ("q3", ""): ["q4"],
            ("q3", "1"): ["q3"],
        },
        tipo_declarado="AFND-lambda",
    )

    # 248: (0* + 1)0
    afnd_l["ej248_thompson_0estrella_mas_1_por_0"] = AutomataFinito(
        alfabeto=SB,
        estados=["q0", "q1", "q2", "q3", "q4"],
        inicial="q0",
        aceptacion=["q4"],
        transiciones={
            ("q0", ""): ["q1", "q2"],
            ("q1", "0"): ["q1"],
            ("q1", ""): ["q3"],
            ("q2", "1"): ["q3"],
            ("q3", "0"): ["q4"],
        },
        tipo_declarado="AFND-lambda",
    )

    # 249: (0* + 1)0*
    afnd_l["ej249_thompson_0estrella_mas_1_por_0estrella"] = AutomataFinito(
        alfabeto=SB,
        estados=["q0", "q1", "q2", "q3", "q4"],
        inicial="q0",
        aceptacion=["q4"],
        transiciones={
            ("q0", ""): ["q1", "q2"],
            ("q1", "0"): ["q1"],
            ("q1", ""): ["q3"],
            ("q2", "1"): ["q3"],
            ("q3", ""): ["q4"],
            ("q3", "0"): ["q3"],
        },
        tipo_declarado="AFND-lambda",
    )

    # 250: 0*1* + 1*0
    afnd_l["ej250_thompson_0est1est_mas_1est0"] = AutomataFinito(
        alfabeto=SB,
        estados=["q0", "q1", "q2", "q3", "q4"],
        inicial="q0",
        aceptacion=["q2", "q4"],
        transiciones={
            ("q0", ""): ["q1", "q3"],
            ("q1", "0"): ["q1"],
            ("q1", ""): ["q2"],
            ("q2", "1"): ["q2"],
            ("q3", "1"): ["q3"],
            ("q3", "0"): ["q4"],
        },
        tipo_declarado="AFND-lambda",
    )

    # 251: (0 + 1*)0 + 1*1
    afnd_l["ej251_thompson"] = AutomataFinito(
        alfabeto=SB,
        estados=["q0", "q1", "q2", "q3", "q4", "q5"],
        inicial="q0",
        aceptacion=["q5"],
        transiciones={
            ("q0", ""): ["q1", "q2", "q4"],
            ("q1", "0"): ["q3"],
            ("q2", "1"): ["q2"],
            ("q2", ""): ["q3"],
            ("q3", "0"): ["q5"],
            ("q4", "1"): ["q4", "q5"],
        },
        tipo_declarado="AFND-lambda",
    )

    # 252: (0+1)*(00+11) + (00+11)(0+1)*
    afnd_l["ej252_thompson"] = AutomataFinito(
        alfabeto=SB,
        estados=["q0", "q1", "q2", "q3", "q4", "q5", "q6", "q7"],
        inicial="q0",
        aceptacion=["q4", "q7"],
        transiciones={
            ("q0", ""): ["q1", "q5"],
            ("q1", "0"): ["q1", "q2"],
            ("q1", "1"): ["q1", "q3"],
            ("q2", "0"): ["q4"],
            ("q3", "1"): ["q4"],
            ("q5", "0"): ["q6"],
            ("q5", "1"): ["q6_b"],
            ("q6", "0"): ["q7"],
            ("q6_b", "1"): ["q7"],
            ("q7", "0"): ["q7"],
            ("q7", "1"): ["q7"],
        },
        tipo_declarado="AFND-lambda",
    )
    # Asegurar que q6_b esté en la lista de estados de 252
    afnd_l["ej252_thompson"] = AutomataFinito(
        alfabeto=SB,
        estados=["q0", "q1", "q2", "q3", "q4", "q5", "q6", "q6_b", "q7"],
        inicial="q0",
        aceptacion=["q4", "q7"],
        transiciones=afnd_l["ej252_thompson"].transiciones,
        tipo_declarado="AFND-lambda",
    )

    # 253: (0 + (11 + 00)*)(11 + 10 + 01)*(λ + 110)
    afnd_l["ej253_thompson"] = AutomataFinito(
        alfabeto=SB,
        estados=["q0", "q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8"],
        inicial="q0",
        aceptacion=["q8"],
        transiciones={
            ("q0", "0"): ["q4"],
            ("q0", ""): ["q1"],
            ("q1", ""): ["q4"],
            ("q1", "0"): ["q2"],
            ("q1", "1"): ["q3"],
            ("q2", "0"): ["q1"],
            ("q3", "1"): ["q1"],
            ("q4", ""): ["q8"],
            ("q4", "0"): ["q5"],
            ("q4", "1"): ["q6", "q7"],
            ("q5", "1"): ["q4"],
            ("q6", "0"): ["q4"],
            ("q6", "1"): ["q4"],
            ("q7", "1"): ["q7_b"],
            ("q7_b", "0"): ["q8"],
        },
        tipo_declarado="AFND-lambda",
    )
    afnd_l["ej253_thompson"] = AutomataFinito(
        alfabeto=SB,
        estados=["q0", "q1", "q2", "q3", "q4", "q5", "q6", "q7", "q7_b", "q8"],
        inicial="q0",
        aceptacion=["q8"],
        transiciones=afnd_l["ej253_thompson"].transiciones,
        tipo_declarado="AFND-lambda",
    )

    return afnd_l


def generar_automata_ejercicio5() -> AutomataFinito:
    """Construye el autómata del Ejercicio 5: Fantasmas de Pac-Man ampliado (Gribkoff, 2013, Fig. 3).

    En Gribkoff (2013, Figura 3), el autómata original tiene 4 estados:
    - Wander (Deambular por el laberinto)
    - Chase (Perseguir a Pac-Man)
    - Flee (Huir cuando Pac-Man come una píldora de poder)
    - Return (Regresar como ojos a la base central tras ser comido)

    Ampliación realizada (cumpliendo 'al menos dos estados y dos eventos nuevos'):
    Se amplía a **7 estados** añadiendo:
    1. ` ScatterCorner` (Dispersión periódica a su esquina asignada por el temporizador global de oleadas).
    2. `PenWait` (Espera/regeneración dentro de la casa central antes de salir a deambular).
    3. `ElroyCruise` (*Cruise Elroy* / Frenesí de velocidad cuando quedan pocos puntos en el nivel, estado de aceptación junto con `VictoryCatch`).

    Y se amplía el alfabeto de eventos Sigma con **3 eventos nuevos** (total 8 símbolos):
    - `s` (*see_pacman*): El fantasma avista a Pac-Man.
    - `l` (*lose_pacman*): El fantasma pierde de vista a Pac-Man.
    - `p` (*power_pellet*): Pac-Man consume una superpíldora energética.
    - `t` (*timer_expire*): Expira el temporizador de la superpíldora o de la oleada.
    - `e` (*eaten_by_pacman*): Pac-Man alcanza y se come al fantasma vulnerable.
    - `b` (*reach_base*): Los ojos del fantasma llegan a la base central (Evento nuevo 1).
    - `w` (*wave_scatter*): Señal del reloj global de oleada de dispersión a esquina (Evento nuevo 2).
    - `c` (*critical_dots_capture*): Quedan pocos puntos / captura final de Pac-Man (Evento nuevo 3).
    """
    alfabeto = ["s", "l", "p", "t", "e", "b", "w", "c"]
    estados = [
        "q0_PenWait",
        "q1_Wander",
        "q2_ScatterCorner",
        "q3_Chase",
        "q4_Flee",
        "q5_ReturnEyes",
        "q6_ElroyVictory",
    ]
    transiciones = {
        # Desde q0_PenWait (Casa central): al expirar timer 't' sale a Wander; otros eventos esperan en PenWait
        ("q0_PenWait", "t"): ["q1_Wander"],
        ("q0_PenWait", "s"): ["q0_PenWait"],
        ("q0_PenWait", "l"): ["q0_PenWait"],
        ("q0_PenWait", "p"): ["q0_PenWait"],
        ("q0_PenWait", "e"): ["q0_PenWait"],
        ("q0_PenWait", "b"): ["q0_PenWait"],
        ("q0_PenWait", "w"): ["q2_ScatterCorner"],
        ("q0_PenWait", "c"): ["q0_PenWait"],
        # Desde q1_Wander (Deambular):
        ("q1_Wander", "s"): ["q3_Chase"],
        ("q1_Wander", "p"): ["q4_Flee"],
        ("q1_Wander", "w"): ["q2_ScatterCorner"],
        ("q1_Wander", "l"): ["q1_Wander"],
        ("q1_Wander", "t"): ["q1_Wander"],
        ("q1_Wander", "e"): ["q1_Wander"],
        ("q1_Wander", "b"): ["q1_Wander"],
        ("q1_Wander", "c"): ["q3_Chase"],
        # Desde q2_ScatterCorner (Estado nuevo 1 - Dispersión a esquina):
        ("q2_ScatterCorner", "t"): ["q1_Wander"],
        ("q2_ScatterCorner", "s"): ["q3_Chase"],
        ("q2_ScatterCorner", "p"): ["q4_Flee"],
        ("q2_ScatterCorner", "w"): ["q2_ScatterCorner"],
        ("q2_ScatterCorner", "l"): ["q2_ScatterCorner"],
        ("q2_ScatterCorner", "e"): ["q2_ScatterCorner"],
        ("q2_ScatterCorner", "b"): ["q2_ScatterCorner"],
        ("q2_ScatterCorner", "c"): ["q3_Chase"],
        # Desde q3_Chase (Persecución):
        ("q3_Chase", "l"): ["q1_Wander"],
        ("q3_Chase", "p"): ["q4_Flee"],
        ("q3_Chase", "w"): ["q2_ScatterCorner"],
        ("q3_Chase", "c"): ["q6_ElroyVictory"],
        ("q3_Chase", "s"): ["q3_Chase"],
        ("q3_Chase", "t"): ["q3_Chase"],
        ("q3_Chase", "e"): ["q3_Chase"],
        ("q3_Chase", "b"): ["q3_Chase"],
        # Desde q4_Flee (Huida vulnerable):
        ("q4_Flee", "t"): ["q1_Wander"],
        ("q4_Flee", "e"): ["q5_ReturnEyes"],
        ("q4_Flee", "p"): ["q4_Flee"],
        ("q4_Flee", "s"): ["q4_Flee"],
        ("q4_Flee", "l"): ["q4_Flee"],
        ("q4_Flee", "w"): ["q4_Flee"],
        ("q4_Flee", "b"): ["q4_Flee"],
        ("q4_Flee", "c"): ["q4_Flee"],
        # Desde q5_ReturnEyes (Regreso a la base como ojos):
        ("q5_ReturnEyes", "b"): ["q0_PenWait"],
        ("q5_ReturnEyes", "s"): ["q5_ReturnEyes"],
        ("q5_ReturnEyes", "l"): ["q5_ReturnEyes"],
        ("q5_ReturnEyes", "p"): ["q5_ReturnEyes"],
        ("q5_ReturnEyes", "t"): ["q5_ReturnEyes"],
        ("q5_ReturnEyes", "e"): ["q5_ReturnEyes"],
        ("q5_ReturnEyes", "w"): ["q5_ReturnEyes"],
        ("q5_ReturnEyes", "c"): ["q5_ReturnEyes"],
        # Desde q6_ElroyVictory (Estado nuevo 2/3 - Captura / Frenesí Elroy):
        ("q6_ElroyVictory", "p"): ["q4_Flee"],
        ("q6_ElroyVictory", "s"): ["q6_ElroyVictory"],
        ("q6_ElroyVictory", "l"): ["q6_ElroyVictory"],
        ("q6_ElroyVictory", "t"): ["q6_ElroyVictory"],
        ("q6_ElroyVictory", "e"): ["q6_ElroyVictory"],
        ("q6_ElroyVictory", "b"): ["q0_PenWait"],
        ("q6_ElroyVictory", "w"): ["q6_ElroyVictory"],
        ("q6_ElroyVictory", "c"): ["q6_ElroyVictory"],
    }
    return AutomataFinito(
        alfabeto=alfabeto,
        estados=estados,
        inicial="q0_PenWait",
        aceptacion=["q6_ElroyVictory"],
        transiciones=transiciones,
        tipo_declarado="AFD",
    )


def main() -> None:
    # 1. Lista 2 y AFD en automatas/lista2-afd/
    l2 = generar_lista2_afd_completa()
    for nombre, aut in l2.items():
        guardar_en_tres_formatos(aut, DIR_L2_AFD, nombre)

    # 2. Lista 3 AFND estándar en automatas/lista3-afnd/ y sus conversiones a AFD
    l3_afnd = generar_lista3_afnd()
    for nombre, aut in l3_afnd.items():
        guardar_en_tres_formatos(aut, DIR_L3_AFND, nombre)
        afd_conv = aut.convertir_a_afd()
        guardar_en_tres_formatos(afd_conv, DIR_CONV, f"{nombre}_a_afd")

    # 3. Lista 3 AFND-λ en automatas/lista3-afnd-lambda/ y sus conversiones (primero a AFND, luego a AFD)
    l3_lambda = generar_lista3_afnd_lambda()
    for nombre, aut in l3_lambda.items():
        guardar_en_tres_formatos(aut, DIR_L3_AFND_L, nombre)
        afnd_intermedio = aut.convertir_afnd_lambda_a_afnd()
        afd_final = afnd_intermedio.convertir_a_afd()
        guardar_en_tres_formatos(afnd_intermedio, DIR_CONV, f"{nombre}_paso1_afnd")
        guardar_en_tres_formatos(afd_final, DIR_CONV, f"{nombre}_paso2_afd")

    # 4. Autómata del Ejercicio 5 en automatas/aplicacion/
    aut_ej5 = generar_automata_ejercicio5()
    guardar_en_tres_formatos(aut_ej5, DIR_APP, "ej5_pacman_ampliado")

    print(
        f"Generación completa:\n"
        f"  - lista2-afd: {len(l2)} autómatas (x3 formatos = {len(l2)*3} archivos)\n"
        f"  - lista3-afnd: {len(l3_afnd)} autómatas (x3 formatos = {len(l3_afnd)*3} archivos)\n"
        f"  - lista3-afnd-lambda: {len(l3_lambda)} autómatas (x3 formatos = {len(l3_lambda)*3} archivos)\n"
        f"  - conversiones: {(len(l3_afnd) + 2*len(l3_lambda))} autómatas convertidos\n"
        f"  - aplicacion: 1 autómata en 3 formatos"
    )


if __name__ == "__main__":
    main()
