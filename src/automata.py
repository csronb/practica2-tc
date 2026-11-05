"""Módulo `automata.py`: Modelo de datos y algoritmos para AFD, AFND y AFND-lambda.

Este módulo es puro (sin dependencias de Flet ni bibliotecas externas de autómatas) y proporciona:
- Clase `AutomataFinito`: Representación de la quíntupla M = (Q, Σ, δ, q0, F).
- Clasificación automática e inspección del tipo ("AFD", "AFND", "AFND-lambda").
- 2.1: Cálculo de la λ-clausura (`lambda_clausura_estado`, `lambda_clausura`, `tabla_lambda_clausuras`)
  y simulación directa de un AFN-λ (`simular_directo_afnd_lambda` y `simular`) mostrando en cada paso
  los estados activos *antes* y *después* de aplicar la λ-clausura.
- 2.2: Eliminación de transiciones λ (`eliminar_transiciones_lambda_detallado` y
  `convertir_afnd_lambda_a_afnd`) mostrando explícitamente las transiciones añadidas y los
  estados que pasan a ser de aceptación.
- 2.3: Construcción de subconjuntos (`construccion_subconjuntos_detallada` y `convertir_a_afd`)
  construyendo únicamente los subconjuntos alcanzables desde el estado inicial, mostrando la
  tabla de transición conforme se genera e indicando qué subconjuntos resultan de aceptación y por qué.
- 2.4: Minimización de AFD y equivalencia (`minimizar_afd_detallado`, `minimizar_afd` y
  `son_afd_equivalentes`) eliminando estados inaccesibles y obteniendo el AFD mínimo mediante
  refinamiento de particiones y tabla de pares distinguibles ronda por ronda, además de decidir
  si dos AFD son equivalentes por isomorfismo canónico de sus AFD mínimos.
- 2.5: Validación de cadenas desde archivo (`validar_archivo_cadenas`) leyendo un archivo `.txt`
  con una cadena por línea y guardando un reporte detallado con el resultado de cada una.
- Herramientas algebraicas puras para verificación de conversión de AFD a Expresión Regular
  (eliminación de estados, matriz recursiva R_ij^(k) de Kleene y sistema de ecuaciones de Arden).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class PasoSimulacion:
    """Representa un paso en la traza de ejecución del autómata.

    Incluye `estados_antes_de_lambda` (δ directo con el símbolo leído) y
    `estados_despues_de_lambda` (tras aplicar Cl_λ) para satisfacer el requisito 2.1.
    """

    indice: int
    simbolo: str  # "λ" para paso inicial (λ-clausura inicial)
    estados_origen: list[str]
    estados_destino: list[str]
    transiciones_tomadas: list[str]
    estados_antes_de_lambda: list[str] = field(default_factory=list)
    estados_despues_de_lambda: list[str] = field(default_factory=list)


@dataclass
class ResultadoSimulacion:
    """Resultado completo de validar una cadena en un autómata finito."""

    cadena: str
    aceptada: bool
    estados_finales_alcanzados: list[str]
    pasos: list[PasoSimulacion]
    caminos: list[list[str]]


@dataclass
class ResultadoEliminacionLambda:
    """Detalle paso a paso de la eliminación de transiciones λ (Ejercicio 2.2)."""

    automata_sin_lambda: AutomataFinito
    clausuras: dict[str, list[str]]
    transiciones_originales_sin_lambda: list[tuple[str, str, str]]
    transiciones_anadidas: list[tuple[str, str, str, str]]  # (origen, simbolo, destino, justificacion)
    estados_aceptacion_originales: list[str]
    nuevos_estados_aceptacion: list[tuple[str, str]]  # (estado, justificacion: qué estado final alcanza vía λ)


@dataclass
class FilaSubconjunto:
    """Representa una fila de la tabla de transición generada durante la construcción de subconjuntos (Ejercicio 2.3)."""

    orden_descubrimiento: int
    nombre_estado: str
    subconjunto: list[str]
    transiciones_por_simbolo: dict[str, tuple[list[str], str]]  # simbolo -> (mov_directo_con_clausura, nombre_subconjunto_destino)
    es_inicial: bool
    es_aceptacion: bool
    razon_aceptacion: str


@dataclass
class ResultadoSubconjuntos:
    """Detalle completo de la construcción de subconjuntos alcanzables (Ejercicio 2.3)."""

    afd: AutomataFinito
    estado_inicial_subconjunto: list[str]
    filas: list[FilaSubconjunto]
    subconjuntos_aceptacion_justificacion: dict[str, str]


@dataclass
class RondaParticion:
    """Representa una ronda en el refinamiento de particiones de Hopcroft/Moore (Ejercicio 2.4)."""

    numero_ronda: int
    grupos: list[list[str]]
    divisiones_realizadas: list[str]


@dataclass
class RondaTablaPares:
    """Representa una ronda en el algoritmo de la tabla de pares distinguibles (Ejercicio 2.4)."""

    numero_ronda: int
    pares_marcados_en_ronda: list[tuple[str, str, str]]  # (p, q, motivo)
    matriz_actual: dict[tuple[str, str], str]  # (p, q) con p < q -> "" (no marcado) o "X (ronda k: motivo)"


@dataclass
class ResultadoMinimizacion:
    """Detalle completo de la minimización de un AFD (Ejercicio 2.4)."""

    afd_original: AutomataFinito
    estados_accesibles: list[str]
    estados_inaccesibles_eliminados: list[str]
    afd_accesible_completo: AutomataFinito
    rondas_particion: list[RondaParticion]
    rondas_tabla_pares: list[RondaTablaPares]
    pares_equivalentes: list[tuple[str, str]]
    clases_equivalencia: list[list[str]]
    afd_minimo: AutomataFinito


@dataclass
class ResultadoEquivalenciaAFD:
    """Resultado de decidir si dos AFD son equivalentes a partir de sus AFD mínimos (Ejercicio 2.4)."""

    equivalentes: bool
    min_afd1: ResultadoMinimizacion
    min_afd2: ResultadoMinimizacion
    biyeccion_estados: dict[str, str]
    testigo_diferencia: str | None
    justificacion: str


@dataclass
class LineaReporteCadena:
    """Resultado de validar una cadena individual dentro de un lote por archivo (Ejercicio 2.5)."""

    numero_linea: int
    cadena_original: str
    cadena_mostrada: str
    aceptada: bool
    estados_finales: list[str]


@dataclass
class AutomataFinito:
    """Representa un Autómata Finito (AFD, AFND o AFND-lambda) como quíntupla."""

    alfabeto: list[str]
    estados: list[str]
    inicial: str
    aceptacion: list[str]
    # transiciones: dict[(estado_origen, simbolo_o_vacio), list[estado_destino]]
    transiciones: dict[tuple[str, str], list[str]] = field(default_factory=dict)
    tipo_declarado: str | None = None
    coordenadas: dict[str, tuple[float, float]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # Normalizar listas sin perder el orden
        self.alfabeto = list(dict.fromkeys(s for s in self.alfabeto if s != ""))
        self.estados = list(dict.fromkeys(self.estados))
        self.aceptacion = [e for e in dict.fromkeys(self.aceptacion) if e in self.estados]
        if self.inicial and self.inicial not in self.estados and self.estados:
            self.inicial = self.estados[0]

        trans_limpias: dict[tuple[str, str], list[str]] = {}
        for (u, sym), destinos in self.transiciones.items():
            if u not in self.estados:
                continue
            dest_unicos = [v for v in dict.fromkeys(destinos) if v in self.estados]
            if dest_unicos:
                trans_limpias[(u, sym)] = dest_unicos
        self.transiciones = trans_limpias

    @property
    def tiene_transiciones_lambda(self) -> bool:
        """Indica si existe al menos una transición con símbolo vacío '' (λ)."""
        return any(sym == "" and len(dest) > 0 for (_, sym), dest in self.transiciones.items())

    @property
    def es_determinista(self) -> bool:
        """Verifica si el autómata carece de λ y tiene a lo sumo 1 destino por par (q, a)."""
        if self.tiene_transiciones_lambda:
            return False
        for (_, sym), dest in self.transiciones.items():
            if len(dest) > 1:
                return False
        return True

    @property
    def tipo(self) -> str:
        """Determina el tipo del autómata ('AFD', 'AFND' o 'AFND-lambda')."""
        if self.tiene_transiciones_lambda:
            return "AFND-lambda"
        if not self.es_determinista or self.tipo_declarado == "AFND":
            return "AFND"
        if self.tipo_declarado in ("AFD", "AFND", "AFND-lambda"):
            return self.tipo_declarado
        return "AFD"

    def destinos(self, estado: str, simbolo: str) -> list[str]:
        """Devuelve la lista de estados destino δ(estado, simbolo)."""
        return list(self.transiciones.get((estado, simbolo), []))

    def agregar_transicion(self, desde: str, simbolo: str, hacia: str) -> None:
        """Agrega una transición δ(desde, simbolo) -> hacia."""
        if desde not in self.estados:
            self.estados.append(desde)
        if hacia not in self.estados:
            self.estados.append(hacia)
        if simbolo != "" and simbolo not in self.alfabeto:
            self.alfabeto.append(simbolo)
        actuales = self.transiciones.setdefault((desde, simbolo), [])
        if hacia not in actuales:
            actuales.append(hacia)

    # =========================================================================
    # 2.1 CLAUSURA LAMBDA Y SIMULACIÓN DIRECTA DE AFN-λ
    # =========================================================================

    def lambda_clausura_estado(self, estado: str) -> list[str]:
        """Calcula Cl_λ({estado}) mediante búsqueda en anchura (BFS)."""
        if estado not in self.estados:
            return []
        visitados: set[str] = {estado}
        orden: list[str] = [estado]
        cola: list[str] = [estado]
        while cola:
            u = cola.pop(0)
            for v in self.destinos(u, ""):
                if v not in visitados:
                    visitados.add(v)
                    orden.append(v)
                    cola.append(v)
        pos = {e: i for i, e in enumerate(self.estados)}
        return sorted(orden, key=lambda x: pos.get(x, 9999))

    def lambda_clausura(self, estados_base: list[str] | set[str]) -> list[str]:
        """Calcula Cl_λ(Z) = ∪_{q ∈ Z} Cl_λ({q})."""
        acumulado: set[str] = set()
        for q in estados_base:
            acumulado.update(self.lambda_clausura_estado(q))
        pos = {e: i for i, e in enumerate(self.estados)}
        return sorted(acumulado, key=lambda x: pos.get(x, 9999))

    def tabla_lambda_clausuras(self) -> dict[str, list[str]]:
        """Devuelve un diccionario {estado: Cl_λ({estado})} para todos los estados."""
        return {q: self.lambda_clausura_estado(q) for q in self.estados}

    def delta_extendida(self, estados_inicio: list[str] | set[str] | str, cadena: str) -> list[str]:
        """Calcula δ̂(Z, w) desde cualquier estado o conjunto inicial Z."""
        if isinstance(estados_inicio, str):
            base = [estados_inicio]
        else:
            base = list(estados_inicio)
        activos = self.lambda_clausura(base)
        for ch in cadena:
            if ch not in self.alfabeto:
                return []
            mov: set[str] = set()
            for q in activos:
                mov.update(self.destinos(q, ch))
            activos = self.lambda_clausura(mov)
        return activos

    def simular(self, cadena: str, max_caminos: int = 32) -> ResultadoSimulacion:
        """Simula directamente una cadena paso a paso mostrando estados antes y después de λ-clausura."""
        pos = {e: i for i, e in enumerate(self.estados)}
        antes_ini = [self.inicial] if self.inicial else []
        activos = self.lambda_clausura(antes_ini)

        trans_ini: list[str] = []
        if len(activos) > 1:
            for q in activos:
                if q != self.inicial:
                    trans_ini.append(f"{self.inicial} --λ*--> {q}")
        else:
            trans_ini.append(f"Inicio en {self.inicial}")

        pasos: list[PasoSimulacion] = [
            PasoSimulacion(
                indice=0,
                simbolo="λ",
                estados_origen=antes_ini,
                estados_destino=activos,
                transiciones_tomadas=trans_ini,
                estados_antes_de_lambda=antes_ini,
                estados_despues_de_lambda=activos,
            )
        ]

        caminos_actuales: list[list[str]] = [[q] for q in activos]

        for idx, ch in enumerate(cadena, start=1):
            if ch not in self.alfabeto:
                pasos.append(
                    PasoSimulacion(
                        indice=idx,
                        simbolo=ch,
                        estados_origen=activos,
                        estados_destino=[],
                        transiciones_tomadas=[f"Símbolo '{ch}' fuera del alfabeto Σ"],
                        estados_antes_de_lambda=[],
                        estados_despues_de_lambda=[],
                    )
                )
                activos = []
                caminos_actuales = []
                break

            siguientes_directos: set[str] = set()
            detalle_trans: list[str] = []
            nuevos_caminos: list[list[str]] = []

            for u in activos:
                dest_u = self.destinos(u, ch)
                for v in dest_u:
                    siguientes_directos.add(v)
                    cl_v = self.lambda_clausura_estado(v)
                    if len(cl_v) > 1:
                        detalle_trans.append(f"δ({u}, {ch}) → {v} ⇒ Cl_λ({v})={cl_v}")
                    else:
                        detalle_trans.append(f"δ({u}, {ch}) → {v}")

                    for cam in caminos_actuales:
                        if cam[-1] == u and len(nuevos_caminos) < max_caminos:
                            for w_cl in cl_v:
                                etiqueta = f"{v}(via λ→{w_cl})" if w_cl != v else v
                                nuevos_caminos.append(cam + [f"--{ch}--> {etiqueta}", w_cl])

            antes_lambda = sorted(siguientes_directos, key=lambda x: pos.get(x, 9999))
            despues_lambda = self.lambda_clausura(antes_lambda)
            if not detalle_trans:
                detalle_trans.append(f"∅ (sin transiciones con '{ch}' desde {activos})")

            pasos.append(
                PasoSimulacion(
                    indice=idx,
                    simbolo=ch,
                    estados_origen=activos,
                    estados_destino=despues_lambda,
                    transiciones_tomadas=detalle_trans,
                    estados_antes_de_lambda=antes_lambda,
                    estados_despues_de_lambda=despues_lambda,
                )
            )
            activos = sorted(despues_lambda, key=lambda x: pos.get(x, 9999))
            caminos_actuales = nuevos_caminos[:max_caminos]

        finales_alcanzados = [q for q in activos if q in self.aceptacion]
        aceptada = len(finales_alcanzados) > 0

        return ResultadoSimulacion(
            cadena=cadena,
            aceptada=aceptada,
            estados_finales_alcanzados=finales_alcanzados,
            pasos=pasos,
            caminos=list(caminos_actuales),
        )

    def simular_directo_afnd_lambda(self, cadena: str) -> ResultadoSimulacion:
        """Alias explícito para el Ejercicio 2.1: simula un AFN-λ sin convertirlo."""
        return self.simular(cadena)

    def acepta(self, cadena: str) -> bool:
        """Devuelve True si la cadena es aceptada por el autómata."""
        return self.simular(cadena).aceptada

    # =========================================================================
    # 2.2 ELIMINACIÓN DE TRANSICIONES LAMBDA (AFN-λ -> AFN)
    # =========================================================================

    def eliminar_transiciones_lambda_detallado(self) -> ResultadoEliminacionLambda:
        """Transforma un AFN-λ en un AFN sin transiciones λ detallando los cambios (Ejercicio 2.2).

        Regla formal (Hopcroft, Motwani & Ullman, Cap. 2 / Notas del curso):
        1. δ_N(q, a) = Cl_λ( ∪_{p ∈ Cl_λ({q})} δ(p, a) ) para todo q ∈ Q, a ∈ Σ.
        2. F_N = { q ∈ Q | Cl_λ({q}) ∩ F ≠ ∅ }.
        """
        clausuras = self.tabla_lambda_clausuras()
        nuevas_trans: dict[tuple[str, str], list[str]] = {}
        orig_sin_lambda: list[tuple[str, str, str]] = []
        trans_anadidas: list[tuple[str, str, str, str]] = []
        nuevos_finales: list[str] = []
        nuevos_estados_aceptacion_info: list[tuple[str, str]] = []

        for q in self.estados:
            for a in self.alfabeto:
                for d in self.destinos(q, a):
                    orig_sin_lambda.append((q, a, d))

        orig_set = set(orig_sin_lambda)

        for q in self.estados:
            cl_q = clausuras[q]
            alcanzados_finales = [p for p in cl_q if p in self.aceptacion]
            if alcanzados_finales:
                nuevos_finales.append(q)
                if q not in self.aceptacion:
                    nuevos_estados_aceptacion_info.append(
                        (q, f"Cl_λ({{{q}}}) = {{{', '.join(cl_q)}}} contiene a {alcanzados_finales} ∈ F")
                    )

            for a in self.alfabeto:
                intermedios: set[str] = set()
                testigos: dict[str, list[str]] = {}
                for p in cl_q:
                    for r in self.destinos(p, a):
                        intermedios.add(r)
                        for w in clausuras[r]:
                            testigos.setdefault(w, []).append(f"{q} --λ*--> {p} --{a}--> {r} --λ*--> {w}")
                dest_final = self.lambda_clausura(intermedios)
                if dest_final:
                    nuevas_trans[(q, a)] = dest_final
                    for w in dest_final:
                        if (q, a, w) not in orig_set:
                            camino_just = testigos.get(w, [f"vía Cl_λ({{{q}}})"])[0]
                            trans_anadidas.append((q, a, w, camino_just))

        afn_sin_lambda = AutomataFinito(
            alfabeto=list(self.alfabeto),
            estados=list(self.estados),
            inicial=self.inicial,
            aceptacion=nuevos_finales,
            transiciones=nuevas_trans,
            tipo_declarado="AFND",
            coordenadas=dict(self.coordenadas),
        )

        return ResultadoEliminacionLambda(
            automata_sin_lambda=afn_sin_lambda,
            clausuras=clausuras,
            transiciones_originales_sin_lambda=orig_sin_lambda,
            transiciones_anadidas=trans_anadidas,
            estados_aceptacion_originales=list(self.aceptacion),
            nuevos_estados_aceptacion=nuevos_estados_aceptacion_info,
        )

    def convertir_afnd_lambda_a_afnd(self) -> AutomataFinito:
        """Elimina las transiciones λ devolviendo el AFND equivalente."""
        return self.eliminar_transiciones_lambda_detallado().automata_sin_lambda

    # =========================================================================
    # 2.3 CONSTRUCCIÓN DE SUBCONJUNTOS (AFN / AFN-λ -> AFD)
    # =========================================================================

    def construccion_subconjuntos_detallada(self, incluir_pozo: bool = False) -> ResultadoSubconjuntos:
        """Transforma un AFN (o AFN-λ) en un AFD equivalente construyendo sólo subconjuntos alcanzables.

        Registra la tabla de transición conforme se descubren los subconjuntos e indica qué
        subconjuntos resultan de aceptación y por qué (S ∩ F ≠ ∅).
        """
        pos = {e: i for i, e in enumerate(self.estados)}

        def ordenar_sub(sub: frozenset[str] | set[str] | list[str]) -> list[str]:
            return sorted(sub, key=lambda x: pos.get(x, 9999))

        def nombre_subconjunto(sub: frozenset[str]) -> str:
            if not sub:
                return "∅"
            ordenados = ordenar_sub(sub)
            return "{" + ",".join(ordenados) + "}"

        s0_lista = self.lambda_clausura([self.inicial]) if self.inicial else []
        s0 = frozenset(s0_lista)
        cola: list[frozenset[str]] = [s0]
        visitados: list[frozenset[str]] = [s0]
        trans_sub: dict[tuple[frozenset[str], str], frozenset[str]] = {}

        while cola:
            actual = cola.pop(0)
            for a in self.alfabeto:
                mov: set[str] = set()
                for q in actual:
                    mov.update(self.destinos(q, a))
                sig = frozenset(self.lambda_clausura(mov))
                if not sig and not incluir_pozo:
                    continue
                trans_sub[(actual, a)] = sig
                if sig not in visitados:
                    visitados.append(sig)
                    cola.append(sig)

        mapa_nombres = {s: nombre_subconjunto(s) for s in visitados}
        filas: list[FilaSubconjunto] = []
        justificaciones_aceptacion: dict[str, str] = {}

        for idx, s in enumerate(visitados):
            nom_s = mapa_nombres[s]
            lista_s = ordenar_sub(s)
            inter_f = [q for q in lista_s if q in self.aceptacion]
            es_acep = len(inter_f) > 0
            if es_acep:
                razon = f"{nom_s} ∩ F = {{{', '.join(inter_f)}}} ≠ ∅"
                justificaciones_aceptacion[nom_s] = razon
            else:
                razon = f"{nom_s} ∩ F = ∅"

            trans_fila: dict[str, tuple[list[str], str]] = {}
            for a in self.alfabeto:
                if (s, a) in trans_sub:
                    dest_set = trans_sub[(s, a)]
                    trans_fila[a] = (ordenar_sub(dest_set), mapa_nombres[dest_set])
                else:
                    trans_fila[a] = ([], "∅")

            filas.append(
                FilaSubconjunto(
                    orden_descubrimiento=idx,
                    nombre_estado=nom_s,
                    subconjunto=lista_s,
                    transiciones_por_simbolo=trans_fila,
                    es_inicial=(s == s0),
                    es_aceptacion=es_acep,
                    razon_aceptacion=razon,
                )
            )

        estados_afd = [mapa_nombres[s] for s in visitados]
        inicial_afd = mapa_nombres[s0]
        aceptacion_afd = [
            mapa_nombres[s]
            for s in visitados
            if any(q in self.aceptacion for q in s)
        ]
        trans_afd: dict[tuple[str, str], list[str]] = {}
        for (s_orig, a), s_dest in trans_sub.items():
            trans_afd[(mapa_nombres[s_orig], a)] = [mapa_nombres[s_dest]]

        afd = AutomataFinito(
            alfabeto=list(self.alfabeto),
            estados=estados_afd,
            inicial=inicial_afd,
            aceptacion=aceptacion_afd,
            transiciones=trans_afd,
            tipo_declarado="AFD",
        )

        return ResultadoSubconjuntos(
            afd=afd,
            estado_inicial_subconjunto=s0_lista,
            filas=filas,
            subconjuntos_aceptacion_justificacion=justificaciones_aceptacion,
        )

    def convertir_a_afd(self, incluir_pozo: bool = False) -> AutomataFinito:
        """Convierte cualquier AFND o AFND-λ a su AFD equivalente (Construcción de Subconjuntos)."""
        return self.construccion_subconjuntos_detallada(incluir_pozo=incluir_pozo).afd

    # =========================================================================
    # 2.4 MINIMIZACIÓN DE AFD Y EQUIVALENCIA DE DOS AFD
    # =========================================================================

    def obtener_estados_accesibles(self) -> tuple[list[str], list[str]]:
        """Devuelve (estados_accesibles, estados_inaccesibles) desde el estado inicial mediante BFS."""
        if not self.inicial or self.inicial not in self.estados:
            return [], list(self.estados)
        visitados: set[str] = {self.inicial}
        cola: list[str] = [self.inicial]
        while cola:
            u = cola.pop(0)
            for sym in list(self.alfabeto) + [""]:
                for v in self.destinos(u, sym):
                    if v not in visitados:
                        visitados.add(v)
                        cola.append(v)
        accesibles = [q for q in self.estados if q in visitados]
        inaccesibles = [q for q in self.estados if q not in visitados]
        return accesibles, inaccesibles

    def eliminar_estados_inaccesibles(self) -> AutomataFinito:
        """Devuelve un nuevo autómata conservando únicamente los estados alcanzables desde q0."""
        accesibles, _ = self.obtener_estados_accesibles()
        conj_acc = set(accesibles)
        nuevas_trans: dict[tuple[str, str], list[str]] = {}
        for (u, sym), dests in self.transiciones.items():
            if u in conj_acc:
                d_acc = [v for v in dests if v in conj_acc]
                if d_acc:
                    nuevas_trans[(u, sym)] = d_acc
        return AutomataFinito(
            alfabeto=list(self.alfabeto),
            estados=accesibles,
            inicial=self.inicial if self.inicial in conj_acc else "",
            aceptacion=[q for q in self.aceptacion if q in conj_acc],
            transiciones=nuevas_trans,
            tipo_declarado=self.tipo,
            coordenadas={q: c for q, c in self.coordenadas.items() if q in conj_acc},
        )

    def completar_afd(self, nombre_pozo: str = "q_pozo") -> AutomataFinito:
        """Si el AFD tiene transiciones faltantes, añade un estado sumidero/pozo explícito."""
        estados_nuevos = list(self.estados)
        trans_nuevas: dict[tuple[str, str], list[str]] = {
            k: list(v) for k, v in self.transiciones.items()
        }
        requiere_pozo = False
        for q in self.estados:
            for a in self.alfabeto:
                if not trans_nuevas.get((q, a)):
                    requiere_pozo = True
                    break

        if not requiere_pozo:
            return AutomataFinito(
                alfabeto=list(self.alfabeto),
                estados=estados_nuevos,
                inicial=self.inicial,
                aceptacion=list(self.aceptacion),
                transiciones=trans_nuevas,
                tipo_declarado="AFD",
                coordenadas=dict(self.coordenadas),
            )

        pozo = nombre_pozo
        idx_p = 1
        while pozo in estados_nuevos:
            pozo = f"{nombre_pozo}_{idx_p}"
            idx_p += 1
        estados_nuevos.append(pozo)

        for q in estados_nuevos:
            for a in self.alfabeto:
                if not trans_nuevas.get((q, a)):
                    trans_nuevas[(q, a)] = [pozo]

        return AutomataFinito(
            alfabeto=list(self.alfabeto),
            estados=estados_nuevos,
            inicial=self.inicial,
            aceptacion=list(self.aceptacion),
            transiciones=trans_nuevas,
            tipo_declarado="AFD",
            coordenadas=dict(self.coordenadas),
        )

    def minimizar_afd_detallado(self) -> ResultadoMinimizacion:
        """Minimiza un AFD (convirtiéndolo antes si es AFND) mostrando cada ronda de partición y tabla de pares."""
        base_afd = self if self.es_determinista else self.convertir_a_afd()
        accesibles, inaccesibles = base_afd.obtener_estados_accesibles()
        afd_acc = base_afd.eliminar_estados_inaccesibles()
        afd_comp = afd_acc.completar_afd()

        pos = {e: i for i, e in enumerate(afd_comp.estados)}
        estados_ord = list(afd_comp.estados)

        # ---------------------------------------------------------------------
        # Método A: Refinamiento de particiones ronda por ronda (Moore / Hopcroft)
        # ---------------------------------------------------------------------
        finales = [q for q in estados_ord if q in afd_comp.aceptacion]
        no_finales = [q for q in estados_ord if q not in afd_comp.aceptacion]
        particion_actual: list[list[str]] = [g for g in (no_finales, finales) if g]

        rondas_particion: list[RondaParticion] = [
            RondaParticion(
                numero_ronda=0,
                grupos=[list(g) for g in particion_actual],
                divisiones_realizadas=["Partición inicial Π_0 = {Q \\ F, F}"],
            )
        ]

        ronda_num = 1
        while True:
            indice_grupo: dict[str, int] = {}
            for idx_g, grupo in enumerate(particion_actual):
                for q in grupo:
                    indice_grupo[q] = idx_g

            nueva_particion: list[list[str]] = []
            divisiones_ronda: list[str] = []

            for grupo in particion_actual:
                if len(grupo) <= 1:
                    nueva_particion.append(list(grupo))
                    continue

                clases_firma: dict[tuple[int, ...], list[str]] = {}
                for q in grupo:
                    firma = tuple(
                        indice_grupo[afd_comp.destinos(q, a)[0]]
                        for a in afd_comp.alfabeto
                    )
                    clases_firma.setdefault(firma, []).append(q)

                subgrupos = list(clases_firma.values())
                nueva_particion.extend(subgrupos)
                if len(subgrupos) > 1:
                    detalles_div: list[str] = []
                    for q in grupo:
                        dest_grupos = ", ".join(
                            f"δ({q},{a})={afd_comp.destinos(q, a)[0]}∈G_{indice_grupo[afd_comp.destinos(q, a)[0]]}"
                            for a in afd_comp.alfabeto
                        )
                        detalles_div.append(f"{q}:({dest_grupos})")
                    divisiones_ronda.append(
                        f"Grupo {{{','.join(grupo)}}} se divide en "
                        + ", ".join("{" + ",".join(sg) + "}" for sg in subgrupos)
                        + f" [{'; '.join(detalles_div)}]"
                    )

            if len(nueva_particion) == len(particion_actual):
                rondas_particion.append(
                    RondaParticion(
                        numero_ronda=ronda_num,
                        grupos=[list(g) for g in nueva_particion],
                        divisiones_realizadas=["Sin cambios (estabilización Π_{k} = Π_{k-1})"],
                    )
                )
                particion_actual = nueva_particion
                break

            rondas_particion.append(
                RondaParticion(
                    numero_ronda=ronda_num,
                    grupos=[list(g) for g in nueva_particion],
                    divisiones_realizadas=divisiones_ronda,
                )
            )
            particion_actual = nueva_particion
            ronda_num += 1

        # ---------------------------------------------------------------------
        # Método B: Tabla de pares distinguibles ronda por ronda
        # ---------------------------------------------------------------------
        pares_totales: list[tuple[str, str]] = []
        for i in range(len(estados_ord)):
            for j in range(i + 1, len(estados_ord)):
                pares_totales.append((estados_ord[i], estados_ord[j]))

        tabla_marcas: dict[tuple[str, str], str] = {par: "" for par in pares_totales}
        marcados_r0: list[tuple[str, str, str]] = []
        conj_finales = set(afd_comp.aceptacion)

        for p, q in pares_totales:
            if (p in conj_finales) != (q in conj_finales):
                motivo = f"uno está en F y el otro en Q\\F ({p}∈{'F' if p in conj_finales else 'Q\\F'}, {q}∈{'F' if q in conj_finales else 'Q\\F'})"
                tabla_marcas[(p, q)] = f"X (R0: {motivo})"
                marcados_r0.append((p, q, motivo))

        rondas_tabla: list[RondaTablaPares] = [
            RondaTablaPares(
                numero_ronda=0,
                pares_marcados_en_ronda=marcados_r0,
                matriz_actual=dict(tabla_marcas),
            )
        ]

        r_par = 1
        while True:
            nuevos_marcados: list[tuple[str, str, str]] = []
            for p, q in pares_totales:
                if tabla_marcas[(p, q)] != "":
                    continue
                for a in afd_comp.alfabeto:
                    p_sig = afd_comp.destinos(p, a)[0]
                    q_sig = afd_comp.destinos(q, a)[0]
                    if p_sig == q_sig:
                        continue
                    par_dest = (p_sig, q_sig) if pos[p_sig] < pos[q_sig] else (q_sig, p_sig)
                    if tabla_marcas[par_dest] != "":
                        motivo = f"con '{a}' van a ({p_sig}, {q_sig}) ya distinguibles"
                        nuevos_marcados.append((p, q, motivo))
                        break

            for p, q, motivo in nuevos_marcados:
                tabla_marcas[(p, q)] = f"X (R{r_par}: {motivo})"

            rondas_tabla.append(
                RondaTablaPares(
                    numero_ronda=r_par,
                    pares_marcados_en_ronda=nuevos_marcados,
                    matriz_actual=dict(tabla_marcas),
                )
            )
            if not nuevos_marcados:
                break
            r_par += 1

        pares_equivalentes = [par for par in pares_totales if tabla_marcas[par] == ""]

        # ---------------------------------------------------------------------
        # Construir el AFD mínimo a partir de las clases de equivalencia
        # Eliminando la clase del estado pozo artificial si no alcanza ningún estado de aceptación
        # y el AFD original era parcial, o conservando solo estados que pertenecen al AFD accesible
        # si el usuario no tenía estado pozo explícito. Para mantener un AFD estándar limpio:
        # ---------------------------------------------------------------------
        clases_ordenadas = sorted(
            [sorted(g, key=lambda x: pos.get(x, 9999)) for g in particion_actual],
            key=lambda g: (0 if afd_comp.inicial in g else 1, pos.get(g[0], 9999)),
        )

        # Filtrar clase que contenga exclusivamente el estado pozo artificial agregado por completar_afd
        estados_reales_acc = set(afd_acc.estados)
        clases_reales: list[list[str]] = []
        for cl in clases_ordenadas:
            miembros_reales = [q for q in cl if q in estados_reales_acc]
            if miembros_reales:
                clases_reales.append(miembros_reales)

        def nombre_clase(cl: list[str]) -> str:
            return cl[0] if len(cl) == 1 else "{" + ",".join(cl) + "}"

        mapa_estado_a_clase: dict[str, str] = {}
        for cl in clases_reales:
            nom = nombre_clase(cl)
            for q in cl:
                mapa_estado_a_clase[q] = nom

        estados_min = [nombre_clase(cl) for cl in clases_reales]
        inicial_min = mapa_estado_a_clase.get(afd_acc.inicial, estados_min[0] if estados_min else "")
        aceptacion_min = [
            nombre_clase(cl)
            for cl in clases_reales
            if any(q in afd_acc.aceptacion for q in cl)
        ]

        trans_min: dict[tuple[str, str], list[str]] = {}
        for cl in clases_reales:
            rep = cl[0]
            nom_orig = nombre_clase(cl)
            for a in afd_acc.alfabeto:
                dests = afd_acc.destinos(rep, a)
                if dests and dests[0] in mapa_estado_a_clase:
                    trans_min[(nom_orig, a)] = [mapa_estado_a_clase[dests[0]]]

        afd_min = AutomataFinito(
            alfabeto=list(afd_acc.alfabeto),
            estados=estados_min,
            inicial=inicial_min,
            aceptacion=aceptacion_min,
            transiciones=trans_min,
            tipo_declarado="AFD",
        )

        return ResultadoMinimizacion(
            afd_original=base_afd,
            estados_accesibles=accesibles,
            estados_inaccesibles_eliminados=inaccesibles,
            afd_accesible_completo=afd_comp,
            rondas_particion=rondas_particion,
            rondas_tabla_pares=rondas_tabla,
            pares_equivalentes=pares_equivalentes,
            clases_equivalencia=clases_reales,
            afd_minimo=afd_min,
        )

    def minimizar_afd(self) -> AutomataFinito:
        """Devuelve el AFD mínimo equivalente."""
        return self.minimizar_afd_detallado().afd_minimo

    def son_afd_equivalentes(self, otro: AutomataFinito) -> ResultadoEquivalenciaAFD:
        """Decide si dos autómatas (AFD/AFND) reconocen el mismo lenguaje a partir de sus AFD mínimos.

        Por el Teorema de Myhill-Nerode, el AFD mínimo completo es único salvo isomorfismo
        (renombramiento de estados). Se realiza un recorrido BFS canónico desde ambos estados
        iniciales verificando correspondencia biyectiva en estados de aceptación y transiciones.
        """
        alf_unificado = list(dict.fromkeys(list(self.alfabeto) + list(otro.alfabeto)))
        a1 = AutomataFinito(
            alfabeto=alf_unificado,
            estados=list(self.estados),
            inicial=self.inicial,
            aceptacion=list(self.aceptacion),
            transiciones=dict(self.transiciones),
            tipo_declarado=self.tipo,
        )
        a2 = AutomataFinito(
            alfabeto=alf_unificado,
            estados=list(otro.estados),
            inicial=otro.inicial,
            aceptacion=list(otro.aceptacion),
            transiciones=dict(otro.transiciones),
            tipo_declarado=otro.tipo,
        )

        min1 = a1.minimizar_afd_detallado()
        min2 = a2.minimizar_afd_detallado()

        # Para el isomorfismo canónico usamos los AFD mínimos completados y luego re-minimizados
        # con estado pozo si es necesario, de modo que ambos sean funciones totales sobre Σ.
        m1_tot = min1.afd_minimo.completar_afd("pozo1").minimizar_afd_detallado().afd_minimo.completar_afd("pozo1")
        m2_tot = min2.afd_minimo.completar_afd("pozo2").minimizar_afd_detallado().afd_minimo.completar_afd("pozo2")

        biyeccion: dict[str, str] = {m1_tot.inicial: m2_tot.inicial}
        inversa: dict[str, str] = {m2_tot.inicial: m1_tot.inicial}
        cola: list[tuple[str, str, str]] = [(m1_tot.inicial, m2_tot.inicial, "")]
        fallo_estructural: str | None = None

        while cola:
            q1, q2, prefijo = cola.pop(0)
            es_fin1 = q1 in m1_tot.aceptacion
            es_fin2 = q2 in m2_tot.aceptacion
            if es_fin1 != es_fin2:
                cad_testigo = "λ" if prefijo == "" else prefijo
                return ResultadoEquivalenciaAFD(
                    equivalentes=False,
                    min_afd1=min1,
                    min_afd2=min2,
                    biyeccion_estados=biyeccion,
                    testigo_diferencia=prefijo,
                    justificacion=(
                        f"No son equivalentes: con la cadena testigo w = '{cad_testigo}', "
                        f"el primer autómata llega a '{q1}' ({'aceptación' if es_fin1 else 'no aceptación'}) "
                        f"y el segundo llega a '{q2}' ({'aceptación' if es_fin2 else 'no aceptación'})."
                    ),
                )

            for sym in alf_unificado:
                d1 = m1_tot.destinos(q1, sym)[0]
                d2 = m2_tot.destinos(q2, sym)[0]
                if d1 in biyeccion or d2 in inversa:
                    if biyeccion.get(d1) != d2 or inversa.get(d2) != d1:
                        if fallo_estructural is None:
                            fallo_estructural = (
                                f"Fallo de isomorfismo en transición con '{sym}' "
                                f"desde ({q1}, {q2}) hacia ({d1}, {d2})."
                            )
                else:
                    biyeccion[d1] = d2
                    inversa[d2] = d1
                    cola.append((d1, d2, prefijo + sym))

        if fallo_estructural is not None:
            # Buscar mediante BFS en el producto cartesiano la cadena más corta donde difiere la aceptación
            cola_prod: list[tuple[str, str, str]] = [(m1_tot.inicial, m2_tot.inicial, "")]
            vis_prod: set[tuple[str, str]] = {(m1_tot.inicial, m2_tot.inicial)}
            testigo_real = ""
            while cola_prod:
                u1, u2, w_act = cola_prod.pop(0)
                if (u1 in m1_tot.aceptacion) != (u2 in m2_tot.aceptacion):
                    testigo_real = w_act
                    break
                for sym in alf_unificado:
                    v1 = m1_tot.destinos(u1, sym)[0]
                    v2 = m2_tot.destinos(u2, sym)[0]
                    if (v1, v2) not in vis_prod:
                        vis_prod.add((v1, v2))
                        cola_prod.append((v1, v2, w_act + sym))
            cad_t = "λ" if testigo_real == "" else testigo_real
            return ResultadoEquivalenciaAFD(
                equivalentes=False,
                min_afd1=min1,
                min_afd2=min2,
                biyeccion_estados=biyeccion,
                testigo_diferencia=testigo_real,
                justificacion=f"No son equivalentes: {fallo_estructural} Cadena testigo de longitud mínima: w = '{cad_t}'.",
            )

        return ResultadoEquivalenciaAFD(
            equivalentes=True,
            min_afd1=min1,
            min_afd2=min2,
            biyeccion_estados=biyeccion,
            testigo_diferencia=None,
            justificacion=(
                "Los dos AFD son equivalentes: sus AFD mínimos son isomorfos bajo la biyección "
                + ", ".join(f"{k} ↔ {v}" for k, v in biyeccion.items())
                + "."
            ),
        )

    # =========================================================================
    # 2.5 VALIDACIÓN DE CADENAS POR LOTES DESDE ARCHIVO .TXT
    # =========================================================================

    def validar_archivo_cadenas(
        self,
        ruta_entrada: str | Path,
        ruta_salida: str | Path | None = None,
    ) -> tuple[list[LineaReporteCadena], str]:
        """Lee un archivo `.txt` con una cadena por línea, las valida todas y guarda el reporte (Ejercicio 2.5).

        Nota: una línea vacía o la cadena literal 'λ' / 'epsilon' se interpreta como la cadena vacía "".
        """
        p_in = Path(ruta_entrada)
        lineas_raw = p_in.read_text(encoding="utf-8").splitlines()
        resultados: list[LineaReporteCadena] = []

        for idx, linea in enumerate(lineas_raw, start=1):
            limpia = linea.strip()
            cadena_eval = "" if limpia in ("", "λ", "lambda", "epsilon", "ε") else limpia
            sim = self.simular(cadena_eval)
            mostrada = "λ" if cadena_eval == "" else cadena_eval
            resultados.append(
                LineaReporteCadena(
                    numero_linea=idx,
                    cadena_original=linea,
                    cadena_mostrada=mostrada,
                    aceptada=sim.aceptada,
                    estados_finales=sim.estados_finales_alcanzados,
                )
            )

        total = len(resultados)
        aceptadas = sum(1 for r in resultados if r.aceptada)
        rechazadas = total - aceptadas

        lineas_rep = [
            "======================================================================",
            "REPORTE DE VALIDACIÓN DE CADENAS POR LOTES (PRÁCTICA 3 - EJERCICIO 2.5)",
            "======================================================================",
            f"Archivo de entrada : {p_in.as_posix()}",
            f"Tipo de autómata   : {self.tipo}",
            f"Quíntupla          : Q={self.estados}, Σ={self.alfabeto}, q0={self.inicial}, F={self.aceptacion}",
            f"Total de cadenas   : {total} (Aceptadas: {aceptadas} | Rechazadas: {rechazadas})",
            "----------------------------------------------------------------------",
            f"{'#':>3} | {'Cadena':<20} | {'Resultado':<12} | {'Estados finales en F'}",
            "----------------------------------------------------------------------",
        ]
        for r in resultados:
            veredicto = "ACEPTADA" if r.aceptada else "RECHAZADA"
            est_fin = "{" + ", ".join(r.estados_finales) + "}" if r.estados_finales else "∅"
            lineas_rep.append(f"{r.numero_linea:>3} | {r.cadena_mostrada:<20} | {veredicto:<12} | {est_fin}")
        lineas_rep.append("======================================================================\n")

        texto_reporte = "\n".join(lineas_rep)
        if ruta_salida is not None:
            p_out = Path(ruta_salida)
            p_out.parent.mkdir(parents=True, exist_ok=True)
            p_out.write_text(texto_reporte, encoding="utf-8")

        return resultados, texto_reporte

    def equivalentes_estructuralmente(self, otro: AutomataFinito) -> bool:
        """Comprueba si dos autómatas tienen exactamente la misma quíntupla."""
        if set(self.alfabeto) != set(otro.alfabeto):
            return False
        if set(self.estados) != set(otro.estados):
            return False
        if self.inicial != otro.inicial:
            return False
        if set(self.aceptacion) != set(otro.aceptacion):
            return False
        simbolos = list(self.alfabeto) + [""]
        for q in self.estados:
            for s in simbolos:
                if set(self.destinos(q, s)) != set(otro.destinos(q, s)):
                    return False
        return True
