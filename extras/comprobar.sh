#!/usr/bin/env bash
# =============================================================================
#  Comprobación del entorno · Teoría de la Computación · 2027-1
#
#  Lee con Python puro el autómata M₁ de la sección 1.2.3 —el de las cadenas
#  con un número par de ceros—, guardado en el formato de JFLAP, y comprueba
#  que acepta y rechaza lo que debe. Después revisa pytest, el volumen y Flet.
#
#  Se ejecuta desde dentro del contenedor:
#      docker compose up -d
#      docker compose exec teoria bash
#      bash extras/comprobar.sh
# =============================================================================
set -uo pipefail        # sin -e: se quieren ver todas las fallas, no sólo la primera

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EJ="$AQUI/ejemplos"
export PYTHONDONTWRITEBYTECODE=1        # no dejar __pycache__ en su carpeta
ROJO=$'\033[0;31m'; VERDE=$'\033[0;32m'; GRIS=$'\033[0;90m'; NEGRITA=$'\033[1m'; FIN=$'\033[0m'

fallos=0

titulo() { printf '\n%s%s%s\n' "$NEGRITA" "$1" "$FIN"; }
ok()     { printf '  %s✓%s %s\n' "$VERDE" "$FIN" "$1"; }
nota()   { printf '    %s%s%s\n' "$GRIS" "$1" "$FIN"; }
mal()    { printf '  %s✗%s %s\n' "$ROJO" "$FIN" "$1"; [ -n "${2:-}" ] && nota "$2"; fallos=$((fallos + 1)); }

titulo "1 · Dónde se está ejecutando"
if [ -f /.dockerenv ]; then
    ok "Dentro del contenedor."
else
    mal "Esto no parece un contenedor." "Entre primero con: docker compose exec teoria bash"
    exit 1
fi

titulo "2 · Versiones instaladas"
printf '  %-8s %s\n' "Python" "$(python --version 2>&1 | cut -d' ' -f2)"
printf '  %-8s %s\n' "Flet"   "$(python -c 'import importlib.metadata as m; print(m.version("flet"))' 2>&1)"
printf '  %-8s %s\n' "pytest" "$(python -c 'import importlib.metadata as m; print(m.version("pytest"))' 2>&1)"

titulo "3 · Un autómata de JFLAP, leído con Python puro"
echo "  M₁ = ({s₁, s₂}, {0, 1}, δ, s₁, {s₁}): acepta las cadenas con un número par de ceros."
echo
salida=$(python "$EJ/afd.py" "" 111 10 100 1001 2>&1)
printf '%s\n' "$salida" | sed 's/^/  /'
veredictos=$(printf '%s\n' "$salida" | awk '{print $NF}' | tr '\n' ' ')
echo
if [ "$veredictos" = "acepta acepta rechaza acepta acepta " ]; then
    ok "Las cinco cadenas dan el resultado que corresponde."
else
    mal "El resultado no es el esperado." "Revise extras/ejemplos/afd.py y m1_par_de_ceros.jff"
fi

titulo "4 · Pruebas automatizadas"
if res=$(python -m pytest -q -p no:cacheprovider "$EJ" 2>&1); then
    ok "pytest: $(printf '%s\n' "$res" | tail -1)"
    nota "Una de las pruebas compara M₁ contra la definición del lenguaje"
    nota "en las 2047 cadenas de longitud 0 a 10."
else
    mal "Alguna prueba falló." "Ejecute: pytest extras/ejemplos   y lea el primer error"
    printf '%s\n' "$res" | tail -5 | sed 's/^/    /'
fi

titulo "5 · Escritura en el volumen"
marca="$AQUI/.comprobacion_entorno.txt"
if printf 'Entorno comprobado: %s\n' "$(date -Iseconds)" > "$marca" 2>/dev/null; then
    ok "Se puede escribir en la carpeta compartida con su computadora."
    rm -f "$marca"
else
    mal "No se puede escribir en /trabajo." "Revise la línea './:/trabajo' en volumes: del compose.yaml"
fi

titulo "6 · La interfaz de Flet"
responde() {
    python - <<'PY' 2>/dev/null
import sys, urllib.request
try:
    urllib.request.urlopen("http://127.0.0.1:8550/", timeout=2)
except Exception:
    sys.exit(1)
PY
}
if responde; then
    ok "Ya hay una interfaz abierta en el puerto 8550."
    nota "En su computadora se ve en http://localhost:8550"
else
    prueba="$(mktemp --suffix=.py)"
    cat > "$prueba" <<'PY'
import flet as ft
ft.run(lambda page: page.add(ft.Text("Comprobación del entorno")))
PY
    python "$prueba" > /dev/null 2>&1 &
    pid=$!
    listo=no
    for _ in $(seq 1 30); do
        if responde; then listo=si; break; fi
        sleep 1
    done
    kill "$pid" 2>/dev/null; wait "$pid" 2>/dev/null; rm -f "$prueba"
    if [ "$listo" = si ]; then
        ok "Flet sirve una interfaz en el puerto 8550."
        nota "Cuando ejecute la suya, se ve en su navegador en http://localhost:8550"
    else
        mal "Flet no respondió en 30 segundos." "Revise que FLET_FORCE_WEB_SERVER y FLET_SERVER_PORT estén en el Dockerfile"
    fi
fi

echo
if [ "$fallos" -eq 0 ]; then
    printf '%s%s  Entorno listo.%s\n' "$NEGRITA" "$VERDE" "$FIN"
    nota "JFLAP y, si la usa, una interfaz con Tkinter se ejecutan en su computadora,"
    nota "no aquí: el contenedor no tiene pantalla donde abrir una ventana."
    echo
else
    printf '%s%s  %d comprobación(es) fallaron.%s\n\n' "$NEGRITA" "$ROJO" "$fallos" "$FIN"
    exit 1
fi
