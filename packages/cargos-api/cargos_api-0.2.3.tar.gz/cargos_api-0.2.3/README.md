# cargos-api


[![PyPI](https://img.shields.io/pypi/v/cargos-api.svg)](https://pypi.org/project/cargos-api/) [![Python Versions](https://img.shields.io/pypi/pyversions/cargos-api.svg)](https://pypi.org/project/cargos-api/) [![License](https://img.shields.io/pypi/l/cargos-api.svg)](#license)


A small Python library to build and submit rental booking records to the Italian Police Ca.R.G.O.S. API.

## Table of Contents
- [cargos-api](#cargos-api)
- [Table of Contents](#table-of-contents)
- [Install](#install)
- [Quick start](#quick-start)
- [Formatting the data](#formatting-the-data)
  - [Required fields](#required-fields)
  - [Optional fields](#optional-fields)
  - [Lookup tables (locations, documents, payments, vehicles)](#lookup-tables-locations-documents-payments-vehicles)
- [API usage notes](#api-usage-notes)
- [Inspecting the record as a mapping](#inspecting-the-record-as-a-mapping)

---

This repository was created to interact with the Ca.R.G.O.S. APIs for a client who needed to automate the submission of rental booking details to the Italian Police.

The official documentation (see [docs.pdf](./docs/docs.pdf)) is difficult to follow and sparse on examples. The goal of this project is to provide a clean, documented Python module that makes the integration straightforward and consistent.

This module handles all the location -> id conversions, data formatting and submission to the Ca.R.G.O.S. API.

---

## Install

```
pip install cargos-api
```

## Quick start

```python
from cargos_api import CargosAPI, CargosRecordMapper, models as m

# Credentials
api = CargosAPI(username="...", password="...", api_key="...48-chars...")

# Build a booking using codes from your catalogs (examples below use placeholder codes)
booking = m.BookingData(
    contract_id="CONTR-001",
    contract_datetime="2025-01-01T10:00:00",   # ISO-like; mapper outputs dd/mm/YYYY HH:MM
    payment_type_code="1",                     # per Ca.R.G.O.S. table
    checkout_datetime="2025-01-01T11:00:00",
    checkout_place=m.Address(location_code=403015146, street="Via X 1"),  # Roma (example)
    checkin_datetime="2025-01-02T11:00:00",
    checkin_place=m.Address(location_code=402020327, street="Via Y 2"),    # Verona (example)
    operator=m.Operator(
        id="SYSTEM",
        agency_id="1",
        agency_name="ACME",
        agency_place_code=403015146,
        agency_address="Via Z 3",
        agency_phone="0000",
    ),
    car=m.Car(
        type_code="A",  # vehicle type code (per table)
        brand="Fiat",
        model="Panda",
        plate="AB123CD",
        color="Bianco",
    ),
    customer=m.Customer(
        surname="Rossi",
        name="Mario",
        birth_date="1990-01-01",
        birth_place_code=401028044,           # Genova (example)
        citizenship_code=100000001,           # Italia (example)
        id_doc_type_code="CI",
        id_doc_number="XYZ12345",
        id_doc_issuing_place_code=401028044,
        driver_licence_number="LIC123456",
        driver_licence_issuing_place_code=401028044,
        contact="0000000000",
    ),
)

# Map to Ca.R.G.O.S. fixed-width record (1505 chars)
record = CargosRecordMapper().build_record(booking)

# Validate or send
api.check_contracts([record])
# api.send_contracts([record])
```

## Formatting the data

This library exposes typed dataclasses in `cargos_api.models` that you fill with your normalized data and pass to the mapper.

- `BookingData`: `contract_id`, `contract_datetime`, `payment_type_code`, `checkout_datetime`, `checkout_place` (Address), `checkin_datetime`, `checkin_place` (Address), `operator` (Operator), `car` (Car), `customer` (Customer), `second_driver` (optional)
- `Customer`: `surname`, `name`, `birth_date`, `birth_place_code`, `citizenship_code`, `residence` (Address, optional), `id_doc_type_code`, `id_doc_number`, `id_doc_issuing_place_code`, `driver_licence_number`, `driver_licence_issuing_place_code`, `contact`
- `SecondDriver`: same as `Customer` (without `residence`); if present, all fields are mandatory
- `Car`: `type_code`, `brand`, `model`, `plate`, `color` (optional), `has_gps` (optional), `has_immobilizer` (optional)
- `Address`: `location_code`, `street`
- `Operator`: `id`, `agency_id`, `agency_name`, `agency_place_code`, `agency_address`, `agency_phone`

### Ca.R.G.O.S. Tracciato Record Parameters

| Name | Required | Description |
|------|-----------|-------------|
| CONTRATTO_ID | ✅ | Unique contract identifier |
| CONTRATTO_DATA | ✅ | Contract date (format `gg/mm/aaaa hh:mm`) |
| CONTRATTO_TIPOP | ✅ | Payment type (see **TABELLA TIPO PAGAMENTI**) |
| CONTRATTO_CHECKOUT_DATA | ✅ | Checkout date (format `gg/mm/aaaa hh:mm`) |
| CONTRATTO_CHECKOUT_LUOGO_COD | ✅ | Police location code (**TABELLA LUOGHI POLIZIA**) |
| CONTRATTO_CHECKOUT_INDIRIZZO | ✅ | Checkout address (length > 3) |
| CONTRATTO_CHECKIN_DATA | ✅ | Check-in date (format `gg/mm/aaaa hh:mm`) |
| CONTRATTO_CHECKIN_LUOGO_COD | ✅ | Police location code (**TABELLA LUOGHI POLIZIA**) |
| CONTRATTO_CHECKIN_INDIRIZZO | ✅ | Check-in address (length > 3) |
| OPERATORE_ID | ✅ | Operator identifier |
| AGENZIA_ID | ✅ | Agency identifier (unique) |
| AGENZIA_NOME | ✅ | Agency name |
| AGENZIA_LUOGO_COD | ✅ | Police location code (**TABELLA LUOGHI POLIZIA**) |
| AGENZIA_INDIRIZZO | ✅ | Agency address (length > 3) |
| AGENZIA_RECAPITO_TEL | ✅ | Agency phone number (length > 3) |
| VEICOLO_TIPO | ✅ | Vehicle type (**TABELLA TIPO VEICOLO**) |
| VEICOLO_MARCA | ✅ | Vehicle brand |
| VEICOLO_MODELLO | ✅ | Vehicle model |
| VEICOLO_TARGA | ✅ | Vehicle plate number (length > 3) |
| VEICOLO_COLORE | ❌ | Vehicle color |
| VEICOLO_GPS | ❌ | GPS presence flag |
| VEICOLO_BLOCCOM | ❌ | Immobilizer presence flag |
| CONDUCENTE_CONTRAENTE_COGNOME | ✅ | Driver’s surname |
| CONDUCENTE_CONTRAENTE_NOME | ✅ | Driver’s name |
| CONDUCENTE_CONTRAENTE_NASCITA_DATA | ✅ | Driver’s date of birth (`gg/mm/aaaa`) |
| CONDUCENTE_CONTRAENTE_NASCITA_LUOGO_COD | ✅ | Birthplace (**COMUNE ITALIANO** or **STATO ESTERO**) |
| CONDUCENTE_CONTRAENTE_CITTADINANZA_COD | ✅ | Citizenship code (**TABELLA LUOGHI POLIZIA**) |
| CONDUCENTE_CONTRAENTE_RESIDENZA_LUOGO_COD | ❌* | Residence (**COMUNE ITALIANO** or **STATO ESTERO**) |
| CONDUCENTE_CONTRAENTE_RESIDENZA_INDIRIZZO | ❌* | Residence address (e.g., “VIA DEL CASTRO PRETORIO 10, ROMA”) |
| CONDUCENTE_CONTRAENTE_DOCIDE_TIPO_COD | ✅ | Document type (**TABELLA DOCUMENTI POLIZIA**) |
| CONDUCENTE_CONTRAENTE_DOCIDE_NUMERO | ✅ | Document number (length > 4) |
| CONDUCENTE_CONTRAENTE_DOCIDE_LUOGORIL_COD | ✅ | Document issuing place (**COMUNE ITALIANO** or **STATO ESTERO**) |
| CONDUCENTE_CONTRAENTE_PATENTE_NUMERO | ✅ | Driver’s license number (length > 4) |
| CONDUCENTE_CONTRAENTE_PATENTE_LUOGORIL_COD | ✅ | License issuing place (**COMUNE ITALIANO** or **STATO ESTERO**) |
| CONDUCENTE_CONTRAENTE_RECAPITO | ❌ | Driver’s contact number |
| CONDUCENTE2_COGNOME | ❌** | Second driver surname |
| CONDUCENTE2_NOME | ❌** | Second driver name |
| CONDUCENTE2_NASCITA_DATA | ❌** | Second driver date of birth (`gg/mm/aaaa`) |
| CONDUCENTE2_NASCITA_LUOGO_COD | ❌** | Second driver birthplace (**COMUNE ITALIANO** or **STATO ESTERO**) |
| CONDUCENTE2_CITTADINANZA_COD | ❌** | Second driver citizenship (**TABELLA LUOGHI POLIZIA**) |
| CONDUCENTE2_DOCIDE_TIPO_COD | ❌** | Second driver document type |
| CONDUCENTE2_DOCIDE_NUMERO | ❌** | Second driver document number |
| CONDUCENTE2_DOCIDE_LUOGORIL_COD | ❌** | Second driver document issuing place |
| CONDUCENTE2_PATENTE_NUMERO | ❌** | Second driver license number (length > 4) |
| CONDUCENTE2_PATENTE_LUOGORIL_COD | ❌** | Second driver license issuing place |
| CONDUCENTE2_RECAPITO | ❌** | Second driver contact number |

---

### Notes
- `*` → Both residence fields (**LUOGO_COD** and **INDIRIZZO**) must be filled together, otherwise the data is rejected.
- `**` → If a second driver is present, **all** fields under `CONDUCENTE2_` become **mandatory**.
- Each block of records must not contain more than **100 contracts** (rows).

### Required fields
The mapper validates inputs and raises `InvalidInput` if anything is missing:
- booking: `id`, `creation_date`, `from_date`, `to_date`
- customer: `birth_date`, `firstname`, `lastname`, `birth_place`, `citizenship`, and one of (`document_id`, `driver_licence_number`) and one of (`cellphone`, `email`)
- car: `brand`, `model`, `plate`, `color`
- delivery_place: `address_city`, `address`
- return_place: `address_city`, `address`
- operator: `id`, `agency_id`, `agency_name`, `city`, `address`, `phone`

### Optional fields
- `Customer.address` is emitted as free-text in the record when provided
- `Address.address_country` is currently not mapped to a dedicated field

### Lookup tables (locations, documents, payments, vehicles)
- Packaged CSV catalogs under `cargos_api/data/` are used at runtime:
  - `luoghi.csv` (location/country codes)
  - `tipo_documento.csv` (document types)
  - `tipo_pagamento.csv` (payment types)
  - `tipo_veicolo.csv` (vehicle types)
- Lookups are case-insensitive; expired locations (rows with `DataFineVal`) are ignored
- Use `CatalogLoader` if you need to resolve human-readable labels to Ca.R.G.O.S. codes in your app:
  ```python
  from cargos_api.locations_loader import CatalogLoader
  code = CatalogLoader().document_type_code('CI')
  ```
- If a required code is not found, the mapper raises a `ValueError`

## Inspecting the record as a mapping
Sometimes you want to verify exactly what each field contains after padding/truncation. You can ask the mapper to return both the fixed-width string and a JSON-like mapping of field names to their exact slices by passing `with_map=True`:

```python
from cargos_api import CargosRecordMapper, models as m

booking = m.BookingData(
    contract_id="123", contract_datetime="2025-01-05T09:00:00", payment_type_code="1",
    checkout_datetime="2025-01-06T10:00:00", checkout_place=m.Address(location_code=403015146, street="Via A 10"),
    checkin_datetime="2025-01-07T10:00:00", checkin_place=m.Address(location_code=403015146, street="Via B 20"),
    operator=m.Operator(id="SYS", agency_id="AG1", agency_name="ACME", agency_place_code=403015146, agency_address="Via C 30", agency_phone="06..."),
    car=m.Car(type_code="A", brand="VW", model="Golf", plate="ZZ999ZZ"),
    customer=m.Customer(
        surname="Bianchi", name="Anna", birth_date="1985-05-20",
        birth_place_code=403015146, citizenship_code=100000001,
        id_doc_type_code="CI", id_doc_number="X1", id_doc_issuing_place_code=403015146,
        driver_licence_number="L1", driver_licence_issuing_place_code=403015146,
    ),
)
record, mapping = CargosRecordMapper().build_record(booking, with_map=True)
print(len(record))              # 1505
print(mapping["CONTRATTO_ID"])  # 50-char padded slice for the contract ID
```

## API usage notes
- `CargosAPI.get_token()` fetches the token using HTTP Basic auth
- The `api_key` must be exactly 48 characters: first 32 chars are the AES key and the last 16 chars are the IV used to encrypt the bearer token
- Use `check_contracts(records)` to validate records before submission; use `send_contracts(records)` to submit them

## Example: minimal end-to-end flow
```python
from cargos_api import CargosAPI, CargosRecordMapper, models as m

api = CargosAPI(username="ORG", password="PASS", api_key="...48-chars...")
booking = m.BookingData(
    contract_id="123",
    contract_datetime="2025-01-05T09:00:00",
    payment_type_code="1",
    checkout_datetime="2025-01-06T10:00:00",
    checkout_place=m.Address(location_code=403015146, street="Via A 10"),
    checkin_datetime="2025-01-07T10:00:00",
    checkin_place=m.Address(location_code=403015146, street="Via B 20"),
    operator=m.Operator(id="SYS", agency_id="AG1", agency_name="ACME", agency_place_code=403015146, agency_address="Via C 30", agency_phone="06..."),
    car=m.Car(type_code="A", brand="VW", model="Golf", plate="ZZ999ZZ", color="Nero"),
    customer=m.Customer(
        surname="Bianchi", name="Anna", birth_date="1985-05-20",
        birth_place_code=403015146, citizenship_code=100000001,
        id_doc_type_code="CI", id_doc_number="DOC1", id_doc_issuing_place_code=403015146,
        driver_licence_number="LIC1", driver_licence_issuing_place_code=403015146,
        contact="333...",
    ),
)
record = CargosRecordMapper().build_record(booking)
api.check_contracts([record])
```

## Troubleshooting
- `ValueError`: location not found → check the spelling of city/country names
- `InvalidInput`: missing fields → read the error message for which fields are missing
- `InvalidResponse`: HTTP errors → network issues or server response with `errore` field

## Building something with it?
If you nee dhelp implementing this in your project, please reach out.


## Author

If you found this project helpful or interesting, consider starring the repo and following me for more security research and tools, or buy me a coffee to keep me up

<p align="center">
  <a href="https://github.com/GlizzyKingDreko"><img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" alt="GitHub"></a>
  <a href="https://twitter.com/GlizzyKingDreko"><img src="https://img.shields.io/badge/Twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white" alt="Twitter"></a>
  <a href="https://medium.com/@GlizzyKingDreko"><img src="https://img.shields.io/badge/Medium-12100E?style=for-the-badge&logo=medium&logoColor=white" alt="Medium"></a>
  <a href="https://discord.com/users/GlizzyKingDreko"><img src="https://img.shields.io/badge/Discord-7289DA?style=for-the-badge&logo=discord&logoColor=white" alt="Discord"></a>
  <a href="mailto:glizzykingdreko@protonmail.com"><img src="https://img.shields.io/badge/ProtonMail-8B89CC?style=for-the-badge&logo=protonmail&logoColor=white" alt="Email"></a>
  <a href="https://buymeacoffee.com/glizzykingdreko"><img src="https://img.shields.io/badge/Buy%20Me%20a%20Coffee-yellow?style=for-the-badge&logo=buy-me-a-coffee&logoColor=white" alt="Buy Me a Coffee"></a>
</p>

---
