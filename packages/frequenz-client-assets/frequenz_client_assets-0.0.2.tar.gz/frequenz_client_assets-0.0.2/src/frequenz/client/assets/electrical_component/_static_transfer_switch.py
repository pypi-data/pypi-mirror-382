# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""StaticTransferSwitch component."""

import dataclasses
from typing import Literal

from ._category import ElectricalComponentCategory
from ._electrical_component import ElectricalComponent


@dataclasses.dataclass(frozen=True, kw_only=True)
class StaticTransferSwitch(ElectricalComponent):
    """A static transfer switch component."""

    category: Literal[ElectricalComponentCategory.STATIC_TRANSFER_SWITCH] = (
        ElectricalComponentCategory.STATIC_TRANSFER_SWITCH
    )
    """The category of this component."""
