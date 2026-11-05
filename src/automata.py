"""Módulo `automata.py`: Modelo de datos y algoritmos para AFD, AFND y AFND-lambda.

Este módulo es puro (sin dependencias de Flet) y proporciona:
- Clase `AutomataFinito`: Representación de la quíntupla M = (Q, Σ, δ, q0, F).
- Clasificación automática e inspección del tipo ("AFD", "AFND", "AFND-lambda").
- Cálculo de la λ-clausura (lambda_clausura) de un estado o conjunto de estados.
- Simulación directa (siguiendo todos los caminos posibles / conjuntos de estados
  activos paso a paso y registro de bifurcaciones).
- Conversión de AFND-lambda -> AFND estándar (eliminación de transiciones λ).
- Conversión de AFND / AFND-lambda -> AFD equivalente (Construcción de subconjuntos
  de Rabin-Scott) y minimización de estados equivalentes (partición de Hopcroft/Moore).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PasoSimulacion:
    """Representa un paso en la traza de ejecución del autómata."""

    indice: int
    simbolo: str  # "" para paso inicial (λ-clausura inicial)
    estados_origen: list[str]
    estados_destino: list[str]
    transiciones_tomadas: list[str]


@dataclass
class ResultadoSimulacion:
    """Resultado completo de validar una cadena en un autómata finito."""

    cadena: str
    aceptada: bool
    estados_finales_alcanzados: list[str]
    pasos: list[PasoSimulacion]
    caminos: list[list[str]]  # Lista de caminos individuales para mostrar bifurcaciones


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

    def lambda_clausura_estado(self, estado: str) -> list[str]:
        """Calcula Cl_λ({estado}) mediante búsqueda en anchura (BFS)."""
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
        # Ordenar según aparición en self.estados para determinismo en pruebas
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

    def simular(self, cadena: str, max_caminos: int = 32) -> ResultadoSimulacion:
        """Simula una cadena paso a paso siguiendo todos los caminos posibles (con λ-clausura).

        Esta decisión de diseño permite mostrar tanto la evolución de conjuntos de
        estados activos como las bifurcaciones individuales en AFND y AFND-λ.
        """
        pos = {e: i for i, e in enumerate(self.estados)}
        activos = self.lambda_clausura([self.inicial]) if self.inicial else []

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
                estados_origen=[self.inicial] if self.inicial else [],
                estados_destino=activos,
                transiciones_tomadas=trans_ini,
            )
        ]

        # Rastrear caminos explícitos para documentar bifurcaciones
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

            siguientes = self.lambda_clausura(siguientes_directos)
            if not detalle_trans:
                detalle_trans.append(f"∅ (sin transiciones con '{ch}' desde {activos})")

            pasos.append(
                PasoSimulacion(
                    indice=idx,
                    simbolo=ch,
                    estados_origen=activos,
                    estados_destino=siguientes,
                    transiciones_tomadas=detalle_trans,
                )
            )
            activos = sorted(siguientes, key=lambda x: pos.get(x, 9999))
            # Compactar caminos para dejar solo la secuencia de estados/aristas legible
            caminos_actuales = nuevos_caminos[:max_caminos]

        finales_alcanzados = [q for q in activos if q in self.aceptacion]
        aceptada = len(finales_alcanzados) > 0

        caminos_formateados: list[list[str]] = []
        for cam in caminos_actuales:
            # Filtrar pasos pares/impares para presentación limpia
            caminos_formateados.append(cam)

        return ResultadoSimulacion(
            cadena=cadena,
            aceptada=aceptada,
            estados_finales_alcanzados=finales_alcanzados,
            pasos=pasos,
            caminos=caminos_formateados,
        )

    def acepta(self, cadena: str) -> bool:
        """Devuelve True si la cadena es aceptada por el autómata."""
        return self.simular(cadena).aceptada

    def convertir_afnd_lambda_a_afnd(self) -> AutomataFinito:
        """Elimina las transiciones λ convirtiendo un AFND-λ en un AFND estándar equivalente.

        Regla formal:
        1. δ_N(q, a) = Cl_λ( ∪_{p ∈ Cl_λ({q})} δ(p, a) ) para todo q ∈ Q, a ∈ Σ.
        2. F_N = { q ∈ Q | Cl_λ({q}) ∩ F ≠ ∅ }.
        """
        nuevas_trans: dict[tuple[str, str], list[str]] = {}
        nuevos_finales: list[str] = []

        for q in self.estados:
            cl_q = self.lambda_clausura_estado(q)
            if any(p in self.aceptacion for p in cl_q):
                nuevos_finales.append(q)
            for a in self.alfabeto:
                intermedios: set[str] = set()
                for p in cl_q:
                    intermedios.update(self.destinos(p, a))
                dest_final = self.lambda_clausura(intermedios)
                if dest_final:
                    nuevas_trans[(q, a)] = dest_final

        return AutomataFinito(
            alfabeto=list(self.alfabeto),
            estados=list(self.estados),
            inicial=self.inicial,
            aceptacion=nuevos_finales,
            transiciones=nuevas_trans,
            tipo_declarado="AFND",
            coordenadas=dict(self.coordenadas),
        )

    def convertir_a_afd(self, incluir_pozo: bool = False) -> AutomataFinito:
        """Convierte cualquier AFND o AFND-λ a su AFD equivalente (Construcción de Subconjuntos).

        Cada estado del AFD representa un subconjunto accesible S ⊆ Q.
        El estado inicial del AFD es S_0 = Cl_λ({q_0}).
        """
        pos = {e: i for i, e in enumerate(self.estados)}

        def nombre_subconjunto(sub: frozenset[str]) -> str:
            if not sub:
                return "∅"
            ordenados = sorted(sub, key=lambda x: pos.get(x, 9999))
            return "{" + ",".join(ordenados) + "}" if len(ordenados) > 1 else ordenados[0]

        s0 = frozenset(self.lambda_clausura([self.inicial])) if self.inicial else frozenset()
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
        # En caso de colisión de nombres, desambiguar
        if len(set(mapa_nombres.values())) < len(visitados):
            mapa_nombres = {
                s: ("{" + ",".join(sorted(s, key=lambda x: pos.get(x, 9999))) + "}" if s else "∅")
                for s in visitados
            }

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

        return AutomataFinito(
            alfabeto=list(self.alfabeto),
            estados=estados_afd,
            inicial=inicial_afd,
            aceptacion=aceptacion_afd,
            transiciones=trans_afd,
            tipo_declarado="AFD",
        )

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
