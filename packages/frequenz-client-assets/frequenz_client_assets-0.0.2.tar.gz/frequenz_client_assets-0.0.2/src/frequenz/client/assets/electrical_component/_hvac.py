# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""HVAC component."""

import dataclasses
from typing import Literal

from ._category import ElectricalComponentCategory
from ._electrical_component import ElectricalComponent


@dataclasses.dataclass(frozen=True, kw_only=True)
class Hvac(ElectricalComponent):
    """A heating, ventilation, and air conditioning (HVAC) component."""

    category: Literal[ElectricalComponentCategory.HVAC] = (
        ElectricalComponentCategory.HVAC
    )
    """The category of this component."""
