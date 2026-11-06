"""Suite de pruebas automatizadas con pytest para la Práctica 4:
Uso de las Expresiones Regulares y Extensión de Software para Convertir Expresiones Regulares.

Cubre íntegramente los requisitos de verificación de los Ejercicios 2, 3 y 4:
1. Ejercicio 2 (De expresión regular a autómata):
   - Precedencia de operadores (* > concatenación > +), asociatividad y paréntesis.
   - Rechazo de expresiones mal formadas indicando la posición exacta del error (`ErrorSintaxisER`).
   - Construcción paso a paso del AFN-λ en forma estándar (Parte I del Teorema de Kleene / Thompson)
     y aplicación encadenada de eliminación de transiciones λ, construcción de subconjuntos y
     minimización de AFD.
   - Casos de prueba: Lista 3 (ejercicios 241 a 253) y Lista 4 (ejercicios 272, 273 y 278),
     incluyendo exportación e importación en formato `.jff`.
2. Ejercicio 3 (De autómata a expresión regular):
   - Verificación de determinismo al importar desde `.jff`, indicando qué estado y qué símbolo
     lo impiden cuando el autómata no es determinista.
   - Obtención de la expresión regular por eliminación de estados mostrando el GNFA tras cada
     estado eliminado.
   - Demostración formal de equivalencia con la expresión obtenida con JFLAP en la Práctica 3
     convirtiendo ambas expresiones en AFD mínimos con el Ejercicio 2 y comparándolos con la
     prueba de equivalencia de la Práctica 3 (`son_afd_equivalentes`).
   - Casos de prueba: Lista 3 (ejercicios 254 a 258 / cinco autómatas del Ejercicio 1 de la
     Práctica 3) y Lista 4 (ejercicios 276 y 277).
3. Ejercicio 4 (Aplicaciones: validadores y congruencia entre modelos):
   - Verificación de los cuatro validadores (`correo`, `telefono_nacional`, `url`, `fecha`),
     conteo de estados del AFD antes y después de minimizar, y exportación a `.jff`.
   - Congruencia entre modelos: para cada validador, comparación entre el autómata obtenido con
     el Ejercicio 2 y `re.fullmatch` sobre un conjunto de al menos 500 cadenas válidas e inválidas
     generadas mediante el procedimiento documentado en `validadores.py`.
"""

from __future__ import annotations

from itertools import product
from pathlib import Path
import re
import pytest

from automata import AutomataFinito
from expresiones import (
    CLASES_PREDEFINIDAS,
    ErrorSintaxisER,
    analizar_expresion,
    comparar_expresiones_por_afd_minimo,
    eliminacion_de_estados_detallada,
    er_a_afn_lambda_detallado,
    er_a_automata_completo,
)
from formatos import cargar_automata, guardar_automata
from validadores import (
    DECLARACION_CLASES_CURSO,
    ESPECIFICACIONES_VALIDADORES,
    generar_corpus_validador,
    obtener_validador,
    verificar_congruencia_validador,
)

RAIZ = Path(__file__).resolve().parent.parent
DIR_P4_EJ2 = RAIZ / "automatas" / "practica4" / "er-a-automata"
DIR_P4_EJ3 = RAIZ / "automatas" / "practica4" / "afd-a-er"
DIR_P4_EJ4 = RAIZ / "automatas" / "practica4" / "validadores"
DIR_P3_CASOS = RAIZ / "automatas" / "practica3" / "casos-de-prueba"


def generar_todas_las_cadenas(alfabeto: list[str], max_len: int) -> list[str]:
    """Genera todas las cadenas en Σ^{<= max_len} en orden longitud-lexicográfico."""
    cadenas: list[str] = []
    for k in range(max_len + 1):
        for tupla in product(alfabeto, repeat=k):
            cadenas.append("".join(tupla))
    return cadenas


# =============================================================================
# 1. EJERCICIO 2: ANALIZADOR SINTÁCTICO, PRECEDENCIA Y POSICIÓN DE ERRORES
# =============================================================================

