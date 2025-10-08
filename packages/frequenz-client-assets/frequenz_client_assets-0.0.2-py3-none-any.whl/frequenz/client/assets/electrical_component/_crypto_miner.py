# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Crypto miner component."""

import dataclasses
from typing import Literal

from ._category import ElectricalComponentCategory
from ._electrical_component import ElectricalComponent


@dataclasses.dataclass(frozen=True, kw_only=True)
class CryptoMiner(ElectricalComponent):
    """A crypto miner component."""

    category: Literal[ElectricalComponentCategory.CRYPTO_MINER] = (
        ElectricalComponentCategory.CRYPTO_MINER
    )
    """The category of this component."""
