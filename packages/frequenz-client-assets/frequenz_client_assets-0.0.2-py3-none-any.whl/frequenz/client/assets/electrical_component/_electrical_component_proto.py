# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Electrical component proto."""

import logging
from collections.abc import Sequence
from typing import NamedTuple, assert_never

from frequenz.api.common.v1alpha8.microgrid.electrical_components import (
    electrical_components_pb2,
)
from frequenz.client.common import enum_proto
from frequenz.client.common.microgrid import MicrogridId
from frequenz.client.common.microgrid.electrical_components import ElectricalComponentId

from .._lifetime import Lifetime
from .._lifetime_proto import lifetime_from_proto
from ..metrics._bounds import Bounds
from ..metrics._bounds_proto import bounds_from_proto
from ..metrics._metric import Metric
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
from ._problematic import UnrecognizedComponent, UnspecifiedComponent
from ._static_transfer_switch import StaticTransferSwitch
from ._types import ElectricalComponentType
from ._uninterruptible_power_supply import UninterruptiblePowerSupply
from ._wind_turbine import WindTurbine

_logger = logging.getLogger(__name__)


def electrical_component_proto(
    message: electrical_components_pb2.ElectricalComponent,
) -> ElectricalComponentType:
    """Convert a protobuf message to a `Component` instance.

    Args:
        message: The protobuf message.

    Returns:
        The resulting `ElectricalComponent` instance.
    """
    major_issues: list[str] = []
    minor_issues: list[str] = []

    component = electrical_component_from_proto_with_issues(
        message,
        major_issues=major_issues,
        minor_issues=minor_issues,
    )

    if major_issues:
        _logger.warning(
            "Found issues in component: %s | Protobuf message:\n%s",
            ", ".join(major_issues),
            message,
        )
    if minor_issues:
        _logger.debug(
            "Found minor issues in component: %s | Protobuf message:\n%s",
            ", ".join(minor_issues),
            message,
        )

    return component


class ElectricalComponentBaseData(NamedTuple):
    """Base data for a component, extracted from a protobuf message."""

    component_id: ElectricalComponentId
    microgrid_id: MicrogridId
    name: str | None
    manufacturer: str | None
    model_name: str | None
    category: ElectricalComponentCategory | int
    lifetime: Lifetime
    rated_bounds: dict[Metric | int, Bounds]


def component_base_from_proto_with_issues(
    message: electrical_components_pb2.ElectricalComponent,
    *,
    major_issues: list[str],
    minor_issues: list[str],
) -> ElectricalComponentBaseData:
    """Extract base data from a protobuf message and collect issues.

    Args:
        message: The protobuf message.
        major_issues: A list to append major issues to.
        minor_issues: A list to append minor issues to.

    Returns:
        A `ElectricalComponentBaseData` named tuple containing the extracted data.
    """
    component_id = ElectricalComponentId(message.id)
    microgrid_id = MicrogridId(message.microgrid_id)

    name = message.name or None
    if name is None:
        minor_issues.append("name is empty")

    manufacturer = message.manufacturer or None
    if manufacturer is None:
        minor_issues.append("manufacturer is empty")

    model_name = message.model_name or None
    if model_name is None:
        minor_issues.append("model_name is empty")

    lifetime = _get_operational_lifetime_from_proto(
        message, major_issues=major_issues, minor_issues=minor_issues
    )

    rated_bounds = _metric_config_bounds_from_proto(
        message.metric_config_bounds,
        major_issues=major_issues,
        minor_issues=minor_issues,
    )

    category = enum_proto.enum_from_proto(message.category, ElectricalComponentCategory)
    if category is ElectricalComponentCategory.UNSPECIFIED:
        major_issues.append("category is unspecified")
    elif isinstance(category, int):
        major_issues.append(f"category {category} is unrecognized")

    return ElectricalComponentBaseData(
        component_id,
        microgrid_id,
        name,
        manufacturer,
        model_name,
        category,
        lifetime,
        rated_bounds,
    )