def test_precedencia_operadores_y_parentesis():
    """Verifica que * > concatenación > + y que los paréntesis alteran el árbol correctamente."""
    # 'a + bc*' debe interpretarse como 'a + (b(c*))'
    n1 = analizar_expresion("a + bc*")
    assert n1.tipo == "union"
    assert n1.hijos[0].tipo == "simbolo" and n1.hijos[0].valor == "a"
    assert n1.hijos[1].tipo == "concat"
    assert n1.hijos[1].hijos[0].valor == "b"
    assert n1.hijos[1].hijos[1].tipo == "estrella"
    assert n1.hijos[1].hijos[1].hijos[0].valor == "c"

    # '(a + b)c*' tiene concatenación en la raíz
    n2 = analizar_expresion("(a + b)c*")
    assert n2.tipo == "concat"
    assert n2.hijos[0].tipo == "union"
    assert n2.hijos[1].tipo == "estrella"

    # Diferencia semántica entre 'ab*' y '(ab)*'
    r_ab_est = er_a_automata_completo("ab*", alfabeto=["a", "b"])
    r_par_ab_est = er_a_automata_completo("(ab)*", alfabeto=["a", "b"])
    assert r_ab_est.afd_minimo.acepta("abb") is True
    assert r_par_ab_est.afd_minimo.acepta("abb") is False
    assert r_par_ab_est.afd_minimo.acepta("abab") is True
    assert r_ab_est.afd_minimo.acepta("abab") is False


@pytest.mark.parametrize(
    "expresion_invalida,pos_esperada",
    [
        ("", 1),            # Expresión vacía
        ("+a", 1),          # '+' al inicio sin operando izquierdo
        ("a+b+", 4),        # '+' al final sin operando derecho
        ("a++b", 3),        # Dos operadores '+' consecutivos
        ("*a", 1),          # '*' al inicio sin operando previo
        ("a+*b", 3),        # '*' inmediatamente después de '+'
        ("(*a)", 2),        # '*' inmediatamente después de '('
        ("()", 2),          # Paréntesis vacíos
        ("((a+b)", 1),      # Paréntesis '(' en pos 1 sin cerrar
        ("a+b)", 4),        # Paréntesis ')' en pos 4 sin abrir
        ("a?b", 2),         # Metacaracter '?' ajeno a la notación del curso
    ],
)
def test_rechazo_expresiones_mal_formadas_con_posicion_exacta(expresion_invalida: str, pos_esperada: int):
    """Comprueba que analizar_expresion rechaza expresiones mal formadas indicando la posición exacta."""
    with pytest.raises(ErrorSintaxisER) as exc_info:
        analizar_expresion(expresion_invalida)
    err = exc_info.value
    assert err.posicion == pos_esperada, (
        f"Para '{expresion_invalida}' se esperaba posición {pos_esperada}, pero se reportó {err.posicion}: {err}"
    )
    assert f"posición {pos_esperada}" in str(err)


# =============================================================================
# 2. EJERCICIO 2: CASOS DE PRUEBA DE LA LISTA 3 (241 A 253)
# =============================================================================

CASOS_LISTA3_EJ2 = [
    ("241", "0 + 1"),
    ("242", "0* + 1"),
    ("243", "(0 + 1)*"),
    ("244", "0(0 + 1)"),
    ("245", "0(0 + 1)*"),
    ("246", "0*(0 + 1)"),
    ("247", "(01)* + 1*"),
    ("248", "(0* + 1)0"),
    ("249", "(0* + 1)0*"),
    ("250", "0*1* + 1*0"),
    ("251", "(0 + 1*)0 + 1*1"),
    ("252", "(0 + 1)*(00 + 11) + (00 + 11)(0 + 1)*"),
    ("253", "(0 + (11 + 00)*)(11 + 10 + 01)*(λ + 110)"),
]


