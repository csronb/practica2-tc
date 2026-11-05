#!/usr/bin/env bash
# =============================================================================
#  Comprobación de la Práctica 3 · Teoría de la Computación · 2027-1
#
#  Complementa a extras/comprobar.sh (material del profesor, ContenedorV1).
#  Primero ejecuta la comprobación del entorno del curso y después verifica
#  los algoritmos de la Práctica 3 sobre los casos de prueba de la Lista 3.
#
#  Se ejecuta desde dentro del contenedor:
#      docker compose up -d --build
#      docker compose exec teoria bash
#      bash extras/comprobar_practica3.sh
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

titulo "B · Algoritmos de la Práctica 3 sobre la Lista 3"
cd "$RAIZ" || exit 1
python - <<'PY'
import sys
sys.path.insert(0, "src")
from pathlib import Path
from formatos import cargar_automata
for ruta in sorted(Path("automatas/practica3/casos-de-prueba").glob("*.jff")):
    m = cargar_automata(ruta)
    afd = m.construccion_subconjuntos_detallada().afd
    mini = afd.minimizar_afd_detallado().afd_minimo
    print(f"  {ruta.stem:<24} {m.tipo:<12} |Q|={len(m.estados):<3} |Q_AFD|={len(afd.estados):<3} |Q_min|={len(mini.estados)}")
PY

titulo "C · Pruebas automatizadas (pytest)"
if res=$(python -m pytest -q -p no:cacheprovider 2>&1); then
    ok "pytest: $(printf '%s\n' "$res" | tail -1)"
else
    mal "Alguna prueba falló."
    printf '%s\n' "$res" | tail -15 | sed 's/^/    /'
fi

echo
if [ "$fallos" -eq 0 ]; then
    printf '%s%s  Práctica 3 lista.%s\n\n' "$NEGRITA" "$VERDE" "$FIN"
else
    printf '%s%s  %d comprobación(es) fallaron.%s\n\n' "$NEGRITA" "$ROJO" "$fallos" "$FIN"
    exit 1
fi
