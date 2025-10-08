# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Electrolyzer component."""

import dataclasses
from typing import Literal

from ._category import ElectricalComponentCategory
from ._electrical_component import ElectricalComponent


@dataclasses.dataclass(frozen=True, kw_only=True)
class Electrolyzer(ElectricalComponent):
    """An electrolyzer component."""

    category: Literal[ElectricalComponentCategory.ELECTROLYZER] = (
        ElectricalComponentCategory.ELECTROLYZER
    )
    """The category of this component."""
