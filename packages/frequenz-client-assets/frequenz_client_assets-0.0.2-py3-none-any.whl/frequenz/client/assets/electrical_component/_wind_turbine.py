# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Wind Turbine component."""

import dataclasses
from typing import Literal

from ._category import ElectricalComponentCategory
from ._electrical_component import ElectricalComponent


@dataclasses.dataclass(frozen=True, kw_only=True)
class WindTurbine(ElectricalComponent):
    """A wind turbine component."""

    category: Literal[ElectricalComponentCategory.WIND_TURBINE] = (
        ElectricalComponentCategory.WIND_TURBINE
    )
    """The category of this component."""
