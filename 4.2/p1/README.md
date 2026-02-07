# Estadísticas descriptivas (P1)

### Entregable 4.2 Práctica 1


## Ejecución
Ubica los archivos de datos en `4.2/p1/source/input/` (o usa rutas absolutas/relativas). Desde `4.2/p1/source`:
```bash
python computeStatistics.py ./input/TC3.txt ./input/TC4.txt
```
- La consola muestra solo los resultados de la corrida actual.
- El archivo acumulado se escribe en `4.2/p1/results/StatisticsResults.txt`, agregando columnas por cada archivo de la corrida y conservando las previas.

## Opciones
Actualmente no hay flags adicionales. Para reiniciar el historial, borra `4.2/p1/results/StatisticsResults.txt` antes de ejecutar.

## Tests
Desde la raíz del repo:
```bash
. .venv/bin/activate
python -m unittest discover -s 4.2/p1/test -p "test_computeStatistics.py"
```

## Notas
- Los valores inválidos en los archivos se reportan por stderr y se omiten.
- Si un archivo no tiene datos válidos, se marca `#N/A` en la columna correspondiente.
