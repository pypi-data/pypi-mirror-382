from __future__ import annotations
from datetime import datetime
from typing import Optional, Iterable, List, Dict, Tuple, Union
from .models import BookingData


class CargosRecordError(ValueError):
    """Raised for mapping/validation errors against the Ca.R.G.O.S. spec."""


class FixedWidthField:
    """A field in the Ca.R.G.O.S. fixed-width record, inclusive [start, end]."""

    def __init__(self, start: int, end: int, name: str, align: str = "left"):
        self.start = start
        self.end = end
        self.name = name
        self.align = align

    @property
    def length(self) -> int:
        return self.end - self.start + 1

    def pad(self, value: Optional[str]) -> str:
        s = "" if value is None else str(value)
        if len(s) > self.length:
            s = s[: self.length]
        padlen = self.length - len(s)
        if self.align == "right":
            return (" " * padlen) + s
        return s + (" " * padlen)


class DateFormatter:
    """Date/time canonicalizers for Ca.R.G.O.S. format."""

    @staticmethod
    def to_dt_hm(s: str) -> str:
        """Return 'dd/mm/YYYY HH:MM' from ISO-like input (tolerates 'Z')."""
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y %H:%M")

    @staticmethod
    def to_d(s: str) -> str:
        """Return 'dd/mm/YYYY' from ISO-like input (tolerates 'Z')."""
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y")


