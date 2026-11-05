"""Suite de pruebas automatizadas con pytest para la Práctica 3 (Ejercicio 2.6).

Verifica para cada caso de prueba de la Lista 3 almacenado en `automatas/practica3/casos-de-prueba/`:
- Que el autómata original (AFN-λ, AFN o AFD), el AFN sin transiciones λ, el AFD por
  construcción de subconjuntos alcanzables y el AFD mínimo acepten exactamente las mismas
  cadenas sobre todas las palabras del alfabeto Σ de longitud 0 a MAX_LEN (5 para |Σ|=2,
  4 para |Σ|=3), justificando que esta cota supera el diámetro de alcanzabilidad y la
  cota de distinguibilidad (|Q_min| - 1) de todos los autómatas evaluados.
- Que el número de estados del AFD mínimo sea menor o igual que el del AFD obtenido por
  construcción de subconjuntos (|Q_{AFD_min}| <= |Q_{AFD}|).
- Las respuestas exactas a los incisos de los ejercicios 191-194, 196-200, 151-157 y 260-263.
- La equivalencia de los 5 AFD del Ejercicio 1 con sus expresiones regulares (tanto la
  obtenida por eliminación de estados en JFLAP como la simplificada algebraicamente).
- La validación de cadenas por lotes desde archivo `.txt` y generación de reporte (Ejercicio 2.5).
"""

from __future__ import annotations

from itertools import product
from pathlib import Path
import re
import pytest

from automata import AutomataFinito
from expresiones import compilar, tres_metodos
from formatos import cargar_automata

RAIZ = Path(__file__).resolve().parent.parent
DIR_CASOS = RAIZ / "automatas" / "practica3" / "casos-de-prueba"
DIR_AFD_ER = RAIZ / "automatas" / "practica3" / "afd-a-er"


def generar_todas_las_cadenas(alfabeto: list[str], max_len: int) -> list[str]:
    """Genera todas las cadenas en Σ^{<= max_len} en orden longitud-lexicográfico."""
    cadenas: list[str] = []
    for k in range(max_len + 1):
        for tupla in product(alfabeto, repeat=k):
            cadenas.append("".join(tupla))
    return cadenas


def er_jflap_a_regex_python(expr: str) -> re.Pattern[str]:
    """Convierte una expresión regular con notación del curso ('+' para unión, 'λ' para vacía) a regex de Python."""
    limpia = expr.replace(" ", "").replace("+", "|").replace("λ", "")
    return re.compile(f"^({limpia})$")


# =============================================================================
# 1. EQUIVALENCIA EXHAUSTIVA DE LA CADENA DE TRANSFORMACIONES (EJERCICIO 2.6)
# =============================================================================

ARCHIVOS_CASOS = sorted(DIR_CASOS.glob("*.jff"))


