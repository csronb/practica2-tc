"""Aplicación interactiva en Flet para las Prácticas 1, 2 y 3:
Simulador de Autómatas Finitos (AFD, AFND, AFND-λ), Transformaciones, Minimización y Lenguajes.

Cumple todos los requisitos acumulados de las tres prácticas:
- Práctica 1: Operaciones sobre cadenas (`prefijos`, `sufijos`, `subcadenas`) y lenguajes (`Σ*`, `Σ+`).
- Práctica 2: Definición interactiva de la quíntupla, importación y exportación inversa en
  `.jff`, `.json` y `.xml`, y simulación con traza y bifurcaciones.
- Práctica 3 (Ejercicio 2):
  * 2.1: Cálculo de la λ-clausura de cada estado (mostrando la del estado que el usuario seleccione)
    y simulación directa de un AFN-λ mostrando en cada paso el conjunto de estados activos *antes*
    y *después* de aplicar la λ-clausura.
  * 2.2: Eliminación de transiciones λ (AFN-λ -> AFN) mostrando explícitamente las transiciones
    añadidas y los estados que pasan a ser de aceptación.
  * 2.3: Construcción de subconjuntos (AFN -> AFD) construyendo únicamente los subconjuntos
    alcanzables desde el estado inicial, mostrando la tabla de transición conforme se genera e
    indicando qué subconjuntos resultan de aceptación y por qué.
  * 2.4: Minimización de AFD (eliminando estados inaccesibles y mostrando en cada ronda la
    partición y la tabla de pares distinguibles) y decisión de equivalencia entre dos AFD.
  * 2.5: Validación de cadenas por lotes desde un archivo `.txt` (una cadena por línea) y
    guardado del reporte detallado en disco.
"""

from __future__ import annotations

from pathlib import Path
import flet as ft

