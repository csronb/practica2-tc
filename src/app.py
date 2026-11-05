"""Aplicación interactiva en Flet para la Práctica 2: Simulador de Autómatas y Lenguajes.

Cumple todos los requisitos del Ejercicio 3:
- 3.1 Definición interactiva del autómata (alfabeto, estados, estado inicial, estados
  de aceptación y tabla de transiciones editable).
- 3.2 Importación desde archivos `.jff`, `.json` y `.xml` verificando la quíntupla.
- 3.3 Simulación y validación de cadenas (validación rápida y ejecución paso a paso
  mostrando estado/conjunto activo, transiciones tomadas, λ-clausura y bifurcaciones,
  además de botón para convertir AFND-λ -> AFND -> AFD en vivo).
- 3.4 Exportación en `.jff`, `.json` y `.xml` + integración de las operaciones sobre
  cadenas y lenguajes de la Práctica 1 (`prefijos`, `sufijos`, `subcadenas`, `Σ*`, `Σ+`).
"""

from __future__ import annotations

from pathlib import Path
import flet as ft

from automata import AutomataFinito, ResultadoSimulacion
from formatos import (
    cargar_automata,
    exportar_jff_texto,
    exportar_json_texto,
    exportar_xml_texto,
    guardar_en_tres_formatos,
)
from lenguajes import (
    LIMITE_CADENAS,
    cerradura_kleene,
    cerradura_positiva,
    formatear_cadena,
    normalizar_alfabeto,
    prefijos,
    subcadenas,
    sufijos,
)

DIR_EXPORT = Path("salidas")


def automata_inicial_demo() -> AutomataFinito:
    """Devuelve el AFND-λ del Anexo 3 o el autómata de Pac-Man ampliado como ejemplo inicial."""
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


