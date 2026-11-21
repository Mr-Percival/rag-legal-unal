"""Pruebas del partidor (rag/partir.py).

Correr desde la raíz del repositorio:
    python -m unittest tests.test_partir -v
(o `python -m pytest tests/test_partir.py` si tienes pytest)
"""
import sys
import unittest
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from rag.partir import NORMA_POR_DEFECTO, partir_archivo, partir_texto  # noqa: E402

TEXTO = NORMA_POR_DEFECTO.read_text(encoding="utf-8")
CHUNKS, SEGMENTOS = partir_archivo(NORMA_POR_DEFECTO)
POR_ID = {c["id"].split("#")[1]: c for c in CHUNKS}


def lineas_utiles(texto: str) -> list[str]:
    return [l.strip() for l in texto.splitlines() if l.strip()]


class ReconstruyeLaNorma(unittest.TestCase):
    """El «hecho cuando» de la tarea: sin perder ni duplicar texto."""

    def test_los_bloques_cubren_el_archivo_sin_huecos_ni_solapes(self):
        ordenados = sorted(SEGMENTOS, key=lambda s: s["inicio"])
        self.assertEqual(ordenados[0]["inicio"], 0)
        self.assertEqual(ordenados[-1]["fin"], len(TEXTO))
        for a, b in zip(ordenados, ordenados[1:]):
            self.assertEqual(a["fin"], b["inicio"], f"hueco o solape entre {a['tipo']} y {b['tipo']}")

    def test_cada_linea_de_la_norma_aparece_exactamente_una_vez(self):
        """Compara línea por línea la norma original con lo que dicen los chunks."""
        reconstruido = Counter()
        for s in SEGMENTOS:
            if s["tipo"] != "chunk":  # preámbulo, encabezados y cierre
                reconstruido.update(lineas_utiles(TEXTO[s["inicio"]:s["fin"]]))
        for c in CHUNKS:  # el contenido sale de los chunks, no del archivo
            reconstruido.update(c["texto"].split("\n"))
            reconstruido.update(c["notas"])
        self.assertEqual(reconstruido, Counter(lineas_utiles(TEXTO)))

    def test_el_texto_de_cada_chunk_mas_sus_notas_es_su_region(self):
        for c in CHUNKS:
            region = lineas_utiles(TEXTO[c["inicio"]:c["fin"]])
            self.assertEqual(Counter(region), Counter(c["texto"].split("\n") + c["notas"]), c["id"])


class UnChunkPorArticuloOParagrafo(unittest.TestCase):
    def test_hay_62_articulos_en_orden_y_sin_repetir(self):
        articulos = [c for c in CHUNKS if "-par-" not in c["id"]]
        self.assertEqual([c["id"].split("#art-")[1] for c in articulos], [str(n) for n in range(1, 63)])

    def test_los_ids_son_unicos(self):
        ids = [c["id"] for c in CHUNKS]
        self.assertEqual(len(ids), len(set(ids)))

    def test_cada_paragrafo_va_justo_despues_de_su_articulo(self):
        articulo_actual = None
        for c in CHUNKS:
            if "-par-" in c["id"]:
                self.assertTrue(c["id"].startswith(articulo_actual + "-par-"), c["id"])
            else:
                articulo_actual = c["id"]

    def test_el_articulo_no_repite_el_texto_de_sus_paragrafos(self):
        self.assertNotIn("Quienes sean autorizados", POR_ID["art-1"]["texto"])
        self.assertIn("Quienes sean autorizados", POR_ID["art-1-par-unico"]["texto"])
        self.assertTrue(all("PARÁGRAFO" not in c["texto"] for c in CHUNKS if "-par-" not in c["id"]))

    def test_parrafos_numerados(self):
        for n in (1, 2):
            self.assertIn(f"art-15-par-{n}", POR_ID)
        self.assertIn("Artículo 15, Parágrafo 2", POR_ID["art-15-par-2"]["articulo"])

    def test_jerarquia(self):
        self.assertEqual(
            POR_ID["art-2"]["jerarquia"],
            "Capítulo I: Del proceso de formación > De la admisión > Artículo 2",
        )
        self.assertTrue(POR_ID["art-57"]["jerarquia"].startswith("Capítulo II: De las distinciones"))

    def test_campos_del_contrato(self):
        for c in CHUNKS:
            for campo in ("id", "norma", "articulo", "jerarquia", "texto", "enlace", "vigente", "modificado_por"):
                self.assertIn(campo, c)
            self.assertTrue(c["texto"])
        self.assertEqual(CHUNKS[0]["norma"], "Acuerdo 008 de 2008 del CSU")


