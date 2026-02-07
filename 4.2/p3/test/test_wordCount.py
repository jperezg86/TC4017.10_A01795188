"""Pruebas unitarias para wordCount."""

# pylint: disable=invalid-name,wrong-import-position

import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from p3.source.wordCount import (  # type: ignore
    construir_reporte,
    contar_palabras,
    es_palabra_valida,
    leer_tokens,
)


class WordCountTest(unittest.TestCase):
    """Pruebas de conteo y validación."""

    def test_es_palabra_valida(self) -> None:
        """Valida tokens permitiendo guiones y apóstrofes."""

        self.assertTrue(es_palabra_valida("Hola"))
        self.assertTrue(es_palabra_valida("rock-n-roll"))
        self.assertTrue(es_palabra_valida("l'amour"))
        self.assertFalse(es_palabra_valida("hola123"))
        self.assertFalse(es_palabra_valida("-"))
        self.assertFalse(es_palabra_valida(""))

    def test_contar_palabras(self) -> None:
        """Cuenta ocurrencias preservando el orden de aparición."""

        tokens = ["hola", "mundo", "hola", "rock-n-roll"]
        conteo, orden = contar_palabras(tokens)
        self.assertEqual(conteo["hola"], 2)
        self.assertEqual(conteo["mundo"], 1)
        self.assertEqual(conteo["rock-n-roll"], 1)
        self.assertEqual(orden, ["hola", "mundo", "rock-n-roll"])

    def test_leer_tokens_con_error(self) -> None:
        """Lee tokens, omitiendo inválidos y acumulando errores."""

        with tempfile.TemporaryDirectory() as tmpdir:
            ruta = Path(tmpdir) / "datos.txt"
            ruta.write_text("hola 123 l'amour mundo\n", encoding="utf-8")
            tokens, errores = leer_tokens(ruta)
        self.assertEqual(tokens, ["hola", "l'amour", "mundo"])
        self.assertEqual(len(errores), 1)
        self.assertIn("dato inválido", errores[0])

    def test_construir_reporte(self) -> None:
        """Construye reporte en orden de aparición con totales."""

        conteo = {"hola": 2, "mundo": 1}
        orden = ["hola", "mundo"]
        lineas = construir_reporte("demo.txt", conteo, total=3, orden=orden)
        self.assertEqual(lineas[0], "Row Labels\tCount of demo")
        self.assertEqual(lineas[1], "hola\t2")
        self.assertEqual(lineas[2], "mundo\t1")
        self.assertEqual(lineas[-1], "Grand Total\t3")


if __name__ == "__main__":
    unittest.main()