def main(page: ft.Page) -> None:
    page.title = "Práctica 2 - Simulador de Autómatas Finitos (AFD, AFND, AFND-λ) y Lenguajes"
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20

    estado_actual: dict[str, object] = {
        "automata": automata_inicial_demo(),
        "resultado_sim": None,
        "paso_idx": 0,
    }

    # =========================================================================
    # CONTROLES DE 3.1 DEFINICIÓN INTERACTIVA Y 3.2 IMPORTACIÓN / 3.4 EXPORTACIÓN
    # =========================================================================
    tf_alfabeto = ft.TextField(label="Alfabeto Σ (separado por comas)", value="a, b", width=260)
    tf_estados = ft.TextField(label="Estados Q (separados por comas)", value="q0, q1", width=280)
    tf_inicial = ft.TextField(label="Estado inicial (q0)", value="q0", width=160)
    tf_aceptacion = ft.TextField(label="Estados de aceptación F", value="q1", width=220)
    tf_transiciones = ft.TextField(
        label="Función de transición δ (una por línea: origen, simbolo_o_λ, destino1|destino2)",
        value="q0, a, q1\nq0, b, q0\nq0, λ, q1",
        multiline=True,
        min_lines=5,
        max_lines=8,
        width=540,
    )
    tf_ruta_archivo = ft.TextField(
        label="Ruta de archivo para Importar / Exportar (.jff, .json, .xml)",
        value="automatas/aplicacion/ej5_pacman_ampliado.jff",
        width=480,
    )
    txt_quintupla = ft.Text(weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900)
    txt_tabla_md = ft.Markdown(value="", selectable=True)
    txt_estado_io = ft.Text(color=ft.Colors.GREEN_800)

    def sincronizar_controles_desde_automata(aut: AutomataFinito) -> None:
        tf_alfabeto.value = ", ".join(aut.alfabeto)
        tf_estados.value = ", ".join(aut.estados)
        tf_inicial.value = aut.inicial
        tf_aceptacion.value = ", ".join(aut.aceptacion)
        lineas_tr: list[str] = []
        for (u, sym), dest in aut.transiciones.items():
            etiqueta_sym = "λ" if sym == "" else sym
            lineas_tr.append(f"{u}, {etiqueta_sym}, {'|'.join(dest)}")
        tf_transiciones.value = "\n".join(lineas_tr)
        actualizar_vista_quintupla(aut)

    def actualizar_vista_quintupla(aut: AutomataFinito) -> None:
        txt_quintupla.value = (
            f"Tipo detectado: {aut.tipo}  |  "
            f"Q = {{{', '.join(aut.estados)}}} (|Q|={len(aut.estados)})  |  "
            f"Σ = {{{', '.join(aut.alfabeto)}}}  |  "
            f"q0 = {aut.inicial}  |  "
            f"F = {{{', '.join(aut.aceptacion)}}}"
        )
        # Generar tabla Markdown de transiciones y λ-clausura
        cols = list(aut.alfabeto) + (["λ"] if aut.tiene_transiciones_lambda else [])
        encabezado = "| Estado | " + " | ".join(f"`{c}`" for c in cols) + " | `λ-clausura` |\n"
        separador = "| :--- | " + " | ".join(":---:" for _ in cols) + " | :--- |\n"
        filas: list[str] = []
        for q in aut.estados:
            pref = ""
            if q == aut.inicial:
                pref += "→ "
            if q in aut.aceptacion:
                pref += "* "
            celdas: list[str] = []
            for c in cols:
                sym_real = "" if c == "λ" else c
                d = aut.destinos(q, sym_real)
                celdas.append("{" + ", ".join(d) + "}" if d else "∅")
            cl_q = "{ " + ", ".join(aut.lambda_clausura_estado(q)) + " }"
            filas.append(f"| {pref}**{q}** | " + " | ".join(celdas) + f" | `{cl_q}` |")
        txt_tabla_md.value = encabezado + separador + "\n".join(filas)

    def aplicar_definicion_manual(e: ft.ControlEvent | None = None) -> None:
        alf = normalizar_alfabeto((tf_alfabeto.value or "").split(","))
        ests = normalizar_alfabeto((tf_estados.value or "").split(","))
        ini = (tf_inicial.value or "").strip()
        acep = normalizar_alfabeto((tf_aceptacion.value or "").split(","))
        trans: dict[tuple[str, str], list[str]] = {}
        for ln in (tf_transiciones.value or "").splitlines():
            ln_s = ln.strip()
            if not ln_s:
                continue
            partes = [p.strip() for p in ln_s.split(",")]
            if len(partes) < 3:
                continue
            u, sym_raw, dest_raw = partes[0], partes[1], partes[2]
            sym = "" if sym_raw in ("", "λ", "lambda", "epsilon", "ε") else sym_raw
            destinos = [d.strip() for d in dest_raw.split("|") if d.strip()]
            trans[(u, sym)] = destinos

        aut = AutomataFinito(
            alfabeto=alf,
            estados=ests,
            inicial=ini,
            aceptacion=acep,
            transiciones=trans,
        )
        estado_actual["automata"] = aut
        actualizar_vista_quintupla(aut)
        txt_estado_io.value = "Definición interactiva actualizada correctamente."
        page.update()

    def importar_desde_ruta(e: ft.ControlEvent) -> None:
        ruta = (tf_ruta_archivo.value or "").strip()
        try:
            aut = cargar_automata(ruta)
            estado_actual["automata"] = aut
            sincronizar_controles_desde_automata(aut)
            txt_estado_io.value = f"Importado con éxito desde: {ruta} ({aut.tipo})"
        except Exception as err:
            txt_estado_io.value = f"Error al importar '{ruta}': {err}"
        page.update()

    def exportar_tres_formatos_ui(e: ft.ControlEvent) -> None:
        aut: AutomataFinito = estado_actual["automata"]  # type: ignore[assignment]
        nombre_base = Path((tf_ruta_archivo.value or "automata_exportado").strip()).stem
        r_jff, r_json, r_xml = guardar_en_tres_formatos(aut, DIR_EXPORT, nombre_base)
        txt_estado_io.value = (
            f"Exportado en 3 formatos: {r_jff.as_posix()}, {r_json.as_posix()} y {r_xml.as_posix()}"
        )
        page.update()

    def convertir_a_afd_ui(e: ft.ControlEvent) -> None:
        aut: AutomataFinito = estado_actual["automata"]  # type: ignore[assignment]
        afd = aut.convertir_a_afd()
        estado_actual["automata"] = afd
        sincronizar_controles_desde_automata(afd)
        txt_estado_io.value = f"Convertido a AFD equivalente con {len(afd.estados)} estados accesibles."
        page.update()

    # =========================================================================
    # CONTROLES DE 3.3 SIMULACIÓN Y VALIDACIÓN PASO A PASO
    # =========================================================================
    tf_cadena_sim = ft.TextField(
        label="Cadena a simular en el autómata (deje vacío para λ)",
        value="a",
        width=360,
    )
    txt_resultado_sim = ft.Text(weight=ft.FontWeight.BOLD, size=16)
    txt_paso_actual = ft.Text(weight=ft.FontWeight.BOLD, color=ft.Colors.INDIGO_900)
    tf_traza_completa = ft.TextField(
        label="Traza completa del recorrido y bifurcaciones",
        multiline=True,
        min_lines=6,
        max_lines=10,
        read_only=True,
    )

    def mostrar_paso(res: ResultadoSimulacion, idx: int) -> None:
        if not res.pasos:
            return
        idx = max(0, min(idx, len(res.pasos) - 1))
        estado_actual["paso_idx"] = idx
        p = res.pasos[idx]
        txt_paso_actual.value = (
            f"Paso {p.indice}/{len(res.pasos) - 1}  |  "
            f"Símbolo leído: '{p.simbolo}'  |  "
            f"Estados activos: {{{', '.join(p.estados_destino)}}}  |  "
            f"Transiciones: {'; '.join(p.transiciones_tomadas)}"
        )

    def ejecutar_simulacion_completa(e: ft.ControlEvent | None = None) -> None:
        aut: AutomataFinito = estado_actual["automata"]  # type: ignore[assignment]
        w = tf_cadena_sim.value or ""
        res = aut.simular(w)
        estado_actual["resultado_sim"] = res
        estado_actual["paso_idx"] = 0

        veredicto = "ACEPTADA" if res.aceptada else "RECHAZADA"
        txt_resultado_sim.color = ft.Colors.GREEN_800 if res.aceptada else ft.Colors.RED_800
        txt_resultado_sim.value = (
            f"Cadena '{formatear_cadena(w)}': {veredicto}  |  "
            f"Estados de aceptación alcanzados: {res.estados_finales_alcanzados or 'Ninguno'}"
        )

        lineas: list[str] = []
        for p in res.pasos:
            lineas.append(
                f"[Paso {p.indice}] Símbolo='{p.simbolo}' | "
                f"Origen={p.estados_origen} -> Destino={p.estados_destino} | "
                f"Reglas: {', '.join(p.transiciones_tomadas)}"
            )
        if res.caminos:
            lineas.append("\nBifurcaciones / Caminos explorados:")
            for i_c, cam in enumerate(res.caminos, start=1):
                lineas.append(f"  Camino {i_c}: {' '.join(cam)}")

        tf_traza_completa.value = "\n".join(lineas)
        mostrar_paso(res, len(res.pasos) - 1)
        page.update()

    def paso_anterior(e: ft.ControlEvent) -> None:
        res: ResultadoSimulacion | None = estado_actual["resultado_sim"]  # type: ignore[assignment]
        if res is None:
            ejecutar_simulacion_completa()
            res = estado_actual["resultado_sim"]  # type: ignore[assignment]
        if res is not None:
            mostrar_paso(res, int(estado_actual["paso_idx"]) - 1)  # type: ignore[arg-type]
            page.update()

    def paso_siguiente(e: ft.ControlEvent) -> None:
        res: ResultadoSimulacion | None = estado_actual["resultado_sim"]  # type: ignore[assignment]
        if res is None:
            ejecutar_simulacion_completa()
            res = estado_actual["resultado_sim"]  # type: ignore[assignment]
        if res is not None:
            mostrar_paso(res, int(estado_actual["paso_idx"]) + 1)  # type: ignore[arg-type]
            page.update()

    # =========================================================================
    # CONTROLES DE 3.4 OPERACIONES SOBRE CADENAS Y LENGUAJES (PRÁCTICA 1)
    # =========================================================================
    tf_cad_p1 = ft.TextField(label="Cadena w (Prefijos, Sufijos y Subcadenas)", value="abba", width=300)
    tf_alf_p1 = ft.TextField(label="Alfabeto Σ (para Σ* y Σ+)", value="0, 1", width=220)
    tf_len_p1 = ft.TextField(label="Longitud máx. n", value="3", width=140)
    tf_salida_p1 = ft.TextField(
        label="Resultados de Operaciones sobre Cadenas y Lenguajes (Práctica 1)",
        multiline=True,
        min_lines=5,
        max_lines=8,
        read_only=True,
    )

    def calcular_operaciones_p1(e: ft.ControlEvent | None = None) -> None:
        w = tf_cad_p1.value or ""
        pref = [formatear_cadena(x) for x in prefijos(w)]
        suf = [formatear_cadena(x) for x in sufijos(w)]
        sub = [formatear_cadena(x) for x in subcadenas(w)]

        simbolos = normalizar_alfabeto((tf_alf_p1.value or "").split(","))
        try:
            n = int((tf_len_p1.value or "0").strip())
            kl = [formatear_cadena(x) for x in cerradura_kleene(simbolos, n, limite=LIMITE_CADENAS)]
            pos = [formatear_cadena(x) for x in cerradura_positiva(simbolos, n, limite=LIMITE_CADENAS)]
            texto_cerr = (
                f"Σ* (|Σ*|={len(kl)}): {', '.join(kl[:300])}\n"
                f"Σ+ (|Σ+|={len(pos)}): {', '.join(pos[:300]) if pos else '∅'}"
            )
        except ValueError as err:
            texto_cerr = f"Error en cerraduras: {err}"

        tf_salida_p1.value = (
            f"Prefijos ({len(pref)}): {', '.join(pref)}\n"
            f"Sufijos ({len(suf)}): {', '.join(suf)}\n"
            f"Subcadenas ({len(sub)}): {', '.join(sub)}\n"
            f"{texto_cerr}"
        )
        page.update()

    # Construcción visual de la página
    page.add(
        ft.Text(
            "Práctica 2: Simulador de Autómatas Finitos (AFD, AFND, AFND-λ) y Lenguajes",
            size=22,
            weight=ft.FontWeight.BOLD,
        ),
        ft.Text(
            "Instituto Politécnico Nacional — Escuela Superior de Cómputo (ESCOM) — Teoría de la Computación",
            size=13,
        ),
        ft.Divider(),
        ft.Text("1. Definición Interactiva, Importación y Exportación (.jff, .json, .xml)", size=17, weight=ft.FontWeight.BOLD),
        ft.Row([tf_alfabeto, tf_estados, tf_inicial, tf_aceptacion], wrap=True),
        ft.Row(
            [
                tf_transiciones,
                ft.Column(
                    [
                        ft.ElevatedButton("Actualizar Autómata desde Tabla", on_click=aplicar_definicion_manual),
                        ft.OutlinedButton("Convertir a AFD Equivalente (Subconjuntos)", on_click=convertir_a_afd_ui),
                        tf_ruta_archivo,
                        ft.Row(
                            [
                                ft.ElevatedButton("Importar Archivo", on_click=importar_desde_ruta),
                                ft.OutlinedButton("Exportar (.jff, .json, .xml)", on_click=exportar_tres_formatos_ui),
                            ]
                        ),
                    ]
                ),
            ],
            wrap=True,
        ),
        txt_estado_io,
        txt_quintupla,
        txt_tabla_md,
        ft.Divider(),
        ft.Text("2. Simulación y Validación de Cadenas (Paso a Paso y Traza Completa)", size=17, weight=ft.FontWeight.BOLD),
        ft.Row(
            [
                tf_cadena_sim,
                ft.ElevatedButton("Validar Cadena (Traza Completa)", on_click=ejecutar_simulacion_completa),
                ft.OutlinedButton("◀ Paso Anterior", on_click=paso_anterior),
                ft.OutlinedButton("Paso Siguiente ▶", on_click=paso_siguiente),
            ],
            wrap=True,
        ),
        txt_resultado_sim,
        txt_paso_actual,
        tf_traza_completa,
        ft.Divider(),
        ft.Text("3. Operaciones sobre Cadenas y Lenguajes (Módulo reutilizado de Práctica 1)", size=17, weight=ft.FontWeight.BOLD),
        ft.Row(
            [
                tf_cad_p1,
                tf_alf_p1,
                tf_len_p1,
                ft.ElevatedButton("Calcular Operaciones de Lenguajes", on_click=calcular_operaciones_p1),
            ],
            wrap=True,
        ),
        tf_salida_p1,
    )

    sincronizar_controles_desde_automata(estado_actual["automata"])  # type: ignore[arg-type]
    ejecutar_simulacion_completa()
    calcular_operaciones_p1()


if __name__ == "__main__":
    ft.run(main)
