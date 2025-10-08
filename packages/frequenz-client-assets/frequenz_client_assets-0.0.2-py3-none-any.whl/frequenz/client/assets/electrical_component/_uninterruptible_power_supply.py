# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""UninterruptiblePowerSupply component."""

import dataclasses
from typing import Literal

from ._category import ElectricalComponentCategory
from ._electrical_component import ElectricalComponent


@dataclasses.dataclass(frozen=True, kw_only=True)
class UninterruptiblePowerSupply(ElectricalComponent):
    """An uninterruptible power supply component."""

    category: Literal[ElectricalComponentCategory.UNINTERRUPTIBLE_POWER_SUPPLY] = (
        ElectricalComponentCategory.UNINTERRUPTIBLE_POWER_SUPPLY
    )
    """The category of this component."""
