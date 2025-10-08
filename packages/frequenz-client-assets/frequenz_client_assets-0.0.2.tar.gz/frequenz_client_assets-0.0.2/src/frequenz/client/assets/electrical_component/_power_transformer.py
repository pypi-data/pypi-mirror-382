# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Power transformer component."""

import dataclasses
from typing import Literal

from ._category import ElectricalComponentCategory
from ._electrical_component import ElectricalComponent


@dataclasses.dataclass(frozen=True, kw_only=True)
class PowerTransformer(ElectricalComponent):
    """A power transformer designed for the bulk transfer of electrical energy.

    Power transformers are essential components in electrical power systems that
    transfer electrical energy between different voltage levels. Their primary
    function is to "step-up" or "step-down" voltage levels for efficient
    transmission and distribution of power across the electrical grid.
    """

    category: Literal[ElectricalComponentCategory.POWER_TRANSFORMER] = (
        ElectricalComponentCategory.POWER_TRANSFORMER
    )
    """The category of this component."""

    primary_power: float
    """The primary voltage of the power transformer."""

    secondary_power: float
    """The secondary voltage of the power transformer."""