@pytest.mark.parametrize("ruta_jff", ARCHIVOS_CASOS, ids=lambda p: p.stem)
def test_cadena_transformaciones_y_minimizacion(ruta_jff: Path):
    """Comprueba que M_orig, M_sin_λ, M_subconjuntos y M_min aceptan las mismas cadenas y |Q_min| <= |Q_afd|."""
    m_orig = cargar_automata(ruta_jff)
    res_sin_lambda = m_orig.eliminar_transiciones_lambda_detallado()
    m_sin_lambda = res_sin_lambda.automata_sin_lambda

    res_sub = m_orig.construccion_subconjuntos_detallada()
    m_afd = res_sub.afd

    res_min = m_afd.minimizar_afd_detallado()
    m_min = res_min.afd_minimo

    # Propiedades estructurales garantizadas por cada transformación
    assert not m_sin_lambda.tiene_transiciones_lambda
    assert m_afd.es_determinista
    assert m_min.es_determinista
    assert len(m_min.estados) <= len(m_afd.estados), (
        f"El AFD mínimo ({len(m_min.estados)}) no puede tener más estados que el AFD ({len(m_afd.estados)})"
    )

    # Si el autómata original ya era un AFD, también comparamos minimizar directamente m_orig
    if m_orig.es_determinista:
        res_min_dir = m_orig.minimizar_afd_detallado()
        assert len(res_min_dir.afd_minimo.estados) <= len(m_orig.estados)
        assert m_orig.son_afd_equivalentes(res_min_dir.afd_minimo).equivalentes

    # Equivalencia formal mediante isomorfismo de AFD mínimos (Ejercicio 2.4)
    eq_check = m_afd.son_afd_equivalentes(m_min)
    assert eq_check.equivalentes, eq_check.justificacion

    # Longitud máxima justificada: k=5 para alfabetos binarios (63 cadenas) y k=4 para ternarios (121 cadenas)
    max_len = 5 if len(m_orig.alfabeto) <= 2 else 4
    for w in generar_todas_las_cadenas(m_orig.alfabeto, max_len):
        v_orig = m_orig.acepta(w)
        v_sin_l = m_sin_lambda.acepta(w)
        v_afd = m_afd.acepta(w)
        v_min = m_min.acepta(w)
        assert v_orig == v_sin_l == v_afd == v_min, (
            f"Discrepancia en {ruta_jff.name} para w='{w}': "
            f"orig={v_orig}, sin_λ={v_sin_l}, afd={v_afd}, min={v_min}"
        )


# =============================================================================
# 2. PRUEBAS DE LOS REACTIVOS 196-200 (CLAUSURA λ Y SIMULACIÓN DIRECTA 2.1 / 2.2)
# =============================================================================

def test_reactivos_196_a_200_clausuras_y_delta_extendida():
    """Verifica todos los incisos a)-e) de los ejercicios 196 a 200 de la Lista 3."""
    # Ejercicio 196
    m196 = cargar_automata(DIR_CASOS / "ej196_afnd_lambda.jff")
    assert m196.lambda_clausura_estado("A") == ["A", "B"]
    assert m196.lambda_clausura_estado("B") == ["B"]
    assert m196.lambda_clausura(["A", "B"]) == ["A", "B"]
    assert m196.destinos("A", "0") == ["A"]
    assert m196.delta_extendida("A", "110") == []
    # Verificar traza paso a paso con antes y después de λ-clausura en cadena aceptada "01"
    sim196 = m196.simular_directo_afnd_lambda("01")
    assert sim196.aceptada
    assert sim196.pasos[0].estados_antes_de_lambda == ["A"]
    assert sim196.pasos[0].estados_despues_de_lambda == ["A", "B"]
    assert sim196.pasos[1].estados_antes_de_lambda == ["A", "B"]
    assert sim196.pasos[1].estados_despues_de_lambda == ["A", "B"]
    assert sim196.pasos[2].estados_antes_de_lambda == ["C"]
    assert sim196.pasos[2].estados_despues_de_lambda == ["C"]

    # Ejercicio 197
    m197 = cargar_automata(DIR_CASOS / "ej197_afnd_lambda.jff")
    assert set(m197.lambda_clausura_estado("A")) == {"A", "B", "C", "D"}
    assert set(m197.lambda_clausura(["B", "D"])) == {"B", "D"}
    assert set(m197.lambda_clausura(["A", "B", "C"])) == {"A", "B", "C", "D"}
    assert set(m197.destinos("A", "0")) == {"B", "D"}
    assert set(m197.delta_extendida("A", "010")) == {"A", "B", "C", "D"}
    # Al eliminar λ, como D ∈ Cl_λ(A), Cl_λ(B), Cl_λ(C), todos los estados pasan a ser de aceptación
    elim197 = m197.eliminar_transiciones_lambda_detallado()
    assert set(elim197.automata_sin_lambda.aceptacion) == {"A", "B", "C", "D"}
    assert len(elim197.nuevos_estados_aceptacion) == 3

    # Ejercicio 198
    m198 = cargar_automata(DIR_CASOS / "ej198_afnd_lambda.jff")
    assert set(m198.lambda_clausura_estado("A")) == {"A", "B", "C"}
    assert set(m198.lambda_clausura(["C", "D"])) == {"B", "C", "D"}
    assert set(m198.lambda_clausura(["A", "C", "D"])) == {"A", "B", "C", "D"}
    assert set(m198.delta_extendida("B", "0111")) == {"B", "C", "D"}

    # Ejercicio 199
    m199 = cargar_automata(DIR_CASOS / "ej199_afnd_lambda.jff")
    assert set(m199.lambda_clausura_estado("A")) == {"A", "B", "C", "E"}
    assert set(m199.lambda_clausura_estado("C")) == {"C", "E"}
    assert set(m199.delta_extendida("A", "011")) == {"D"}

    # Ejercicio 200
    m200 = cargar_automata(DIR_CASOS / "ej200_afnd_lambda.jff")
    assert set(m200.lambda_clausura_estado("A")) == {"A", "B"}
    assert set(m200.lambda_clausura(["C", "D"])) == {"C", "D", "E", "F"}
    assert set(m200.delta_extendida("C", "1011")) == {"A", "B", "C", "D", "E", "F"}


