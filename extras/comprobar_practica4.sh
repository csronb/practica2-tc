#!/usr/bin/env bash
# =============================================================================
#  Comprobación de la Práctica 4 · Teoría de la Computación · 2027-1
#
#  Complementa a extras/comprobar.sh (material del profesor, ContenedorV1).
#  Primero ejecuta la comprobación del entorno del curso y después verifica
#  los Ejercicios 2, 3 y 4 de la Práctica 4 sobre las Listas 3 y 4 y los
#  cuatro validadores (congruencia en 500 cadenas frente a re.fullmatch).
#
#  Se ejecuta desde dentro del contenedor:
#      docker compose up -d --build
#      docker compose exec teoria bash
#      bash extras/comprobar_practica4.sh
# =============================================================================
set -uo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAIZ="$(cd "$AQUI/.." && pwd)"
export PYTHONDONTWRITEBYTECODE=1
ROJO=$'\033[0;31m'; VERDE=$'\033[0;32m'; NEGRITA=$'\033[1m'; FIN=$'\033[0m'
fallos=0

titulo() { printf '\n%s%s%s\n' "$NEGRITA" "$1" "$FIN"; }
ok()     { printf '  %s✓%s %s\n' "$VERDE" "$FIN" "$1"; }
mal()    { printf '  %s✗%s %s\n' "$ROJO" "$FIN" "$1"; fallos=$((fallos + 1)); }

titulo "A · Entorno del curso (extras/comprobar.sh)"
if bash "$AQUI/comprobar.sh"; then ok "Entorno del curso listo."; else mal "Falló la comprobación del entorno."; fi

titulo "B · Ejercicio 2 (ER -> AFN-λ -> AFN -> AFD -> AFD mínimo) y Ejercicio 3 (GNFA)"
cd "$RAIZ" || exit 1
python - <<'PY'
import sys
sys.path.insert(0, "src")
from expresiones import er_a_automata_completo, eliminacion_de_estados_detallada, comparar_expresiones_por_afd_minimo
from formatos import cargar_automata
from pathlib import Path

for nombre, er in [
    ("272a", "a + b*"),
    ("272b", "(ab)*a"),
    ("272c", "(a + b)*abb"),
    ("272d", "a(ba)* + b"),
    ("272e", "(a + λ)(b + ∅)"),
    ("278", "(a + b)*b"),
]:
    r = er_a_automata_completo(er, alfabeto=["a", "b"])
    print(f"  {nombre:<6} ER={er:<18} |Q_AFN-λ|={len(r.afn_lambda.estados):<3} |Q_AFD|={len(r.afd.estados):<2} |Q_min|={len(r.afd_minimo.estados)}")

for ruta in sorted(Path("automatas/practica4/afd-a-er").glob("*.jff")):
    aut = cargar_automata(ruta)
    el = eliminacion_de_estados_detallada(aut)
    print(f"  {ruta.stem:<26} |Q|={len(aut.estados)} -> ER={el.expresion_texto}")
PY

titulo "C · Ejercicio 4 (Validadores y congruencia sobre 500 cadenas vs re.fullmatch)"
python - <<'PY'
import sys
sys.path.insert(0, "src")
from validadores import ESPECIFICACIONES_VALIDADORES, obtener_validador, verificar_congruencia_validador

for clave in ESPECIFICACIONES_VALIDADORES:
    v = obtener_validador(clave)
    c = verificar_congruencia_validador(clave, total=500, semilla=2026)
    print(f"  {clave:<18} AFD={v.estados_afd_antes_minimizar:>2}q -> AFD_min={v.estados_afd_despues_minimizar:>2}q | {c.coincidencias_afd_minimo_vs_re}/{c.total_cadenas} cadenas congruentes")
PY

titulo "D · Pruebas automatizadas (pytest)"
if res=$(python -m pytest -q -p no:cacheprovider 2>&1); then
    ok "pytest: $(printf '%s\n' "$res" | tail -1)"
else
    mal "Alguna prueba falló."
    printf '%s\n' "$res" | tail -15 | sed 's/^/    /'
fi

echo
if [ "$fallos" -eq 0 ]; then
    printf '%s%s  Práctica 4 lista.%s\n\n' "$NEGRITA" "$VERDE" "$FIN"
else
    printf '%s%s  %d comprobación(es) fallaron.%s\n\n' "$NEGRITA" "$ROJO" "$fallos" "$FIN"
    exit 1
fi