@pytest.mark.parametrize("num_ej,expresion", CASOS_LISTA3_EJ2)
def test_lista3_ejercicios_241_a_253_er_a_automata(num_ej: str, expresion: str, tmp_path: Path):
    """Verifica para los ejercicios 241–253 de la Lista 3 la construcción paso a paso,
    la forma estándar de cada autómata parcial, la cadena AFN-λ -> AFN -> AFD -> AFD mínimo,
    la exportación a `.jff` y la coincidencia en Σ^{<=6}."""
    res = er_a_automata_completo(expresion, alfabeto=["0", "1"])

    # Verificar que se registraron los autómatas parciales paso a paso en forma estándar de Thompson
    assert len(res.kleene_uno.pasos) >= 1
    for paso in res.kleene_uno.pasos:
        ap = paso.automata_parcial
        assert ap.inicial == paso.estado_inicial
        assert ap.aceptacion == [paso.estado_final]
        assert paso.estado_inicial != paso.estado_final
        # En la forma estándar de Kleene I / Thompson, el estado final no tiene transiciones salientes
        for sym in list(ap.alfabeto) + [""]:
            assert ap.destinos(paso.estado_final, sym) == []

    # Verificar que el AFD mínimo no tiene más estados que el AFD por subconjuntos
    assert len(res.afd_minimo.estados) <= len(res.afd.estados)

    # Verificar exportación e importación a .jff
    ruta_jff = tmp_path / f"ej{num_ej}.jff"
    guardar_automata(res.afd_minimo, ruta_jff)
    reimportado = cargar_automata(ruta_jff)
    assert res.afd_minimo.equivalentes_estructuralmente(reimportado)

    # Verificar equivalencia en todas las cadenas de {0, 1}^{<= 6} (127 cadenas)
    patron = re.compile(res.kleene_uno.regex_python)
    for w in generar_todas_las_cadenas(["0", "1"], 6):
        esp = bool(patron.fullmatch(w))
        assert res.afn_lambda.acepta(w) == esp, f"Ej {num_ej} AFN-λ falló en w='{w}'"
        assert res.afn.acepta(w) == esp, f"Ej {num_ej} AFN falló en w='{w}'"
        assert res.afd.acepta(w) == esp, f"Ej {num_ej} AFD falló en w='{w}'"
        assert res.afd_minimo.acepta(w) == esp, f"Ej {num_ej} AFD_min falló en w='{w}'"


# =============================================================================
# 3. EJERCICIO 2: CASOS DE PRUEBA DE LA LISTA 4 (272, 273 Y 278)
# =============================================================================

@pytest.mark.parametrize(
    "inciso,expresion,estados_afn_lambda,pasos_esperados",
    [
        ("272a", "a + b*", 8, 4),
        ("272b", "(ab)*a", 8, 6),
        ("272c", "(a + b)*abb", 14, 10),
        ("272d", "a(ba)* + b", 12, 8),
        ("272e", "(a + λ)(b + ∅)", 12, 7),
    ],
)
def test_lista4_ejercicio_272_construccion_kleene_parte_i(
    inciso: str, expresion: str, estados_afn_lambda: int, pasos_esperados: int
):
    """Verifica los cinco incisos del ejercicio 272 de la Lista 4 (número de estados del AFN-λ,
    pasos parciales y equivalencia a lo largo de toda la tubería hasta el AFD mínimo)."""
    res = er_a_automata_completo(expresion, alfabeto=["a", "b"])
    assert len(res.afn_lambda.estados) == estados_afn_lambda
    assert len(res.kleene_uno.pasos) == pasos_esperados

    patron = re.compile(res.kleene_uno.regex_python)
    for w in generar_todas_las_cadenas(["a", "b"], 6):
        esp = bool(patron.fullmatch(w))
        assert res.afn_lambda.acepta(w) == esp
        assert res.afn.acepta(w) == esp
        assert res.afd.acepta(w) == esp
        assert res.afd_minimo.acepta(w) == esp


def test_lista4_ejercicio_273_validacion_con_clausuras_lambda():
    """Verifica el ejercicio 273 de la Lista 4 sobre los autómatas de 272(b) `(ab)*a`
    y 272(c) `(a + b)*abb` para las cadenas `aba`, `ab`, `babb` y `abab`."""
    res_272b = er_a_automata_completo("(ab)*a", alfabeto=["a", "b"])
    res_272c = er_a_automata_completo("(a + b)*abb", alfabeto=["a", "b"])

    esperados_272b = {"aba": True, "ab": False, "babb": False, "abab": False}
    esperados_272c = {"aba": False, "ab": False, "babb": True, "abab": False}

    for cad, esp in esperados_272b.items():
        sim_b = res_272b.afn_lambda.simular(cad)
        assert sim_b.aceptada is esp
        assert res_272b.afd_minimo.acepta(cad) is esp

    for cad, esp in esperados_272c.items():
        sim_c = res_272c.afn_lambda.simular(cad)
        assert sim_c.aceptada is esp
        assert res_272c.afd_minimo.acepta(cad) is esp


