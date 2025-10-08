# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""CHP component."""

import dataclasses
from typing import Literal

from ._category import ElectricalComponentCategory
from ._electrical_component import ElectricalComponent


@dataclasses.dataclass(frozen=True, kw_only=True)
class Chp(ElectricalComponent):
    """A combined heat and power (CHP) component."""

    category: Literal[ElectricalComponentCategory.CHP] = ElectricalComponentCategory.CHP
    """The category of this component."""
