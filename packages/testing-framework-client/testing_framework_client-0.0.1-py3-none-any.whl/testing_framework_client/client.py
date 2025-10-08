from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
import requests
from requests import Response

from .auth import AuthClient


class Unit(str, Enum):
    W = "W"
    A = "A"


class DistributionStrategy(str, Enum):
    HOLD = "Hold"
    DISTRIBUTE = "Distribute"


class TFClientError(Exception):
    """Custom error type for TFClient API failures."""


class TFClient:
    """
    Client for Testing Framework public endpoints.
    Uses AuthClient for token management.
    """

    def __init__(self, auth_client: AuthClient = None):
        self.auth_client = auth_client or AuthClient()

    @staticmethod
    def _raise_then_json(resp: Response) -> Dict[str, Any]:
        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            raise TFClientError(
                f"API call failed: {resp.status_code} {resp.text}"
            ) from e
        return resp.json()

    # ----------------------
    # Set Limit
    # ----------------------
    def set_charge_limit(
        self,
        limit: float,
        unit: Unit,
        valid_to: datetime,
        chargebox_id: int,
        connector_id: int,
        input_phases: Optional[float] = None,
        input_voltage: Optional[float] = None,
        distribution_strategy: DistributionStrategy = DistributionStrategy.HOLD,
    ) -> Dict[str, Any]:
        payload = {
            "limit": limit,
            "unit": unit.value,
            "valid_to": valid_to.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "chargebox_id": chargebox_id,
            "connector_id": connector_id,
            "input_phases": input_phases,
            "input_voltage": input_voltage,
            "distribution_strategy": distribution_strategy.value,
        }
        path = "/public/v1/set-charge-limit"
        resp = self.auth_client.request(path, method="POST", json=payload)
        resp.raise_for_status()
        # NOTE: endpoint only returns 200 if successfuly, no body

    # ----------------------
    # Clear Charge Limit
    # ----------------------
    def clear_charge_limit(
        self, chargebox_id: int, connector_id: int
    ) -> Dict[str, Any]:
        path = "/public/v1/clear-charge-limit"
        payload = {
            "chargebox_id": chargebox_id,
            "connector_id": connector_id,
        }
        resp = self.auth_client.request(path, method="POST", json=payload)
        resp.raise_for_status()

    # ----------------------
    # Get Chargebox
    # ----------------------
    def get_chargebox(self, chargebox_id: int) -> Dict[str, Any]:
        path = f"/public/v1/chargeboxes/{chargebox_id}"
        resp = self.auth_client.request(path, method="GET")
        return self._raise_then_json(resp)

    # ----------------------
    # Get Connector
    # ----------------------
    def get_connector(self, chargebox_id: int, connector_id: int) -> Dict[str, Any]:
        path = f"/public/v1/chargeboxes/{chargebox_id}/connectors/{connector_id}"
        resp = self.auth_client.request(path, method="GET")
        return self._raise_then_json(resp)
