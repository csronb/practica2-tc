"""Módulo `formatos.py`: Lectura y escritura de autómatas en formatos .jff, .json y .xml.

Cumple las especificaciones del Anexo 3 de la Práctica 2:
1. `.jff` (formato nativo de JFLAP 7.1): `<structure><type>fa</type><automaton>...`
   Tolerante a coordenadas `<x>`, `<y>` y etiquetas `<read/>` vacías para λ.
2. `.json`: Representa los cinco componentes de la quíntupla (`alfabeto`, `estados`,
   `inicial`, `aceptacion`, `transiciones`) más el campo `"tipo"`. La cadena vacía `""`
   en `"lee"` representa la transición λ.
3. `.xml`: Esquema propio `<automata tipo="..."><alfabeto>...<estados>...<transiciones>...`
   con `lee=""` para λ.

La exportación y la importación en los tres formatos son operaciones inversas sobre la
quíntupla M = (Q, Sigma, delta, q0, F).
"""

from __future__ import annotations

import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

try:
    from automata import AutomataFinito
except ImportError:  # pragma: no cover
    from src.automata import AutomataFinito


# =============================================================================
# 1. FORMATO .JFF (JFLAP)
# =============================================================================

def exportar_jff_texto(automata: AutomataFinito) -> str:
    """Serializa un `AutomataFinito` a una cadena XML en formato `.jff` de JFLAP."""
    estructura = ET.Element("structure")
    ET.SubElement(estructura, "type").text = "fa"
    aut_el = ET.SubElement(estructura, "automaton")

    n = len(automata.estados)
    radio = max(100.0, 30.0 * n)
    cx, cy = radio + 80.0, radio + 80.0

    nombre_a_id: dict[str, str] = {}
    for idx, nombre in enumerate(automata.estados):
        st_id = str(idx)
        nombre_a_id[nombre] = st_id
        if nombre in automata.coordenadas:
            x, y = automata.coordenadas[nombre]
        else:
            ang = math.pi + (2.0 * math.pi * idx) / max(1, n)
            x = round(cx + radio * math.cos(ang), 1)
            y = round(cy + radio * math.sin(ang), 1)

        st_el = ET.SubElement(aut_el, "state", id=st_id, name=nombre)
        ET.SubElement(st_el, "x").text = str(x)
        ET.SubElement(st_el, "y").text = str(y)
        if nombre == automata.inicial:
            ET.SubElement(st_el, "initial")
        if nombre in automata.aceptacion:
            ET.SubElement(st_el, "final")

    # Ordenar transiciones de manera determinista
    for (desde, simbolo), lista_hacia in automata.transiciones.items():
        if desde not in nombre_a_id:
            continue
        for hacia in lista_hacia:
            if hacia not in nombre_a_id:
                continue
            tr_el = ET.SubElement(aut_el, "transition")
            ET.SubElement(tr_el, "from").text = nombre_a_id[desde]
            ET.SubElement(tr_el, "to").text = nombre_a_id[hacia]
            read_el = ET.SubElement(tr_el, "read")
            if simbolo != "":
                read_el.text = simbolo

    ET.indent(estructura, space="  ")
    cuerpo = ET.tostring(estructura, encoding="unicode")
    return '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n' + cuerpo + "\n"