def electrical_component_from_proto_with_issues(
    message: electrical_components_pb2.ElectricalComponent,
    *,
    major_issues: list[str],
    minor_issues: list[str],
) -> ElectricalComponentType:
    """Convert a protobuf message to a `ElectricalComponent` instance and collect issues.

    Args:
        message: The protobuf message.
        major_issues: A list to append major issues to.
        minor_issues: A list to append minor issues to.

    Returns:
        The resulting `ElectricalComponent` instance.
    """
    base_data = component_base_from_proto_with_issues(
        message, major_issues=major_issues, minor_issues=minor_issues
    )

    match base_data.category:
        case int():
            return UnrecognizedComponent(
                id=base_data.component_id,
                microgrid_id=base_data.microgrid_id,
                name=base_data.name,
                manufacturer=base_data.manufacturer,
                model_name=base_data.model_name,
                category=base_data.category,
                operational_lifetime=base_data.lifetime,
                rated_bounds=base_data.rated_bounds,
            )
        case (
            ElectricalComponentCategory.UNSPECIFIED
            | ElectricalComponentCategory.CHP
            | ElectricalComponentCategory.CONVERTER
            | ElectricalComponentCategory.CRYPTO_MINER
            | ElectricalComponentCategory.ELECTROLYZER
            | ElectricalComponentCategory.HVAC
            | ElectricalComponentCategory.METER
            | ElectricalComponentCategory.PRECHARGER
            | ElectricalComponentCategory.BREAKER
            | ElectricalComponentCategory.PLC
            | ElectricalComponentCategory.STATIC_TRANSFER_SWITCH
            | ElectricalComponentCategory.UNINTERRUPTIBLE_POWER_SUPPLY
            | ElectricalComponentCategory.CAPACITOR_BANK
            | ElectricalComponentCategory.WIND_TURBINE
        ):
            return _trivial_category_to_class(base_data.category)(
                id=base_data.component_id,
                microgrid_id=base_data.microgrid_id,
                name=base_data.name,
                manufacturer=base_data.manufacturer,
                model_name=base_data.model_name,
                operational_lifetime=base_data.lifetime,
                rated_bounds=base_data.rated_bounds,
            )
        case ElectricalComponentCategory.BATTERY:
            battery_enum_to_class: dict[
                BatteryType, type[UnspecifiedBattery | LiIonBattery | NaIonBattery]
            ] = {
                BatteryType.UNSPECIFIED: UnspecifiedBattery,
                BatteryType.LI_ION: LiIonBattery,
                BatteryType.NA_ION: NaIonBattery,
            }
            battery_type = enum_proto.enum_from_proto(
                message.category_specific_info.battery.type, BatteryType
            )
            match battery_type:
                case BatteryType.UNSPECIFIED | BatteryType.LI_ION | BatteryType.NA_ION:
                    if battery_type is BatteryType.UNSPECIFIED:
                        major_issues.append("battery type is unspecified")
                    return battery_enum_to_class[battery_type](
                        id=base_data.component_id,
                        microgrid_id=base_data.microgrid_id,
                        name=base_data.name,
                        manufacturer=base_data.manufacturer,
                        model_name=base_data.model_name,
                        operational_lifetime=base_data.lifetime,
                        rated_bounds=base_data.rated_bounds,
                    )
                case int():
                    major_issues.append(f"battery type {battery_type} is unrecognized")
                    return UnrecognizedBattery(
                        id=base_data.component_id,
                        microgrid_id=base_data.microgrid_id,
                        name=base_data.name,
                        manufacturer=base_data.manufacturer,
                        model_name=base_data.model_name,
                        operational_lifetime=base_data.lifetime,
                        type=battery_type,
                        rated_bounds=base_data.rated_bounds,
                    )
                case unexpected_battery_type:
                    assert_never(unexpected_battery_type)
        case ElectricalComponentCategory.EV_CHARGER:
            ev_charger_enum_to_class: dict[
                EvChargerType,
                type[
                    UnspecifiedEvCharger | AcEvCharger | DcEvCharger | HybridEvCharger
                ],
            ] = {
                EvChargerType.UNSPECIFIED: UnspecifiedEvCharger,
                EvChargerType.AC: AcEvCharger,
                EvChargerType.DC: DcEvCharger,
                EvChargerType.HYBRID: HybridEvCharger,
            }
            ev_charger_type = enum_proto.enum_from_proto(
                message.category_specific_info.ev_charger.type, EvChargerType
            )
            match ev_charger_type:
                case (
                    EvChargerType.UNSPECIFIED
                    | EvChargerType.AC
                    | EvChargerType.DC
                    | EvChargerType.HYBRID
                ):
                    if ev_charger_type is EvChargerType.UNSPECIFIED:
                        major_issues.append("ev_charger type is unspecified")
                    return ev_charger_enum_to_class[ev_charger_type](
                        id=base_data.component_id,
                        microgrid_id=base_data.microgrid_id,
                        name=base_data.name,
                        manufacturer=base_data.manufacturer,
                        model_name=base_data.model_name,
                        operational_lifetime=base_data.lifetime,
                        rated_bounds=base_data.rated_bounds,
                    )
                case int():
                    major_issues.append(
                        f"ev_charger type {ev_charger_type} is unrecognized"
                    )
                    return UnrecognizedEvCharger(
                        id=base_data.component_id,
                        microgrid_id=base_data.microgrid_id,
                        name=base_data.name,
                        manufacturer=base_data.manufacturer,
                        model_name=base_data.model_name,
                        operational_lifetime=base_data.lifetime,
                        type=ev_charger_type,
                        rated_bounds=base_data.rated_bounds,
                    )
                case unexpected_ev_charger_type:
                    assert_never(unexpected_ev_charger_type)
        case ElectricalComponentCategory.INVERTER:
            inverter_enum_to_class: dict[
                InverterType,
                type[
                    UnspecifiedInverter | BatteryInverter | PvInverter | HybridInverter
                ],
            ] = {
                InverterType.UNSPECIFIED: UnspecifiedInverter,
                InverterType.BATTERY: BatteryInverter,
                InverterType.PV: PvInverter,
                InverterType.HYBRID: HybridInverter,
            }
            inverter_type = enum_proto.enum_from_proto(
                message.category_specific_info.inverter.type, InverterType
            )
            match inverter_type:
                case (
                    InverterType.UNSPECIFIED
                    | InverterType.BATTERY
                    | InverterType.PV
                    | InverterType.HYBRID
                ):
                    if inverter_type is InverterType.UNSPECIFIED:
                        major_issues.append("inverter type is unspecified")
                    return inverter_enum_to_class[inverter_type](
                        id=base_data.component_id,
                        microgrid_id=base_data.microgrid_id,
                        name=base_data.name,
                        manufacturer=base_data.manufacturer,
                        model_name=base_data.model_name,
                        operational_lifetime=base_data.lifetime,
                        rated_bounds=base_data.rated_bounds,
                    )
                case int():
                    major_issues.append(
                        f"inverter type {inverter_type} is unrecognized"
                    )
                    return UnrecognizedInverter(
                        id=base_data.component_id,
                        microgrid_id=base_data.microgrid_id,
                        name=base_data.name,
                        manufacturer=base_data.manufacturer,
                        model_name=base_data.model_name,
                        operational_lifetime=base_data.lifetime,
                        rated_bounds=base_data.rated_bounds,
                        type=inverter_type,
                    )
                case unexpected_inverter_type:
                    assert_never(unexpected_inverter_type)
        case ElectricalComponentCategory.GRID:
            rated_fuse_current = (
                message.category_specific_info.grid_connection_point.rated_fuse_current
            )
            # No need to check for negatives because the protobuf type is uint32.
            return GridConnectionPoint(
                id=base_data.component_id,
                microgrid_id=base_data.microgrid_id,
                name=base_data.name,
                manufacturer=base_data.manufacturer,
                model_name=base_data.model_name,
                operational_lifetime=base_data.lifetime,
                rated_bounds=base_data.rated_bounds,
                rated_fuse_current=rated_fuse_current,
            )
        case ElectricalComponentCategory.POWER_TRANSFORMER:
            return PowerTransformer(
                id=base_data.component_id,
                microgrid_id=base_data.microgrid_id,
                name=base_data.name,
                manufacturer=base_data.manufacturer,
                model_name=base_data.model_name,
                operational_lifetime=base_data.lifetime,
                rated_bounds=base_data.rated_bounds,
                primary_power=message.category_specific_info.power_transformer.primary,
                secondary_power=message.category_specific_info.power_transformer.secondary,
            )
        case unexpected_category:
            assert_never(unexpected_category)


