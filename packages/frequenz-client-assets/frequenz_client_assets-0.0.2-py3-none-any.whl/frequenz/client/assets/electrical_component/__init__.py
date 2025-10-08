# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Electrical component types."""

from ._battery import (
    BatteryType,
    LiIonBattery,
    NaIonBattery,
    UnrecognizedBattery,
    UnspecifiedBattery,
)
from ._breaker import Breaker
from ._capacitor_bank import CapacitorBank
from ._category import ElectricalComponentCategory
from ._chp import Chp
from ._converter import Converter
from ._crypto_miner import CryptoMiner
from ._electrical_component import ElectricalComponent
from ._electrolyzer import Electrolyzer
from ._ev_charger import (
    AcEvCharger,
    DcEvCharger,
    EvChargerType,
    HybridEvCharger,
    UnrecognizedEvCharger,
    UnspecifiedEvCharger,
)
from ._grid_connection_point import GridConnectionPoint
from ._hvac import Hvac
from ._inverter import (
    BatteryInverter,
    HybridInverter,
    InverterType,
    PvInverter,
    UnrecognizedInverter,
    UnspecifiedInverter,
)
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

__all__ = [
    "Chp",
    "CryptoMiner",
    "BatteryType",
    "LiIonBattery",
    "NaIonBattery",
    "UnrecognizedBattery",
    "UnspecifiedBattery",
    "Breaker",
    "Converter",
    "CapacitorBank",
    "ElectricalComponentCategory",
    "ElectricalComponent",
    "Electrolyzer",
    "AcEvCharger",
    "DcEvCharger",
    "EvChargerType",
    "HybridEvCharger",
    "UnrecognizedEvCharger",
    "UnspecifiedEvCharger",
    "GridConnectionPoint",
    "Hvac",
    "BatteryInverter",
    "HybridInverter",
    "InverterType",
    "PvInverter",
    "UnrecognizedInverter",
    "UnspecifiedInverter",
    "Meter",
    "Plc",
    "PowerTransformer",
    "Precharger",
    "MismatchedCategoryComponent",
    "UnrecognizedComponent",
    "UnspecifiedComponent",
    "StaticTransferSwitch",
    "UninterruptiblePowerSupply",
    "WindTurbine",
]