def importar_jff_texto(contenido: str, alfabeto_forzado: list[str] | None = None) -> AutomataFinito:
    """Construye un `AutomataFinito` a partir del texto XML de un archivo `.jff`."""
    raiz = ET.fromstring(contenido.strip())
    aut_el = raiz.find("automaton")
    if aut_el is None:
        raise ValueError("El archivo .jff no contiene el elemento <automaton>.")

    id_a_nombre: dict[str, str] = {}
    estados: list[str] = []
    inicial: str = ""
    aceptacion: list[str] = []
    coordenadas: dict[str, tuple[float, float]] = {}

    for st_el in aut_el.findall("state"):
        st_id = st_el.attrib.get("id", "")
        nombre = st_el.attrib.get("name") or f"q{st_id}"
        id_a_nombre[st_id] = nombre
        estados.append(nombre)

        x_el = st_el.find("x")
        y_el = st_el.find("y")
        if x_el is not None and y_el is not None and x_el.text and y_el.text:
            try:
                coordenadas[nombre] = (float(x_el.text), float(y_el.text))
            except ValueError:
                pass

        if st_el.find("initial") is not None:
            inicial = nombre
        if st_el.find("final") is not None:
            aceptacion.append(nombre)

    if not inicial and estados:
        inicial = estados[0]

    alfabeto_inferido: list[str] = list(alfabeto_forzado) if alfabeto_forzado else []
    transiciones: dict[tuple[str, str], list[str]] = {}

    for tr_el in aut_el.findall("transition"):
        from_el = tr_el.find("from")
        to_el = tr_el.find("to")
        read_el = tr_el.find("read")
        if from_el is None or to_el is None or from_el.text is None or to_el.text is None:
            continue
        u = id_a_nombre.get(from_el.text.strip(), from_el.text.strip())
        v = id_a_nombre.get(to_el.text.strip(), to_el.text.strip())
        simbolo = (read_el.text or "") if read_el is not None else ""
        if simbolo != "" and simbolo not in alfabeto_inferido:
            alfabeto_inferido.append(simbolo)
        dest_actuales = transiciones.setdefault((u, simbolo), [])
        if v not in dest_actuales:
            dest_actuales.append(v)

    return AutomataFinito(
        alfabeto=alfabeto_inferido,
        estados=estados,
        inicial=inicial,
        aceptacion=aceptacion,
        transiciones=transiciones,
        coordenadas=coordenadas,
    )


# =============================================================================
# 2. FORMATO .JSON (Anexo 3)
# =============================================================================

def exportar_json_texto(automata: AutomataFinito) -> str:
    """Serializa un `AutomataFinito` al esquema JSON del Anexo 3."""
    lista_trans: list[dict[str, object]] = []
    for (desde, lee), hacia in automata.transiciones.items():
        if hacia:
            lista_trans.append(
                {
                    "desde": desde,
                    "lee": lee,
                    "hacia": list(hacia),
                }
            )
    datos = {
        "tipo": automata.tipo,
        "alfabeto": list(automata.alfabeto),
        "estados": list(automata.estados),
        "inicial": automata.inicial,
        "aceptacion": list(automata.aceptacion),
        "transiciones": lista_trans,
    }
    return json.dumps(datos, indent=2, ensure_ascii=False) + "\n"


def importar_json_texto(contenido: str) -> AutomataFinito:
    """Construye un `AutomataFinito` a partir de una cadena JSON según el Anexo 3."""
    datos = json.loads(contenido)
    tipo = datos.get("tipo")
    alfabeto = [str(s) for s in datos.get("alfabeto", [])]
    estados = [str(e) for e in datos.get("estados", [])]
    inicial = str(datos.get("inicial", estados[0] if estados else ""))
    aceptacion = [str(e) for e in datos.get("aceptacion", [])]

    transiciones: dict[tuple[str, str], list[str]] = {}
    for item in datos.get("transiciones", []):
        desde = str(item["desde"])
        lee = str(item.get("lee", ""))
        hacia_raw = item.get("hacia", [])
        if isinstance(hacia_raw, str):
            hacia_lista = [hacia_raw]
        else:
            hacia_lista = [str(x) for x in hacia_raw]
        actuales = transiciones.setdefault((desde, lee), [])
        for h in hacia_lista:
            if h not in actuales:
                actuales.append(h)

    return AutomataFinito(
        alfabeto=alfabeto,
        estados=estados,
        inicial=inicial,
        aceptacion=aceptacion,
        transiciones=transiciones,
        tipo_declarado=tipo,
    )


# =============================================================================
# 3. FORMATO .XML (Anexo 3)
# =============================================================================

def exportar_xml_texto(automata: AutomataFinito) -> str:
    """Serializa un `AutomataFinito` al esquema XML del Anexo 3."""
    raiz = ET.Element("automata", tipo=automata.tipo)
    alf_el = ET.SubElement(raiz, "alfabeto")
    for s in automata.alfabeto:
        ET.SubElement(alf_el, "simbolo").text = s

    est_el = ET.SubElement(raiz, "estados")
    for q in automata.estados:
        atributos: dict[str, str] = {"nombre": q}
        if q == automata.inicial:
            atributos["inicial"] = "true"
        if q in automata.aceptacion:
            atributos["aceptacion"] = "true"
        ET.SubElement(est_el, "estado", **atributos)

    tr_cont = ET.SubElement(raiz, "transiciones")
    for (desde, lee), lista_hacia in automata.transiciones.items():
        for hacia in lista_hacia:
            ET.SubElement(
                tr_cont,
                "transicion",
                desde=desde,
                lee=lee,
                hacia=hacia,
            )

    ET.indent(raiz, space="  ")
    cuerpo = ET.tostring(raiz, encoding="unicode")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + cuerpo + "\n"


