"""Aplicación interactiva en Flet para las Prácticas 1, 2, 3 y 4:
Simulador de Autómatas Finitos (AFD, AFND, AFND-λ), Transformaciones, Minimización,
Conversión en Ambas Direcciones del Teorema de Kleene y Validadores de Expresiones Regulares.

Cumple todos los requisitos acumulados de las cuatro prácticas:
- Práctica 1: Operaciones sobre cadenas (`prefijos`, `sufijos`, `subcadenas`) y lenguajes (`Σ*`, `Σ+`).
- Práctica 2: Definición interactiva de la quíntupla, importación y exportación inversa en
  `.jff`, `.json` y `.xml`, y simulación con traza y bifurcaciones.
- Práctica 3 (Ejercicio 2):
  * 2.1: Cálculo de la λ-clausura de cada estado y simulación directa de un AFN-λ mostrando
    en cada paso los estados activos *antes* y *después* de aplicar la λ-clausura.
  * 2.2: Eliminación de transiciones λ (AFN-λ -> AFN).
  * 2.3: Construcción de subconjuntos alcanzables (AFN -> AFD).
  * 2.4: Minimización de AFD y decisión de equivalencia entre dos AFD.
  * 2.5: Validación de cadenas por lotes desde archivo `.txt` y guardado de reporte.
- Práctica 4 (Ejercicios 2, 3 y 4):
  * Ejercicio 2 (De expresión regular a autómata): Analizador sintáctico con la notación del curso
    (`+`, concatenación, `*`, `λ`, `∅`, paréntesis) que indica la posición exacta de cualquier error;
    construcción paso a paso del AFN-λ (Kleene Parte I / Thompson); encadenamiento con eliminación
    de λ, subconjuntos y minimización hasta obtener el AFD mínimo; exportación a `.jff` y validación
    de cadenas contra la expresión.
  * Ejercicio 3 (De autómata a expresión regular): Importación de un AFD desde `.jff` verificando
    que sea determinista (indicando qué estado y qué símbolo lo impiden en caso contrario);
    obtención de la expresión regular por eliminación de estados mostrando el GNFA después de cada
    estado eliminado; y comparación de equivalencia con la expresión de JFLAP de la Práctica 3
    mediante sus AFD mínimos.
  * Ejercicio 4 (Aplicaciones: validadores): Cuatro validadores (correo electrónico, teléfono
    nacional, URL y fecha en distintos formatos) con su expresión en la notación del curso, su
    traducción al módulo `re` de Python, el conteo de estados del AFD antes y después de minimizar,
    su justificación normativa y validación interactiva de texto.
"""

from __future__ import annotations

from pathlib import Path
import flet as ft

