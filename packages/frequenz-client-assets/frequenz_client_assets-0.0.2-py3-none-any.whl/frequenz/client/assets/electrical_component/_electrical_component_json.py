# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""JSON encoder for ElectricalComponent objects."""

import json
from dataclasses import asdict

from .._utils import AssetsJSONEncoder
from ._electrical_component import ElectricalComponent


def electrical_components_to_json(
    electrical_components: list[ElectricalComponent],
) -> str:
    """Convert a list of ElectricalComponent objects to a JSON string."""
    return json.dumps(
        [asdict(component) for component in electrical_components],
        cls=AssetsJSONEncoder,
        indent=2,
    )