def importar_xml_texto(contenido: str) -> AutomataFinito:
    """Construye un `AutomataFinito` a partir de una cadena XML del Anexo 3."""
    raiz = ET.fromstring(contenido.strip())
    # Si se le pasa un .jff por error, delegar a importar_jff_texto
    if raiz.tag == "structure":
        return importar_jff_texto(contenido)

    tipo = raiz.attrib.get("tipo")
    alfabeto: list[str] = []
    alf_el = raiz.find("alfabeto")
    if alf_el is not None:
        for sim_el in alf_el.findall("simbolo"):
            if sim_el.text:
                alfabeto.append(sim_el.text)

    estados: list[str] = []
    inicial = ""
    aceptacion: list[str] = []
    est_el = raiz.find("estados")
    if est_el is not None:
        for q_el in est_el.findall("estado"):
            nombre = q_el.attrib["nombre"]
            estados.append(nombre)
            if q_el.attrib.get("inicial", "").lower() == "true":
                inicial = nombre
            if q_el.attrib.get("aceptacion", "").lower() == "true":
                aceptacion.append(nombre)

    transiciones: dict[tuple[str, str], list[str]] = {}
    tr_cont = raiz.find("transiciones")
    if tr_cont is not None:
        for tr_el in tr_cont.findall("transicion"):
            desde = tr_el.attrib["desde"]
            lee = tr_el.attrib.get("lee", "")
            hacia = tr_el.attrib["hacia"]
            dest = transiciones.setdefault((desde, lee), [])
            if hacia not in dest:
                dest.append(hacia)
            if lee != "" and lee not in alfabeto:
                alfabeto.append(lee)

    return AutomataFinito(
        alfabeto=alfabeto,
        estados=estados,
        inicial=inicial,
        aceptacion=aceptacion,
        transiciones=transiciones,
        tipo_declarado=tipo,
    )


# =============================================================================
# FUNCIONES DE ARCHIVO UNIFICADAS
# =============================================================================

def guardar_automata(automata: AutomataFinito, ruta: str | Path) -> Path:
    """Guarda un autómata en `.jff`, `.json` o `.xml` según la extensión de `ruta`."""
    p = Path(ruta)
    p.parent.mkdir(parents=True, exist_ok=True)
    ext = p.suffix.lower()
    if ext == ".jff":
        p.write_text(exportar_jff_texto(automata), encoding="utf-8")
    elif ext == ".json":
        p.write_text(exportar_json_texto(automata), encoding="utf-8")
    elif ext == ".xml":
        p.write_text(exportar_xml_texto(automata), encoding="utf-8")
    else:
        raise ValueError(f"Formato no soportado: {ext}. Use .jff, .json o .xml.")
    return p


def cargar_automata(ruta: str | Path) -> AutomataFinito:
    """Carga un autómata desde un archivo `.jff`, `.json` o `.xml`."""
    p = Path(ruta)
    contenido = p.read_text(encoding="utf-8")
    ext = p.suffix.lower()
    if ext == ".jff":
        return importar_jff_texto(contenido)
    if ext == ".json":
        return importar_json_texto(contenido)
    if ext == ".xml":
        return importar_xml_texto(contenido)
    raise ValueError(f"Formato no soportado: {ext}. Use .jff, .json o .xml.")


def guardar_en_tres_formatos(automata: AutomataFinito, directorio: str | Path, nombre_base: str) -> tuple[Path, Path, Path]:
    """Guarda el autómata simultáneamente en `.jff`, `.json` y `.xml`."""
    base_dir = Path(directorio)
    base_dir.mkdir(parents=True, exist_ok=True)
    limpio = nombre_base.removesuffix(".jff").removesuffix(".json").removesuffix(".xml")
    r_jff = guardar_automata(automata, base_dir / f"{limpio}.jff")
    r_json = guardar_automata(automata, base_dir / f"{limpio}.json")
    r_xml = guardar_automata(automata, base_dir / f"{limpio}.xml")
    return r_jff, r_json, r_xml
