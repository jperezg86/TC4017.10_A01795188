"""Interfaz de consola para el sistema de reservaciones de hotel."""

from __future__ import annotations

import argparse
import datetime
import sys
from pathlib import Path

from src.hotel_system import HotelSystem


RESULT_FILE = (
    Path(__file__).resolve().parents[1]
    / "result"
    / "HotelSystemResults.txt"
)


class FlujoDuplicado:
    """Replica la salida a consola y a un archivo de resultados."""

    def __init__(self, consola, archivo) -> None:
        """Inicializa destino principal y secundario de salida."""
        self.consola = consola
        self.archivo = archivo

    def write(self, mensaje: str) -> int:
        """Escribe en ambos destinos."""
        self.consola.write(mensaje)
        self.archivo.write(mensaje)
        return len(mensaje)

    def flush(self) -> None:
        """Fuerza el vaciado del buffer en ambos destinos."""
        self.consola.flush()
        self.archivo.flush()


def parse_args() -> argparse.Namespace:
    """Procesa argumentos de linea de comandos."""
    parser = argparse.ArgumentParser(
        description="Sistema de reservaciones de hotel por consola"
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "source" / "input",
        help=(
            "Directorio donde se almacenan hotels.jsonl, "
            "customers.jsonl y reservations.jsonl"
        ),
    )
    return parser.parse_args()


def solicitar_entero(mensaje: str) -> int:
    """Solicita un numero entero al usuario con reintento."""
    while True:
        valor = input(mensaje).strip()
        try:
            return int(valor)
        except ValueError:
            print("ERROR: debes ingresar un numero entero.")


def mostrar_menu() -> None:
    """Imprime las opciones disponibles en consola."""
    print("\n=== Sistema de Reservaciones de Hotel ===")
    print("1. Crear hotel")
    print("2. Eliminar hotel")
    print("3. Mostrar informacion de hotel")
    print("4. Modificar informacion de hotel")
    print("5. Crear cliente")
    print("6. Eliminar cliente")
    print("7. Mostrar informacion de cliente")
    print("8. Modificar informacion de cliente")
    print("9. Crear reservacion")
    print("10. Cancelar reservacion")
    print("0. Salir")


def opcion_crear_hotel(sistema: HotelSystem) -> None:
    """Solicita datos y crea un hotel."""
    nombre = input("Nombre del hotel: ").strip()
    ubicacion = input("Ubicacion: ").strip()
    total_cuartos = solicitar_entero("Total de cuartos: ")
    amenidades_crudas = input(
        "Amenidades separadas por coma (opcional): "
    ).strip()
    amenidades = []
    if amenidades_crudas:
        amenidades = [
            item.strip()
            for item in amenidades_crudas.split(",")
            if item.strip()
        ]

    hotel = sistema.create_hotel(nombre, ubicacion, total_cuartos, amenidades)
    if hotel is None:
        print("No fue posible crear el hotel.")
        return
    print("Hotel creado con exito.")
    print(f"ID asignado: {hotel.hotel_id}")
    print(f"Guardado en: {sistema.hotels_file}")


def opcion_eliminar_hotel(sistema: HotelSystem) -> None:
    """Solicita ID y elimina un hotel."""
    hotel_id = input("ID del hotel a eliminar: ").strip()
    eliminado = sistema.delete_hotel(hotel_id)
    if eliminado:
        print("Hotel eliminado correctamente.")
        print(f"Archivo actualizado: {sistema.hotels_file}")


def opcion_mostrar_hotel(sistema: HotelSystem) -> None:
    """Solicita ID y muestra informacion de hotel."""
    hotel_id = input("ID del hotel a consultar: ").strip()
    data = sistema.display_hotel_information(hotel_id)
    if data is not None:
        print(data)


def opcion_modificar_hotel(sistema: HotelSystem) -> None:
    """Solicita cambios y modifica un hotel."""
    hotel_id = input("ID del hotel a modificar: ").strip()
    print("Deja en blanco los campos que no quieras cambiar.")

    cambios: dict[str, object] = {}
    nombre = input("Nuevo nombre: ").strip()
    if nombre:
        cambios["name"] = nombre

    ubicacion = input("Nueva ubicacion: ").strip()
    if ubicacion:
        cambios["location"] = ubicacion

    total_cuartos = input("Nuevo total de cuartos: ").strip()
    if total_cuartos:
        try:
            cambios["total_rooms"] = int(total_cuartos)
        except ValueError:
            print("ERROR: total de cuartos invalido.")
            return

    disponibles = input("Nuevo numero de cuartos disponibles: ").strip()
    if disponibles:
        try:
            cambios["available_rooms"] = int(disponibles)
        except ValueError:
            print("ERROR: cuartos disponibles invalido.")
            return

    amenidades = input("Nuevas amenidades separadas por coma: ").strip()
    if amenidades:
        cambios["amenities"] = [
            item.strip() for item in amenidades.split(",") if item.strip()
        ]

    if not cambios:
        print("No se proporcionaron cambios.")
        return

    modificado = sistema.modify_hotel_information(hotel_id, **cambios)
    if modificado:
        print("Hotel actualizado correctamente.")
        print(f"Archivo actualizado: {sistema.hotels_file}")


