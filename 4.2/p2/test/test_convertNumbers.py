"""Pruebas unitarias para convertNumbers."""

# pylint: disable=invalid-name,wrong-import-position

import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from p2.source.convertNumbers import (  # type: ignore
    a_binario,
    a_hexadecimal,
    construir_reporte_para_archivo,
    convertir_base,
    leer_numeros_desde_archivo,
)


class ConvertNumbersTest(unittest.TestCase):
    """Pruebas de conversión y parsing."""

    def test_convertir_base_binario_y_hex(self) -> None:
        """Convierte binario y hexadecimal sin funciones nativas."""

        self.assertEqual(convertir_base(0, 2, "01"), "0")
        self.assertEqual(convertir_base(10, 2, "01"), "1010")
        self.assertEqual(convertir_base(255, 16, "0123456789ABCDEF"), "FF")
        self.assertEqual(convertir_base(-15, 16, "0123456789ABCDEF"), "-F")

    def test_a_binario_y_hexadecimal_helpers(self) -> None:
        """Wrappers producen las representaciones esperadas."""

        self.assertEqual(a_binario(5), "101")
        self.assertEqual(a_hexadecimal(26), "1A")
        self.assertEqual(a_binario(-39), "1111011001")
        self.assertEqual(a_hexadecimal(-39), "FFFFFFFFD9")

    def test_leer_numeros_con_errores(self) -> None:
        """Lee números y reporta tokens inválidos sin detenerse."""

        with tempfile.TemporaryDirectory() as tmpdir:
            ruta = Path(tmpdir) / "datos.txt"
            ruta.write_text("1 2 x\n3\n", encoding="utf-8")
            tokens, errores = leer_numeros_desde_archivo(ruta)
        self.assertEqual(tokens, ["1", "2", "x", "3"])
        self.assertEqual(len(errores), 1)
        self.assertIn("dato inválido", errores[0])

    def test_construir_reporte_para_archivo(self) -> None:
        """El reporte incluye encabezados y conversiones."""

        lineas = construir_reporte_para_archivo("demo.txt", ["2", "10"])
        self.assertEqual(lineas[0], "ITEM\tdemo\tBIN\tHEX")
        self.assertEqual(lineas[1], "1\t2\t10\t2")
        self.assertEqual(lineas[2], "2\t10\t1010\tA")


if __name__ == "__main__":
    unittest.main()
