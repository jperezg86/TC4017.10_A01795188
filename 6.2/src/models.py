"""Modelos de dominio para hoteles, clientes y reservaciones."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Hotel:
    """Representa un hotel con capacidad disponible para reservaciones."""

    hotel_id: str
    name: str
    location: str
    total_rooms: int
    available_rooms: int
    amenities: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        """Convierte la instancia a diccionario serializable."""
        return {
            "hotel_id": self.hotel_id,
            "name": self.name,
            "location": self.location,
            "total_rooms": self.total_rooms,
            "available_rooms": self.available_rooms,
            "amenities": self.amenities,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> Hotel | None:
        """Construye un hotel desde un diccionario validando sus datos."""
        try:
            hotel = cls(
                hotel_id=str(payload["hotel_id"]),
                name=str(payload["name"]),
                location=str(payload["location"]),
                total_rooms=int(payload["total_rooms"]),
                available_rooms=int(payload["available_rooms"]),
                amenities=list(payload.get("amenities", [])),
            )
        except (KeyError, TypeError, ValueError) as exc:
            print(f"ERROR: registro de hotel inválido: {exc}")
            return None

        if hotel.total_rooms < 0 or hotel.available_rooms < 0:
            print("ERROR: el hotel no puede tener cuartos negativos")
            return None
        if hotel.available_rooms > hotel.total_rooms:
            print(
                "ERROR: cuartos disponibles no puede ser mayor al total "
                f"en hotel {hotel.hotel_id}"
            )
            return None
        return hotel


@dataclass
class Customer:
    """Representa un cliente del sistema de hoteles."""

    customer_id: str
    full_name: str
    email: str
    phone: str

    def to_dict(self) -> dict[str, str]:
        """Convierte la instancia a diccionario serializable."""
        return {
            "customer_id": self.customer_id,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> Customer | None:
        """Construye un cliente desde un diccionario validando sus datos."""
        try:
            customer = cls(
                customer_id=str(payload["customer_id"]),
                full_name=str(payload["full_name"]),
                email=str(payload["email"]),
                phone=str(payload["phone"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            print(f"ERROR: registro de cliente inválido: {exc}")
            return None

        if "@" not in customer.email or not customer.full_name.strip():
            print(
                "ERROR: datos inválidos de cliente "
                f"{customer.customer_id}"
            )
            return None
        return customer


@dataclass
class Reservation:
    """Representa una reservación entre un cliente y un hotel."""

    reservation_id: str
    customer_id: str
    hotel_id: str
    room_count: int
    status: str = "active"

    def to_dict(self) -> dict[str, object]:
        """Convierte la instancia a diccionario serializable."""
        return {
            "reservation_id": self.reservation_id,
            "customer_id": self.customer_id,
            "hotel_id": self.hotel_id,
            "room_count": self.room_count,
            "status": self.status,
        }

    @classmethod
    def from_dict(
        cls,
        payload: dict[str, object],
    ) -> Reservation | None:
        """Construye una reservación desde un diccionario."""
        try:
            reservation = cls(
                reservation_id=str(payload["reservation_id"]),
                customer_id=str(payload["customer_id"]),
                hotel_id=str(payload["hotel_id"]),
                room_count=int(payload["room_count"]),
                status=str(payload.get("status", "active")),
            )
        except (KeyError, TypeError, ValueError) as exc:
            print(f"ERROR: registro de reservación inválido: {exc}")
            return None

        if reservation.room_count <= 0:
            print(
                "ERROR: cantidad de cuartos inválida en reservación "
                f"{reservation.reservation_id}"
            )
            return None
        if reservation.status not in {"active", "cancelled"}:
            print(
                "ERROR: estatus inválido en reservación "
                f"{reservation.reservation_id}"
            )
            return None
        return reservation
