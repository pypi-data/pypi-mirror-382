# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Converter component."""

import dataclasses
from typing import Literal

from ._category import ElectricalComponentCategory
from ._electrical_component import ElectricalComponent


@dataclasses.dataclass(frozen=True, kw_only=True)
class Converter(ElectricalComponent):
    """An AC-DC converter component."""

    category: Literal[ElectricalComponentCategory.CONVERTER] = (
        ElectricalComponentCategory.CONVERTER
    )
    """The category of this component."""
