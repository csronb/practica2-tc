"""Suite de pruebas automatizadas con pytest para la Práctica 2 (y reutilización de Práctica 1).

Cubre:
1. Pruebas heredadas de la Práctica 1 (`lenguajes.py`: cadena vacía, |Σ|=1, longitud 1,
   Σ* vs Σ+ en n=0, y rechazo del límite de 200,000 cadenas).
2. La exportación y la importación de un mismo autómata en los tres formatos (`.jff`,
   `.json` y `.xml`), comprobando que ambas operaciones son inversas (incluyendo el
   ejemplo canónico del Anexo 3 con transición λ).
3. La aceptación y el rechazo de cadenas en un AFD.
4. La aceptación de una cadena en un AFND-λ cuyo reconocimiento requiera la λ-clausura.
5. La conversión de AFND-λ -> AFND estándar -> AFD equivalente, comprobando que
   reconocen exactamente el mismo lenguaje, y el autómata de aplicación del Ejercicio 5.
"""

from __future__ import annotations

from pathlib import Path
import pytest

from automata import AutomataFinito
from formatos import (
    cargar_automata,
    exportar_jff_texto,
    exportar_json_texto,
    exportar_xml_texto,
    guardar_en_tres_formatos,
    importar_jff_texto,
    importar_json_texto,
    importar_xml_texto,
)
from lenguajes import (
    LIMITE_CADENAS,
    cerradura_kleene,
    cerradura_positiva,
    contar_cadenas_cerradura,
    formatear_cadena,
    prefijos,
    subcadenas,
    sufijos,
)


# =============================================================================
# 1. PRUEBAS REUTILIZADAS DE LA PRÁCTICA 1 (lenguajes.py)
# =============================================================================

def test_p1_cadena_vacia():
    assert prefijos("") == [""]
    assert sufijos("") == [""]
    assert subcadenas("") == [""]
    assert formatear_cadena("") == "λ"


def test_p1_prefijos_sufijos_longitud_1():
    assert prefijos("a") == ["", "a"]
    assert sufijos("a") == ["", "a"]
    assert subcadenas("a") == ["", "a"]


def test_p1_diferencia_kleene_positiva_longitud_cero():
    assert cerradura_kleene(["0", "1"], 0) == [""]
    assert cerradura_positiva(["0", "1"], 0) == []


def test_p1_alfabeto_un_solo_simbolo():
    assert cerradura_kleene(["a"], 3) == ["", "a", "aa", "aaa"]
    assert cerradura_positiva(["a"], 3) == ["a", "aa", "aaa"]


def test_p1_rechazo_limite_200k():
    alfabeto_10 = [str(i) for i in range(10)]
    with pytest.raises(ValueError, match="Límite excedido"):
        cerradura_kleene(alfabeto_10, 6)
    assert contar_cadenas_cerradura(10, 5, incluir_vacia=True) == 111_111 <= LIMITE_CADENAS


# =============================================================================
# 2. PRUEBAS DE EXPORTACIÓN E IMPORTACIÓN INVERSA (.jff, .json, .xml)
# =============================================================================

def crear_automata_anexo3() -> AutomataFinito:
    """Crea el AFND-λ de ejemplo del Anexo 3 sobre {a, b}."""
    return AutomataFinito(
        alfabeto=["a", "b"],
        estados=["q0", "q1"],
        inicial="q0",
        aceptacion=["q1"],
        transiciones={
            ("q0", "a"): ["q1"],
            ("q0", "b"): ["q0"],
            ("q0", ""): ["q1"],
        },
        tipo_declarado="AFND-lambda",
    )


def test_exportacion_importacion_inversa_en_memoria():
    """Comprueba que exportar e importar en .jff, .json y .xml son operaciones inversas."""
    original = crear_automata_anexo3()

    # 1. Formato .jff
    txt_jff = exportar_jff_texto(original)
    rec_jff = importar_jff_texto(txt_jff)
    assert original.equivalentes_estructuralmente(rec_jff)
    assert rec_jff.tipo == "AFND-lambda"

    # 2. Formato .json
    txt_json = exportar_json_texto(original)
    rec_json = importar_json_texto(txt_json)
    assert original.equivalentes_estructuralmente(rec_json)
    assert rec_json.tipo == "AFND-lambda"

    # 3. Formato .xml
    txt_xml = exportar_xml_texto(original)
    rec_xml = importar_xml_texto(txt_xml)
    assert original.equivalentes_estructuralmente(rec_xml)
    assert rec_xml.tipo == "AFND-lambda"


def test_exportacion_importacion_inversa_en_archivos(tmp_path: Path):
    """Comprueba la lectura y escritura en disco de .jff, .json y .xml."""
    aut = AutomataFinito(
        alfabeto=["0", "1"],
        estados=["A", "B", "C"],
        inicial="A",
        aceptacion=["C"],
        transiciones={
            ("A", "0"): ["A", "B"],
            ("A", "1"): ["A"],
            ("B", "1"): ["C"],
        },
        tipo_declarado="AFND",
    )
    r_jff, r_json, r_xml = guardar_en_tres_formatos(aut, tmp_path, "prueba_afnd")

    c_jff = cargar_automata(r_jff)
    c_json = cargar_automata(r_json)
    c_xml = cargar_automata(r_xml)

    assert aut.equivalentes_estructuralmente(c_jff)
    assert aut.equivalentes_estructuralmente(c_json)
    assert aut.equivalentes_estructuralmente(c_xml)


