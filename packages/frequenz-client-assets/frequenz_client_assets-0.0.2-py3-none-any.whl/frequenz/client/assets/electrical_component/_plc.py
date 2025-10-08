# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""PLC component."""

import dataclasses
from typing import Literal

from ._category import ElectricalComponentCategory
from ._electrical_component import ElectricalComponent


@dataclasses.dataclass(frozen=True, kw_only=True)
class Plc(ElectricalComponent):
    """A PLC component."""

    category: Literal[ElectricalComponentCategory.PLC] = ElectricalComponentCategory.PLC
    """The category of this component."""