# =============================================================================
# 3. PRUEBAS DE LOS REACTIVOS 191-194 Y 260-263 (SUBCONJUNTOS 2.3)
# =============================================================================

def test_reactivos_191_a_194_subconjuntos_y_delta():
    """Verifica δ̂(Z, w) en el AFN y δ̂_D(Z, w) en el AFD de subconjuntos para 191-194."""
    # Ejercicio 192
    m192 = cargar_automata(DIR_CASOS / "ej192_subconjuntos.jff")
    assert set(m192.delta_extendida(["A"], "0111")) == set()
    assert set(m192.delta_extendida(["B", "C"], "010111")) == set()
    sub192 = m192.construccion_subconjuntos_detallada()
    assert "{B,C}" in sub192.afd.aceptacion
    assert "C" in sub192.subconjuntos_aceptacion_justificacion["{B,C}"]

    # Ejercicio 193
    m193 = cargar_automata(DIR_CASOS / "ej193_subconjuntos.jff")
    assert set(m193.delta_extendida(["A"], "01101")) == set()
    assert set(m193.delta_extendida(["A", "B"], "1101")) == {"A", "B", "C", "D"}
    assert set(m193.delta_extendida(["C"], "1101")) == {"A", "B", "C", "D"}

    # Ejercicio 194
    m194 = cargar_automata(DIR_CASOS / "ej194_subconjuntos.jff")
    assert set(m194.delta_extendida(["A", "C"], "0121")) == {"A", "C"}
    assert set(m194.delta_extendida(["B"], "20111")) == set()
    assert set(m194.delta_extendida(["C"], "02112")) == {"A"}
    assert set(m194.delta_extendida(["A", "B"], "0121")) == {"A", "C"}

    # Ejercicio 191 / 195
    m191 = cargar_automata(DIR_CASOS / "ej191_subconjuntos.jff")
    assert set(m191.delta_extendida(["A"], "10010")) == {"A", "B"}
    assert set(m191.delta_extendida(["A", "D"], "0110")) == {"A", "B", "D"}
    assert set(m191.delta_extendida(["B", "E"], "0100")) == {"A", "B", "D"}
    assert set(m191.delta_extendida(["B", "C", "D"], "10100")) == {"A", "B", "D", "E"}


# =============================================================================
# 4. PRUEBAS DE LOS REACTIVOS 151-157 (MINIMIZACIÓN E INACCESIBLES 2.4)
# =============================================================================