class NormasQueModificanOExceptuan(unittest.TestCase):
    def normas(self, clave, tipo=None):
        return [e["norma"] for e in POR_ID[clave]["modificado_por"] if tipo in (None, e["tipo"])]

    def test_marca_dentro_del_texto(self):
        self.assertEqual(
            self.normas("art-4", "exceptuado"), ["Acuerdo 28 de 2024 del Consejo Superior Universitario"]
        )
        self.assertEqual(self.normas("art-42", "modificado"), ["Acuerdo CSU 040 de 2012"])

    def test_el_punto_de_art_no_corta_la_frase(self):
        self.assertEqual(
            self.normas("art-57", "exceptuado"),
            ["Resolución 40 de 2023 de la Comisión Delegataria del Consejo Superior Universitario"],
        )

    def test_notas_de_vigencia_con_verbo(self):
        art10 = self.normas("art-10", "exceptuado")
        self.assertEqual(len(art10), 7)
        self.assertEqual(art10[0], "Resolución 41 de 2020 de la Comisión Delegataria del Consejo Superior Universitario")
        self.assertEqual(len(self.normas("art-15", "exceptuado")), 7)

    def test_lista_de_covid(self):
        self.assertEqual(len(self.normas("art-12", "modificado_transitoriamente")), 5)

    def test_el_parrafo_hereda_lo_del_articulo(self):
        self.assertEqual(POR_ID["art-15-par-1"]["modificado_por"], POR_ID["art-15"]["modificado_por"])
        self.assertEqual(POR_ID["art-15-par-1"]["vigente"], "parcial")

    def test_reglamentado_o_ver_no_cuentan_como_modificacion(self):
        self.assertEqual(POR_ID["art-2"]["modificado_por"], [])
        self.assertEqual(POR_ID["art-2"]["vigente"], "sí")
        self.assertEqual(len(POR_ID["art-2"]["notas"]), 2)

    def test_cada_anotacion_cita_la_fuente(self):
        """Nada se infiere: la cita es una frase literal del archivo y contiene la norma."""
        for c in CHUNKS:
            for e in c["modificado_por"]:
                self.assertIn(e["cita"], TEXTO, c["id"])
                self.assertIn(e["norma"], e["cita"], c["id"])


class CasosChicos(unittest.TestCase):
    MINI = (
        "ACUERDA:\n\nCAPÍTULO I\nDEL INICIO\n\nARTÍCULO 1. Uno.\nVer algo.\n\n"
        "PARÁGRAFO. Cola.\n\nNota de vigencia\nLa Resolución 5 de 2020 exceptuó el artículo 1.\n\n"
        "ARTÍCULO 2-1. Dos.\n\nCOMUNÍQUESE Y CÚMPLASE.\nFirma\n"
    )

    def test_articulo_con_guion_y_parrafo_unico(self):
        chunks, _ = partir_texto(self.MINI, "x", "X")
        self.assertEqual([c["id"] for c in chunks], ["x#art-1", "x#art-1-par-unico", "x#art-2-1"])
        self.assertEqual(chunks[1]["modificado_por"][0]["norma"], "Resolución 5 de 2020")
        self.assertEqual(chunks[0]["vigente"], "parcial")
        self.assertEqual(chunks[2]["vigente"], "sí")

    def test_sin_acuerda_falla_con_mensaje_claro(self):
        with self.assertRaises(ValueError):
            partir_texto("ARTÍCULO 1. Algo.\n", "x", "X")


if __name__ == "__main__":
    unittest.main()