try:
    from automata import AutomataFinito, ResultadoSimulacion
    from expresiones import (
        CLASES_PREDEFINIDAS,
        ErrorSintaxisER,
        ResultadoEliminacionEstados,
        ResultadoERaAutomata,
        comparar_expresiones_por_afd_minimo,
        eliminacion_de_estados_detallada,
        er_a_automata_completo,
    )
    from formatos import (
        cargar_automata,
        guardar_automata,
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
    from validadores import (
        DECLARACION_CLASES_CURSO,
        ESPECIFICACIONES_VALIDADORES,
        obtener_validador,
        verificar_congruencia_validador,
    )
except ImportError:  # pragma: no cover
    from src.automata import AutomataFinito, ResultadoSimulacion
    from src.expresiones import (
        CLASES_PREDEFINIDAS,
        ErrorSintaxisER,
        ResultadoEliminacionEstados,
        ResultadoERaAutomata,
        comparar_expresiones_por_afd_minimo,
        eliminacion_de_estados_detallada,
        er_a_automata_completo,
    )
    from src.formatos import (
        cargar_automata,
        guardar_automata,
        guardar_en_tres_formatos,
    )
    from src.lenguajes import (
        LIMITE_CADENAS,
        cerradura_kleene,
        cerradura_positiva,
        formatear_cadena,
        normalizar_alfabeto,
        prefijos,
        subcadenas,
        sufijos,
    )
    from src.validadores import (
        DECLARACION_CLASES_CURSO,
        ESPECIFICACIONES_VALIDADORES,
        obtener_validador,
        verificar_congruencia_validador,
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

    # =========================================================================
    # 6. PRÁCTICA 4 — EJERCICIO 2: DE EXPRESIÓN REGULAR A AUTÓMATA (KLEENE I)
    # =========================================================================
    estado_p4_ej2: dict[str, object] = {
        "resultado": None,
        "paso_kleene_idx": 0,
    }

    casos_ej2_opciones = [
        ("241", "0 + 1", "0, 1", "Lista 3 - Ej. 241: 0 + 1"),
        ("242", "0* + 1", "0, 1", "Lista 3 - Ej. 242: 0* + 1"),
        ("243", "(0 + 1)*", "0, 1", "Lista 3 - Ej. 243: (0 + 1)*"),
        ("244", "0(0 + 1)", "0, 1", "Lista 3 - Ej. 244: 0(0 + 1)"),
        ("245", "0(0 + 1)*", "0, 1", "Lista 3 - Ej. 245: 0(0 + 1)*"),
        ("246", "0*(0 + 1)", "0, 1", "Lista 3 - Ej. 246: 0*(0 + 1)"),
        ("247", "(01)* + 1*", "0, 1", "Lista 3 - Ej. 247: (01)* + 1*"),
        ("248", "(0* + 1)0", "0, 1", "Lista 3 - Ej. 248: (0* + 1)0"),
        ("249", "(0* + 1)0*", "0, 1", "Lista 3 - Ej. 249: (0* + 1)0*"),
        ("250", "0*1* + 1*0", "0, 1", "Lista 3 - Ej. 250: 0*1* + 1*0"),
        ("251", "(0 + 1*)0 + 1*1", "0, 1", "Lista 3 - Ej. 251: (0 + 1*)0 + 1*1"),
        ("252", "(0 + 1)*(00 + 11) + (00 + 11)(0 + 1)*", "0, 1", "Lista 3 - Ej. 252: (0+1)*(00+11)+(00+11)(0+1)*"),
        ("253", "(0 + (11 + 00)*)(11 + 10 + 01)*(λ + 110)", "0, 1", "Lista 3 - Ej. 253: (0+(11+00)*)(11+10+01)*(λ+110)"),
        ("272a", "a + b*", "a, b", "Lista 4 - Ej. 272(a): a + b*"),
        ("272b", "(ab)*a", "a, b", "Lista 4 - Ej. 272(b)/273: (ab)*a"),
        ("272c", "(a + b)*abb", "a, b", "Lista 4 - Ej. 272(c)/273: (a + b)*abb"),
        ("272d", "a(ba)* + b", "a, b", "Lista 4 - Ej. 272(d): a(ba)* + b"),
        ("272e", "(a + λ)(b + ∅)", "a, b", "Lista 4 - Ej. 272(e): (a + λ)(b + ∅)"),
        ("278", "(a + b)*b", "a, b", "Lista 4 - Ej. 278: (a + b)*b"),
    ]
    mapa_casos_ej2 = {k: (er, alf) for k, er, alf, _ in casos_ej2_opciones}

    dd_casos_ej2 = ft.Dropdown(
        label="Caso de prueba (Lista 3: 241–253 / Lista 4: 272, 273, 278)",
        width=420,
        options=[ft.dropdown.Option(k, etiq) for k, _, _, etiq in casos_ej2_opciones],
        value="278",
    )
    tf_er_ej2 = ft.TextField(
        label="Expresión regular (notación del curso: +, concatenación, *, λ, ∅, paréntesis)",
        value="(a + b)*b",
        width=480,
    )
    tf_alf_ej2 = ft.TextField(label="Alfabeto Σ (opcional)", value="a, b", width=160)
    cb_clases_ej2 = ft.Checkbox(label="Activar clases declaradas (D, N, P, L, A, U, R, T, C)", value=False)
    txt_estado_ej2 = ft.Text(weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900)
    txt_paso_kleene_ej2 = ft.Text(weight=ft.FontWeight.BOLD, color=ft.Colors.INDIGO_900)
    md_detalle_ej2 = ft.Markdown(value="", selectable=True)

    tf_cadena_ej2 = ft.TextField(
        label="Cadena(s) a validar contra la expresión (separadas por coma; ej. 273: aba, ab, babb, abab)",
        value="aba, ab, babb, abab",
        width=520,
    )
    txt_validacion_ej2 = ft.Text(weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_900)

    def _tabla_md_compacta(aut: AutomataFinito) -> str:
        cols = list(aut.alfabeto) + (["λ"] if aut.tiene_transiciones_lambda else [])
        enc = "| Estado | " + " | ".join(f"`{c}`" for c in cols) + " |\n"
        sep = "| :--- | " + " | ".join(":---:" for _ in cols) + " |\n"
        filas = []
        for q in aut.estados:
            pref = ("→ " if q == aut.inicial else "") + ("* " if q in aut.aceptacion else "")
            celdas = []
            for c in cols:
                sym = "" if c == "λ" else c
                d = aut.destinos(q, sym)
                celdas.append("{" + ", ".join(d) + "}" if d else "∅")
            filas.append(f"| {pref}**{q}** | " + " | ".join(celdas) + " |")
        return enc + sep + "\n".join(filas)

    def actualizar_vista_paso_kleene_ej2() -> None:
        res: ResultadoERaAutomata | None = estado_p4_ej2["resultado"]  # type: ignore[assignment]
        if res is None or not res.kleene_uno.pasos:
            txt_paso_kleene_ej2.value = "Construya primero una expresión regular válida."
            md_detalle_ej2.value = ""
            return
        pasos = res.kleene_uno.pasos
        idx = max(0, min(int(estado_p4_ej2["paso_kleene_idx"]), len(pasos) - 1))  # type: ignore[arg-type]
        estado_p4_ej2["paso_kleene_idx"] = idx
        p = pasos[idx]
        txt_paso_kleene_ej2.value = (
            f"Pieza parcial {p.numero_paso}/{len(pasos)} — [{p.operacion}] Subexpresión: `{p.subexpresion}` "
            f"(ini={p.estado_inicial}, fin={p.estado_final}, |Q|={len(p.automata_parcial.estados)})"
        )
        lineas = [
            f"### Resumen de la tubería completa (Ejercicio 2) para `{res.kleene_uno.expresion_normalizada}`",
            f"- **Expresión analizada**: `{res.kleene_uno.expresion_normalizada}`  |  **Traducción `re` Python**: `{res.kleene_uno.regex_python}`",
            f"- **1) AFN-λ (Teorema de Kleene I / Thompson)**: `{len(res.afn_lambda.estados)}` estados (`q0={res.afn_lambda.inicial}`, `F={res.afn_lambda.aceptacion}`)",
            f"- **2) AFN sin transiciones λ (Práctica 3, 2.2)**: `{len(res.afn.estados)}` estados (`F={res.afn.aceptacion}`)",
            f"- **3) AFD por Construcción de Subconjuntos (Práctica 3, 2.3)**: `{len(res.afd.estados)}` estados alcanzables (`Q={res.afd.estados}`)",
            f"- **4) AFD Mínimo (Práctica 3, 2.4)**: `{len(res.afd_minimo.estados)}` estados (`Q={res.afd_minimo.estados}`, `F={res.afd_minimo.aceptacion}`)",
            "",
            f"### Pieza parcial {p.numero_paso} de {len(pasos)}: {p.operacion} sobre `{p.subexpresion}`",
            f"- {p.descripcion}",
            _tabla_md_compacta(p.automata_parcial),
            "",
            "### Tabla de transición del AFD Mínimo resultante",
            _tabla_md_compacta(res.afd_minimo),
        ]
        md_detalle_ej2.value = "\n".join(lineas)

    def construir_er_a_automata_ui(e: ft.ControlEvent | None = None) -> None:
        expr = (tf_er_ej2.value or "").strip()
        alf_raw = normalizar_alfabeto((tf_alf_ej2.value or "").split(","))
        clases = CLASES_PREDEFINIDAS if cb_clases_ej2.value else None
        try:
            res = er_a_automata_completo(expr, alfabeto=alf_raw or None, clases=clases)
            estado_p4_ej2["resultado"] = res
            estado_p4_ej2["paso_kleene_idx"] = len(res.kleene_uno.pasos) - 1
            txt_estado_ej2.color = ft.Colors.GREEN_900
            txt_estado_ej2.value = (
                f"Conversión exitosa: AFN-λ ({len(res.afn_lambda.estados)} estados, {len(res.kleene_uno.pasos)} piezas) "
                f"→ AFN ({len(res.afn.estados)} estados) → AFD ({len(res.afd.estados)} estados) "
                f"→ AFD mínimo ({len(res.afd_minimo.estados)} estados)."
            )
            actualizar_vista_paso_kleene_ej2()
            validar_cadenas_ej2_ui()
        except ErrorSintaxisER as err_sint:
            estado_p4_ej2["resultado"] = None
            txt_estado_ej2.color = ft.Colors.RED_800
            txt_estado_ej2.value = f"Expresión rechazada en la posición {err_sint.posicion}: {err_sint.detalle}"
            txt_paso_kleene_ej2.value = f"Posición exacta del error: carácter #{err_sint.posicion}"
            md_detalle_ej2.value = f"```text\n{err_sint}\n```"
        except Exception as err:
            txt_estado_ej2.color = ft.Colors.RED_800
            txt_estado_ej2.value = f"Error al construir autómata: {err}"
        page.update()

    def paso_kleene_anterior_ui(e: ft.ControlEvent) -> None:
        if estado_p4_ej2["resultado"] is not None:
            estado_p4_ej2["paso_kleene_idx"] = max(0, int(estado_p4_ej2["paso_kleene_idx"]) - 1)  # type: ignore[arg-type]
            actualizar_vista_paso_kleene_ej2()
            page.update()

    def paso_kleene_siguiente_ui(e: ft.ControlEvent) -> None:
        res: ResultadoERaAutomata | None = estado_p4_ej2["resultado"]  # type: ignore[assignment]
        if res is not None:
            estado_p4_ej2["paso_kleene_idx"] = min(
                len(res.kleene_uno.pasos) - 1, int(estado_p4_ej2["paso_kleene_idx"]) + 1  # type: ignore[arg-type]
            )
            actualizar_vista_paso_kleene_ej2()
            page.update()

    def exportar_jff_ej2_ui(e: ft.ControlEvent) -> None:
        res: ResultadoERaAutomata | None = estado_p4_ej2["resultado"]  # type: ignore[assignment]
        if res is None:
            txt_estado_ej2.value = "Construya primero una expresión regular antes de exportar a .jff."
            page.update()
            return
        DIR_EXPORT.mkdir(parents=True, exist_ok=True)
        r1 = guardar_automata(res.afn_lambda, DIR_EXPORT / "ej2_afn_lambda.jff")
        r2 = guardar_automata(res.afn, DIR_EXPORT / "ej2_afn_sin_lambda.jff")
        r3 = guardar_automata(res.afd, DIR_EXPORT / "ej2_afd_subconjuntos.jff")
        r4 = guardar_automata(res.afd_minimo, DIR_EXPORT / "ej2_afd_minimo.jff")
        estado_actual["automata"] = res.afd_minimo
        sincronizar_controles_desde_automata(res.afd_minimo)
        txt_estado_ej2.value = (
            f"Exportados en .jff: {r1.as_posix()}, {r2.as_posix()}, {r3.as_posix()} y {r4.as_posix()} "
            "(AFD mínimo cargado en el editor principal)."
        )
        page.update()

    def validar_cadenas_ej2_ui(e: ft.ControlEvent | None = None) -> None:
        res: ResultadoERaAutomata | None = estado_p4_ej2["resultado"]  # type: ignore[assignment]
        if res is None:
            txt_validacion_ej2.value = "Construya primero el autómata de la expresión regular."
            page.update()
            return
        partes = [p.strip() for p in (tf_cadena_ej2.value or "").split(",")]
        if not partes:
            partes = [""]
        resumenes = []
        for cad_raw in partes:
            cad = "" if cad_raw in ("λ", "lambda", "epsilon", "ε") else cad_raw
            mostrada = "λ" if cad == "" else cad
            sim_lambda = res.afn_lambda.simular(cad)
            ok_min = res.afd_minimo.acepta(cad)
            veredicto = "ACEPTADA" if ok_min else "RECHAZADA"
            resumenes.append(
                f"'{mostrada}': {veredicto} (AFN-λ activos finales={sim_lambda.pasos[-1].estados_despues_de_lambda}, AFD_min={ok_min})"
            )
        txt_validacion_ej2.value = "  |  ".join(resumenes)
        page.update()

    def seleccionar_caso_ej2_ui(e: ft.ControlEvent) -> None:
        k = dd_casos_ej2.value
        if k and k in mapa_casos_ej2:
            er_str, alf_str = mapa_casos_ej2[k]
            tf_er_ej2.value = er_str
            tf_alf_ej2.value = alf_str
            construir_er_a_automata_ui()

    dd_casos_ej2.on_change = seleccionar_caso_ej2_ui

    # =========================================================================
    # 7. PRÁCTICA 4 — EJERCICIO 3: DE AUTÓMATA A EXPRESIÓN REGULAR (GNFA)
    # =========================================================================
    estado_p4_ej3: dict[str, object] = {
        "resultado_gnfa": None,
        "paso_gnfa_idx": 0,
    }

    casos_ej3_opciones = [
        ("automatas/practica4/afd-a-er/ej254_termina_en_1.jff", "0*1(1+00*1)*", "Lista 3 / Prác. 3 - Ej. 254 (termina en 1)"),
        ("automatas/practica4/afd-a-er/ej255_ciclo_par_b.jff", "((0+1)1*0)*", "Lista 3 / Prác. 3 - Ej. 255 (ciclo par en B)"),
        ("automatas/practica4/afd-a-er/ej256_ternario.jff", "(1+2)*0(0+1+2(1+2)*0)*", "Lista 3 / Prác. 3 - Ej. 256 (alfabeto {0,1,2})"),
        ("automatas/practica4/afd-a-er/ej257_tres_estados_bc.jff", "((1+01*0)(0+1))*01*+((1+01*0)(0+1))*(1+01*0)", "Lista 3 / Prác. 3 - Ej. 257 (finales B y C)"),
        ("automatas/practica4/afd-a-er/ej258_tres_estados_c.jff", "(0+1)(01+(1+00)(0+1))*", "Lista 3 / Prác. 3 - Ej. 258 (final C)"),
        ("automatas/practica4/afd-a-er/ej276_multiplo_3_a.jff", "(b+ab*ab*a)*", "Lista 4 - Ej. 276 (número de 'a' múltiplo de 3)"),
        ("automatas/practica4/afd-a-er/ej277_termina_en_1.jff", "0*1(1+00*1)*", "Lista 4 - Ej. 277 (termina en 1 sobre {0,1})"),
        ("automatas/practica3/casos-de-prueba/ej196_afnd_lambda.jff", "", "Prueba negativa no determinista: Ej. 196 (AFN-λ)"),
    ]
    mapa_casos_ej3 = {ruta: er_ref for ruta, er_ref, _ in casos_ej3_opciones}

    dd_casos_ej3 = ft.Dropdown(
        label="Seleccionar archivo .jff (Lista 3: 254–258, Lista 4: 276–277)",
        width=450,
        options=[ft.dropdown.Option(r, etiq) for r, _, etiq in casos_ej3_opciones],
        value="automatas/practica4/afd-a-er/ej276_multiplo_3_a.jff",
    )
    tf_ruta_jff_ej3 = ft.TextField(
        label="Ruta del archivo .jff a importar para eliminación de estados",
        value="automatas/practica4/afd-a-er/ej276_multiplo_3_a.jff",
        width=440,
    )
    tf_er_jflap_ej3 = ft.TextField(
        label="Expresión de referencia (ej. JFLAP Práctica 3) para probar equivalencia con Ejercicio 2",
        value="(b+ab*ab*a)*",
        width=460,
    )
    txt_verif_afd_ej3 = ft.Text(weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900)
    txt_paso_gnfa_ej3 = ft.Text(weight=ft.FontWeight.BOLD, color=ft.Colors.INDIGO_900)
    md_gnfa_ej3 = ft.Markdown(value="", selectable=True)

    def actualizar_vista_gnfa_ej3() -> None:
        res_g: ResultadoEliminacionEstados | None = estado_p4_ej3["resultado_gnfa"]  # type: ignore[assignment]
        if res_g is None or not res_g.pasos_gnfa:
            return
        pasos = res_g.pasos_gnfa
        idx = max(0, min(int(estado_p4_ej3["paso_gnfa_idx"]), len(pasos) - 1))  # type: ignore[arg-type]
        estado_p4_ej3["paso_gnfa_idx"] = idx
        pg = pasos[idx]
        txt_paso_gnfa_ej3.value = (
            f"GNFA paso {pg.numero_paso}/{len(pasos) - 1} — "
            + (f"Estado eliminado: '{pg.estado_eliminado}' (bucle={pg.expresion_bucle})" if pg.estado_eliminado else "GNFA inicial")
            + f"  |  Expresión final obtenida: `{res_g.expresion_texto}`"
        )
        lineas = [
            f"### Expresión regular obtenida por Eliminación de Estados: `{res_g.expresion_texto}`",
            f"- **Orden de eliminación de estados**: `{res_g.orden_eliminacion}`",
            f"- **{pg.resumen_paso}**",
            "",
            f"#### Matriz de transiciones generalizadas del GNFA (Paso {pg.numero_paso})",
            pg.tabla_markdown,
        ]
        er_ref = (tf_er_jflap_ej3.value or "").strip()
        if er_ref:
            try:
                comp = comparar_expresiones_por_afd_minimo(
                    res_g.expresion_texto,
                    er_ref,
                    alfabeto=res_g.afd_origen.alfabeto,
                )
                lineas.extend(
                    [
                        "",
                        "### Comparación de equivalencia con la expresión de JFLAP / Referencia (vía Ejercicio 2 + Práctica 3)",
                        f"- **Expresión 1 (Eliminación de estados)**: `{comp.expresion_1}` → AFD mínimo de `{len(comp.tuberia_1.afd_minimo.estados)}` estados",
                        f"- **Expresión 2 (JFLAP / Referencia)**: `{comp.expresion_2}` → AFD mínimo de `{len(comp.tuberia_2.afd_minimo.estados)}` estados",
                        f"- **Resultado de equivalencia (`son_afd_equivalentes`)**: **{'EQUIVALENTES' if comp.equivalentes else 'NO EQUIVALENTES'}** — {comp.equivalencia_afd.justificacion}",
                    ]
                )
            except Exception as err_eq:
                lineas.append(f"\n- *Aviso al comparar con expresión de referencia*: {err_eq}")
        md_gnfa_ej3.value = "\n".join(lineas)

    def ejecutar_afd_a_er_ui(e: ft.ControlEvent | None = None) -> None:
        ruta = (tf_ruta_jff_ej3.value or "").strip()
        try:
            aut = cargar_automata(ruta)
            verif = aut.verificar_determinismo()
            if not verif.es_determinista:
                estado_p4_ej3["resultado_gnfa"] = None
                txt_verif_afd_ej3.color = ft.Colors.RED_800
                txt_verif_afd_ej3.value = verif.mensaje
                txt_paso_gnfa_ej3.value = (
                    f"Conversión detenida: estado '{verif.primer_estado_conflicto}' con símbolo "
                    f"'{verif.primer_simbolo_conflicto}' impide el determinismo."
                )
                md_gnfa_ej3.value = (
                    "### Verificación de Determinismo Fallida\n"
                    + "\n".join(f"- **{v.motivo}**" for v in verif.violaciones)
                )
                page.update()
                return

            res_g = eliminacion_de_estados_detallada(aut)
            estado_p4_ej3["resultado_gnfa"] = res_g
            estado_p4_ej3["paso_gnfa_idx"] = len(res_g.pasos_gnfa) - 1
            txt_verif_afd_ej3.color = ft.Colors.GREEN_900
            txt_verif_afd_ej3.value = (
                f"{verif.mensaje}  |  Expresión regular obtenida: {res_g.expresion_texto}"
            )
            actualizar_vista_gnfa_ej3()
        except Exception as err:
            txt_verif_afd_ej3.color = ft.Colors.RED_800
            txt_verif_afd_ej3.value = f"Error en Ejercicio 3: {err}"
        page.update()

    def paso_gnfa_anterior_ui(e: ft.ControlEvent) -> None:
        if estado_p4_ej3["resultado_gnfa"] is not None:
            estado_p4_ej3["paso_gnfa_idx"] = max(0, int(estado_p4_ej3["paso_gnfa_idx"]) - 1)  # type: ignore[arg-type]
            actualizar_vista_gnfa_ej3()
            page.update()

    def paso_gnfa_siguiente_ui(e: ft.ControlEvent) -> None:
        res_g: ResultadoEliminacionEstados | None = estado_p4_ej3["resultado_gnfa"]  # type: ignore[assignment]
        if res_g is not None:
            estado_p4_ej3["paso_gnfa_idx"] = min(
                len(res_g.pasos_gnfa) - 1, int(estado_p4_ej3["paso_gnfa_idx"]) + 1  # type: ignore[arg-type]
            )
            actualizar_vista_gnfa_ej3()
            page.update()

    def seleccionar_caso_ej3_ui(e: ft.ControlEvent) -> None:
        r = dd_casos_ej3.value
        if r:
            tf_ruta_jff_ej3.value = r
            tf_er_jflap_ej3.value = mapa_casos_ej3.get(r, "")
            ejecutar_afd_a_er_ui()

    dd_casos_ej3.on_change = seleccionar_caso_ej3_ui

    # =========================================================================
    # 8. PRÁCTICA 4 — EJERCICIO 4: APLICACIONES — VALIDADORES
    # =========================================================================
    dd_validador_ej4 = ft.Dropdown(
        label="Seleccionar validador (Ejercicio 4)",
        width=460,
        options=[
            ft.dropdown.Option(k, esp.titulo)
            for k, esp in ESPECIFICACIONES_VALIDADORES.items()
        ],
        value="correo",
    )
    tf_texto_ej4 = ft.TextField(
        label="Texto a validar con el autómata obtenido en el Ejercicio 2",
        value="cesar.navarro@alumno.ipn.mx",
        width=460,
    )
    dd_ejemplos_ej4 = ft.Dropdown(label="Cargar ejemplo de prueba rápido", width=360)
    txt_resultado_ej4 = ft.Text(weight=ft.FontWeight.BOLD, size=15, color=ft.Colors.GREEN_900)
    md_ficha_ej4 = ft.Markdown(value="", selectable=True)

    def actualizar_ficha_validador_ej4(ejecutar_congruencia: bool = False) -> None:
        clave = dd_validador_ej4.value or "correo"
        val = obtener_validador(clave)
        esp = val.especificacion

        opciones_ej = [
            ft.dropdown.Option(ej, f"[Válido] {ej}") for ej in esp.ejemplos_validos
        ] + [
            ft.dropdown.Option(ej, f"[Inválido] {ej}") for ej in esp.ejemplos_invalidos
        ]
        dd_ejemplos_ej4.options = opciones_ej

        res_val = val.validar(tf_texto_ej4.value or "")
        txt_resultado_ej4.color = ft.Colors.GREEN_900 if res_val.aceptada_automata else ft.Colors.RED_800
        txt_resultado_ej4.value = res_val.detalle

        clases_doc = [
            f"  - `{c} = {DECLARACION_CLASES_CURSO[c].definicion_curso}` (`{DECLARACION_CLASES_CURSO[c].equivalente_regex_python}` — {DECLARACION_CLASES_CURSO[c].descripcion})"
            for c in esp.clases_empleadas
            if c in DECLARACION_CLASES_CURSO
        ]
        linea_cong = ""
        if ejecutar_congruencia:
            cong = verificar_congruencia_validador(clave, total=500, semilla=2026)
            linea_cong = (
                f"\n- **Prueba de congruencia sobre {cong.total_cadenas} cadenas ({cong.total_validas} válidas + "
                f"{cong.total_invalidas} inválidas)**: Coincidencias AFD mínimo vs `re.fullmatch` = "
                f"**{cong.coincidencias_afd_minimo_vs_re}/{cong.total_cadenas}** (`congruente={cong.congruente}`)."
            )

        md_ficha_ej4.value = "\n".join(
            [
                f"### {esp.titulo}",
                f"- **Expresión en la notación del curso**: `{esp.expresion_curso}`",
                f"- **Traducción a la sintaxis del módulo `re` de Python**: `{val.regex_python}`",
                "- **Clases de símbolos declaradas**:",
                *clases_doc,
                f"- **Autómata del Ejercicio 2**: AFN-λ = `{len(val.afn_lambda.estados)}` estados  |  "
                f"**AFD antes de minimizar = `{val.estados_afd_antes_minimizar}` estados**  |  "
                f"**AFD después de minimizar = `{val.estados_afd_despues_minimizar}` estados**"
                + linea_cong,
                f"- **Norma o estándar consultado**: {esp.norma_consultada}",
                f"- **Casos válidos cubiertos**: {esp.casos_validos_cubiertos}",
                f"- **Justificación de casos válidos o inválidos que quedan fuera de la expresión**: {esp.casos_fuera_de_la_expresion}",
            ]
        )

    def cambiar_validador_ej4_ui(e: ft.ControlEvent) -> None:
        clave = dd_validador_ej4.value or "correo"
        esp = ESPECIFICACIONES_VALIDADORES[clave]
        if esp.ejemplos_validos:
            tf_texto_ej4.value = esp.ejemplos_validos[0]
        actualizar_ficha_validador_ej4(ejecutar_congruencia=False)
        page.update()

    def elegir_ejemplo_ej4_ui(e: ft.ControlEvent) -> None:
        if dd_ejemplos_ej4.value is not None:
            tf_texto_ej4.value = dd_ejemplos_ej4.value
            actualizar_ficha_validador_ej4(ejecutar_congruencia=False)
            page.update()

    def validar_texto_ej4_ui(e: ft.ControlEvent) -> None:
        actualizar_ficha_validador_ej4(ejecutar_congruencia=False)
        page.update()

    def probar_500_cadenas_ej4_ui(e: ft.ControlEvent) -> None:
        actualizar_ficha_validador_ej4(ejecutar_congruencia=True)
        page.update()

    dd_validador_ej4.on_change = cambiar_validador_ej4_ui
    dd_ejemplos_ej4.on_change = elegir_ejemplo_ej4_ui

    page.title = "Práctica 4 - Expresiones Regulares, Teorema de Kleene (Ambas Direcciones) y Validadores"

    # Construcción visual de la interfaz
    page.add(
        ft.Text(
            "Práctica 4: Uso de las Expresiones Regulares y Extensión de Software para Convertir Expresiones Regulares",
            size=22,
            weight=ft.FontWeight.BOLD,
        ),
        ft.Text(
            "Instituto Politécnico Nacional — Escuela Superior de Cómputo (ESCOM) — Teoría de la Computación (Prácticas 1, 2, 3 y 4)",
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
        ft.Divider(),
        ft.Text("6. Práctica 4 — Ejercicio 2: De Expresión Regular a Autómata (AFN-λ → AFN → AFD → AFD Mínimo)", size=17, weight=ft.FontWeight.BOLD),
        ft.Row([dd_casos_ej2, tf_er_ej2, tf_alf_ej2, cb_clases_ej2], wrap=True),
        ft.Row(
            [
                ft.ElevatedButton("Construir AFN-λ, AFN, AFD y AFD Mínimo", on_click=construir_er_a_automata_ui),
                ft.OutlinedButton("◀ Pieza Parcial Anterior", on_click=paso_kleene_anterior_ui),
                ft.OutlinedButton("Pieza Parcial Siguiente ▶", on_click=paso_kleene_siguiente_ui),
                ft.OutlinedButton("Exportar Autómatas a .jff", on_click=exportar_jff_ej2_ui),
            ],
            wrap=True,
        ),
        ft.Row(
            [
                tf_cadena_ej2,
                ft.ElevatedButton("Validar Cadena(s) con el Autómata", on_click=validar_cadenas_ej2_ui),
            ],
            wrap=True,
        ),
        txt_estado_ej2,
        txt_validacion_ej2,
        txt_paso_kleene_ej2,
        md_detalle_ej2,
        ft.Divider(),
        ft.Text("7. Práctica 4 — Ejercicio 3: De Autómata a Expresión Regular (Eliminación de Estados GNFA y Equivalencia)", size=17, weight=ft.FontWeight.BOLD),
        ft.Row([dd_casos_ej3, tf_ruta_jff_ej3, tf_er_jflap_ej3], wrap=True),
        ft.Row(
            [
                ft.ElevatedButton("Importar .jff, Verificar Determinismo y Eliminar Estados", on_click=ejecutar_afd_a_er_ui),
                ft.OutlinedButton("◀ Estado GNFA Anterior", on_click=paso_gnfa_anterior_ui),
                ft.OutlinedButton("Estado GNFA Siguiente ▶", on_click=paso_gnfa_siguiente_ui),
            ],
            wrap=True,
        ),
        txt_verif_afd_ej3,
        txt_paso_gnfa_ej3,
        md_gnfa_ej3,
        ft.Divider(),
        ft.Text("8. Práctica 4 — Ejercicio 4: Aplicaciones — Validadores Basados en Expresiones Regulares", size=17, weight=ft.FontWeight.BOLD),
        ft.Row([dd_validador_ej4, dd_ejemplos_ej4, tf_texto_ej4], wrap=True),
        ft.Row(
            [
                ft.ElevatedButton("Validar Texto con el Autómata (Ejercicio 2)", on_click=validar_texto_ej4_ui),
                ft.OutlinedButton("Comprobar Congruencia en 500 Cadenas vs re.fullmatch", on_click=probar_500_cadenas_ej4_ui),
            ],
            wrap=True,
        ),
        txt_resultado_ej4,
        md_ficha_ej4,
    )

    sincronizar_controles_desde_automata(estado_actual["automata"])  # type: ignore[arg-type]
    ejecutar_simulacion_completa()
    calcular_operaciones_p1()
    construir_er_a_automata_ui()
    ejecutar_afd_a_er_ui()
    actualizar_ficha_validador_ej4(ejecutar_congruencia=False)


if __name__ == "__main__":
    ft.run(main)
