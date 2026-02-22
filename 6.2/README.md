# Práctica 6.2 - Sistema de Reservaciones de Hotel

Estructura del proyecto:

- `src/`: código fuente
- `test/`: pruebas unitarias con `unittest`
- `source/input/`: archivos de entrada en texto (casos de prueba)
- `input/`: archivos de datos persistidos por el sistema (`*.jsonl`)
- `result/`: resultados de ejecución (cobertura, lint, etc.)

Este módulo implementa clases y persistencia en archivos para:

- Hoteles
- Clientes
- Reservaciones

## Requisitos

- Python 3
- Dependencias de desarrollo instaladas (opcional para lint/cobertura)

Instalación sugerida:

```bash
pip install -r requirements-dev.txt
```

## Ejecución del sistema (menú interactivo)

Desde la raíz del repositorio:

```bash
cd 6.2
python3 -m src.main
```

Para usar un directorio de datos específico:

```bash
cd 6.2
python3 -m src.main --data-dir source/input
```

Salida de ejecución:

- La salida en consola también se guarda en `6.2/result/HotelSystemResults.txt`
- Cada ejecución agrega una nueva sección con marca de tiempo

## Ejecutar pruebas unitarias

```bash
cd 6.2
python3 -m unittest discover -s test -v
```

## Cobertura

```bash
cd 6.2
coverage run -m unittest discover -s test
coverage report -m
coverage html -d result/htmlcov
```

## Validación de estilo y calidad

```bash
flake8 6.2/src 6.2/test
pylint 6.2/src/*.py 6.2/test/*.py
```

### Importante

La evidencia documentada de ejecución está en result/screenrecord, es un video mp4 donde pueden ver la ejecución del programa.
