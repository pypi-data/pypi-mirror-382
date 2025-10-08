# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""CapacitorBank component."""

import dataclasses
from typing import Literal

from ._category import ElectricalComponentCategory
from ._electrical_component import ElectricalComponent


@dataclasses.dataclass(frozen=True, kw_only=True)
class CapacitorBank(ElectricalComponent):
    """A capacitor bank component."""

    category: Literal[ElectricalComponentCategory.CAPACITOR_BANK] = (
        ElectricalComponentCategory.CAPACITOR_BANK
    )
    """The category of this component."""