def opcion_crear_cliente(sistema: HotelSystem) -> None:
    """Solicita datos y crea un cliente."""
    nombre = input("Nombre completo: ").strip()
    correo = input("Correo electronico: ").strip()
    telefono = input("Telefono: ").strip()
    cliente = sistema.create_customer(nombre, correo, telefono)
    if cliente is None:
        print("No fue posible crear el cliente.")
        return
    print("Cliente creado con exito.")
    print(f"ID asignado: {cliente.customer_id}")
    print(f"Guardado en: {sistema.customers_file}")


def opcion_eliminar_cliente(sistema: HotelSystem) -> None:
    """Solicita ID y elimina un cliente."""
    customer_id = input("ID del cliente a eliminar: ").strip()
    eliminado = sistema.delete_customer(customer_id)
    if eliminado:
        print("Cliente eliminado correctamente.")
        print(f"Archivo actualizado: {sistema.customers_file}")


def opcion_mostrar_cliente(sistema: HotelSystem) -> None:
    """Solicita ID y muestra informacion de cliente."""
    customer_id = input("ID del cliente a consultar: ").strip()
    data = sistema.display_customer_information(customer_id)
    if data is not None:
        print(data)


def opcion_modificar_cliente(sistema: HotelSystem) -> None:
    """Solicita cambios y modifica un cliente."""
    customer_id = input("ID del cliente a modificar: ").strip()
    print("Deja en blanco los campos que no quieras cambiar.")

    cambios: dict[str, object] = {}
    nombre = input("Nuevo nombre completo: ").strip()
    if nombre:
        cambios["full_name"] = nombre

    correo = input("Nuevo correo electronico: ").strip()
    if correo:
        cambios["email"] = correo

    telefono = input("Nuevo telefono: ").strip()
    if telefono:
        cambios["phone"] = telefono

    if not cambios:
        print("No se proporcionaron cambios.")
        return

    modificado = sistema.modify_customer_information(customer_id, **cambios)
    if modificado:
        print("Cliente actualizado correctamente.")
        print(f"Archivo actualizado: {sistema.customers_file}")


def opcion_crear_reservacion(sistema: HotelSystem) -> None:
    """Solicita datos y crea una reservacion."""
    customer_id = input("ID del cliente: ").strip()
    hotel_id = input("ID del hotel: ").strip()
    room_count = solicitar_entero("Cantidad de cuartos a reservar: ")

    reservacion = sistema.create_reservation(customer_id, hotel_id, room_count)
    if reservacion is None:
        print("No fue posible crear la reservacion.")
        return
    print("Reservacion creada con exito.")
    print(f"ID asignado: {reservacion.reservation_id}")
    print(f"Archivo actualizado: {sistema.reservations_file}")
    print(f"Archivo actualizado: {sistema.hotels_file}")


def opcion_cancelar_reservacion(sistema: HotelSystem) -> None:
    """Solicita ID y cancela una reservacion."""
    reservation_id = input("ID de la reservacion a cancelar: ").strip()
    cancelada = sistema.cancel_reservation(reservation_id)
    if cancelada:
        print("Reservacion cancelada correctamente.")
        print(f"Archivo actualizado: {sistema.reservations_file}")
        print(f"Archivo actualizado: {sistema.hotels_file}")


def ejecutar_menu(sistema: HotelSystem) -> None:
    """Ejecuta el ciclo principal del menu interactivo."""
    acciones = {
        "1": opcion_crear_hotel,
        "2": opcion_eliminar_hotel,
        "3": opcion_mostrar_hotel,
        "4": opcion_modificar_hotel,
        "5": opcion_crear_cliente,
        "6": opcion_eliminar_cliente,
        "7": opcion_mostrar_cliente,
        "8": opcion_modificar_cliente,
        "9": opcion_crear_reservacion,
        "10": opcion_cancelar_reservacion,
    }

    while True:
        mostrar_menu()
        opcion = input("Selecciona una opcion: ").strip()

        if opcion == "0":
            print("Saliendo del sistema. Hasta luego.")
            break

        accion = acciones.get(opcion)
        if accion is None:
            print("ERROR: opcion invalida.")
            continue

        accion(sistema)


def main() -> int:
    """Punto de entrada del programa."""
    args = parse_args()
    args.data_dir.mkdir(parents=True, exist_ok=True)
    sistema = HotelSystem(data_dir=args.data_dir)
    RESULT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with RESULT_FILE.open("a", encoding="utf-8") as salida:
        salida.write("\n" + "=" * 60 + "\n")
        salida.write(
            "Inicio de ejecucion: "
            f"{datetime.datetime.now().isoformat(timespec='seconds')}\n"
        )

        salida_duplicada = FlujoDuplicado(sys.stdout, salida)
        error_duplicado = FlujoDuplicado(sys.stderr, salida)
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        sys.stdout = salida_duplicada
        sys.stderr = error_duplicado
        try:
            print(f"Directorio de datos: {args.data_dir}")
            print(f"Archivo de resultados: {RESULT_FILE}")
            ejecutar_menu(sistema)
        finally:
            sys.stdout = original_stdout
            sys.stderr = original_stderr

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
