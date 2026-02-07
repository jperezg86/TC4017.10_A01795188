# Conversión de números (P2)

Herramienta de línea de comandos para convertir números enteros a base binaria y hexadecimal.

## Requisitos
- Python 3.10+ (este proyecto usa `.venv`)
- Dependencias ya listadas en `requirements-dev.txt` (se instalan en `.venv`)

## Preparación del entorno
Desde la raíz del repo:
```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
```

## Ejecución
Coloca los archivos de entrada (texto con enteros separados por espacio/salto de línea) y ejecuta desde `4.2/p2/source`:
```bash
python convertNumbers.py ./input/TC1.txt ./input/TC2.txt
```
- La consola muestra solo el resultado de la corrida actual.
- El reporte se guarda en `4.2/p2/results/ConvertionResults.txt`.
- Cada bloque usa el formato del archivo de ejemplo `A4.2.P2.Results.txt`:
	- Encabezado: `ITEM<TAB>TCX<TAB>BIN<TAB>HEX` (TCX es el nombre del archivo sin extensión).
	- Filas: índice 1..N, valor leído, binario y hexadecimal; datos inválidos se muestran como `#VALUE!`.

## Manejo de datos inválidos
- Tokens no convertibles a entero se reportan en stderr, pero también aparecen en el reporte con `#VALUE!`.
- Si un archivo está vacío, se omite y se informa en stderr.

## Lógica de conversión
- Conversión hecha con algoritmos básicos (sin `bin`/`hex`).
- Binario: estilo DEC2BIN de Excel; negativos usan complemento a dos de 10 bits.
- Hexadecimal: estilo DEC2HEX de Excel; negativos usan complemento a dos de 40 bits con 10 dígitos hexadecimales.

## Tests
Desde la raíz del repo:
```bash
. .venv/bin/activate
python -m unittest discover -s 4.2/p2/test -p "test_convertNumbers.py"
```

## Notas
- Soporta uno o varios archivos en una sola ejecución.
- Escala para cientos/miles de ítems por archivo.
