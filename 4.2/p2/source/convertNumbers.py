"""Herramienta CLI para convertir números a binario y hexadecimal."""

# pylint: disable=invalid-name

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, List, Tuple


def leer_numeros_desde_archivo(ruta: Path) -> Tuple[List[str], List[str]]:
    """Lee tokens desde un archivo, reportando datos inválidos."""

    tokens: List[str] = []
    errores: List[str] = []

    with ruta.open("r", encoding="utf-8") as archivo:
        for linea_idx, linea in enumerate(archivo, start=1):
            for token in linea.strip().split():
                if not token:
                    continue
                tokens.append(token)
                try:
                    int(token)
                except ValueError:
                    mensaje = (
                        f"{ruta.name}: dato inválido en línea {linea_idx}: "
                        f"{token}"
                    )
                    errores.append(mensaje)

    return tokens, errores


def convertir_base(numero: int, base: int, simbolos: str) -> str:
    """Convierte un entero a otra base sin usar funciones nativas."""

    if numero == 0:
        return "0"

    signo = ""
    valor = numero
    if numero < 0:
        signo = "-"
        valor = -numero

    digitos: List[str] = []
    while valor > 0:
        valor, residuo = divmod(valor, base)
        digitos.append(simbolos[residuo])

    return signo + "".join(reversed(digitos))


def a_binario(numero: int) -> str:
    """Convierte a binario estilo DEC2BIN (dos complementos para negativos)."""

    if numero < 0:
        complemento_dos = (1 << 10) + numero
        return format(complemento_dos, "010b")

    return convertir_base(numero, 2, "01")


def a_hexadecimal(numero: int) -> str:
    """Convierte a hexadecimal estilo DEC2HEX (dos complementos para negativos)."""

    if numero < 0:
        complemento_dos = (1 << 40) + numero
        return format(complemento_dos, "010X")

    return convertir_base(numero, 16, "0123456789ABCDEF")


def construir_reporte_para_archivo(
    nombre: str,
    tokens: Iterable[str],
) -> List[str]:
    """Genera líneas de reporte con ITEM, valor y conversiones."""

    encabezado = f"ITEM\t{Path(nombre).stem}\tBIN\tHEX"
    lineas = [encabezado]

    for indice, token in enumerate(tokens, start=1):
        try:
            numero = int(token)
        except ValueError:
            binario = "#VALUE!"
            hexadecimal = "#VALUE!"
        else:
            binario = a_binario(numero)
            hexadecimal = a_hexadecimal(numero)

        lineas.append(f"{indice}\t{token}\t{binario}\t{hexadecimal}")

    return lineas


def parse_args() -> argparse.Namespace:
    """Parsea argumentos de línea de comandos."""

    parser = argparse.ArgumentParser(
        description=(
            "Convierte números de archivos de texto a binario y hexadecimal, "
            "manejando datos inválidos sin detener la ejecución."
        )
    )
    parser.add_argument(
        "data_files",
        nargs="+",
        type=Path,
        help="Uno o más archivos de entrada con números enteros",
    )
    return parser.parse_args()


def main() -> int:
    """Punto de entrada del programa."""

    args = parse_args()
    errores: List[str] = []
    bloques_reporte: List[str] = []
    total_registros = 0

    for ruta in args.data_files:
        if not ruta.is_file():
            errores.append(f"Archivo no encontrado: {ruta}")
            continue

        tokens, errores_archivo = leer_numeros_desde_archivo(ruta)
        errores.extend(errores_archivo)

        if not tokens:
            errores.append(f"{ruta.name}: archivo vacío. Se omite.")
            continue

        bloque = construir_reporte_para_archivo(ruta.name, tokens)
        bloques_reporte.extend(bloque)
        bloques_reporte.append("")  # línea en blanco separadora
        total_registros += len(tokens)

    for error in errores:
        print(error, file=sys.stderr)

    if total_registros == 0:
        mensaje = "No se procesaron datos. Nada que convertir."
        print(mensaje, file=sys.stderr)
        return 1

    # Imprime solo el resultado de la corrida actual.
    for linea in bloques_reporte:
        print(linea)

    # Escribe el archivo de salida.
    resultado_path = (
        Path(__file__).resolve().parents[1]
        / "results"
        / "ConvertionResults.txt"
    )
    resultado_path.parent.mkdir(parents=True, exist_ok=True)
    resultado_path.write_text(
        "\n".join(bloques_reporte) + "\n",
        encoding="utf-8",
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
