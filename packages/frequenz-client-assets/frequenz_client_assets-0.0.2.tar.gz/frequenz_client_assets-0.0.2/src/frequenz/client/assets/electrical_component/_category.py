# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""The component categories that can be used in a microgrid."""

import enum

from frequenz.api.common.v1alpha8.microgrid.electrical_components import (
    electrical_components_pb2,
)


@enum.unique
class ElectricalComponentCategory(enum.Enum):
    """The known categories of components that can be present in a microgrid."""

    UNSPECIFIED = electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_UNSPECIFIED
    """The component category is unspecified, probably due to an error in the message."""

    GRID = electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_GRID_CONNECTION_POINT
    """The point where the local microgrid is connected to the grid."""

    METER = electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_METER
    """A meter, for measuring electrical metrics, e.g., current, voltage, etc."""

    INVERTER = electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_INVERTER
    """An electricity generator, with batteries or solar energy."""

    BREAKER = electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_BREAKER
    """A breaker, used to interrupt the flow of electricity."""

    CONVERTER = electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_CONVERTER
    """A DC-DC converter."""

    BATTERY = electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_BATTERY
    """A storage system for electrical energy, used by inverters."""

    EV_CHARGER = electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_EV_CHARGER
    """A station for charging electrical vehicles."""

    CRYPTO_MINER = electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_CRYPTO_MINER
    """A crypto miner."""

    ELECTROLYZER = electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_ELECTROLYZER
    """An electrolyzer for converting water into hydrogen and oxygen."""

    CHP = electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_CHP
    """A heat and power combustion plant (CHP stands for combined heat and power)."""

    PRECHARGER = electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_PRECHARGER
    """A precharge module.

    Precharging involves gradually ramping up the DC voltage to prevent any
    potential damage to sensitive electrical components like capacitors.

    While many inverters and batteries come equipped with in-built precharging
    mechanisms, some may lack this feature. In such cases, we need to use
    external precharging modules.
    """

    HVAC = electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_HVAC
    """A Heating, Ventilation, and Air Conditioning (HVAC) system."""

    POWER_TRANSFORMER = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_POWER_TRANSFORMER
    )
    """A power transformer."""

    PLC = electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_PLC
    """An industrial controller or PLC (Programmable Logic Controller)."""

    STATIC_TRANSFER_SWITCH = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_STATIC_TRANSFER_SWITCH
    )
    """A static transfer switch (STS)."""

    UNINTERRUPTIBLE_POWER_SUPPLY = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_UNINTERRUPTIBLE_POWER_SUPPLY
    )
    """An uninterruptible power supply (UPS)."""

    CAPACITOR_BANK = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_CAPACITOR_BANK
    )
    """A capacitor bank for power factor correction."""

    WIND_TURBINE = electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_WIND_TURBINE
    """A wind turbine."""