class CargosRecordMapper:
    """
    Build Ca.R.G.O.S. 'Tracciato Record' strings (exactly 1505 chars) with full validation.

    Guarantees:
      - Field positions & lengths exactly as per spec.
      - Required/optional logic respected (residence pairing, second driver all-or-nothing).
      - Date formats: 'dd/mm/YYYY HH:MM' and 'dd/mm/YYYY'.
      - Right alignment for numeric codes where appropriate.

    Methods:
      - build_record(booking) -> str
      - build_batch(bookings) -> List[str]   (also enforces <= 100 records per block)
    """

    # Field map (inclusive ranges)
    F = {
        # Contract
        "CONTRATTO_ID": FixedWidthField(1, 50, "CONTRATTO_ID"),
        "CONTRATTO_DATA": FixedWidthField(51, 66, "CONTRATTO_DATA"),
        "CONTRATTO_TIPOP": FixedWidthField(67, 67, "CONTRATTO_TIPOP"),
        "CONTRATTO_CHECKOUT_DATA": FixedWidthField(68, 83, "CONTRATTO_CHECKOUT_DATA"),
        "CONTRATTO_CHECKOUT_LUOGO_COD": FixedWidthField(84, 92, "CONTRATTO_CHECKOUT_LUOGO_COD", align="right"),
        "CONTRATTO_CHECKOUT_INDIRIZZO": FixedWidthField(93, 242, "CONTRATTO_CHECKOUT_INDIRIZZO"),
        "CONTRATTO_CHECKIN_DATA": FixedWidthField(243, 258, "CONTRATTO_CHECKIN_DATA"),
        "CONTRATTO_CHECKIN_LUOGO_COD": FixedWidthField(259, 267, "CONTRATTO_CHECKIN_LUOGO_COD", align="right"),
        "CONTRATTO_CHECKIN_INDIRIZZO": FixedWidthField(268, 417, "CONTRATTO_CHECKIN_INDIRIZZO"),
        # Operator/Agency
        "OPERATORE_ID": FixedWidthField(418, 467, "OPERATORE_ID"),
        "AGENZIA_ID": FixedWidthField(468, 497, "AGENZIA_ID"),
        "AGENZIA_NOME": FixedWidthField(498, 567, "AGENZIA_NOME"),
        "AGENZIA_LUOGO_COD": FixedWidthField(568, 576, "AGENZIA_LUOGO_COD", align="right"),
        "AGENZIA_INDIRIZZO": FixedWidthField(577, 726, "AGENZIA_INDIRIZZO"),
        "AGENZIA_RECAPITO_TEL": FixedWidthField(727, 746, "AGENZIA_RECAPITO_TEL"),
        # Vehicle
        "VEICOLO_TIPO": FixedWidthField(747, 747, "VEICOLO_TIPO"),
        "VEICOLO_MARCA": FixedWidthField(748, 797, "VEICOLO_MARCA"),
        "VEICOLO_MODELLO": FixedWidthField(798, 897, "VEICOLO_MODELLO"),
        "VEICOLO_TARGA": FixedWidthField(898, 912, "VEICOLO_TARGA"),
        "VEICOLO_COLORE": FixedWidthField(913, 962, "VEICOLO_COLORE"),
        "VEICOLO_GPS": FixedWidthField(963, 963, "VEICOLO_GPS"),
        "VEICOLO_BLOCCOM": FixedWidthField(964, 964, "VEICOLO_BLOCCOM"),
        # Customer (contraente/conducente 1)
        "C1_COGNOME": FixedWidthField(965, 1014, "CONDUCENTE_CONTRAENTE_COGNOME"),
        "C1_NOME": FixedWidthField(1015, 1044, "CONDUCENTE_CONTRAENTE_NOME"),
        "C1_NASCITA_DATA": FixedWidthField(1045, 1054, "CONDUCENTE_CONTRAENTE_NASCITA_DATA"),
        "C1_NASCITA_LUOGO_COD": FixedWidthField(1055, 1063, "CONDUCENTE_CONTRAENTE_NASCITA_LUOGO_COD", align="right"),
        "C1_CITTADINANZA_COD": FixedWidthField(1064, 1072, "CONDUCENTE_CONTRAENTE_CITTADINANZA_COD", align="right"),
        "C1_RESIDENZA_LUOGO_COD": FixedWidthField(1073, 1081, "CONDUCENTE_CONTRAENTE_RESIDENZA_LUOGO_COD", align="right"),
        "C1_RESIDENZA_INDIRIZZO": FixedWidthField(1082, 1231, "CONDUCENTE_CONTRAENTE_RESIDENZA_INDIRIZZO"),
        "C1_DOCIDE_TIPO_COD": FixedWidthField(1232, 1236, "CONDUCENTE_CONTRAENTE_DOCIDE_TIPO_COD"),
        "C1_DOCIDE_NUMERO": FixedWidthField(1237, 1256, "CONDUCENTE_CONTRAENTE_DOCIDE_NUMERO"),
        "C1_DOCIDE_LUOGORIL_COD": FixedWidthField(1257, 1265, "CONDUCENTE_CONTRAENTE_DOCIDE_LUOGORIL_COD", align="right"),
        "C1_PATENTE_NUMERO": FixedWidthField(1266, 1285, "CONDUCENTE_CONTRAENTE_PATENTE_NUMERO"),
        "C1_PATENTE_LUOGORIL_COD": FixedWidthField(1286, 1294, "CONDUCENTE_CONTRAENTE_PATENTE_LUOGORIL_COD", align="right"),
        "C1_RECAPITO": FixedWidthField(1295, 1314, "CONDUCENTE_CONTRAENTE_RECAPITO"),
        # Second driver (all mandatory if present)
        "C2_COGNOME": FixedWidthField(1315, 1364, "CONDUCENTE2_COGNOME"),
        "C2_NOME": FixedWidthField(1365, 1394, "CONDUCENTE2_NOME"),
        "C2_NASCITA_DATA": FixedWidthField(1395, 1404, "CONDUCENTE2_NASCITA_DATA"),
        "C2_NASCITA_LUOGO_COD": FixedWidthField(1405, 1413, "CONDUCENTE2_NASCITA_LUOGO_COD", align="right"),
        "C2_CITTADINANZA_COD": FixedWidthField(1414, 1422, "CONDUCENTE2_CITTADINANZA_COD", align="right"),
        "C2_DOCIDE_TIPO_COD": FixedWidthField(1423, 1427, "CONDUCENTE2_DOCIDE_TIPO_COD"),
        "C2_DOCIDE_NUMERO": FixedWidthField(1428, 1447, "CONDUCENTE2_DOCIDE_NUMERO"),
        "C2_DOCIDE_LUOGORIL_COD": FixedWidthField(1448, 1456, "CONDUCENTE2_DOCIDE_LUOGORIL_COD", align="right"),
        "C2_PATENTE_NUMERO": FixedWidthField(1457, 1476, "CONDUCENTE2_PATENTE_NUMERO"),
        "C2_PATENTE_LUOGORIL_COD": FixedWidthField(1477, 1485, "CONDUCENTE2_PATENTE_LUOGORIL_COD", align="right"),
        "C2_RECAPITO": FixedWidthField(1486, 1505, "CONDUCENTE2_RECAPITO"),
    }

    RECORD_LENGTH = 1505

    # ---------- Public API ----------

    def build_record(self, b: BookingData, *, with_map: bool = False, collect_errors: bool = False) -> Union[str, Tuple[str, Dict[str, str]], Tuple[str, List[str]], Tuple[str, Dict[str, str], List[str]]]:
        """Return a single fixed-width record (length 1505).

        Parameters
        ----------
        b : BookingData
            Input booking payload.
        with_map : bool, optional
            When True, also return a mapping of field names to their exact padded slices.
        collect_errors : bool, optional
            When True, do not raise validation exceptions; instead collect them and return
            alongside the record (and mapping if requested).
        """
        p = []  # parts
        errors: List[str] = []

        # Contract
        p.append(self.F["CONTRATTO_ID"].pad(b.contract_id))
        p.append(self.F["CONTRATTO_DATA"].pad(DateFormatter.to_dt_hm(b.contract_datetime)))
        p.append(self.F["CONTRATTO_TIPOP"].pad(b.payment_type_code))
        p.append(self.F["CONTRATTO_CHECKOUT_DATA"].pad(DateFormatter.to_dt_hm(b.checkout_datetime)))
        p.append(self.F["CONTRATTO_CHECKOUT_LUOGO_COD"].pad(self._num(b.checkout_place.location_code)))
        p.append(self.F["CONTRATTO_CHECKOUT_INDIRIZZO"].pad(b.checkout_place.street))
        p.append(self.F["CONTRATTO_CHECKIN_DATA"].pad(DateFormatter.to_dt_hm(b.checkin_datetime)))
        p.append(self.F["CONTRATTO_CHECKIN_LUOGO_COD"].pad(self._num(b.checkin_place.location_code)))
        p.append(self.F["CONTRATTO_CHECKIN_INDIRIZZO"].pad(b.checkin_place.street))

        # Operator / Agency
        p.append(self.F["OPERATORE_ID"].pad(b.operator.id))
        p.append(self.F["AGENZIA_ID"].pad(b.operator.agency_id))
        p.append(self.F["AGENZIA_NOME"].pad(b.operator.agency_name))
        p.append(self.F["AGENZIA_LUOGO_COD"].pad(self._num(b.operator.agency_place_code)))
        p.append(self.F["AGENZIA_INDIRIZZO"].pad(b.operator.agency_address))
        p.append(self.F["AGENZIA_RECAPITO_TEL"].pad(b.operator.agency_phone))

        # Vehicle
        p.append(self.F["VEICOLO_TIPO"].pad(b.car.type_code))
        p.append(self.F["VEICOLO_MARCA"].pad(b.car.brand))
        p.append(self.F["VEICOLO_MODELLO"].pad(b.car.model))
        p.append(self.F["VEICOLO_TARGA"].pad(b.car.plate))
        p.append(self.F["VEICOLO_COLORE"].pad(b.car.color))
        p.append(self.F["VEICOLO_GPS"].pad(self._flag(b.car.has_gps)))
        p.append(self.F["VEICOLO_BLOCCOM"].pad(self._flag(b.car.has_immobilizer)))

        # Customer
        c = b.customer
        p.append(self.F["C1_COGNOME"].pad(c.surname))
        p.append(self.F["C1_NOME"].pad(c.name))
        p.append(self.F["C1_NASCITA_DATA"].pad(DateFormatter.to_d(c.birth_date)))
        p.append(self.F["C1_NASCITA_LUOGO_COD"].pad(self._num(c.birth_place_code)))
        p.append(self.F["C1_CITTADINANZA_COD"].pad(self._num(c.citizenship_code)))

        # Residence pairing rule
        res_loc = c.residence.location_code if c.residence else None
        res_addr = c.residence.street if c.residence else None
        if bool(res_loc) ^ bool(res_addr):
            msg = "Residence fields must be provided together (code + street)."
            if collect_errors:
                errors.append(msg)
                res_loc, res_addr = None, None  # neutralize inconsistent pair
            else:
                raise CargosRecordError(msg)
        p.append(self.F["C1_RESIDENZA_LUOGO_COD"].pad(self._num(res_loc)))
        p.append(self.F["C1_RESIDENZA_INDIRIZZO"].pad(res_addr))

        # Identity / License
        p.append(self.F["C1_DOCIDE_TIPO_COD"].pad(c.id_doc_type_code))
        p.append(self.F["C1_DOCIDE_NUMERO"].pad(c.id_doc_number))
        p.append(self.F["C1_DOCIDE_LUOGORIL_COD"].pad(self._num(c.id_doc_issuing_place_code)))
        p.append(self.F["C1_PATENTE_NUMERO"].pad(c.driver_licence_number))
        p.append(self.F["C1_PATENTE_LUOGORIL_COD"].pad(self._num(c.driver_licence_issuing_place_code)))
        p.append(self.F["C1_RECAPITO"].pad(c.contact))

        # Second driver block (all mandatory if present)
        if b.second_driver:
            sd = b.second_driver
            required = [
                sd.surname, sd.name, sd.birth_date, sd.birth_place_code, sd.citizenship_code,
                sd.id_doc_type_code, sd.id_doc_number, sd.id_doc_issuing_place_code,
                sd.driver_licence_number, sd.driver_licence_issuing_place_code,
            ]
            invalid_second = any(x in (None, "", 0) for x in required)
            if invalid_second:
                msg = "All CONDUCENTE2_* fields are mandatory when a second driver is present."
                if collect_errors:
                    errors.append(msg)
                    # Pad the whole second-driver segment with spaces instead of partial data
                    p.append(" " * (self.RECORD_LENGTH - 1315 + 1))
                else:
                    raise CargosRecordError(msg)
            else:
                p.append(self.F["C2_COGNOME"].pad(sd.surname))
                p.append(self.F["C2_NOME"].pad(sd.name))
                p.append(self.F["C2_NASCITA_DATA"].pad(DateFormatter.to_d(sd.birth_date)))
                p.append(self.F["C2_NASCITA_LUOGO_COD"].pad(self._num(sd.birth_place_code)))
                p.append(self.F["C2_CITTADINANZA_COD"].pad(self._num(sd.citizenship_code)))
                p.append(self.F["C2_DOCIDE_TIPO_COD"].pad(sd.id_doc_type_code))
                p.append(self.F["C2_DOCIDE_NUMERO"].pad(sd.id_doc_number))
                p.append(self.F["C2_DOCIDE_LUOGORIL_COD"].pad(self._num(sd.id_doc_issuing_place_code)))
                p.append(self.F["C2_PATENTE_NUMERO"].pad(sd.driver_licence_number))
                p.append(self.F["C2_PATENTE_LUOGORIL_COD"].pad(self._num(sd.driver_licence_issuing_place_code)))
                p.append(self.F["C2_RECAPITO"].pad(sd.contact))
        else:
            # Fill the remainder (1315–1505) with spaces
            p.append(" " * (self.RECORD_LENGTH - 1315 + 1))

        record = "".join(p)

        if len(record) != self.RECORD_LENGTH:
            msg = f"Record must be {self.RECORD_LENGTH} chars, got {len(record)}"
            if collect_errors:
                errors.append(msg)
            else:
                raise CargosRecordError(msg)

        try:
            self._validate_required_minima(b)
        except CargosRecordError as e:
            if collect_errors:
                errors.append(str(e))
            else:
                raise

        if with_map:
            mapping: Dict[str, str] = {
                k: record[f.start - 1 : f.end]
                for k, f in self.F.items()
            }
            if collect_errors:
                return record, mapping, errors
            return record, mapping

        if collect_errors:
            return record, errors
        return record

    def build_batch(self, bookings: Iterable[BookingData]) -> List[str]:
        """
        Build multiple records and enforce the max block size (<= 100 contracts).
        """
        records = [self.build_record(b) for b in bookings]
        if len(records) > 100:
            raise CargosRecordError("Each block must not contain more than 100 contracts.")
        return records

    # ---------- internals ----------

    @staticmethod
    def _num(n: Optional[int]) -> Optional[str]:
        if n is None:
            return None
        return str(int(n))  # right-aligned by field.pad

    @staticmethod
    def _flag(v: Optional[bool]) -> Optional[str]:
        if v is None:
            return None
        return "1" if v else "0"

    @staticmethod
    def _validate_required_minima(b: BookingData) -> None:
        """
        Minimal presence checks for hard 'SI' fields from spec.
        """
        c = b.customer
        must_have = {
            "CONTRATTO_ID": b.contract_id,
            "CONTRATTO_DATA": b.contract_datetime,
            "CONTRATTO_TIPOP": b.payment_type_code,
            "CONTRATTO_CHECKOUT_DATA": b.checkout_datetime,
            "CONTRATTO_CHECKOUT_LUOGO_COD": b.checkout_place.location_code,
            "CONTRATTO_CHECKOUT_INDIRIZZO": b.checkout_place.street,
            "CONTRATTO_CHECKIN_DATA": b.checkin_datetime,
            "CONTRATTO_CHECKIN_LUOGO_COD": b.checkin_place.location_code,
            "CONTRATTO_CHECKIN_INDIRIZZO": b.checkin_place.street,
            "OPERATORE_ID": b.operator.id,
            "AGENZIA_ID": b.operator.agency_id,
            "AGENZIA_NOME": b.operator.agency_name,
            "AGENZIA_LUOGO_COD": b.operator.agency_place_code,
            "AGENZIA_INDIRIZZO": b.operator.agency_address,
            "AGENZIA_RECAPITO_TEL": b.operator.agency_phone,
            "VEICOLO_TIPO": b.car.type_code,
            "VEICOLO_MARCA": b.car.brand,
            "VEICOLO_MODELLO": b.car.model,
            "VEICOLO_TARGA": b.car.plate,
            "C1_COGNOME": c.surname,
            "C1_NOME": c.name,
            "C1_NASCITA_DATA": c.birth_date,
            "C1_NASCITA_LUOGO_COD": c.birth_place_code,
            "C1_CITTADINANZA_COD": c.citizenship_code,
            "C1_DOCIDE_TIPO_COD": c.id_doc_type_code,
            "C1_DOCIDE_NUMERO": c.id_doc_number,
            "C1_DOCIDE_LUOGORIL_COD": c.id_doc_issuing_place_code,
            "C1_PATENTE_NUMERO": c.driver_licence_number,
            "C1_PATENTE_LUOGORIL_COD": c.driver_licence_issuing_place_code,
        }
        missing = [k for k, v in must_have.items() if v in (None, "", 0)]
        if missing:
            raise CargosRecordError(f"Missing required fields: {', '.join(missing)}")