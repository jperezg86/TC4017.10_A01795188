# Conteo de palabras (P3)

Herramienta de línea de comandos para contar palabras únicas y su frecuencia en uno o más archivos de texto.

## Uso
Desde `4.2/p3/source`:
```bash
python wordCount.py ./input/TC1.txt
```
- Muestra en consola el reporte y errores de datos inválidos.
- Guarda un reporte consolidado en `4.2/p3/results/WordCountResults.txt`.
- Genera también un archivo por entrada con formato estilo `TC1.Results.txt` en `4.2/p3/results/<nombre>.Results.txt`.
- Incluye al final el tiempo transcurrido en segundos.

## Formato de salida
- Encabezado: `Row Labels<TAB>Count of <nombre>` donde `<nombre>` es el nombre del archivo sin extensión.
- Filas: palabra en minúsculas y su conteo, orden en que aparece por primera vez en el archivo.
- Línea `(blank)` vacía y `Grand Total` con el total de palabras válidas.
- Tiempo transcurrido al final del reporte consolidado.

## Datos inválidos
- Tokens válidos pueden incluir letras, guiones o apóstrofes (ej. `rock-n-roll`, `l'amour`).
- Tokens con otros caracteres se reportan en stderr y se omiten del conteo.
- La ejecución continúa aunque haya errores.

## Pruebas
Desde la raíz del repo:
```bash
. .venv/bin/activate
python -m pytest 4.2/p3/test/test_wordCount.py
```
