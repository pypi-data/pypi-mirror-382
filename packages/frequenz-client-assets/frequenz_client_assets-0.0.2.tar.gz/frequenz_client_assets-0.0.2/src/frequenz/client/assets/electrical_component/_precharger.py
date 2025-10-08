# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Precharger component."""

import dataclasses
from typing import Literal

from ._category import ElectricalComponentCategory
from ._electrical_component import ElectricalComponent


@dataclasses.dataclass(frozen=True, kw_only=True)
class Precharger(ElectricalComponent):
    """A precharger component."""

    category: Literal[ElectricalComponentCategory.PRECHARGER] = (
        ElectricalComponentCategory.PRECHARGER
    )
    """The category of this component."""
