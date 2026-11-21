"""Partidor: corta una norma en chunks, uno por artículo o por parágrafo.

Uso (desde la raíz del repositorio):
    python -m rag.partir                    # datos/normas/acuerdo-008-2008-csu.md
    python -m rag.partir ruta/otra-norma.md

Escribe datos/chunks.jsonl con el formato de tareas/semana-1.md.

Cómo piensa el programa
-----------------------
Recorre la norma línea por línea y reparte cada línea en uno de estos bloques:

    preámbulo   todo lo anterior a «ACUERDA:» (ficha, considerandos)
    encabezado  «CAPÍTULO I», «DE LA ADMISIÓN»... (van a la `jerarquia`)
    chunk       un ARTÍCULO o un PARÁGRAFO, con su texto y sus notas
    cierre      desde «COMUNÍQUESE Y CÚMPLASE.» hasta el final

Los bloques cubren el archivo completo, sin huecos ni solapes; por eso la
prueba puede reconstruir la norma desde los chunks.

Dentro de un chunk, cada línea es `texto` (la norma) o `nota` (las líneas que
trae el Régimen Legal: «Ver...», «Reglamentado por...», «Nota de vigencia...»).
De las notas y de las marcas dentro del texto («Exceptuado por...», «fue
modificado por...») sale `modificado_por`.
"""
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
NORMA_POR_DEFECTO = RAIZ / "datos" / "normas" / "acuerdo-008-2008-csu.md"
SALIDA = RAIZ / "datos" / "chunks.jsonl"

SIGLAS = {"Consejo Superior Universitario": "CSU", "Consejo Académico": "CA"}

ARTICULO = re.compile(r"^ARTÍCULO\s+(\d+(?:-\d+)?)\.\s*")
PARAGRAFO = re.compile(r"^PARÁGRAFO(?:\s+(\d+))?\.\s*")
CAPITULO = re.compile(r"^CAPÍTULO\s+([IVXLC]+)$")
NOTA_SUELTA = re.compile(r"^(?:Ver\b|Reglamentado\b)")
CABECERA_NOTA = re.compile(r"^(?:Nota de vigencia|En el marco de la pandemia)")

# Frases de las notas de vigencia. Solo cuentan los verbos que dice la fuente.
ACTIVA = re.compile(r"^(?:La|El)\s+(?P<norma>.+?)\s+(?P<verbo>exceptuó|modificó|derogó|adicionó)\b")
PASIVA = re.compile(
    r"^(?:La|El)\s+.+?\s+fue\s+(?P<verbo>exceptuado|modificado|derogado|adicionado)\s+por\s+"
    r"(?:la|el)\s+(?P<norma>.+?)(?=\s+únicamente|,\s|\s*\(|\.\s*$|$)"
)
# Marca dentro del texto: «Exceptuado por el artículo 1 del Acuerdo...», «fue modificado por Art. 1, Acuerdo...».
# El punto de «Art.» no cierra la frase.
EN_EL_TEXTO = re.compile(
    r"\b(?P<verbo>[Ee]xceptuado|[Mm]odificado|[Dd]erogado|[Aa]dicionado)\s+por\s+"
    r"(?P<ref>.+?)(?<!Art)(?<!art)\.(?=\s|$)"
)
NOMBRE_NORMA = re.compile(r"(?:Acuerdo|Resolución|Circular|Decreto)\b.*$")

TIPO = {
    "exceptuó": "exceptuado", "exceptuado": "exceptuado",
    "modificó": "modificado", "modificado": "modificado",
    "derogó": "derogado", "derogado": "derogado",
    "adicionó": "adicionado", "adicionado": "adicionado",
}
TRANSITORIA = "modificado_transitoriamente"
MENCIONADA = "mencionado_en_nota_de_vigencia"


def _titulo(linea: str) -> str:
    return linea.capitalize()


def _leer_ficha(texto: str) -> dict:
    """Lee la ficha (entre las dos primeras líneas «---»), si existe."""
    lineas = texto.splitlines()
    if not lineas or lineas[0].strip() != "---":
        return {}
    ficha = {}
    for linea in lineas[1:]:
        if linea.strip() == "---":
            break
        if ":" in linea:
            clave, _, valor = linea.partition(":")
            ficha[clave.strip()] = valor.strip()
    return ficha


