"""Electrical component types."""

import dataclasses
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Self

from frequenz.client.common.microgrid import MicrogridId
from frequenz.client.common.microgrid.electrical_components import ElectricalComponentId

from frequenz.client.assets.electrical_component._category import (
    ElectricalComponentCategory,
)
from frequenz.client.assets.metrics._bounds import Bounds
from frequenz.client.assets.metrics._metric import Metric

from .._lifetime import Lifetime


@dataclass(frozen=True, kw_only=True)
class ElectricalComponent:  # pylint: disable=too-many-instance-attributes
    """A wrapper class for the protobuf ElectricalComponent message.

    An electrical component is a physical device that can be used to generate or consume
    electricity.
    """

    id: ElectricalComponentId
    """Unique identifier for the electrical component."""

    microgrid_id: MicrogridId
    """Unique identifier for the microgrid that the electrical component belongs to."""

    name: str | None = None
    """Human-readable name for the electrical component."""

    category: ElectricalComponentCategory | int
    """The component category. E.g., Inverter, Battery, etc."""

    manufacturer: str | None = None
    """The manufacturer of the electrical component."""

    model_name: str | None = None
    """The model name of the electrical component."""

    operational_lifetime: Lifetime = dataclasses.field(default_factory=Lifetime)
    """The operational lifetime of the electrical component."""

    rated_bounds: Mapping[Metric | int, Bounds] = dataclasses.field(
        default_factory=dict,
        # dict is not hashable, so we don't use this field to calculate the hash. This
        # shouldn't be a problem since it is very unlikely that two components with all
        # other attributes being equal would have different category specific metadata,
        # so hash collisions should be still very unlikely.
        hash=False,
    )
    """List of rated bounds present for the component identified by Metric."""

    def __new__(cls, *_: Any, **__: Any) -> Self:
        """Prevent instantiation of this class."""
        if cls is ElectricalComponent:
            raise TypeError(f"Cannot instantiate {cls.__name__} directly")
        return super().__new__(cls)

    @property
    def identity(self) -> tuple[ElectricalComponentId, MicrogridId]:
        """The identity of this component.

        This uses the electrical component ID and microgrid ID to identify a component
        without considering the other attributes, so even if a component state
        changed, the identity remains the same.
        """
        return (self.id, self.microgrid_id)

    def __str__(self) -> str:
        """Return the ID of this electrical component as a string."""
        name = f":{self.name}" if self.name else ""
        return f"{self.id}{name}"
