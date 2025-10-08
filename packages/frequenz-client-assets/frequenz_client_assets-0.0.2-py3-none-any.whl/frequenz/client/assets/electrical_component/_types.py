# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Electrical component types."""

from typing import TypeAlias

from ._battery import BatteryTypes, UnrecognizedBattery, UnspecifiedBattery
from ._breaker import Breaker
from ._capacitor_bank import CapacitorBank
from ._chp import Chp
from ._converter import Converter
from ._crypto_miner import CryptoMiner
from ._electrolyzer import Electrolyzer
from ._ev_charger import EvChargerTypes, UnrecognizedEvCharger, UnspecifiedEvCharger
from ._grid_connection_point import GridConnectionPoint
from ._hvac import Hvac
from ._inverter import InverterTypes, UnrecognizedInverter, UnspecifiedInverter
from ._meter import Meter
from ._plc import Plc
from ._power_transformer import PowerTransformer
from ._precharger import Precharger
from ._problematic import (
    MismatchedCategoryComponent,
    UnrecognizedComponent,
    UnspecifiedComponent,
)
from ._static_transfer_switch import StaticTransferSwitch
from ._uninterruptible_power_supply import UninterruptiblePowerSupply
from ._wind_turbine import WindTurbine

UnspecifiedComponentTypes: TypeAlias = (
    UnspecifiedBattery
    | UnspecifiedComponent
    | UnspecifiedEvCharger
    | UnspecifiedInverter
)
"""All unspecified component types."""

UnrecognizedComponentTypes: TypeAlias = (
    UnrecognizedBattery
    | UnrecognizedComponent
    | UnrecognizedEvCharger
    | UnrecognizedInverter
)

ProblematicComponentTypes: TypeAlias = (
    MismatchedCategoryComponent | UnrecognizedComponentTypes | UnspecifiedComponentTypes
)
"""All possible component types that has a problem."""

ElectricalComponentType: TypeAlias = (
    BatteryTypes
    | Chp
    | Converter
    | CryptoMiner
    | Electrolyzer
    | Hvac
    | Meter
    | Precharger
    | Breaker
    | Plc
    | StaticTransferSwitch
    | UninterruptiblePowerSupply
    | CapacitorBank
    | WindTurbine
    | InverterTypes
    | PowerTransformer
    | EvChargerTypes
    | GridConnectionPoint
    | ProblematicComponentTypes
)
"""The type of the electrical component."""
