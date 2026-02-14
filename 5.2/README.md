# Compute Sales

`computeSales.py` calcula el costo total de ventas usando:
- un catálogo de precios en JSON
- un registro de ventas en JSON

## Requisitos
- Python 3

## Ejecución mínima
Desde la raíz del repositorio:

```bash
python 5.2/source/computeSales.py priceCatalogue.json salesRecord.json
```

También puedes ejecutarlo desde `5.2/source`:

```bash
python computeSales.py priceCatalogue.json salesRecord.json
```

## Formato esperado del catálogo (`priceCatalogue.json`)
Arreglo de objetos con `title` y `price`.

```json
[
  {"title": "apple", "price": 2.5},
  {"title": "banana", "price": 1.0}
]
```

## Formato esperado de ventas (`salesRecord.json`)
Arreglo de ventas. Cada venta tiene `items` como lista.

Un item puede ser:
- texto: nombre del producto
- objeto: `{ "title": "...", "quantity": N }`

```json
[
  {
    "items": [
      "apple",
      {"title": "banana", "quantity": 3}
    ]
  },
  {
    "items": [
      {"title": "apple", "quantity": 2}
    ]
  }
]
```

## Salida
El programa imprime un resumen legible en consola y además genera:
- `SalesResults.txt`

La salida incluye:
- total por venta
- total general (`Grand Total`)
- tiempo transcurrido (`Elapsed time`)

## Manejo de errores
Si encuentra datos inválidos:
- muestra mensajes en consola con prefijo `ERROR:`
- continúa procesando el resto de la información válida

## Pruebas
```bash
pytest -q 5.2/source/tests/test_computeSales.py
```