def test_reactivos_151_a_157_estados_inaccesibles_y_particiones():
    """Verifica la detección de estados inaccesibles y clases de equivalencia en 151-157."""
    # 151: todos los 10 estados son accesibles, se reducen a 5 clases: {A,D,H}, {B,G}, {I,J}, {C,F}, {E}
    m151 = cargar_automata(DIR_CASOS / "ej151_minimizacion.jff")
    r151 = m151.minimizar_afd_detallado()
    assert r151.estados_inaccesibles_eliminados == []
    assert len(r151.afd_minimo.estados) == 5

    # 152: D y F son equivalentes (además C es equivalente si aplica, verificamos reducción estricta)
    m152 = cargar_automata(DIR_CASOS / "ej152_minimizacion.jff")
    r152 = m152.minimizar_afd_detallado()
    assert len(r152.afd_minimo.estados) < len(m152.estados)
    assert ("D", "F") in r152.pares_equivalentes

    # 153: C y E son equivalentes -> se reduce de 7 estados a 6 clases: {A}, {B}, {C,E}, {D}, {F}, {G}
    m153 = cargar_automata(DIR_CASOS / "ej153_minimizacion.jff")
    r153 = m153.minimizar_afd_detallado()
    assert len(r153.afd_minimo.estados) == 6
    assert ("C", "E") in r153.pares_equivalentes

    # 154: J es inaccesible desde A, y B≡I, C≡F, G≡H -> se reduce de 11 estados a 7 clases
    m154 = cargar_automata(DIR_CASOS / "ej154_minimizacion.jff")
    r154 = m154.minimizar_afd_detallado()
    assert r154.estados_inaccesibles_eliminados == ["J"]
    assert len(r154.afd_minimo.estados) == 7

    # 155: I y L son inaccesibles desde A
    m155 = cargar_automata(DIR_CASOS / "ej155_minimizacion.jff")
    r155 = m155.minimizar_afd_detallado()
    assert set(r155.estados_inaccesibles_eliminados) == {"I", "L"}

    # 156: D es inaccesible desde A, y A≡C -> se reduce a 3 estados
    m156 = cargar_automata(DIR_CASOS / "ej156_minimizacion.jff")
    r156 = m156.minimizar_afd_detallado()
    assert r156.estados_inaccesibles_eliminados == ["D"]
    assert len(r156.afd_minimo.estados) == 3

    # 157: B≡C≡D -> se reduce de 6 estados a 4 clases: {A}, {B,C,D}, {E}, {F}
    m157 = cargar_automata(DIR_CASOS / "ej157_minimizacion.jff")
    r157 = m157.minimizar_afd_detallado()
    assert len(r157.afd_minimo.estados) == 4


def test_equivalencia_dos_afd_positiva_y_negativa():
    """Verifica que son_afd_equivalentes detecta AFD equivalentes y distingue AFD no equivalentes."""
    m153 = cargar_automata(DIR_CASOS / "ej153_minimizacion.jff")
    m153_min = m153.minimizar_afd()
    res_eq = m153.son_afd_equivalentes(m153_min)
    assert res_eq.equivalentes
    assert res_eq.testigo_diferencia is None

    m156 = cargar_automata(DIR_CASOS / "ej156_minimizacion.jff")
    res_neq = m153.son_afd_equivalentes(m156)
    assert not res_neq.equivalentes
    assert res_neq.testigo_diferencia is not None
    # El testigo encontrado debe ser aceptado por uno y rechazado por el otro
    w = res_neq.testigo_diferencia
    assert m153.acepta(w) != m156.acepta(w)


# =============================================================================
# 5. VERIFICACIÓN DE LOS 5 AFD A EXPRESIÓN REGULAR (EJERCICIO 1)
# =============================================================================

def test_cinco_afd_equivalentes_a_sus_expresiones_regulares():
    """Verifica que los 5 AFD en automatas/practica3/afd-a-er/ coinciden con sus ER en Σ^{<=6}."""
    archivos_jff = sorted(DIR_AFD_ER.glob("*.jff"))
    assert len(archivos_jff) == 5

    for ruta_jff in archivos_jff:
        aut = cargar_automata(ruta_jff)
        ruta_er = ruta_jff.with_name(f"{ruta_jff.stem}_er.txt")
        lineas = dict(
            ln.split(": ", 1)
            for ln in ruta_er.read_text(encoding="utf-8").splitlines()
            if ": " in ln
        )
        pat_jflap = er_jflap_a_regex_python(lineas["ER_JFLAP"])
        pat_simp = er_jflap_a_regex_python(lineas["ER_SIMPLIFICADA"])

        max_k = 6 if len(aut.alfabeto) <= 2 else 5
        for w in generar_todas_las_cadenas(aut.alfabeto, max_k):
            en_aut = aut.acepta(w)
            en_jflap = bool(pat_jflap.match(w))
            en_simp = bool(pat_simp.match(w))
            assert en_aut == en_jflap == en_simp, (
                f"Fallo en {ruta_jff.name} con w='{w}': "
                f"AFD={en_aut}, ER_JFLAP={en_jflap}, ER_SIMP={en_simp}"
            )


