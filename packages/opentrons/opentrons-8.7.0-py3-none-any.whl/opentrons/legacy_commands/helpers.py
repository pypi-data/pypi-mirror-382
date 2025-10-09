from typing import List, Union, Sequence

from opentrons.protocol_api.labware import Well, Labware
from opentrons.protocol_api.module_contexts import ModuleContext
from opentrons.protocol_api.disposal_locations import TrashBin, WasteChute
from opentrons.protocol_api._types import OffDeckType
from opentrons.types import Location, DeckLocation


CommandLocation = Union[Location, Well]


def listify(
    location: Union[CommandLocation, List[CommandLocation]]
) -> List[CommandLocation]:
    if isinstance(location, list):
        try:
            return listify(location[0])
        except IndexError:
            # TODO(mc, 2021-10-20): this looks like a bug; should this
            # return an empty list, instead?
            return [location]  # type: ignore[list-item]
    else:
        return [location]


def _stringify_new_loc(loc: CommandLocation) -> str:
    if isinstance(loc, Location):
        if loc.labware.is_empty:
            return str(loc.point)
        else:
            return repr(loc.labware)
    elif isinstance(loc, Well):
        return str(loc)
    else:
        raise TypeError(loc)


def stringify_location(location: Union[CommandLocation, List[CommandLocation]]) -> str:
    loc_str_list = [_stringify_new_loc(loc) for loc in listify(location)]
    return ", ".join(loc_str_list)


def stringify_disposal_location(location: Union[TrashBin, WasteChute]) -> str:
    if isinstance(location, TrashBin):
        return f"Trash Bin on slot {location.location.id}"
    elif isinstance(location, WasteChute):
        return "Waste Chute"


def _group_wells_by_labware(wells: List[Well]) -> List[List[Well]]:
    wells_by_labware: List[List[Well]] = []
    sub_list = []
    active_parent_labware = None
    for well in wells:
        if well.parent == active_parent_labware:
            sub_list.append(well)
        else:
            active_parent_labware = well.parent
            if sub_list:
                wells_by_labware.append(sub_list)
            sub_list = [well]
    if sub_list:
        wells_by_labware.append(sub_list)

    return wells_by_labware


def _stringify_multiple_wells_for_labware(wells: List[Well]) -> str:
    if len(wells) == 0:
        return ""
    elif len(wells) == 1:
        return str(wells[0])
    # TODO(jbl 2025-04-10) this logic can be improved to more intelligently group wells
    elif len(wells) < 9:  # At most we'll print out a full column's worth of well
        return ", ".join([well.well_name for well in wells[:-1]]) + f", {wells[-1]}"
    else:  # Otherwise print the first and last three
        return (
            ", ".join([well.well_name for well in wells[:3]])
            + ", ... "
            + ", ".join([well.well_name for well in wells[-3:-1]])
            + f", {wells[-1]}"
        )


def stringify_well_list(
    wells: Union[Well, Sequence[Well], Sequence[Sequence[Well]]]
) -> str:
    """Takes an arbitrary sequence of wells and returns a string representation of each well, associated by labware."""
    if isinstance(wells, Well):
        well_list = [wells]
    elif len(wells) == 0:
        well_list = []
    elif isinstance(wells, list) and isinstance(wells[0], list):
        well_list = [well for sub_well_list in wells for well in sub_well_list]
    elif isinstance(wells, list):
        well_list = wells
    else:
        return ""

    return "; ".join(
        [
            _stringify_multiple_wells_for_labware(wells_by_labware)
            for wells_by_labware in _group_wells_by_labware(well_list)
        ]
    )


def _stringify_labware_movement_location(
    location: Union[
        DeckLocation, OffDeckType, Labware, ModuleContext, WasteChute, TrashBin
    ]
) -> str:
    if isinstance(location, (int, str)):
        return f"slot {location}"
    elif isinstance(location, OffDeckType):
        return "off-deck"
    elif isinstance(location, Labware):
        return location.name
    elif isinstance(location, ModuleContext):
        return str(location)
    elif isinstance(location, WasteChute):
        return "Waste Chute"
    elif isinstance(location, TrashBin):
        return "Trash Bin " + location.location.name


def stringify_labware_movement_command(
    source_labware: Labware,
    destination: Union[
        DeckLocation, OffDeckType, Labware, ModuleContext, WasteChute, TrashBin
    ],
    use_gripper: bool,
) -> str:
    source_labware_text = _stringify_labware_movement_location(source_labware)
    destination_text = _stringify_labware_movement_location(destination)
    gripper_text = " with gripper" if use_gripper else ""
    return f"Moving {source_labware_text} to {destination_text}{gripper_text}"


def stringify_lid_movement_command(
    source: Union[
        DeckLocation, OffDeckType, Labware, ModuleContext, WasteChute, TrashBin
    ],
    destination: Union[
        DeckLocation, OffDeckType, Labware, ModuleContext, WasteChute, TrashBin
    ],
    use_gripper: bool,
) -> str:
    source_labware_text = _stringify_labware_movement_location(source)
    destination_text = _stringify_labware_movement_location(destination)
    gripper_text = " with gripper" if use_gripper else ""
    return f"Moving lid from {source_labware_text} to {destination_text}{gripper_text}"