def _trivial_category_to_class(
    category: ElectricalComponentCategory,
) -> type[
    UnspecifiedComponent
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
]:
    """Return the class corresponding to a trivial component category."""
    return {
        ElectricalComponentCategory.UNSPECIFIED: UnspecifiedComponent,
        ElectricalComponentCategory.CHP: Chp,
        ElectricalComponentCategory.CONVERTER: Converter,
        ElectricalComponentCategory.CRYPTO_MINER: CryptoMiner,
        ElectricalComponentCategory.ELECTROLYZER: Electrolyzer,
        ElectricalComponentCategory.HVAC: Hvac,
        ElectricalComponentCategory.METER: Meter,
        ElectricalComponentCategory.PRECHARGER: Precharger,
        ElectricalComponentCategory.BREAKER: Breaker,
        ElectricalComponentCategory.PLC: Plc,
        ElectricalComponentCategory.STATIC_TRANSFER_SWITCH: StaticTransferSwitch,
        ElectricalComponentCategory.UNINTERRUPTIBLE_POWER_SUPPLY: UninterruptiblePowerSupply,
        ElectricalComponentCategory.CAPACITOR_BANK: CapacitorBank,
        ElectricalComponentCategory.WIND_TURBINE: WindTurbine,
    }[category]


def _metric_config_bounds_from_proto(
    message: Sequence[electrical_components_pb2.MetricConfigBounds],
    *,
    major_issues: list[str],
    minor_issues: list[str],  # pylint: disable=unused-argument
) -> dict[Metric | int, Bounds]:
    """Convert a `MetricConfigBounds` message to a dictionary of `Metric` to `Bounds`.

    Args:
        message: The `MetricConfigBounds` message.
        major_issues: A list to append major issues to.
        minor_issues: A list to append minor issues to.

    Returns:
        The resulting dictionary of `Metric` to `Bounds`.
    """
    bounds: dict[Metric | int, Bounds] = {}
    for metric_bound in message:
        metric = enum_proto.enum_from_proto(metric_bound.metric, Metric)
        match metric:
            case Metric.UNSPECIFIED:
                major_issues.append("metric_config_bounds has an UNSPECIFIED metric")
            case int():
                minor_issues.append(
                    f"metric_config_bounds has an unrecognized metric {metric}"
                )

        if not metric_bound.HasField("config_bounds"):
            major_issues.append(
                f"metric_config_bounds for {metric} is present but missing "
                "`config_bounds`, considering it unbounded",
            )
            continue

        try:
            bound = bounds_from_proto(metric_bound.config_bounds)
        except ValueError as exc:
            major_issues.append(
                f"metric_config_bounds for {metric} is invalid ({exc}), considering "
                "it as missing (i.e. unbouded)",
            )
            continue
        if metric in bounds:
            major_issues.append(
                f"metric_config_bounds for {metric} is duplicated in the message"
                f"using the last one ({bound})",
            )
        bounds[metric] = bound

    return bounds


def _get_operational_lifetime_from_proto(
    message: electrical_components_pb2.ElectricalComponent,
    *,
    major_issues: list[str],
    minor_issues: list[str],
) -> Lifetime:
    """Get the operational lifetime from a protobuf message."""
    if message.HasField("operational_lifetime"):
        try:
            return lifetime_from_proto(message.operational_lifetime)
        except ValueError as exc:
            major_issues.append(
                f"invalid operational lifetime ({exc}), considering it as missing "
                "(i.e. always operational)",
            )
    else:
        minor_issues.append(
            "missing operational lifetime, considering it always operational",
        )
    return Lifetime()
