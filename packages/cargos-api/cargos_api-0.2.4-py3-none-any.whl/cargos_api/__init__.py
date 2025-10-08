from __future__ import annotations

"""Top-level package for the Ca.R.G.O.S. API client and strict mapper.

This library provides:
- CargosAPI: Thin HTTP client for the Italian Police Ca.R.G.O.S. endpoints
- CargosRecordMapper: Builder for the fixed-width contract records (1505 chars)
- CatalogLoader: Helper to load Ca.R.G.O.S. lookup tables from CSVs
- Exceptions: CargoException, InvalidInput, InvalidResponse
- models: Dataclasses-based models used by the mapper

The public surface avoids side effects (e.g., no logging handlers added) so it can
be embedded in larger applications.
"""

from .api import CargosAPI
from .mapper import CargosRecordMapper
from .exceptions import CargoException, InvalidInput, InvalidResponse
from .locations_loader import CatalogLoader
from . import models

__all__ = ["CargosAPI", "CargosRecordMapper", "CargoException", "InvalidInput", "InvalidResponse", "CatalogLoader", "models"]
__version__ = "0.2.4"