def test_lista4_ejercicio_278_ciclo_completo_kleene_ambas_direcciones():
    """Verifica los cuatro incisos del ejercicio 278 de la Lista 4 para `R = (a + b)*b`:
    (a) AFN-λ por Parte I de Kleene (10 estados),
    (b) Eliminación de transiciones λ a AFN (10 estados),
    (c) Construcción de subconjuntos a AFD (3 estados alcanzables) y minimización (2 estados),
    (d) Conversión del AFD mínimo de vuelta a expresión regular y prueba formal de equivalencia con `(a + b)*b`."""
    res = er_a_automata_completo("(a + b)*b", alfabeto=["a", "b"])
    assert len(res.afn_lambda.estados) == 10
    assert len(res.afn.estados) == 10
    assert len(res.afd.estados) == 3
    assert len(res.afd_minimo.estados) == 2

    # Inciso (d): Obtener ER desde el AFD mínimo y comprobar equivalencia formal con `(a + b)*b`
    res_gnfa = eliminacion_de_estados_detallada(res.afd_minimo)
    comp = comparar_expresiones_por_afd_minimo("(a + b)*b", res_gnfa.expresion_texto, alfabeto=["a", "b"])
    assert comp.equivalentes is True


# =============================================================================
# 4. EJERCICIO 3: VERIFICACIÓN DE DETERMINISMO, ELIMINACIÓN DE ESTADOS Y JFLAP
# =============================================================================

def test_verificacion_determinismo_detecta_estado_y_simbolo_exactos():
    """Comprueba que verificar_determinismo aprueba los AFD e indica qué estado y qué símbolo
    impiden el determinismo cuando se importa un AFN o un AFN-λ."""
    # Caso positivo: AFD determinista (ej276)
    afd_276 = cargar_automata(DIR_P4_EJ3 / "ej276_multiplo_3_a.jff")
    verif_ok = afd_276.verificar_determinismo()
    assert verif_ok.es_determinista is True
    assert verif_ok.violaciones == []

    # Caso negativo 1: AFN-λ con transiciones espontáneas y múltiples destinos (ej196)
    afn_lambda_196 = cargar_automata(DIR_P3_CASOS / "ej196_afnd_lambda.jff")
    verif_196 = afn_lambda_196.verificar_determinismo()
    assert verif_196.es_determinista is False
    assert verif_196.primer_estado_conflicto == "A"
    assert verif_196.primer_simbolo_conflicto == "λ"
    estados_simbolos = {(v.estado, v.simbolo) for v in verif_196.violaciones}
    assert ("A", "λ") in estados_simbolos
    assert ("B", "0") in estados_simbolos

    # Caso negativo 2: AFN sin λ con transición múltiple (ej191: estado A con símbolo 0 va a {A, B})
    afn_191 = cargar_automata(DIR_P3_CASOS / "ej191_subconjuntos.jff")
    verif_191 = afn_191.verificar_determinismo()
    assert verif_191.es_determinista is False
    assert verif_191.primer_estado_conflicto == "A"
    assert verif_191.primer_simbolo_conflicto == "0"

    # Al intentar eliminar estados sobre un autómata no determinista debe lanzarse ValueError con el detalle
    with pytest.raises(ValueError) as exc_info:
        eliminacion_de_estados_detallada(afn_191)
    assert "estado 'A'" in str(exc_info.value)
    assert "símbolo '0'" in str(exc_info.value)


CASOS_EJ3_AFD_A_ER = [
    "ej254_termina_en_1.jff",
    "ej255_ciclo_par_b.jff",
    "ej256_ternario.jff",
    "ej257_tres_estados_bc.jff",
    "ej258_tres_estados_c.jff",
    "ej276_multiplo_3_a.jff",
    "ej277_termina_en_1.jff",
]


