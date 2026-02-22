"""Pruebas unitarias del sistema de reservaciones de hotel."""

from __future__ import annotations

import io
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from src.hotel_system import HotelSystem
from src.storage import load_jsonl


class TestHotelSystem(unittest.TestCase):
    """Valida comportamientos CRUD y de reservaciones."""

    def setUp(self) -> None:
        """Crea un directorio temporal por caso de prueba."""
        temp_path = tempfile.mkdtemp()
        self.data_dir = Path(temp_path)
        self.system = HotelSystem(data_dir=self.data_dir)
        self.addCleanup(shutil.rmtree, self.data_dir)

    def test_create_and_display_hotel(self) -> None:
        """Crea un hotel y recupera su información."""
        created = self.system.create_hotel(
            name="Hotel Centro",
            location="Monterrey",
            total_rooms=20,
            amenities=["wifi", "gym"],
        )

        self.assertIsNotNone(created)
        payload = self.system.display_hotel_information(created.hotel_id)
        self.assertIsNotNone(payload)
        assert payload is not None
        self.assertEqual(payload["name"], "Hotel Centro")
        self.assertEqual(payload["available_rooms"], 20)

    def test_modify_hotel_information(self) -> None:
        """Modifica datos de un hotel existente."""
        hotel = self.system.create_hotel(
            name="Hotel Norte",
            location="Saltillo",
            total_rooms=15,
        )
        assert hotel is not None

        changed = self.system.modify_hotel_information(
            hotel.hotel_id,
            name="Hotel Norte Plus",
            total_rooms=18,
            available_rooms=16,
        )

        self.assertTrue(changed)
        payload = self.system.display_hotel_information(hotel.hotel_id)
        assert payload is not None
        self.assertEqual(payload["name"], "Hotel Norte Plus")
        self.assertEqual(payload["total_rooms"], 18)

    def test_delete_hotel_no_active(self) -> None:
        """Elimina un hotel cuando no hay reservaciones activas."""
        hotel = self.system.create_hotel(
            name="Hotel Sur",
            location="Puebla",
            total_rooms=5,
        )
        assert hotel is not None

        deleted = self.system.delete_hotel(hotel.hotel_id)
        self.assertTrue(deleted)
        self.assertIsNone(
            self.system.display_hotel_information(hotel.hotel_id)
        )

    def test_customer_crud_flow(self) -> None:
        """Ejercita CRUD completo de cliente."""
        customer = self.system.create_customer(
            full_name="Ana Pérez",
            email="ana@example.com",
            phone="8111111111",
        )
        assert customer is not None

        shown = self.system.display_customer_information(customer.customer_id)
        self.assertIsNotNone(shown)

        changed = self.system.modify_customer_information(
            customer.customer_id,
            email="ana.perez@example.com",
            phone="8222222222",
        )
        self.assertTrue(changed)

        shown_after = self.system.display_customer_information(
            customer.customer_id
        )
        assert shown_after is not None
        self.assertEqual(shown_after["email"], "ana.perez@example.com")

        deleted = self.system.delete_customer(customer.customer_id)
        self.assertTrue(deleted)

    def test_create_and_cancel_reserve(self) -> None:
        """Crea y cancela una reservación restaurando disponibilidad."""
        hotel = self.system.create_hotel(
            name="Hotel Plaza",
            location="CDMX",
            total_rooms=10,
        )
        customer = self.system.create_customer(
            full_name="Carlos Ruiz",
            email="carlos@example.com",
            phone="8333333333",
        )
        assert hotel is not None
        assert customer is not None

        reservation = self.system.create_reservation(
            customer.customer_id,
            hotel.hotel_id,
            room_count=3,
        )
        self.assertIsNotNone(reservation)

        hotel_after_reserve = self.system.display_hotel_information(
            hotel.hotel_id
        )
        assert hotel_after_reserve is not None
        self.assertEqual(hotel_after_reserve["available_rooms"], 7)

        assert reservation is not None
        cancelled = self.system.cancel_reservation(reservation.reservation_id)
        self.assertTrue(cancelled)

        hotel_after_cancel = self.system.display_hotel_information(
            hotel.hotel_id
        )
        assert hotel_after_cancel is not None
        self.assertEqual(hotel_after_cancel["available_rooms"], 10)

    def test_reserve_room_wrapper(self) -> None:
        """La API reserve_room usa la creación de reservación."""
        hotel = self.system.create_hotel(
            name="Hotel Lago",
            location="Querétaro",
            total_rooms=4,
        )
        customer = self.system.create_customer(
            full_name="José León",
            email="jose@example.com",
            phone="8444444444",
        )
        assert hotel is not None
        assert customer is not None

        reservation = self.system.reserve_room(
            hotel.hotel_id,
            customer.customer_id,
            room_count=2,
        )
        self.assertIsNotNone(reservation)

    def test_prevent_hotel_delete(self) -> None:
        """Impide borrar hotel cuando existen reservaciones activas."""
        hotel = self.system.create_hotel(
            name="Hotel Activo",
            location="León",
            total_rooms=6,
        )
        customer = self.system.create_customer(
            full_name="Marta Díaz",
            email="marta@example.com",
            phone="8555555555",
        )
        assert hotel is not None
        assert customer is not None

        self.system.create_reservation(customer.customer_id, hotel.hotel_id, 1)
        deleted = self.system.delete_hotel(hotel.hotel_id)
        self.assertFalse(deleted)

    def test_prevent_customer_delete(self) -> None:
        """Impide borrar cliente cuando existen reservaciones activas."""
        hotel = self.system.create_hotel(
            name="Hotel Cliente",
            location="Toluca",
            total_rooms=6,
        )
        customer = self.system.create_customer(
            full_name="Laura Díaz",
            email="laura@example.com",
            phone="8666666666",
        )
        assert hotel is not None
        assert customer is not None

        self.system.create_reservation(customer.customer_id, hotel.hotel_id, 1)
        deleted = self.system.delete_customer(customer.customer_id)
        self.assertFalse(deleted)

    def test_invalid_file_lines_ignored(self) -> None:
        """Reporta líneas inválidas y sigue procesando otras válidas."""
        bad_file = self.data_dir / "hotels.jsonl"
        bad_file.write_text(
            "{\"hotel_id\":\"ok\",\"name\":\"Uno\",\"location\":\"X\","
            "\"total_rooms\":2,\"available_rooms\":2,\"amenities\":[]}\n"
            "{invalido}\n"
            "123\n",
            encoding="utf-8",
        )

        output = io.StringIO()
        with redirect_stdout(output):
            rows = load_jsonl(bad_file, "hoteles")

        self.assertEqual(len(rows), 1)
        self.assertIn("ERROR:", output.getvalue())

    def test_invalid_entities_skipped(self) -> None:
        """Ignora entidades inválidas al cargar modelos desde archivo."""
        self.system.hotels_file.write_text(
            "{\"hotel_id\":\"h1\",\"name\":\"Bueno\",\"location\":\"Y\","
            "\"total_rooms\":3,\"available_rooms\":3,\"amenities\":[]}\n"
            "{\"hotel_id\":\"h2\",\"name\":\"Malo\",\"location\":\"Y\","
            "\"total_rooms\":1,\"available_rooms\":4,\"amenities\":[]}\n",
            encoding="utf-8",
        )

        hotels = self.system._load_hotels()  # pylint: disable=protected-access
        self.assertEqual(len(hotels), 1)

    def test_cancel_reservation_errors(self) -> None:
        """Valida errores de cancelación no existente y doble cancelación."""
        not_found = self.system.cancel_reservation("RES-noexiste")
        self.assertFalse(not_found)

        hotel = self.system.create_hotel(
            name="Hotel Doble",
            location="Mérida",
            total_rooms=2,
        )
        customer = self.system.create_customer(
            full_name="Pablo Vega",
            email="pablo@example.com",
            phone="8777777777",
        )
        assert hotel is not None
        assert customer is not None

        reservation = self.system.create_reservation(
            customer.customer_id,
            hotel.hotel_id,
            1,
        )
        assert reservation is not None

        first_cancel = self.system.cancel_reservation(
            reservation.reservation_id
        )
        second_cancel = self.system.cancel_reservation(
            reservation.reservation_id
        )
        self.assertTrue(first_cancel)
        self.assertFalse(second_cancel)

    def test_invalid_customer_fails(self) -> None:
        """No crea cliente cuando el correo es inválido."""
        customer = self.system.create_customer(
            full_name="Nombre Sin Correo",
            email="correo_invalido",
            phone="8888888888",
        )
        self.assertIsNone(customer)

    def test_display_reservation_info(self) -> None:
        """Recupera una reservación por su identificador."""
        hotel = self.system.create_hotel(
            name="Hotel Busqueda",
            location="Monterrey",
            total_rooms=9,
        )
        customer = self.system.create_customer(
            full_name="Sofia Lopez",
            email="sofia@example.com",
            phone="8999999999",
        )
        assert hotel is not None
        assert customer is not None

        reservation = self.system.create_reservation(
            customer.customer_id,
            hotel.hotel_id,
            2,
        )
        assert reservation is not None

        payload = self.system.display_reservation_information(
            reservation.reservation_id
        )
        self.assertIsNotNone(payload)
        assert payload is not None
        self.assertEqual(payload["reservation_id"], reservation.reservation_id)
        self.assertEqual(payload["customer_name"], "Sofia Lopez")

    def test_search_reserve_name(self) -> None:
        """Busca reservaciones por coincidencia de nombre de cliente."""
        hotel = self.system.create_hotel(
            name="Hotel Nombre",
            location="Guadalajara",
            total_rooms=12,
        )
        customer = self.system.create_customer(
            full_name="Roberto Martinez",
            email="roberto@example.com",
            phone="8000000000",
        )
        assert hotel is not None
        assert customer is not None

        reservation = self.system.create_reservation(
            customer.customer_id,
            hotel.hotel_id,
            1,
        )
        assert reservation is not None

        matches = self.system.search_reservations_by_name("roberto")
        self.assertEqual(len(matches), 1)
        self.assertEqual(
            matches[0]["reservation_id"],
            reservation.reservation_id,
        )
        self.assertEqual(matches[0]["customer_name"], "Roberto Martinez")


if __name__ == "__main__":
    unittest.main()
