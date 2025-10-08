# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""JSON encoder for Microgrid objects."""

import json
from dataclasses import asdict

from ._microgrid import Microgrid
from ._utils import AssetsJSONEncoder


def microgrid_to_json(microgrid: Microgrid) -> str:
    """Convert a Microgrid object to a JSON string."""
    return json.dumps(asdict(microgrid), cls=AssetsJSONEncoder, indent=2)
