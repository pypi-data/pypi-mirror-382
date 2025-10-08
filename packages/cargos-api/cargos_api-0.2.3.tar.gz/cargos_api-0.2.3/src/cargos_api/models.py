from __future__ import annotations
from typing import Optional


class Address:
    """Postal address with an optional Ca.R.G.O.S. 'luogo' code (Comune/State)."""

    def __init__(self, location_code: Optional[int] = None, street: Optional[str] = None):
        self.location_code = location_code
        self.street = street


class Car:
    """Vehicle details according to Ca.R.G.O.S. 'Tracciato Record'."""

    def __init__(
        self,
        type_code: str,        # 1 char (Tabella Tipo Veicolo)
        brand: str,
        model: str,
        plate: str,
        color: Optional[str] = None,
        has_gps: Optional[bool] = None,
        has_immobilizer: Optional[bool] = None,
    ):
        self.type_code = type_code
        self.brand = brand
        self.model = model
        self.plate = plate
        self.color = color
        self.has_gps = has_gps
        self.has_immobilizer = has_immobilizer


class Customer:
    """Primary driver / contraente."""

    def __init__(
        self,
        surname: str,
        name: str,
        birth_date: str,                         # mapper -> dd/mm/YYYY
        birth_place_code: int,                   # 9 digits
        citizenship_code: int,                   # 9 digits
        residence: Optional[Address] = None,     # paired: both code & street or none
        id_doc_type_code: str = "",              # 5 chars (Tabella Documenti Polizia)
        id_doc_number: str = "",                 # length > 4
        id_doc_issuing_place_code: int = 0,      # 9 digits
        driver_licence_number: str = "",         # length > 4
        driver_licence_issuing_place_code: int = 0,  # 9 digits
        contact: Optional[str] = None,           # phone/email
    ):
        self.surname = surname
        self.name = name
        self.birth_date = birth_date
        self.birth_place_code = birth_place_code
        self.citizenship_code = citizenship_code
        self.residence = residence
        self.id_doc_type_code = id_doc_type_code
        self.id_doc_number = id_doc_number
        self.id_doc_issuing_place_code = id_doc_issuing_place_code
        self.driver_licence_number = driver_licence_number
        self.driver_licence_issuing_place_code = driver_licence_issuing_place_code
        self.contact = contact


class SecondDriver:
    """Second driver. If present, ALL fields become mandatory by spec."""

    def __init__(
        self,
        surname: str,
        name: str,
        birth_date: str,
        birth_place_code: int,
        citizenship_code: int,
        id_doc_type_code: str,
        id_doc_number: str,
        id_doc_issuing_place_code: int,
        driver_licence_number: str,
        driver_licence_issuing_place_code: int,
        contact: Optional[str] = None,
    ):
        self.surname = surname
        self.name = name
        self.birth_date = birth_date
        self.birth_place_code = birth_place_code
        self.citizenship_code = citizenship_code
        self.id_doc_type_code = id_doc_type_code
        self.id_doc_number = id_doc_number
        self.id_doc_issuing_place_code = id_doc_issuing_place_code
        self.driver_licence_number = driver_licence_number
        self.driver_licence_issuing_place_code = driver_licence_issuing_place_code
        self.contact = contact


class Operator:
    """Operator and agency info."""

    def __init__(
        self,
        id: str,
        agency_id: str,
        agency_name: str,
        agency_place_code: int,  # 9 digits
        agency_address: str,
        agency_phone: str,
    ):
        self.id = id
        self.agency_id = agency_id
        self.agency_name = agency_name
        self.agency_place_code = agency_place_code
        self.agency_address = agency_address
        self.agency_phone = agency_phone


class BookingData:
    """Complete booking entity mapped 1:1 to the Ca.R.G.O.S. fixed-width record."""

    def __init__(
        self,
        contract_id: str,
        contract_datetime: str,     # mapper -> dd/mm/YYYY HH:MM
        payment_type_code: str,     # 1 char (Tabella Tipo Pagamenti)
        checkout_datetime: str,
        checkout_place: Address,
        checkin_datetime: str,
        checkin_place: Address,
        operator: Operator,
        car: Car,
        customer: Customer,
        second_driver: Optional[SecondDriver] = None,
    ):
        self.contract_id = contract_id
        self.contract_datetime = contract_datetime
        self.payment_type_code = payment_type_code
        self.checkout_datetime = checkout_datetime
        self.checkout_place = checkout_place
        self.checkin_datetime = checkin_datetime
        self.checkin_place = checkin_place
        self.operator = operator
        self.car = car
        self.customer = customer
        self.second_driver = second_driver