# =============================================================================
# 3. ACEPTACIÓN Y RECHAZO EN UN AFD
# =============================================================================

def test_aceptacion_y_rechazo_en_afd():
    """Verifica aceptación y rechazo en un AFD que reconoce múltiplos binarios de 3."""
    afd = AutomataFinito(
        alfabeto=["0", "1"],
        estados=["q0", "q1", "q2"],
        inicial="q0",
        aceptacion=["q0"],
        transiciones={
            ("q0", "0"): ["q0"],
            ("q0", "1"): ["q1"],
            ("q1", "0"): ["q2"],
            ("q1", "1"): ["q0"],
            ("q2", "0"): ["q1"],
            ("q2", "1"): ["q2"],
        },
        tipo_declarado="AFD",
    )
    assert afd.es_determinista
    assert afd.tipo == "AFD"

    # Cadenas válidas: λ (0), 0 (0), 11 (3), 110 (6), 1001 (9), 1100 (12)
    for w_valida in ["", "0", "11", "110", "1001", "1100"]:
        res = afd.simular(w_valida)
        assert res.aceptada, f"Debió aceptar '{w_valida}'"

    # Cadenas inválidas: 1 (1), 10 (2), 100 (4), 101 (5), 111 (7)
    for w_invalida in ["1", "10", "100", "101", "111"]:
        res = afd.simular(w_invalida)
        assert not res.aceptada, f"Debió rechazar '{w_invalida}'"


# =============================================================================
# 4. ACEPTACIÓN EN AFND-λ QUE REQUIERE LA λ-CLAUSURA
# =============================================================================

def test_afnd_lambda_requiere_lambda_clausura():
    """Verifica el reconocimiento de cadenas que dependen directamente de la λ-clausura."""
    # AFND-λ para a* b* c* usando puentes λ: q0 --λ--> q1 --λ--> q2 (final)
    afnd_l = AutomataFinito(
        alfabeto=["a", "b", "c"],
        estados=["q0", "q1", "q2"],
        inicial="q0",
        aceptacion=["q2"],
        transiciones={
            ("q0", "a"): ["q0"],
            ("q0", ""): ["q1"],
            ("q1", "b"): ["q1"],
            ("q1", ""): ["q2"],
            ("q2", "c"): ["q2"],
        },
        tipo_declarado="AFND-lambda",
    )
    assert afnd_l.tiene_transiciones_lambda
    assert afnd_l.lambda_clausura_estado("q0") == ["q0", "q1", "q2"]
    assert afnd_l.lambda_clausura_estado("q1") == ["q1", "q2"]
    assert afnd_l.lambda_clausura_estado("q2") == ["q2"]

    # La cadena vacía "" y la cadena "ac" requieren cruzar transiciones λ sin consumir 'b'
    assert afnd_l.acepta("")
    assert afnd_l.acepta("a")
    assert afnd_l.acepta("c")
    assert afnd_l.acepta("ac")
    assert afnd_l.acepta("aabbc")

    # Cadenas fuera del orden a*b*c* deben ser rechazadas
    assert not afnd_l.acepta("ba")
    assert not afnd_l.acepta("ca")
    assert not afnd_l.acepta("cb")

    # Verificar que la conversión a AFND estándar y a AFD preserva el lenguaje
    afnd_std = afnd_l.convertir_afnd_lambda_a_afnd()
    afd_eq = afnd_std.convertir_a_afd()
    assert not afnd_std.tiene_transiciones_lambda
    assert afd_eq.es_determinista

    for muestra in ["", "a", "b", "c", "ac", "aabbc", "ba", "ca", "cb", "abcba"]:
        assert afnd_l.acepta(muestra) == afnd_std.acepta(muestra) == afd_eq.acepta(muestra)


# =============================================================================
# 5. VALIDACIÓN DEL AUTÓMATA DE APLICACIÓN DEL EJERCICIO 5 (PAC-MAN AMPLIADO)
# =============================================================================

def test_automata_ejercicio5_pacman_diez_cadenas():
    """Carga el archivo .jff del Ejercicio 5 y valida las 12 cadenas de prueba del reporte."""
    ruta_jff = Path(__file__).resolve().parent.parent / "automatas" / "aplicacion" / "ej5_pacman_ampliado.jff"
    aut = cargar_automata(ruta_jff)
    assert aut.tipo == "AFD"
    assert len(aut.estados) == 7
    assert len(aut.alfabeto) == 8

    # 6 cadenas válidas que culminan en q6_ElroyVictory
    cadenas_validas = ["tsc", "wsc", "tslsc", "tsptsc", "tspebtsc", "twtsc"]
    for w in cadenas_validas:
        assert aut.acepta(w), f"La cadena válida '{w}' debió ser aceptada"

    # 6 cadenas inválidas que no terminan en q6_ElroyVictory
    cadenas_invalidas = ["", "ts", "tspe", "tspeb", "tscp", "sc"]
    for w in cadenas_invalidas:
        assert not aut.acepta(w), f"La cadena inválida '{w}' debió ser rechazada"

