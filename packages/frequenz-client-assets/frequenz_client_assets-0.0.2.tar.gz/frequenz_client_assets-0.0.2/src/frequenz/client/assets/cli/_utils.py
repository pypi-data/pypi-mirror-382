"""Utility functions for the CLI."""

import asyncclick as click

from frequenz.client.assets._microgrid import Microgrid
from frequenz.client.assets._microgrid_json import microgrid_to_json
from frequenz.client.assets.electrical_component._electrical_component import (
    ElectricalComponent,
)
from frequenz.client.assets.electrical_component._electrical_component_json import (
    electrical_components_to_json,
)


def print_microgrid_details(microgrid: Microgrid) -> None:
    """
    Print microgrid details to console in JSON format using custom encoder.

    This function converts the Microgrid instance to JSON using a custom
    encoder and outputs it as formatted JSON to the console. The output is
    designed to be machine-readable and can be piped to tools like jq for
    further processing.

    Args:
        microgrid: The Microgrid instance to print to console.
    """
    click.echo(microgrid_to_json(microgrid))


def print_electrical_components(
    electrical_components: list[ElectricalComponent],
) -> None:
    """
    Print electrical components to console in JSON format using custom encoder.

    This function converts the ElectricalComponent instances to JSON using a custom
    encoder and outputs it as formatted JSON to the console. The output is
    designed to be machine-readable and can be piped to tools like jq for
    further processing.

    Args:
        electrical_components: The list of ElectricalComponent instances to print to console.
    """
    click.echo(electrical_components_to_json(electrical_components))