@pytest.mark.parametrize("nombre_jff", CASOS_EJ3_AFD_A_ER)
def test_ejercicio3_eliminacion_estados_gnfa_y_equivalencia_con_jflap(nombre_jff: str):
    """Verifica para los ejercicios 254–258 de la Lista 3 (los cinco autómatas del Ejercicio 1
    de la Práctica 3) y los ejercicios 276 y 277 de la Lista 4:
    1) Que el autómata importado de `.jff` sea determinista.
    2) Que la eliminación de estados registre el GNFA inicial y el GNFA tras cada estado eliminado.
    3) Que la expresión obtenida sea formalmente equivalente tanto a la expresión de JFLAP como a la
       expresión simplificada de la Práctica 3 convirtiendo ambas en AFD mínimos con el Ejercicio 2
       y comparándolos con la prueba de equivalencia de la Práctica 3."""
    ruta_jff = DIR_P4_EJ3 / nombre_jff
    aut = cargar_automata(ruta_jff)
    res_gnfa = eliminacion_de_estados_detallada(aut)

    assert res_gnfa.verificacion_afd.es_determinista is True
    # Paso 0 (GNFA inicial) + 1 paso por cada estado de Q eliminado
    assert len(res_gnfa.pasos_gnfa) == len(aut.estados) + 1
    assert res_gnfa.pasos_gnfa[0].estado_eliminado is None
    assert res_gnfa.pasos_gnfa[-1].estados_vivos == ["⊢ini", "fin⊣"]

    # Leer las expresiones de referencia (ER_JFLAP y ER_SIMPLIFICADA)
    ruta_er = ruta_jff.with_name(f"{ruta_jff.stem}_er.txt")
    lineas = dict(
        ln.split(": ", 1)
        for ln in ruta_er.read_text(encoding="utf-8").splitlines()
        if ": " in ln
    )
    er_jflap = lineas["ER_JFLAP"]
    er_simp = lineas["ER_SIMPLIFICADA"]

    comp_jflap = comparar_expresiones_por_afd_minimo(
        res_gnfa.expresion_texto,
        er_jflap,
        alfabeto=aut.alfabeto,
    )
    assert comp_jflap.equivalentes is True, (
        f"No equivalente con ER_JFLAP en {nombre_jff}: {comp_jflap.equivalencia_afd.justificacion}"
    )

    comp_simp = comparar_expresiones_por_afd_minimo(
        res_gnfa.expresion_texto,
        er_simp,
        alfabeto=aut.alfabeto,
    )
    assert comp_simp.equivalentes is True, (
        f"No equivalente con ER_SIMPLIFICADA en {nombre_jff}: {comp_simp.equivalencia_afd.justificacion}"
    )

    # Además, el AFD mínimo obtenido al reconvertir la expresión debe ser equivalente al AFD original
    assert aut.son_afd_equivalentes(comp_jflap.tuberia_1.afd_minimo).equivalentes is True


# =============================================================================
# 5. EJERCICIO 4: VALIDADORES Y CONGRUENCIA ENTRE MODELOS (>= 500 CADENAS)
# =============================================================================

def test_declaracion_clases_y_cuatro_validadores_implementados():
    """Comprueba que las clases de símbolos estén documentadas y que los cuatro validadores
    muestren reducción de estados al minimizar su AFD."""
    assert len(ESPECIFICACIONES_VALIDADORES) >= 3
    for clave, esp in ESPECIFICACIONES_VALIDADORES.items():
        for c in esp.clases_empleadas:
            assert c in DECLARACION_CLASES_CURSO
            assert c in CLASES_PREDEFINIDAS
        val = obtener_validador(clave)
        assert val.estados_afd_antes_minimizar > val.estados_afd_despues_minimizar > 0
        assert len(esp.norma_consultada) > 20
        assert len(esp.casos_fuera_de_la_expresion) > 40

        # Verificar que todos los ejemplos válidos e inválidos declarados se clasifican correctamente
        for ej_v in esp.ejemplos_validos:
            rv = val.validar(ej_v)
            assert rv.aceptada_automata is True and rv.congruente is True, f"{clave} rechazó válido '{ej_v}'"
        for ej_i in esp.ejemplos_invalidos:
            ri = val.validar(ej_i)
            assert ri.aceptada_automata is False and ri.congruente is True, f"{clave} aceptó inválido '{ej_i}'"


@pytest.mark.parametrize("clave_validador", list(ESPECIFICACIONES_VALIDADORES.keys()))
def test_congruencia_entre_modelos_500_cadenas_por_validador(clave_validador: str):
    """Requisito de Congruencia entre modelos (Ejercicio 4):
    Para cada validador (`correo`, `telefono_nacional`, `url`, `fecha`), compara su autómata
    obtenido en el Ejercicio 2 con `re.fullmatch` sobre un conjunto de al menos 500 cadenas
    válidas e inválidas generadas mediante el procedimiento documentado. Ambos deben coincidir
    en todas las cadenas."""
    corpus = generar_corpus_validador(clave_validador, total=500, semilla=2026)
    assert len(corpus) >= 500

    res_cong = verificar_congruencia_validador(clave_validador, total=500, semilla=2026)
    assert res_cong.total_cadenas >= 500
    assert res_cong.total_validas == 250
    assert res_cong.total_invalidas == 250
    assert res_cong.congruente is True, (
        f"Discrepancias entre el autómata y re.fullmatch en '{clave_validador}': {res_cong.discrepancias}"
    )