def _entradas_de_nota(linea: str, tipo_bloque: str) -> list[dict]:
    """Normas que modifican, según una línea de una nota de vigencia."""
    m = ACTIVA.match(linea)
    if m and re.search(r"\d", m["norma"]):
        return [{"tipo": TIPO[m["verbo"]], "norma": m["norma"].strip(), "cita": linea}]
    m = PASIVA.match(linea)
    if m:
        return [{"tipo": TIPO[m["verbo"]], "norma": m["norma"].strip(), "cita": linea}]
    if re.match(r"^(?:Resolución|Acuerdo|Circular|Decreto)\b", linea):
        norma = linea.split(",")[0].rstrip(". ")
        return [{"tipo": tipo_bloque, "norma": norma, "cita": linea}]
    return []


def _entradas_en_el_texto(linea: str) -> list[dict]:
    salida = []
    for m in EN_EL_TEXTO.finditer(linea):
        nombre = NOMBRE_NORMA.search(m["ref"])
        if nombre:
            salida.append({"tipo": TIPO[m["verbo"].lower()], "norma": nombre.group(0).strip(), "cita": m.group(0)})
    return salida


def _clasificar(lineas: list[str]):
    """Reparte las líneas de un chunk en texto, notas y normas que lo modifican."""
    texto, notas, entradas = [], [], []
    en_nota, tipo_bloque = False, MENCIONADA
    for crudo in lineas:
        linea = crudo.strip()
        if not linea:
            continue
        if CABECERA_NOTA.match(linea):
            en_nota = True
            if "modificaron transitoriamente" in linea:
                tipo_bloque = TRANSITORIA
            elif linea.startswith("Nota de vigencia"):
                tipo_bloque = MENCIONADA
            notas.append(linea)
        elif en_nota:
            notas.append(linea)
            entradas += _entradas_de_nota(linea, tipo_bloque)
        elif NOTA_SUELTA.match(linea):
            notas.append(linea)
        else:
            texto.append(linea)
            entradas += _entradas_en_el_texto(linea)
    return texto, notas, entradas


def _vigencia(entradas: list[dict]) -> str:
    if any(e["tipo"] == "derogado" for e in entradas):
        return "no"
    return "parcial" if entradas else "sí"