from automata import AutomataFinito, ResultadoSimulacion
from formatos import (
    cargar_automata,
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
    """Devuelve el AFN-λ del Ejercicio 196 de la Lista 3 como ejemplo inicial."""
    return AutomataFinito(
        alfabeto=["0", "1"],
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


def main(page: ft.Page) -> None:
    page.title = "Práctica 3 - Simulador de Autómatas (AFD, AFN, AFN-λ), Subconjuntos y Minimización"
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20

    estado_actual: dict[str, object] = {
        "automata": automata_inicial_demo(),
        "resultado_sim": None,
        "paso_idx": 0,
    }

    # =========================================================================
    # 1. DEFINICIÓN INTERACTIVA, IMPORTACIÓN Y EXPORTACIÓN (.jff, .json, .xml)
    # =========================================================================
    tf_alfabeto = ft.TextField(label="Alfabeto Σ (separado por comas)", value="0, 1", width=220)
    tf_estados = ft.TextField(label="Estados Q (separados por comas)", value="A, B, C", width=260)
    tf_inicial = ft.TextField(label="Estado inicial (q0)", value="A", width=150)
    tf_aceptacion = ft.TextField(label="Estados de aceptación F", value="C", width=200)
    tf_transiciones = ft.TextField(
        label="Función de transición δ (origen, simbolo_o_λ, destino1|destino2)",
        value="A, λ, B\nA, 0, A\nB, 0, A|B\nB, 1, C",
        multiline=True,
        min_lines=5,
        max_lines=8,
        width=500,
    )
    tf_ruta_archivo = ft.TextField(
        label="Ruta de archivo (.jff, .json, .xml)",
        value="automatas/practica3/casos-de-prueba/ej196_afnd_lambda.jff",
        width=480,
    )
    dd_casos_rapidos = ft.Dropdown(
        label="Cargar caso de prueba de la Práctica 3",
        width=360,
        options=[
            ft.dropdown.Option("automatas/practica3/casos-de-prueba/ej196_afnd_lambda.jff", "Ej. 196 (AFN-λ)"),
            ft.dropdown.Option("automatas/practica3/casos-de-prueba/ej197_afnd_lambda.jff", "Ej. 197 (AFN-λ)"),
            ft.dropdown.Option("automatas/practica3/casos-de-prueba/ej198_afnd_lambda.jff", "Ej. 198 (AFN-λ)"),
            ft.dropdown.Option("automatas/practica3/casos-de-prueba/ej199_afnd_lambda.jff", "Ej. 199 (AFN-λ)"),
            ft.dropdown.Option("automatas/practica3/casos-de-prueba/ej200_afnd_lambda.jff", "Ej. 200 (AFN-λ)"),
            ft.dropdown.Option("automatas/practica3/casos-de-prueba/ej191_subconjuntos.jff", "Ej. 191/195 (AFN Subconjuntos)"),
            ft.dropdown.Option("automatas/practica3/casos-de-prueba/ej192_subconjuntos.jff", "Ej. 192 (AFN Subconjuntos)"),
            ft.dropdown.Option("automatas/practica3/casos-de-prueba/ej193_subconjuntos.jff", "Ej. 193 (AFN Subconjuntos)"),
            ft.dropdown.Option("automatas/practica3/casos-de-prueba/ej194_subconjuntos.jff", "Ej. 194 (AFN Subconjuntos)"),
            ft.dropdown.Option("automatas/practica3/casos-de-prueba/ej260_subconjuntos.jff", "Ej. 260 (AFN Subconjuntos)"),
            ft.dropdown.Option("automatas/practica3/casos-de-prueba/ej261_subconjuntos.jff", "Ej. 261 (AFN Subconjuntos)"),
            ft.dropdown.Option("automatas/practica3/casos-de-prueba/ej262_subconjuntos.jff", "Ej. 262 (AFN Subconjuntos)"),
            ft.dropdown.Option("automatas/practica3/casos-de-prueba/ej263_subconjuntos.jff", "Ej. 263 (AFN Subconjuntos)"),
            ft.dropdown.Option("automatas/practica3/casos-de-prueba/ej151_minimizacion.jff", "Ej. 151 (AFD Minimización)"),
            ft.dropdown.Option("automatas/practica3/casos-de-prueba/ej152_minimizacion.jff", "Ej. 152 (AFD Minimización)"),
            ft.dropdown.Option("automatas/practica3/casos-de-prueba/ej153_minimizacion.jff", "Ej. 153 (AFD Minimización)"),
            ft.dropdown.Option("automatas/practica3/casos-de-prueba/ej154_minimizacion.jff", "Ej. 154 (AFD Minimización)"),
            ft.dropdown.Option("automatas/practica3/casos-de-prueba/ej155_minimizacion.jff", "Ej. 155 (AFD Minimización)"),
            ft.dropdown.Option("automatas/practica3/casos-de-prueba/ej156_minimizacion.jff", "Ej. 156 (AFD Minimización)"),
            ft.dropdown.Option("automatas/practica3/casos-de-prueba/ej157_minimizacion.jff", "Ej. 157 (AFD Minimización)"),
        ],
    )

    txt_quintupla = ft.Text(weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900)
    txt_tabla_md = ft.Markdown(value="", selectable=True)
    txt_estado_io = ft.Text(color=ft.Colors.GREEN_800)

    # Control de 2.1: Selector de estado para consultar su λ-clausura individual
    dd_estado_clausura = ft.Dropdown(label="Estado q para consultar Cl_λ({q})", width=220)
    txt_clausura_seleccionada = ft.Text(weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_900)

    def actualizar_clausura_estado_ui(e: ft.ControlEvent | None = None) -> None:
        aut: AutomataFinito = estado_actual["automata"]  # type: ignore[assignment]
        q_sel = dd_estado_clausura.value or (aut.estados[0] if aut.estados else "")
        if q_sel and q_sel in aut.estados:
            cl = aut.lambda_clausura_estado(q_sel)
            txt_clausura_seleccionada.value = (
                f"Cl_λ({{{q_sel}}}) = {{ {', '.join(cl)} }}  (|Cl_λ| = {len(cl)})"
            )
        else:
            txt_clausura_seleccionada.value = "Seleccione un estado válido."
        page.update()

    dd_estado_clausura.on_change = actualizar_clausura_estado_ui

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
        dd_estado_clausura.options = [ft.dropdown.Option(q, q) for q in aut.estados]
        dd_estado_clausura.value = aut.inicial if aut.inicial in aut.estados else (aut.estados[0] if aut.estados else None)
        actualizar_vista_quintupla(aut)
        actualizar_clausura_estado_ui()

    def actualizar_vista_quintupla(aut: AutomataFinito) -> None:
        txt_quintupla.value = (
            f"Tipo detectado: {aut.tipo}  |  "
            f"Q = {{{', '.join(aut.estados)}}} (|Q|={len(aut.estados)})  |  "
            f"Σ = {{{', '.join(aut.alfabeto)}}}  |  "
            f"q0 = {aut.inicial}  |  "
            f"F = {{{', '.join(aut.aceptacion)}}}"
        )
        cols = list(aut.alfabeto) + (["λ"] if aut.tiene_transiciones_lambda else [])
        encabezado = "| Estado | " + " | ".join(f"`{c}`" for c in cols) + " | `Cl_λ({q})` |\n"
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
        sincronizar_controles_desde_automata(aut)
        txt_estado_io.value = "Definición interactiva actualizada correctamente."
        page.update()

    def importar_desde_ruta(e: ft.ControlEvent | None = None) -> None:
        ruta = (tf_ruta_archivo.value or "").strip()
        try:
            aut = cargar_automata(ruta)
            estado_actual["automata"] = aut
            sincronizar_controles_desde_automata(aut)
            txt_estado_io.value = f"Importado con éxito desde: {ruta} ({aut.tipo})"
        except Exception as err:
            txt_estado_io.value = f"Error al importar '{ruta}': {err}"
        page.update()

    def seleccionar_caso_rapido(e: ft.ControlEvent) -> None:
        if dd_casos_rapidos.value:
            tf_ruta_archivo.value = dd_casos_rapidos.value
            importar_desde_ruta()

    dd_casos_rapidos.on_change = seleccionar_caso_rapido

    def exportar_tres_formatos_ui(e: ft.ControlEvent) -> None:
        aut: AutomataFinito = estado_actual["automata"]  # type: ignore[assignment]
        nombre_base = Path((tf_ruta_archivo.value or "automata_exportado").strip()).stem
        r_jff, r_json, r_xml = guardar_en_tres_formatos(aut, DIR_EXPORT, nombre_base)
        txt_estado_io.value = (
            f"Exportado en 3 formatos: {r_jff.as_posix()}, {r_json.as_posix()} y {r_xml.as_posix()}"
        )
        page.update()

    # =========================================================================
    # 2.1 SIMULACIÓN DIRECTA DE AFN-λ PASO A PASO (ANTES Y DESPUÉS DE λ-CLAUSURA)
    # =========================================================================
    tf_cadena_sim = ft.TextField(
        label="Cadena a simular directamente (deje vacío para λ)",
        value="01",
        width=340,
    )
    txt_resultado_sim = ft.Text(weight=ft.FontWeight.BOLD, size=16)
    txt_paso_actual = ft.Text(weight=ft.FontWeight.BOLD, color=ft.Colors.INDIGO_900)
    tf_traza_completa = ft.TextField(
        label="Traza paso a paso (Estados activos ANTES y DESPUÉS de aplicar la λ-clausura)",
        multiline=True,
        min_lines=7,
        max_lines=12,
        read_only=True,
    )

    def mostrar_paso(res: ResultadoSimulacion, idx: int) -> None:
        if not res.pasos:
            return
        idx = max(0, min(idx, len(res.pasos) - 1))
        estado_actual["paso_idx"] = idx
        p = res.pasos[idx]
        txt_paso_actual.value = (
            f"Paso {p.indice}/{len(res.pasos) - 1}  |  Símbolo: '{p.simbolo}'  |  "
            f"Antes de λ-clausura: {{{', '.join(p.estados_antes_de_lambda)}}}  ⇒  "
            f"Después de λ-clausura: {{{', '.join(p.estados_despues_de_lambda)}}}  |  "
            f"Reglas: {'; '.join(p.transiciones_tomadas)}"
        )

    def ejecutar_simulacion_completa(e: ft.ControlEvent | None = None) -> None:
        aut: AutomataFinito = estado_actual["automata"]  # type: ignore[assignment]
        w = tf_cadena_sim.value or ""
        res = aut.simular_directo_afnd_lambda(w)
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
                f"Origen={p.estados_origen} -> Antes de Cl_λ={p.estados_antes_de_lambda} "
                f"-> Después de Cl_λ={p.estados_despues_de_lambda} | "
                f"Transiciones: {', '.join(p.transiciones_tomadas)}"
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
    # 2.2, 2.3 y 2.4 TRANSFORMACIONES PASO A PASO Y EQUIVALENCIA DE AFD
    # =========================================================================
    md_transformacion = ft.Markdown(value="", selectable=True)
    tf_ruta_afd2_eq = ft.TextField(
        label="Segundo autómata (.jff/.json/.xml) para comparar Equivalencia (2.4)",
        value="automatas/practica3/casos-de-prueba/ej153_minimizacion.jff",
        width=480,
    )

    def ejecutar_eliminacion_lambda_ui(e: ft.ControlEvent) -> None:
        aut: AutomataFinito = estado_actual["automata"]  # type: ignore[assignment]
        det = aut.eliminar_transiciones_lambda_detallado()
        lineas = [
            "### Resultado 2.2: Eliminación de Transiciones λ (AFN-λ → AFN)",
            f"- **Estados de aceptación originales ($F$):** `{{{', '.join(det.estados_aceptacion_originales)}}}`",
            f"- **Estados de aceptación finales ($F_N$):** `{{{', '.join(det.automata_sin_lambda.aceptacion)}}}`",
        ]
        if det.nuevos_estados_aceptacion:
            lineas.append("- **Estados que pasan a ser de aceptación:**")
            for q_n, just_n in det.nuevos_estados_aceptacion:
                lineas.append(f"  * **`{q_n}`**: {just_n}")
        else:
            lineas.append("- **Estados que pasan a ser de aceptación:** Ninguno nuevo (sólo los originales).")

        if det.transiciones_anadidas:
            lineas.append(f"- **Transiciones añadidas ({len(det.transiciones_anadidas)}):**")
            for u, a, v, camino in det.transiciones_anadidas:
                lineas.append(f"  * `δ_N({u}, {a}) ∋ {v}`  *(justificación: `{camino}`)*")
        else:
            lineas.append("- **Transiciones añadidas:** Ninguna.")

        md_transformacion.value = "\n".join(lineas)
        estado_actual["automata"] = det.automata_sin_lambda
        sincronizar_controles_desde_automata(det.automata_sin_lambda)
        txt_estado_io.value = "Eliminación de transiciones λ completada y cargada en el editor."
        page.update()

    def ejecutar_subconjuntos_ui(e: ft.ControlEvent) -> None:
        aut: AutomataFinito = estado_actual["automata"]  # type: ignore[assignment]
        det = aut.construccion_subconjuntos_detallada()
        cols = list(aut.alfabeto)
        enc = "| # | Subconjunto alcanzable $S$ | " + " | ".join(f"`{a}`" for a in cols) + " | ¿Aceptación? ($S \\cap F \\neq \\emptyset$) |\n"
        sep = "| :---: | :--- | " + " | ".join(":---:" for _ in cols) + " | :--- |\n"
        filas_md: list[str] = []
        for f in det.filas:
            marca = ("→ " if f.es_inicial else "") + ("* " if f.es_aceptacion else "")
            celdas = [f"`{f.transiciones_por_simbolo[a][1]}`" for a in cols]
            filas_md.append(
                f"| {f.orden_descubrimiento} | {marca}**`{f.nombre_estado}`** | "
                + " | ".join(celdas)
                + f" | {'**SÍ**' if f.es_aceptacion else 'No'} (`{f.razon_aceptacion}`) |"
            )

        md_transformacion.value = (
            "### Resultado 2.3: Construcción de Subconjuntos Alcanzables (AFN → AFD)\n"
            f"- **Estado inicial del AFD:** $S_0 = Cl_\\lambda(\\{{ {aut.inicial} \\}}) = \\{{ {', '.join(det.estado_inicial_subconjunto)} \\}}$\n"
            f"- **Total de subconjuntos alcanzables generados:** `{len(det.filas)}` (de $2^{{|Q|}} = {2**len(aut.estados)}$ posibles)\n\n"
            + enc + sep + "\n".join(filas_md)
        )
        estado_actual["automata"] = det.afd
        sincronizar_controles_desde_automata(det.afd)
        txt_estado_io.value = f"Construcción de subconjuntos completada ({len(det.afd.estados)} estados alcanzables)."
        page.update()

    def ejecutar_minimizacion_ui(e: ft.ControlEvent) -> None:
        aut: AutomataFinito = estado_actual["automata"]  # type: ignore[assignment]
        det = aut.minimizar_afd_detallado()
        lineas = [
            "### Resultado 2.4: Minimización de AFD (Eliminación de Inaccesibles, Particiones y Tabla de Pares)",
            f"- **Estados accesibles desde `{det.afd_original.inicial}`:** `{{{', '.join(det.estados_accesibles)}}}`",
            f"- **Estados inaccesibles eliminados:** `{det.estados_inaccesibles_eliminados or 'Ninguno'}`",
            "\n#### A) Refinamiento de Particiones ronda por ronda ($\\Pi_0, \\Pi_1, \\dots$):",
        ]
        for rp in det.rondas_particion:
            grupos_str = ", ".join("{" + ",".join(g) + "}" for g in rp.grupos)
            lineas.append(f"- **Ronda $\\Pi_{{{rp.numero_ronda}}}$:** `{grupos_str}`")
            for div_info in rp.divisiones_realizadas:
                lineas.append(f"  * {div_info}")

        lineas.append("\n#### B) Tabla de Pares Distinguibles ronda por ronda:")
        for rt in det.rondas_tabla_pares:
            if rt.pares_marcados_en_ronda:
                pares_str = "; ".join(f"({p},{q}): {mot}" for p, q, mot in rt.pares_marcados_en_ronda)
                lineas.append(f"- **Ronda {rt.numero_ronda}** ({len(rt.pares_marcados_en_ronda)} pares marcados): {pares_str}")
            else:
                lineas.append(f"- **Ronda {rt.numero_ronda}:** 0 pares nuevos marcados (fin del algoritmo).")

        pares_eq_str = ", ".join(f"({p} ≡ {q})" for p, q in det.pares_equivalentes) or "Ninguno (todos los estados eran distinguibles)"
        lineas.append(f"\n- **Pares de estados equivalentes (no marcados):** `{pares_eq_str}`")
        lineas.append(
            f"- **Reducción de estados:** de `{len(det.afd_original.estados)}` estados en el AFD original a `{len(det.afd_minimo.estados)}` estados en el AFD mínimo."
        )

        md_transformacion.value = "\n".join(lineas)
        estado_actual["automata"] = det.afd_minimo
        sincronizar_controles_desde_automata(det.afd_minimo)
        txt_estado_io.value = f"AFD minimizado a {len(det.afd_minimo.estados)} estados."
        page.update()

    def comparar_equivalencia_ui(e: ft.ControlEvent) -> None:
        aut1: AutomataFinito = estado_actual["automata"]  # type: ignore[assignment]
        ruta2 = (tf_ruta_afd2_eq.value or "").strip()
        try:
            aut2 = cargar_automata(ruta2)
            res_eq = aut1.son_afd_equivalentes(aut2)
            icono = "✅ EQUIVALENTES" if res_eq.equivalentes else "❌ NO EQUIVALENTES"
            md_transformacion.value = (
                f"### Resultado 2.4: Decisión de Equivalencia entre dos AFD ({icono})\n"
                f"- **AFD 1 (actual):** `|Q_min| = {len(res_eq.min_afd1.afd_minimo.estados)}` estados (`{res_eq.min_afd1.afd_minimo.estados}`)\n"
                f"- **AFD 2 (`{ruta2}`):** `|Q_min| = {len(res_eq.min_afd2.afd_minimo.estados)}` estados (`{res_eq.min_afd2.afd_minimo.estados}`)\n"
                f"- **Dictamen formal:** {res_eq.justificacion}"
            )
        except Exception as err:
            md_transformacion.value = f"**Error al comparar equivalencia:** `{err}`"
        page.update()

    # =========================================================================
    # 2.5 VALIDACIÓN DE CADENAS DESDE ARCHIVO (.TXT) Y GUARDADO DE REPORTE
    # =========================================================================
    tf_lote_entrada = ft.TextField(
        label="Archivo de entrada (.txt con una cadena por línea)",
        value="automatas/practica3/casos-de-prueba/lote_cadenas_prueba.txt",
        width=420,
    )
    tf_lote_salida = ft.TextField(
        label="Archivo de salida para guardar el reporte (.txt)",
        value="salidas/reporte_validacion_lote.txt",
        width=380,
    )
    tf_reporte_lote = ft.TextField(
        label="Reporte de validación por lotes (Ejercicio 2.5)",
        multiline=True,
        min_lines=6,
        max_lines=10,
        read_only=True,
    )

    def validar_lote_ui(e: ft.ControlEvent) -> None:
        aut: AutomataFinito = estado_actual["automata"]  # type: ignore[assignment]
        r_in = (tf_lote_entrada.value or "").strip()
        r_out = (tf_lote_salida.value or "").strip()
        try:
            _, texto_rep = aut.validar_archivo_cadenas(r_in, r_out)
            tf_reporte_lote.value = texto_rep
            txt_estado_io.value = f"Reporte de lote generado y guardado en: {r_out}"
        except Exception as err:
            tf_reporte_lote.value = f"Error al procesar lote de cadenas: {err}"
        page.update()

    # =========================================================================
    # 3. OPERACIONES SOBRE CADENAS Y LENGUAJES (PRÁCTICA 1)
    # =========================================================================
    tf_cad_p1 = ft.TextField(label="Cadena w (Prefijos, Sufijos y Subcadenas)", value="abba", width=280)
    tf_alf_p1 = ft.TextField(label="Alfabeto Σ (para Σ* y Σ+)", value="0, 1", width=200)
    tf_len_p1 = ft.TextField(label="Longitud máx. n", value="3", width=130)
    tf_salida_p1 = ft.TextField(
        label="Resultados de Operaciones sobre Cadenas y Lenguajes (Práctica 1)",
        multiline=True,
        min_lines=4,
        max_lines=7,
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

    # Construcción visual de la interfaz
    page.add(
        ft.Text(
            "Práctica 3: Simulador de AFD, AFN, AFN-λ, Construcción de Subconjuntos y Minimización",
            size=22,
            weight=ft.FontWeight.BOLD,
        ),
        ft.Text(
            "Instituto Politécnico Nacional — Escuela Superior de Cómputo (ESCOM) — Teoría de la Computación",
            size=13,
        ),
        ft.Divider(),
        ft.Text("1. Definición, Importación/Exportación (.jff, .json, .xml) y Consulta de λ-Clausura (2.1)", size=17, weight=ft.FontWeight.BOLD),
        ft.Row([tf_alfabeto, tf_estados, tf_inicial, tf_aceptacion, dd_estado_clausura, txt_clausura_seleccionada], wrap=True),
        ft.Row(
            [
                tf_transiciones,
                ft.Column(
                    [
                        ft.ElevatedButton("Actualizar Autómata desde Tabla", on_click=aplicar_definicion_manual),
                        dd_casos_rapidos,
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
        ft.Text("2. Transformaciones Paso a Paso: Eliminación de λ (2.2), Subconjuntos (2.3), Minimización y Equivalencia (2.4)", size=17, weight=ft.FontWeight.BOLD),
        ft.Row(
            [
                ft.ElevatedButton("2.2 Eliminar Transiciones λ (AFN-λ → AFN)", on_click=ejecutar_eliminacion_lambda_ui),
                ft.ElevatedButton("2.3 Construcción de Subconjuntos (AFN → AFD)", on_click=ejecutar_subconjuntos_ui),
                ft.ElevatedButton("2.4 Minimizar AFD (Particiones y Tabla de Pares)", on_click=ejecutar_minimizacion_ui),
            ],
            wrap=True,
        ),
        ft.Row(
            [
                tf_ruta_afd2_eq,
                ft.OutlinedButton("2.4 Comparar Equivalencia con 2º AFD", on_click=comparar_equivalencia_ui),
            ],
            wrap=True,
        ),
        md_transformacion,
        ft.Divider(),
        ft.Text("3. Simulación Directa Paso a Paso mostrando Estados Antes y Después de λ-Clausura (2.1)", size=17, weight=ft.FontWeight.BOLD),
        ft.Row(
            [
                tf_cadena_sim,
                ft.ElevatedButton("Simular Directamente (Traza Completa)", on_click=ejecutar_simulacion_completa),
                ft.OutlinedButton("◀ Paso Anterior", on_click=paso_anterior),
                ft.OutlinedButton("Paso Siguiente ▶", on_click=paso_siguiente),
            ],
            wrap=True,
        ),
        txt_resultado_sim,
        txt_paso_actual,
        tf_traza_completa,
        ft.Divider(),
        ft.Text("4. Validación de Cadenas por Lotes desde Archivo .txt y Guardado de Reporte (2.5)", size=17, weight=ft.FontWeight.BOLD),
        ft.Row(
            [
                tf_lote_entrada,
                tf_lote_salida,
                ft.ElevatedButton("Validar Archivo de Cadenas y Guardar Reporte", on_click=validar_lote_ui),
            ],
            wrap=True,
        ),
        tf_reporte_lote,
        ft.Divider(),
        ft.Text("5. Operaciones sobre Cadenas y Lenguajes (Módulo de Práctica 1)", size=17, weight=ft.FontWeight.BOLD),
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
