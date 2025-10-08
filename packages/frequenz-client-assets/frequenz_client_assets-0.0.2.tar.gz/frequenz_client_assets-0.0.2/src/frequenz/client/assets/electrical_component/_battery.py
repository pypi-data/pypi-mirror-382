# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Battery component."""

import dataclasses
import enum
from typing import Any, Literal, Self, TypeAlias

from frequenz.api.common.v1alpha8.microgrid.electrical_components import (
    electrical_components_pb2,
)

from ._category import ElectricalComponentCategory
from ._electrical_component import ElectricalComponent


@enum.unique
class BatteryType(enum.Enum):
    """The known types of batteries."""

    UNSPECIFIED = electrical_components_pb2.BATTERY_TYPE_UNSPECIFIED
    """The battery type is unspecified."""

    LI_ION = electrical_components_pb2.BATTERY_TYPE_LI_ION
    """Lithium-ion (Li-ion) battery."""

    NA_ION = electrical_components_pb2.BATTERY_TYPE_NA_ION
    """Sodium-ion (Na-ion) battery."""


@dataclasses.dataclass(frozen=True, kw_only=True)
class Battery(ElectricalComponent):
    """An abstract battery component."""

    category: Literal[ElectricalComponentCategory.BATTERY] = (
        ElectricalComponentCategory.BATTERY
    )
    """The category of this component.

    Note:
        This should not be used normally, you should test if a component
        [`isinstance`][] of a concrete component class instead.

        It is only provided for using with a newer version of the API where the client
        doesn't know about a new category yet (i.e. for use with
        [`UnrecognizedComponent`][frequenz.client.assets.electrical_component.UnrecognizedComponent])
        and in case some low level code needs to know the category of a component.
    """

    type: BatteryType | int
    """The type of this battery.

    Note:
        This should not be used normally, you should test if a battery
        [`isinstance`][] of a concrete battery class instead.

        It is only provided for using with a newer version of the API where the client
        doesn't know about the new battery type yet (i.e. for use with
        [`UnrecognizedBattery`][frequenz.client.assets.electrical_component.UnrecognizedBattery]).
    """

    # pylint: disable-next=unused-argument
    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        """Prevent instantiation of this class."""
        if cls is Battery:
            raise TypeError(f"Cannot instantiate {cls.__name__} directly")
        return super().__new__(cls)


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnspecifiedBattery(Battery):
    """A battery of a unspecified type."""

    type: Literal[BatteryType.UNSPECIFIED] = BatteryType.UNSPECIFIED
    """The type of this battery.

    Note:
        This should not be used normally, you should test if a battery
        [`isinstance`][] of a concrete battery class instead.

        It is only provided for using with a newer version of the API where the client
        doesn't know about the new battery type yet (i.e. for use with
        [`UnrecognizedBattery`][frequenz.client.assets.electrical_component.UnrecognizedBattery]).
    """


@dataclasses.dataclass(frozen=True, kw_only=True)
class LiIonBattery(Battery):
    """A Li-ion battery."""

    type: Literal[BatteryType.LI_ION] = BatteryType.LI_ION
    """The type of this battery.

    Note:
        This should not be used normally, you should test if a battery
        [`isinstance`][] of a concrete battery class instead.

        It is only provided for using with a newer version of the API where the client
        doesn't know about the new battery type yet (i.e. for use with
        [`UnrecognizedBattery`][frequenz.client.assets.electrical_component.UnrecognizedBattery]).
    """


@dataclasses.dataclass(frozen=True, kw_only=True)
class NaIonBattery(Battery):
    """A Na-ion battery."""

    type: Literal[BatteryType.NA_ION] = BatteryType.NA_ION
    """The type of this battery.

    Note:
        This should not be used normally, you should test if a battery
        [`isinstance`][] of a concrete battery class instead.

        It is only provided for using with a newer version of the API where the client
        doesn't know about the new battery type yet (i.e. for use with
        [`UnrecognizedBattery`][frequenz.client.assets.electrical_component.UnrecognizedBattery]).
    """


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnrecognizedBattery(Battery):
    """A battery of an unrecognized type."""

    type: int
    """The unrecognized type of this battery."""


BatteryTypes: TypeAlias = (
    LiIonBattery | NaIonBattery | UnrecognizedBattery | UnspecifiedBattery
)
"""All possible battery types."""
