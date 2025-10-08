from __future__ import annotations

"""Ca.R.G.O.S. API client (HTTP wrapper).

Notes
-----
- Handles token acquisition and wraps the /api/Check and /api/Send endpoints.
- Expects the caller to provide fully-formed contract records (fixed-width
  strings produced by CargosRecordMapper).
- This module configures a module-level logger but does not attach handlers;
  handler configuration is the responsibility of the application using this
  library.
"""

import base64
import logging
from typing import Any, Optional

import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

from .exceptions import InvalidInput, InvalidResponse

logger = logging.getLogger(__name__)


class CargosAPI:
    """Ca.R.G.O.S. API client.

    Parameters
    ----------
    username : str
        Organization username for Ca.R.G.O.S.
    password : str
        Password for Ca.R.G.O.S.
    api_key : str
        48-char key where the first 32 chars are the AES key and the last 16
        chars are the IV used to encrypt the bearer token.

    Attributes
    ----------
    BASE_URL : str
        API base URL.
    token : Optional[dict]
        Last token payload as returned by /api/Token.
    """

    BASE_URL = "https://cargos.poliziadistato.it/CARGOS_API"

    def __init__(self, username: str, password: str, api_key: str):
        self.username = username
        self.password = password
        self.api_key = api_key
        self.token: Optional[dict[str, Any]] = None

    # ---- Internal helpers -------------------------------------------------

    def _encrypt_token_aes(self, access_token: str) -> str:
        """Encrypt an access token using AES-CBC and return base64.

        Splits the provided 48-char api_key into key (32 bytes) and iv (16 bytes),
        pads the token to AES.block_size and encrypts using CBC mode.

        Parameters
        ----------
        access_token : str
            Raw token string from /api/Token.

        Returns
        -------
        str
            Base64-encoded ciphertext suitable for Authorization: Bearer.

        Raises
        ------
        InvalidInput
            If api_key length is not 48 chars.
        Exception
            On cryptographic failures.
        """
        if len(self.api_key) != 48:
            raise InvalidInput("api_key must be exactly 48 characters long")
        key = self.api_key[:32].encode("utf-8")
        iv = self.api_key[32:48].encode("utf-8")
        cipher = AES.new(key, AES.MODE_CBC, iv)
        padded = pad(access_token.encode("utf-8"), AES.block_size)
        ct = cipher.encrypt(padded)
        return base64.b64encode(ct).decode("utf-8")

    # ---- Public HTTP methods ---------------------------------------------

    def get_token(self, timeout: int = 30) -> dict[str, Any]:
        """Retrieve an authentication token from /api/Token.

        Performs a basic-authenticated GET to /api/Token. On success, stores and
        returns the JSON payload.

        Parameters
        ----------
        timeout : int, optional
            Request timeout in seconds, by default 30.

        Returns
        -------
        dict
            Token payload as returned by the API.

        Raises
        ------
        requests.RequestException
            On network errors or timeouts.
        InvalidResponse
            If the API returns an error payload.
        """
        url = f"{self.BASE_URL}/api/Token"
        resp = requests.get(url, auth=(self.username, self.password), timeout=timeout)
        data = resp.json()
        if (errore := data.get("errore")):
            raise InvalidResponse(f"Token request failed: {errore}")
        self.token = data
        logger.info("Token obtained successfully")
        return self.token

    def _auth_headers(self) -> dict[str, str]:
        if not self.token:
            self.get_token()
        enc = self._encrypt_token_aes(self.token["access_token"])  # type: ignore[index]
        return {
            "Authorization": f"Bearer {enc}",
            "Organization": self.username,
            "Content-Type": "application/json",
        }

    def check_contracts(self, contracts: list[str], timeout: int = 30) -> list[dict[str, Any]]:
        """Validate contracts via /api/Check.

        Parameters
        ----------
        contracts : list[str]
            Fixed-width record strings to validate.
        timeout : int, optional
            Request timeout in seconds, by default 30.

        Returns
        -------
        list[dict]
            A list of result objects.

        Raises
        ------
        requests.RequestException
            On network errors or timeouts.
        """
        url = f"{self.BASE_URL}/api/Check"
        resp = requests.post(url, headers=self._auth_headers(), json=contracts, timeout=timeout)
        return resp.json()

    def send_contracts(self, contracts: list[str], timeout: int = 30) -> list[dict[str, Any]]:
        """Send contracts via /api/Send.

        Parameters
        ----------
        contracts : list[str]
            Fixed-width record strings to submit.
        timeout : int, optional
            Request timeout in seconds, by default 30.

        Returns
        -------
        list[dict]
            A list of result objects.

        Raises
        ------
        requests.RequestException
            On network errors or timeouts.
        InvalidResponse
            If the API returns an error payload.
        """
        url = f"{self.BASE_URL}/api/Send"
        resp = requests.post(url, headers=self._auth_headers(), json=contracts, timeout=timeout)
        data = resp.json()
        if (errore := data.get("errore")):
            raise InvalidResponse(f"Send request failed: {errore}")
        logger.info("Send completed for %d contracts", len(contracts))
        return data

