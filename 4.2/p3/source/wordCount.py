"""Cuenta frecuencia de palabras en archivos de texto."""

# pylint: disable=invalid-name,duplicate-code

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


def es_palabra_valida(token: str) -> bool:
    """Determina si un token es válido: letras, guiones o apóstrofes."""

    if not token:
        return False

    tiene_letra = False
    for caracter in token:
        codigo = ord(caracter)
        es_mayuscula = 65 <= codigo <= 90  # A-Z
        es_minuscula = 97 <= codigo <= 122  # a-z
        es_guion = caracter == "-"
        es_apostrofe = caracter == "'"
        if es_mayuscula or es_minuscula:
            tiene_letra = True
            continue
        if not (es_guion or es_apostrofe):
            return False

    return tiene_letra


def contar_palabras(tokens: Iterable[str]) -> Tuple[Dict[str, int], List[str]]:
    """Cuenta ocurrencias preservando orden de primera aparición."""

    conteo: Dict[str, int] = {}
    orden: List[str] = []
    for palabra in tokens:
        if palabra in conteo:
            conteo[palabra] += 1
        else:
            conteo[palabra] = 1
            orden.append(palabra)
    return conteo, orden


def leer_tokens(ruta: Path) -> Tuple[List[str], List[str]]:
    """Lee tokens desde archivo, devolviendo válidos y errores."""

    validos: List[str] = []
    errores: List[str] = []

    with ruta.open("r", encoding="utf-8") as archivo:
        for linea_idx, linea in enumerate(archivo, start=1):
            for token in linea.strip().split():
                if not token:
                    continue
                if es_palabra_valida(token):
                    validos.append(token.lower())
                else:
                    mensaje = (
                        f"{ruta.name}: dato inválido en línea {linea_idx}: "
                        f"{token}"
                    )
                    errores.append(mensaje)
    return validos, errores


def construir_reporte(
    nombre_archivo: str, conteo: Dict[str, int], total: int, orden: List[str]
) -> List[str]:
    """Construye líneas de reporte estilo TCX.Results.txt."""

    stem = Path(nombre_archivo).stem
    encabezado = f"Row Labels\tCount of {stem}"
    lineas: List[str] = [encabezado]

    for palabra in orden:
        lineas.append(f"{palabra}\t{conteo[palabra]}")

    lineas.append("(blank)\t")
    lineas.append(f"Grand Total\t{total}")
    return lineas


def parse_args() -> argparse.Namespace:
    """Parsea argumentos de línea de comandos."""

    parser = argparse.ArgumentParser(
        description=(
            "Cuenta frecuencia de palabras en uno o más archivos, "
            "manejando datos inválidos sin detener la ejecución."
        )
    )
    parser.add_argument(
        "data_files",
        nargs="+",
        type=Path,
        help=(
            "Uno o más archivos de entrada con palabras separadas por espacios"
        ),
    )
    return parser.parse_args()


def procesar_archivo(ruta: Path) -> Tuple[List[str], List[str]]:
    """Procesa un archivo y devuelve (reporte, errores)."""

    tokens, errores = leer_tokens(ruta)
    if not tokens:
        errores.append(
            f"{ruta.name}: no se encontraron palabras válidas. Se omite."
        )
        return [], errores

    conteo, orden = contar_palabras(tokens)
    reporte = construir_reporte(ruta.name, conteo, len(tokens), orden)
    return reporte, errores


def main() -> int:
    """Punto de entrada CLI."""

    args = parse_args()
    inicio = time.perf_counter()

    bloques: List[str] = []
    errores_totales: List[str] = []

    for ruta in args.data_files:
        if not ruta.is_file():
            errores_totales.append(f"Archivo no encontrado: {ruta}")
            continue

        reporte, errores = procesar_archivo(ruta)
        errores_totales.extend(errores)

        if not reporte:
            continue

        bloques.extend(reporte)
        bloques.append("")

        # Archivo individual en results/<stem>.Results.txt
        resultado_individual = (
            Path(__file__).resolve().parents[1]
            / "results"
            / f"{ruta.stem}.Results.txt"
        )
        resultado_individual.parent.mkdir(parents=True, exist_ok=True)
        resultado_individual.write_text(
            "\n".join(reporte) + "\n",
            encoding="utf-8",
        )

    for error in errores_totales:
        print(error, file=sys.stderr)

    if not bloques:
        print("No se procesaron datos. Nada que contar.", file=sys.stderr)
        return 1

    elapsed = time.perf_counter() - inicio
    resumen_tiempo = f"Tiempo transcurrido (s):\t{elapsed:.5f}"
    bloques.append(resumen_tiempo)

    # Mostrar en pantalla
    for linea in bloques:
        print(linea)

    # Escribir reporte consolidado
    salida_consolidada = (
        Path(__file__).resolve().parents[1]
        / "results"
        / "WordCountResults.txt"
    )
    salida_consolidada.write_text(
        "\n".join(bloques) + "\n",
        encoding="utf-8",
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