def test_tres_metodos_conversion_afd_a_er():
    """Verifica que Eliminación de estados, R_ij^(k) y Lema de Arden producen ER equivalentes al AFD."""
    for ruta_jff in sorted(DIR_AFD_ER.glob("*.jff")):
        aut = cargar_automata(ruta_jff)
        resultados = tres_metodos(aut)
        assert len(resultados) == 3
        patrones = [compilar(r.expresion) for r in resultados]
        max_k = 5 if len(aut.alfabeto) <= 2 else 4
        for w in generar_todas_las_cadenas(aut.alfabeto, max_k):
            esperado = aut.acepta(w)
            for r, pat in zip(resultados, patrones):
                assert bool(pat.match(w)) == esperado, (
                    f"Discrepancia en {ruta_jff.name} con método {r.metodo} ({r.texto}) para w='{w}'"
                )


# =============================================================================
# 6. INTEGRACIÓN CON EL MATERIAL DEL PROFESOR (ContenedorV1/extras/ejemplos)
# =============================================================================

def test_m1_par_de_ceros_del_profesor_contra_la_definicion():
    """Lee el M₁ de la sección 1.2.3 (m1_par_de_ceros.jff del material del curso) con `formatos.py`.

    Siguiendo el mismo criterio de `extras/ejemplos/test_afd.py`, compara las 2047 cadenas de
    {0,1}* de longitud 0 a 10 contra la definición del lenguaje, y además comprueba que toda la
    cadena de transformaciones de la Práctica 3 conserva ese lenguaje y que M₁ ya es mínimo.
    """
    m1 = cargar_automata(RAIZ / "extras" / "ejemplos" / "m1_par_de_ceros.jff")
    assert set(m1.estados) == {"s1", "s2"}
    assert m1.inicial == "s1"
    assert m1.aceptacion == ["s1"]

    afd = m1.construccion_subconjuntos_detallada().afd
    minimo = m1.minimizar_afd_detallado().afd_minimo
    assert len(minimo.estados) == 2  # M₁ ya es mínimo: s1 y s2 se distinguen con λ

    for n in range(11):
        for w in map("".join, product("01", repeat=n)):
            esperado = w.count("0") % 2 == 0
            assert m1.acepta(w) == afd.acepta(w) == minimo.acepta(w) == esperado, w


# =============================================================================
# 7. VALIDACIÓN POR LOTES DESDE ARCHIVO .TXT (EJERCICIO 2.5)
# =============================================================================

def test_validacion_archivo_cadenas_lote(tmp_path: Path):
    """Comprueba la lectura de un archivo .txt con una cadena por línea y la escritura del reporte."""
    m196 = cargar_automata(DIR_CASOS / "ej196_afnd_lambda.jff")
    archivo_in = DIR_CASOS / "lote_cadenas_prueba.txt"
    archivo_out = tmp_path / "reporte_lote.txt"

    resultados, texto_reporte = m196.validar_archivo_cadenas(archivo_in, archivo_out)
    assert archivo_out.exists()
    assert len(resultados) == 12
    assert "REPORTE DE VALIDACIÓN DE CADENAS POR LOTES" in texto_reporte

    for item in resultados:
        cad_real = "" if item.cadena_mostrada == "λ" else item.cadena_mostrada
        assert item.aceptada == m196.acepta(cad_real)
