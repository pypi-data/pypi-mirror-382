from __future__ import annotations
from typing import Callable, Dict, Optional, Union
import csv
import importlib.resources as pkgres

FallbackT = Union[None, str, int, Callable[[str, str], str]]

class CatalogLoader:
    """
    Loads lookup tables from the installed 'cargos_api' package data folder.

    Defaults:
      - package='cargos_api'
      - subdir='data'
      - filenames: luoghi.csv, tipo_documento.csv, tipo_pagamento.csv, tipo_veicolo.csv

    Fallback:
      - fallback can be a constant or a callable(key, kind) -> str
      - kind ∈ {"location","document","payment","vehicle"}
    """

    def __init__(
        self,
        package: str = "cargos_api",
        *,
        subdir: str = "data",
        luoghi_csv: str = "luoghi.csv",
        tipo_documento_csv: str = "tipo_documento.csv",
        tipo_pagamento_csv: str = "tipo_pagamento.csv",
        tipo_veicolo_csv: str = "tipo_veicolo.csv",
        fallback: FallbackT = None,
    ) -> None:
        self.package = package
        self.subdir = subdir
        self._fallback = fallback

        self._luoghi_by_desc: Dict[str, str] = {}
        self._luoghi_by_code: Dict[str, str] = {}
        self._docs_by_desc: Dict[str, str] = {}
        self._pay_by_desc: Dict[str, str] = {}
        self._veh_by_desc: Dict[str, str] = {}

        self._load_luoghi_csv(luoghi_csv)
        self._docs_by_desc = self._load_simple_map(tipo_documento_csv, code_col="CODICE", desc_col="DESCRIZIONE")
        self._pay_by_desc  = self._load_simple_map(tipo_pagamento_csv, code_col="ID", desc_col="Descrizione")
        self._veh_by_desc  = self._load_simple_map(tipo_veicolo_csv, code_col="ID", desc_col="Descrizione")

    # ---------- Public lookups ----------

    def location_code(self, name: str) -> str:
        return self._by_desc(self._luoghi_by_desc, name, kind="location")

    def location_name(self, code: Union[int, str]) -> str:
        """Return the city/country description for a given Ca.R.G.O.S. luogo code."""
        key = str(int(code)) if isinstance(code, int) else str(code).strip()
        if key in self._luoghi_by_code:
            return self._luoghi_by_code[key]
        raise ValueError(f"location code not found: {code!r}")

    def document_type_code(self, description: str) -> str:
        return self._by_desc(self._docs_by_desc, description, kind="document")

    def payment_type_code(self, description: str) -> str:
        return self._by_desc(self._pay_by_desc, description, kind="payment")

    def vehicle_type_code(self, description: str) -> str:
        return self._by_desc(self._veh_by_desc, description, kind="vehicle")

    # ---------- Internals ----------

    def _read_text(self, filename: str) -> str:
        base = pkgres.files(self.package).joinpath(self.subdir, filename)
        return base.read_text(encoding="utf-8")

    def _load_luoghi_csv(self, filename: str) -> None:
        text = self._read_text(filename)
        reader = csv.DictReader(text.splitlines())
        for row in reader:
            if not row:
                continue
            code = (row.get("Codice") or "").strip()
            desc = (row.get("Descrizione") or "").strip()
            fine = (row.get("DataFineVal") or "").strip()
            if not code or not desc or fine:
                continue
            self._luoghi_by_desc[desc.lower()] = code
            self._luoghi_by_code[code] = desc

    def _load_simple_map(self, filename: str, *, code_col: str, desc_col: str) -> Dict[str, str]:
        text = self._read_text(filename)
        reader = csv.DictReader(text.splitlines())
        out: Dict[str, str] = {}
        for row in reader:
            code = (row.get(code_col) or "").strip()
            desc = (row.get(desc_col) or "").strip()
            if code and desc:
                out[desc.lower()] = code
        return out

    def _by_desc(self, mapping: Dict[str, str], key: str, *, kind: "location|document|payment|vehicle") -> str:
        look_key = (key or "").strip().lower()
        if look_key in mapping:
            return mapping[look_key]
        if callable(self._fallback):
            val = self._fallback(key, kind)
            if not val:
                raise ValueError(f"{kind} not found and fallback returned empty for {key!r}")
            return str(val)
        if self._fallback is not None:
            return str(self._fallback)
        raise ValueError(f"{kind} not found: {key!r}")