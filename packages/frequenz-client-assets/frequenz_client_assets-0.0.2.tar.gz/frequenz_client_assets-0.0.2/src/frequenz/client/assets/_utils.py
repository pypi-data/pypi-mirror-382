# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Utility functions for the Assets API client."""

import enum
import json
from datetime import datetime, timezone
from typing import Any

from frequenz.core.id import BaseId


class AssetsJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for assets-related objects.

    Uses encode() method to pre-process objects and handle:
    - Dictionary keys that are enums → converts to enum values (recursively processed)
    - List/tuple/set/frozenset items → recursively processes nested structures
    - Sets/frozensets are converted to lists for JSON compatibility

    Uses default() method to handle individual objects:
    - BaseId objects → integers
    - Enum objects → their values
    - Datetime objects → UTC ISO format strings
    """

    def default(self, o: Any) -> Any:
        """Convert supported objects to JSON-serializable format."""
        if isinstance(o, BaseId):
            return int(o)

        if isinstance(o, enum.Enum):
            return o.value

        if isinstance(o, datetime):
            if o.tzinfo is None:
                o = o.replace(tzinfo=timezone.utc)
            else:
                o = o.astimezone(timezone.utc)
            return o.isoformat()

        return super().default(o)

    def _encode_containers_recursively(self, o: Any) -> Any:
        """Recursively process objects to convert enum keys to their values."""
        if isinstance(o, dict):
            return {
                (
                    self._encode_containers_recursively(key.value)
                    if isinstance(key, enum.Enum)
                    else self._encode_containers_recursively(key)
                ): self._encode_containers_recursively(value)
                for key, value in o.items()
            }
        if isinstance(o, (list, tuple, set, frozenset)):
            items = [self._encode_containers_recursively(item) for item in o]
            return items if isinstance(o, (list, tuple)) else items
        return o

    def encode(self, o: Any) -> str:
        """Encode the given object to a JSON string, handling enum keys."""
        return super().encode(self._encode_containers_recursively(o))
