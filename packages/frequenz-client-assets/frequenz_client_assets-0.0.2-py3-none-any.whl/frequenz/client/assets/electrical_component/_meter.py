# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Meter component."""

import dataclasses
from typing import Literal

from ._category import ElectricalComponentCategory
from ._electrical_component import ElectricalComponent


@dataclasses.dataclass(frozen=True, kw_only=True)
class Meter(ElectricalComponent):
    """A measuring meter component."""

    category: Literal[ElectricalComponentCategory.METER] = (
        ElectricalComponentCategory.METER
    )
    """The category of this component."""