def partir_texto(texto: str, slug: str, norma: str, enlace: str = ""):
    """Devuelve (chunks, segmentos). Los segmentos cubren `texto` completo."""
    lineas = texto.splitlines(keepends=True)
    desplazamientos, pos = [], 0
    for linea in lineas:
        desplazamientos.append(pos)
        pos += len(linea)
    desplazamientos.append(pos)  # fin del archivo

    try:
        i_acuerda = next(i for i, l in enumerate(lineas) if l.strip() == "ACUERDA:")
    except StopIteration:
        raise ValueError("No encontré la línea «ACUERDA:»; ¿es la norma completa?") from None
    i_cierre = next(
        (i for i in range(i_acuerda + 1, len(lineas)) if lineas[i].strip().startswith("COMUNÍQUESE")),
        len(lineas),
    )

    segmentos = [{"tipo": "preambulo", "inicio": 0, "fin": desplazamientos[i_acuerda + 1]}]
    bloques = []  # chunks sin terminar de armar
    cap = sec = None
    esperando_titulo = False
    articulo_actual = None
    bloque = {"tipo": "encabezado", "inicio": desplazamientos[i_acuerda + 1], "i0": i_acuerda + 1}

    def cerrar(hasta_linea: int):
        bloque["fin"] = desplazamientos[hasta_linea]
        segmentos.append({"tipo": bloque["tipo"], "inicio": bloque["inicio"], "fin": bloque["fin"]})
        if bloque["tipo"] == "chunk":
            bloque["lineas"] = lineas[bloque["i0"]:hasta_linea]
            bloques.append(dict(bloque))

    for i in range(i_acuerda + 1, i_cierre):
        s = lineas[i].strip()
        m_art, m_par = ARTICULO.match(s), PARAGRAFO.match(s)
        if m_art or m_par:
            cerrar(i)
            if m_art:
                articulo_actual = m_art.group(1)
                etiqueta, id_corto = f"Artículo {articulo_actual}", f"art-{articulo_actual}"
                niveles = [n for n in (cap, sec) if n] + [etiqueta]
            else:
                if articulo_actual is None:
                    raise ValueError(f"Parágrafo sin artículo en la línea {i + 1}")
                numero = m_par.group(1)
                etiqueta = f"Artículo {articulo_actual}, Parágrafo" + (f" {numero}" if numero else "")
                id_corto = f"art-{articulo_actual}-par-{numero or 'unico'}"
                niveles = [n for n in (cap, sec) if n] + [f"Artículo {articulo_actual}", etiqueta.split(", ")[1]]
            bloque = {
                "tipo": "chunk", "inicio": desplazamientos[i], "i0": i,
                "articulo_num": articulo_actual, "id": f"{slug}#{id_corto}",
                "articulo": etiqueta, "jerarquia": " > ".join(niveles),
            }
        elif s and s.isupper():  # encabezado
            if bloque["tipo"] == "chunk":
                cerrar(i)
                bloque = {"tipo": "encabezado", "inicio": desplazamientos[i], "i0": i}
            m_cap = CAPITULO.match(s)
            if m_cap:
                cap, sec, esperando_titulo = f"Capítulo {m_cap.group(1)}", None, True
            elif esperando_titulo:
                cap, esperando_titulo = f"{cap}: {_titulo(s)}", False
            else:
                sec = _titulo(s)
        elif s and bloque["tipo"] == "encabezado":
            raise ValueError(f"Línea inesperada entre encabezados (línea {i + 1}): {s[:60]!r}")
    cerrar(i_cierre)
    segmentos.append({"tipo": "cierre", "inicio": desplazamientos[i_cierre], "fin": len(texto)})

    # Primera pasada: texto, notas y normas de cada chunk.
    chunks = []
    for b in bloques:
        t, notas, entradas = _clasificar(b["lineas"])
        chunks.append({
            "id": b["id"], "norma": norma, "articulo": b["articulo"], "jerarquia": b["jerarquia"],
            "texto": "\n".join(t), "enlace": enlace, "vigente": "", "modificado_por": entradas,
            "notas": notas, "inicio": b["inicio"], "fin": b["fin"], "_art": b["articulo_num"],
        })

    # Segunda pasada: las notas hablan del artículo, así que sus parágrafos heredan lo mismo.
    por_articulo = {}
    for c in chunks:
        vistas = por_articulo.setdefault(c["_art"], [])
        for e in c["modificado_por"]:
            if e not in vistas:
                vistas.append(e)
    for c in chunks:
        c["modificado_por"] = list(por_articulo[c.pop("_art")])
        c["vigente"] = _vigencia(c["modificado_por"])
    return chunks, segmentos


def partir_archivo(ruta: Path):
    texto = Path(ruta).read_text(encoding="utf-8")
    ficha = _leer_ficha(texto)
    organo = ficha.get("organo", "")
    norma = f"{ficha.get('norma', Path(ruta).stem)} del {SIGLAS.get(organo, organo)}".strip()
    return partir_texto(texto, slug=Path(ruta).stem, norma=norma, enlace=ficha.get("enlace", ""))


def escribir_jsonl(chunks: list[dict], ruta: Path = SALIDA) -> None:
    with open(ruta, "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")


def main(argv: list[str]) -> None:
    ruta = Path(argv[1]) if len(argv) > 1 else NORMA_POR_DEFECTO
    chunks, _ = partir_archivo(ruta)
    escribir_jsonl(chunks)
    articulos = sum("-par-" not in c["id"] for c in chunks)
    print(f"{ruta.name}: {len(chunks)} chunks ({articulos} artículos, {len(chunks) - articulos} parágrafos) -> {SALIDA}")


if __name__ == "__main__":
    main(sys.argv)
