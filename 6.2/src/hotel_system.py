"""Servicios principales para gestionar hoteles, clientes y reservaciones."""

from __future__ import annotations

import uuid
from pathlib import Path

from .models import Customer
from .models import Hotel
from .models import Reservation
from .storage import load_jsonl
from .storage import save_jsonl


class HotelSystem:
    """Sistema de gestión con persistencia en archivos JSONL."""

    def __init__(self, data_dir: Path | None = None) -> None:
        """Inicializa rutas de persistencia para entidades del sistema."""
        if data_dir is None:
            data_dir = Path(__file__).resolve().parents[1] / "input"
        self.data_dir = data_dir
        self.hotels_file = data_dir / "hotels.jsonl"
        self.customers_file = data_dir / "customers.jsonl"
        self.reservations_file = data_dir / "reservations.jsonl"

    def _generate_id(self, prefix: str) -> str:
        """Genera un identificador corto para las entidades."""
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def _load_hotels(self) -> list[Hotel]:
        """Carga y valida hoteles almacenados."""
        hotels: list[Hotel] = []
        for payload in load_jsonl(self.hotels_file, "hoteles"):
            hotel = Hotel.from_dict(payload)
            if hotel is not None:
                hotels.append(hotel)
        return hotels

    def _load_customers(self) -> list[Customer]:
        """Carga y valida clientes almacenados."""
        customers: list[Customer] = []
        for payload in load_jsonl(self.customers_file, "clientes"):
            customer = Customer.from_dict(payload)
            if customer is not None:
                customers.append(customer)
        return customers

    def _load_reservations(self) -> list[Reservation]:
        """Carga y valida reservaciones almacenadas."""
        reservations: list[Reservation] = []
        for payload in load_jsonl(self.reservations_file, "reservaciones"):
            reservation = Reservation.from_dict(payload)
            if reservation is not None:
                reservations.append(reservation)
        return reservations

    def _save_hotels(self, hotels: list[Hotel]) -> None:
        """Persiste lista de hoteles."""
        save_jsonl(self.hotels_file, [hotel.to_dict() for hotel in hotels])

    def _save_customers(self, customers: list[Customer]) -> None:
        """Persiste lista de clientes."""
        save_jsonl(
            self.customers_file,
            [customer.to_dict() for customer in customers],
        )

    def _save_reservations(self, reservations: list[Reservation]) -> None:
        """Persiste lista de reservaciones."""
        save_jsonl(
            self.reservations_file,
            [reservation.to_dict() for reservation in reservations],
        )

    def create_hotel(
        self,
        name: str,
        location: str,
        total_rooms: int,
        amenities: list[str] | None = None,
    ) -> Hotel | None:
        """Crea un hotel nuevo y lo persiste."""
        hotel = Hotel(
            hotel_id=self._generate_id("HOT"),
            name=name,
            location=location,
            total_rooms=total_rooms,
            available_rooms=total_rooms,
            amenities=amenities or [],
        )
        validated = Hotel.from_dict(hotel.to_dict())
        if validated is None:
            return None

        hotels = self._load_hotels()
        hotels.append(validated)
        self._save_hotels(hotels)
        return validated

    def delete_hotel(self, hotel_id: str) -> bool:
        """Elimina un hotel si no tiene reservaciones activas."""
        reservations = self._load_reservations()
        for reservation in reservations:
            if (
                reservation.hotel_id == hotel_id
                and reservation.status == "active"
            ):
                print(
                    "ERROR: no se puede eliminar hotel con "
                    "reservaciones activas"
                )
                return False

        hotels = self._load_hotels()
        remaining = [hotel for hotel in hotels if hotel.hotel_id != hotel_id]
        if len(remaining) == len(hotels):
            print(f"ERROR: hotel no encontrado: {hotel_id}")
            return False

        self._save_hotels(remaining)
        return True

    def display_hotel_information(
        self,
        hotel_id: str,
    ) -> dict[str, object] | None:
        """Devuelve información de un hotel por identificador."""
        for hotel in self._load_hotels():
            if hotel.hotel_id == hotel_id:
                return hotel.to_dict()
        print(f"ERROR: hotel no encontrado: {hotel_id}")
        return None

    def modify_hotel_information(
        self,
        hotel_id: str,
        **changes: object,
    ) -> bool:
        """Actualiza datos de un hotel existente."""
        hotels = self._load_hotels()
        for hotel in hotels:
            if hotel.hotel_id != hotel_id:
                continue

            if "name" in changes:
                hotel.name = str(changes["name"])
            if "location" in changes:
                hotel.location = str(changes["location"])
            if "amenities" in changes:
                hotel.amenities = list(changes["amenities"])
            if "total_rooms" in changes:
                hotel.total_rooms = int(changes["total_rooms"])
            if "available_rooms" in changes:
                hotel.available_rooms = int(changes["available_rooms"])

            validated = Hotel.from_dict(hotel.to_dict())
            if validated is None:
                return False

            self._save_hotels(hotels)
            return True

        print(f"ERROR: hotel no encontrado: {hotel_id}")
        return False

    def create_customer(
        self,
        full_name: str,
        email: str,
        phone: str,
    ) -> Customer | None:
        """Crea un cliente nuevo y lo persiste."""
        customer = Customer(
            customer_id=self._generate_id("CUS"),
            full_name=full_name,
            email=email,
            phone=phone,
        )
        validated = Customer.from_dict(customer.to_dict())
        if validated is None:
            return None

        customers = self._load_customers()
        customers.append(validated)
        self._save_customers(customers)
        return validated

    def delete_customer(self, customer_id: str) -> bool:
        """Elimina un cliente si no tiene reservaciones activas."""
        reservations = self._load_reservations()
        for reservation in reservations:
            if (
                reservation.customer_id == customer_id
                and reservation.status == "active"
            ):
                print(
                    "ERROR: no se puede eliminar cliente con "
                    "reservaciones activas"
                )
                return False

        customers = self._load_customers()
        remaining = [
            customer
            for customer in customers
            if customer.customer_id != customer_id
        ]
        if len(remaining) == len(customers):
            print(f"ERROR: cliente no encontrado: {customer_id}")
            return False

        self._save_customers(remaining)
        return True

    def display_customer_information(
        self,
        customer_id: str,
    ) -> dict[str, str] | None:
        """Devuelve información de un cliente por identificador."""
        for customer in self._load_customers():
            if customer.customer_id == customer_id:
                return customer.to_dict()
        print(f"ERROR: cliente no encontrado: {customer_id}")
        return None

    def modify_customer_information(
        self,
        customer_id: str,
        **changes: object,
    ) -> bool:
        """Actualiza datos de un cliente existente."""
        customers = self._load_customers()
        for customer in customers:
            if customer.customer_id != customer_id:
                continue

            if "full_name" in changes:
                customer.full_name = str(changes["full_name"])
            if "email" in changes:
                customer.email = str(changes["email"])
            if "phone" in changes:
                customer.phone = str(changes["phone"])

            validated = Customer.from_dict(customer.to_dict())
            if validated is None:
                return False

            self._save_customers(customers)
            return True

        print(f"ERROR: cliente no encontrado: {customer_id}")
        return False

    def reserve_room(
        self,
        hotel_id: str,
        customer_id: str,
        room_count: int = 1,
    ) -> Reservation | None:
        """Reserva cuartos para un cliente en un hotel."""
        return self.create_reservation(customer_id, hotel_id, room_count)

    def create_reservation(
        self,
        customer_id: str,
        hotel_id: str,
        room_count: int = 1,
    ) -> Reservation | None:
        """Crea una reservación validando existencia y disponibilidad."""
        if room_count <= 0:
            print("ERROR: la cantidad de cuartos debe ser mayor a cero")
            return None

        customers = self._load_customers()
        hotels = self._load_hotels()
        reservations = self._load_reservations()

        customer = next(
            (
                current
                for current in customers
                if current.customer_id == customer_id
            ),
            None,
        )
        if customer is None:
            print(f"ERROR: cliente no encontrado: {customer_id}")
            return None

        hotel = next(
            (current for current in hotels if current.hotel_id == hotel_id),
            None,
        )
        if hotel is None:
            print(f"ERROR: hotel no encontrado: {hotel_id}")
            return None

        if hotel.available_rooms < room_count:
            print(
                "ERROR: no hay disponibilidad suficiente para "
                f"el hotel {hotel_id}"
            )
            return None

        hotel.available_rooms -= room_count
        reservation = Reservation(
            reservation_id=self._generate_id("RES"),
            customer_id=customer_id,
            hotel_id=hotel_id,
            room_count=room_count,
            status="active",
        )

        validated = Reservation.from_dict(reservation.to_dict())
        if validated is None:
            return None

        reservations.append(validated)
        self._save_hotels(hotels)
        self._save_reservations(reservations)
        return validated

    def cancel_reservation(self, reservation_id: str) -> bool:
        """Cancela una reservación activa y libera disponibilidad."""
        hotels = self._load_hotels()
        reservations = self._load_reservations()

        target: Reservation | None = None
        for reservation in reservations:
            if reservation.reservation_id == reservation_id:
                target = reservation
                break

        if target is None:
            print(f"ERROR: reservación no encontrada: {reservation_id}")
            return False

        if target.status == "cancelled":
            print("ERROR: la reservación ya estaba cancelada")
            return False

        hotel = next(
            (
                current
                for current in hotels
                if current.hotel_id == target.hotel_id
            ),
            None,
        )
        if hotel is None:
            print(
                "ERROR: hotel asociado no encontrado para "
                f"la reservación {reservation_id}"
            )
            return False

        target.status = "cancelled"
        hotel.available_rooms += target.room_count
        hotel.available_rooms = min(
            hotel.available_rooms,
            hotel.total_rooms,
        )

        self._save_hotels(hotels)
        self._save_reservations(reservations)
        return True

    def display_reservation_information(
        self,
        reservation_id: str,
    ) -> dict[str, object] | None:
        """Devuelve información de una reservación por identificador."""
        customers = self._load_customers()
        customer_lookup = {
            customer.customer_id: customer.full_name
            for customer in customers
        }

        for reservation in self._load_reservations():
            if reservation.reservation_id == reservation_id:
                payload = reservation.to_dict()
                payload["customer_name"] = customer_lookup.get(
                    reservation.customer_id,
                    "Cliente no encontrado",
                )
                return payload
        print(f"ERROR: reservación no encontrada: {reservation_id}")
        return None

    def search_reservations_by_name(
        self,
        customer_name: str,
    ) -> list[dict[str, object]]:
        """Busca reservaciones por nombre de cliente."""
        normalized_name = customer_name.strip().lower()
        if not normalized_name:
            print("ERROR: el nombre de cliente no puede estar vacío")
            return []

        customers = self._load_customers()
        matching_customer_ids = {
            customer.customer_id: customer.full_name
            for customer in customers
            if normalized_name in customer.full_name.strip().lower()
        }
        if not matching_customer_ids:
            print(f"ERROR: cliente no encontrado por nombre: {customer_name}")
            return []

        results: list[dict[str, object]] = []
        for reservation in self._load_reservations():
            if reservation.customer_id not in matching_customer_ids:
                continue
            payload = reservation.to_dict()
            payload["customer_name"] = matching_customer_ids[
                reservation.customer_id
            ]
            results.append(payload)

        if not results:
            print("ERROR: no hay reservaciones para cliente(s) que coincidan")
            print(f"con '{customer_name}'")
        return results
