"""Structures to represent changes that commands want to make to engine state."""

from __future__ import annotations

import dataclasses
import enum
import typing
from typing_extensions import Self, Optional
from datetime import datetime

from opentrons.hardware_control.nozzle_manager import NozzleMap
from opentrons.protocol_engine.resources import pipette_data_provider
from opentrons.protocol_engine.types import (
    DeckPoint,
    LabwareLocation,
    OnLabwareLocation,
    TipGeometry,
    AspiratedFluid,
    LiquidClassRecord,
    ABSMeasureMode,
    LiquidTrackingType,
    StackerStoredLabwareGroup,
    ModuleModel,
    ModuleDefinition,
    LabwareWellId,
)
from opentrons.types import MountType, DeckSlotName
from opentrons_shared_data.labware.labware_definition import LabwareDefinition
from opentrons_shared_data.pipette.types import PipetteNameType


class _NoChangeEnum(enum.Enum):
    NO_CHANGE = enum.auto()


NO_CHANGE: typing.Final = _NoChangeEnum.NO_CHANGE
"""A sentinel value to indicate that a value shouldn't be changed.

Useful when `None` is semantically unclear or already has some other meaning.
"""


NoChangeType: typing.TypeAlias = typing.Literal[_NoChangeEnum.NO_CHANGE]
"""The type of `NO_CHANGE`, as `NoneType` is to `None`.

Unfortunately, mypy doesn't let us write `Literal[NO_CHANGE]`. Use this instead.
"""


class _ClearEnum(enum.Enum):
    CLEAR = enum.auto()


CLEAR: typing.Final = _ClearEnum.CLEAR
"""A sentinel value to indicate that a value should be cleared.

Useful when `None` is semantically unclear or has some other meaning.
"""


ClearType: typing.TypeAlias = typing.Literal[_ClearEnum.CLEAR]
"""The type of `CLEAR`, as `NoneType` is to `None`.

Unfortunately, mypy doesn't let us write `Literal[CLEAR]`. Use this instead.
"""


@dataclasses.dataclass(frozen=True)
class AddressableArea:
    """Designates an addressable area."""

    addressable_area_name: str


@dataclasses.dataclass
class PipetteLocationUpdate:
    """An update to a pipette's location."""

    pipette_id: str
    """The ID of the already-loaded pipette."""

    new_location: LabwareWellId | AddressableArea | None | NoChangeType
    """The pipette's new logical location.

    Note: `new_location=None` means "change the location to `None` (unknown)",
    not "do not change the location".
    """

    new_deck_point: DeckPoint | NoChangeType


@dataclasses.dataclass
class LabwareLocationUpdate:
    """An update to a labware's location."""

    labware_id: str
    """The ID of the already-loaded labware."""

    new_location: LabwareLocation
    """The labware's new location."""

    offset_id: str | None
    """The ID of the labware's new offset, for its new location."""


@dataclasses.dataclass
class BatchLabwareLocationUpdate:
    """An update to the locations of multiple labware."""

    new_locations_by_id: dict[str, LabwareLocation]
    """The new locations of each ID."""
    new_offset_ids_by_id: dict[str, str | None]
    """The new offsets of each id."""


# todo(mm, 2025-04-28): Combine with BatchLoadedLabwareUpdate.
@dataclasses.dataclass
class LoadedLabwareUpdate:
    """An update that loads a new labware."""

    labware_id: str
    """The unique ID of the new labware."""

    new_location: LabwareLocation
    """The labware's initial location."""

    offset_id: str | None
    """The ID of the labware's offset."""

    display_name: str | None

    definition: LabwareDefinition


@dataclasses.dataclass
class BatchLoadedLabwareUpdate:
    """An update that loads multiple new labware."""

    new_locations_by_id: typing.Dict[str, LabwareLocation]
    """Each new labwares's initial location keyed by Labware ID."""

    offset_ids_by_id: typing.Dict[str, str | None]
    """The ID of each labware's offset keyed by labware ID."""

    display_names_by_id: typing.Dict[str, str | None]
    """The Display Name for each new labware keyed by labware ID"""

    definitions_by_id: typing.Dict[str, LabwareDefinition]
    """The Labware Definition for each labware keyed by Labware ID."""


@dataclasses.dataclass
class LoadedLidStackUpdate:
    """An update that loads a new lid stack."""

    stack_id: str
    """The unique ID of the Lid Stack Object."""

    stack_object_definition: LabwareDefinition
    "The System-only Labware Definition of the Lid Stack Object"

    stack_location: LabwareLocation
    "The initial location of the Lid Stack Object."

    new_locations_by_id: typing.Dict[str, OnLabwareLocation]
    """Each lid's initial location keyed by Labware ID."""

    definition: LabwareDefinition | None
    "The Labware Definition of the Lid Labware(s) loaded."


@dataclasses.dataclass
class LabwareLidUpdate:
    """An update that identifies a lid on a given parent labware."""

    parent_labware_ids: typing.List[str]
    """The unique IDs of the parent labwares."""

    lid_ids: typing.List[str | None]
    """The unique IDs of the new lids."""


@dataclasses.dataclass
class LoadPipetteUpdate:
    """An update that loads a new pipette.

    NOTE: Currently, if this is provided, a PipetteConfigUpdate must always be
    provided alongside it to fully initialize everything.
    """

    pipette_id: str
    """The unique ID of the new pipette."""

    pipette_name: PipetteNameType
    mount: MountType
    liquid_presence_detection: bool | None


@dataclasses.dataclass
class PipetteConfigUpdate:
    """An update to a pipette's config."""

    pipette_id: str
    """The ID of the already-loaded pipette."""

    # todo(mm, 2024-10-14): Does serial_number belong in LoadPipetteUpdate?
    serial_number: str

    config: pipette_data_provider.LoadedStaticPipetteData


@dataclasses.dataclass
class PipetteNozzleMapUpdate:
    """Update pipette nozzle map."""

    pipette_id: str
    nozzle_map: NozzleMap


@dataclasses.dataclass
class PipetteTipStateUpdate:
    """Update pipette tip state."""

    pipette_id: str
    tip_geometry: TipGeometry | None
    tip_source: LabwareWellId | None


@dataclasses.dataclass
class PipetteAspirateReadyUpdate:
    """Update pipette ready state."""

    pipette_id: str
    ready_to_aspirate: bool


@dataclasses.dataclass
class TipsUsedUpdate:
    """Represents an update that marks tips in a tip rack as used."""

    labware_id: str
    """The labware ID of the tip rack."""

    well_names: list[str]
    """The exact wells in the tip rack that should be marked as used.

    This is the *full* list, which is probably more than what appeared in the pickUpTip
    command's params, for multi-channel reasons.
    """


@dataclasses.dataclass
class LiquidLoadedUpdate:
    """An update from loading a liquid."""

    labware_id: str
    volumes: typing.Dict[str, float]
    last_loaded: datetime


@dataclasses.dataclass
class LiquidProbedUpdate:
    """An update from probing a liquid."""

    labware_id: str
    well_name: str
    last_probed: datetime
    height: LiquidTrackingType | ClearType
    volume: LiquidTrackingType | ClearType


@dataclasses.dataclass
class LiquidOperatedUpdate:
    """An update from operating a liquid."""

    labware_id: str
    well_names: list[str]
    volume_added: float | ClearType


@dataclasses.dataclass
class PipetteAspiratedFluidUpdate:
    """Represents the pipette aspirating something. Might be air or liquid from a well."""

    pipette_id: str
    fluid: AspiratedFluid
    type: typing.Literal["aspirated"] = "aspirated"


@dataclasses.dataclass
class PipetteEjectedFluidUpdate:
    """Represents the pipette pushing something out. Might be air or liquid."""

    pipette_id: str
    volume: float
    type: typing.Literal["ejected"] = "ejected"


@dataclasses.dataclass
class PipetteUnknownFluidUpdate:
    """Represents the amount of fluid in the pipette becoming unknown."""

    pipette_id: str
    type: typing.Literal["unknown"] = "unknown"


@dataclasses.dataclass
class PipetteEmptyFluidUpdate:
    """Sets the pipette to be valid and empty."""

    pipette_id: str
    clean_tip: bool
    type: typing.Literal["empty"] = "empty"


@dataclasses.dataclass
class AbsorbanceReaderLidUpdate:
    """An update to an absorbance reader's lid location."""

    is_lid_on: bool


@dataclasses.dataclass
class AbsorbanceReaderDataUpdate:
    """An update to an absorbance reader's lid location."""

    read_result: typing.Dict[int, typing.Dict[str, float]]


@dataclasses.dataclass(frozen=True)
class AbsorbanceReaderInitializeUpdate:
    """An update to an absorbance reader's initialization."""

    measure_mode: ABSMeasureMode
    sample_wave_lengths: typing.List[int]
    reference_wave_length: typing.Optional[int]


@dataclasses.dataclass
class AbsorbanceReaderStateUpdate:
    """An update to the absorbance reader module state."""

    module_id: str
    absorbance_reader_lid: AbsorbanceReaderLidUpdate | NoChangeType = NO_CHANGE
    absorbance_reader_data: AbsorbanceReaderDataUpdate | NoChangeType = NO_CHANGE
    initialize_absorbance_reader_update: (
        AbsorbanceReaderInitializeUpdate | NoChangeType
    ) = NO_CHANGE


@dataclasses.dataclass
class FlexStackerPoolConstraint:
    """The labware definitions that are contained in the pool."""

    max_pool_count: int
    pool_overlap: float
    pool_height: float
    primary_definition: LabwareDefinition
    lid_definition: LabwareDefinition | None
    adapter_definition: LabwareDefinition | None


@dataclasses.dataclass
class FlexStackerStateUpdate:
    """An update to the Flex Stacker module state."""

    module_id: str
    pool_constraint: FlexStackerPoolConstraint | NoChangeType = NO_CHANGE
    contained_labware_bottom_first: list[
        StackerStoredLabwareGroup
    ] | NoChangeType = NO_CHANGE

    @classmethod
    def create_or_override(
        cls,
        maybe_inst: FlexStackerStateUpdate | NoChangeType,
        module_id: str,
    ) -> FlexStackerStateUpdate:
        """Build or default a state update."""
        if maybe_inst == NO_CHANGE:
            return FlexStackerStateUpdate(module_id=module_id)
        else:
            return maybe_inst


@dataclasses.dataclass
class LiquidClassLoadedUpdate:
    """The state update from loading a liquid class."""

    liquid_class_id: str
    liquid_class_record: LiquidClassRecord


@dataclasses.dataclass
class FilesAddedUpdate:
    """An update that adds a new data file."""

    file_ids: list[str]


@dataclasses.dataclass
class AddressableAreaUsedUpdate:
    """An update that says an addressable area has been used."""

    addressable_area_name: str


@dataclasses.dataclass
class LoadModuleUpdate:
    """An update that loads a module."""

    module_id: str
    definition: ModuleDefinition
    slot_name: DeckSlotName
    requested_model: ModuleModel
    serial_number: Optional[str]


@dataclasses.dataclass
class StateUpdate:
    """Represents an update to perform on engine state."""

    pipette_location: PipetteLocationUpdate | NoChangeType | ClearType = NO_CHANGE

    loaded_pipette: LoadPipetteUpdate | NoChangeType = NO_CHANGE

    loaded_module: LoadModuleUpdate | NoChangeType = NO_CHANGE

    pipette_config: PipetteConfigUpdate | NoChangeType = NO_CHANGE

    pipette_nozzle_map: PipetteNozzleMapUpdate | NoChangeType = NO_CHANGE

    pipette_tip_state: PipetteTipStateUpdate | NoChangeType = NO_CHANGE

    pipette_aspirated_fluid: (
        PipetteAspiratedFluidUpdate
        | PipetteEjectedFluidUpdate
        | PipetteUnknownFluidUpdate
        | PipetteEmptyFluidUpdate
        | NoChangeType
    ) = NO_CHANGE

    labware_location: LabwareLocationUpdate | NoChangeType = NO_CHANGE

    batch_labware_location: BatchLabwareLocationUpdate | NoChangeType = NO_CHANGE

    loaded_labware: LoadedLabwareUpdate | NoChangeType = NO_CHANGE

    batch_loaded_labware: BatchLoadedLabwareUpdate | NoChangeType = NO_CHANGE

    loaded_lid_stack: LoadedLidStackUpdate | NoChangeType = NO_CHANGE

    labware_lid: LabwareLidUpdate | NoChangeType = NO_CHANGE

    tips_used: TipsUsedUpdate | NoChangeType = NO_CHANGE

    liquid_loaded: LiquidLoadedUpdate | NoChangeType = NO_CHANGE

    liquid_probed: LiquidProbedUpdate | NoChangeType = NO_CHANGE

    liquid_operated: LiquidOperatedUpdate | NoChangeType = NO_CHANGE

    absorbance_reader_state_update: AbsorbanceReaderStateUpdate | NoChangeType = (
        NO_CHANGE
    )

    flex_stacker_state_update: FlexStackerStateUpdate | NoChangeType = NO_CHANGE

    liquid_class_loaded: LiquidClassLoadedUpdate | NoChangeType = NO_CHANGE

    files_added: FilesAddedUpdate | NoChangeType = NO_CHANGE

    addressable_area_used: AddressableAreaUsedUpdate | NoChangeType = NO_CHANGE

    ready_to_aspirate: PipetteAspirateReadyUpdate | NoChangeType = NO_CHANGE

    def append(self, other: Self) -> Self:
        """Apply another `StateUpdate` "on top of" this one.

        This object is mutated in-place, taking values from `other`.
        If an attribute in `other` is `NO_CHANGE`, the value in this object is kept.
        """
        fields = dataclasses.fields(other)
        for field in fields:
            other_value = other.__dict__[field.name]
            if other_value != NO_CHANGE:
                self.__dict__[field.name] = other_value
        return self

    @classmethod
    def reduce(cls: typing.Type[Self], *args: Self) -> Self:
        """Fuse multiple state updates into a single one.

        State updates that are later in the parameter list are preferred to those that are earlier;
        NO_CHANGE is ignored.
        """
        accumulator = cls()
        for arg in args:
            accumulator.append(arg)
        return accumulator

    # These convenience functions let the caller avoid the boilerplate of constructing a
    # complicated dataclass tree, and allow chaining.

    @typing.overload
    def set_pipette_location(
        self: Self, *, pipette_id: str, new_deck_point: DeckPoint
    ) -> Self:
        """Schedule a pipette's coordinates to be changed while preserving its logical location."""

    @typing.overload
    def set_pipette_location(
        self: Self,
        *,
        pipette_id: str,
        new_labware_id: str,
        new_well_name: str,
        new_deck_point: DeckPoint,
    ) -> Self:
        """Schedule a pipette's location to be set to a well."""

    @typing.overload
    def set_pipette_location(
        self: Self,
        *,
        pipette_id: str,
        new_addressable_area_name: str,
        new_deck_point: DeckPoint,
    ) -> Self:
        """Schedule a pipette's location to be set to an addressable area."""
        pass

    def set_pipette_location(  # noqa: D102
        self: Self,
        *,
        pipette_id: str,
        new_labware_id: str | NoChangeType = NO_CHANGE,
        new_well_name: str | NoChangeType = NO_CHANGE,
        new_addressable_area_name: str | NoChangeType = NO_CHANGE,
        new_deck_point: DeckPoint,
    ) -> Self:
        if new_addressable_area_name != NO_CHANGE:
            self.pipette_location = PipetteLocationUpdate(
                pipette_id=pipette_id,
                new_location=AddressableArea(
                    addressable_area_name=new_addressable_area_name
                ),
                new_deck_point=new_deck_point,
            )
        elif new_labware_id == NO_CHANGE or new_well_name == NO_CHANGE:
            self.pipette_location = PipetteLocationUpdate(
                pipette_id=pipette_id,
                new_location=NO_CHANGE,
                new_deck_point=new_deck_point,
            )
        else:
            self.pipette_location = PipetteLocationUpdate(
                pipette_id=pipette_id,
                new_location=LabwareWellId(
                    labware_id=new_labware_id, well_name=new_well_name
                ),
                new_deck_point=new_deck_point,
            )
        return self

    def clear_all_pipette_locations(self) -> Self:
        """Mark all pipettes as having an unknown location."""
        self.pipette_location = CLEAR
        return self

    def set_labware_location(
        self: Self,
        *,
        labware_id: str,
        new_location: LabwareLocation,
        new_offset_id: str | None,
    ) -> Self:
        """Set a labware's location. See `LabwareLocationUpdate`."""
        self.labware_location = LabwareLocationUpdate(
            labware_id=labware_id,
            new_location=new_location,
            offset_id=new_offset_id,
        )
        return self

    def set_batch_labware_location(
        self: Self,
        *,
        new_locations_by_id: typing.Mapping[str, LabwareLocation],
        new_offset_ids_by_id: typing.Mapping[str, str | None],
    ) -> Self:
        """Update the location of multiple labware objects."""
        self.batch_labware_location = BatchLabwareLocationUpdate(
            new_locations_by_id=dict(new_locations_by_id),
            new_offset_ids_by_id=dict(new_offset_ids_by_id),
        )
        return self

    def set_loaded_labware(
        self: Self,
        definition: LabwareDefinition,
        labware_id: str,
        offset_id: str | None,
        display_name: str | None,
        location: LabwareLocation,
    ) -> Self:
        """Add a new labware to state. See `LoadedLabwareUpdate`."""
        self.loaded_labware = LoadedLabwareUpdate(
            definition=definition,
            labware_id=labware_id,
            offset_id=offset_id,
            new_location=location,
            display_name=display_name,
        )
        return self

    def set_batch_loaded_labware(
        self: Self,
        definitions_by_id: typing.Mapping[str, LabwareDefinition],
        offset_ids_by_id: typing.Mapping[str, str | None],
        display_names_by_id: typing.Mapping[str, str | None],
        new_locations_by_id: typing.Mapping[str, LabwareLocation],
    ) -> Self:
        """Add a set of new labwares to state. See `BatchLoadedLabwareUpdate`."""
        self.batch_loaded_labware = BatchLoadedLabwareUpdate(
            new_locations_by_id=dict(new_locations_by_id),
            offset_ids_by_id=dict(offset_ids_by_id),
            display_names_by_id=dict(display_names_by_id),
            definitions_by_id=dict(definitions_by_id),
        )
        return self

    def set_loaded_lid_stack(
        self: Self,
        stack_id: str,
        stack_object_definition: LabwareDefinition,
        stack_location: LabwareLocation,
        locations: typing.Dict[str, OnLabwareLocation],
        labware_definition: LabwareDefinition | None,
    ) -> Self:
        """Add a new lid stack to state. See `LoadedLidStackUpdate`."""
        self.loaded_lid_stack = LoadedLidStackUpdate(
            stack_id=stack_id,
            stack_object_definition=stack_object_definition,
            stack_location=stack_location,
            definition=labware_definition,
            new_locations_by_id=locations,
        )
        return self

    def set_lids(
        self: Self,
        parent_labware_ids: typing.Sequence[str],
        lid_ids: typing.Sequence[str | None],
    ) -> Self:
        """Update the labware parent of a loaded or moved lid. See `LabwareLidUpdate`."""
        self.labware_lid = LabwareLidUpdate(
            parent_labware_ids=list(parent_labware_ids),
            lid_ids=list(lid_ids),
        )
        return self

    def set_load_pipette(
        self: Self,
        pipette_id: str,
        pipette_name: PipetteNameType,
        mount: MountType,
        liquid_presence_detection: bool | None,
    ) -> Self:
        """Add a new pipette to state. See `LoadPipetteUpdate`."""
        self.loaded_pipette = LoadPipetteUpdate(
            pipette_id=pipette_id,
            pipette_name=pipette_name,
            mount=mount,
            liquid_presence_detection=liquid_presence_detection,
        )
        return self

    def set_load_module(
        self: Self,
        module_id: str,
        definition: ModuleDefinition,
        slot_name: DeckSlotName,
        requested_model: ModuleModel,
        serial_number: Optional[str],
    ) -> Self:
        """Add a new module to state. See `LoadModuleUpdate`."""
        self.loaded_module = LoadModuleUpdate(
            module_id=module_id,
            definition=definition,
            serial_number=serial_number,
            slot_name=slot_name,
            requested_model=requested_model,
        )
        return self

    def update_pipette_config(
        self: Self,
        pipette_id: str,
        config: pipette_data_provider.LoadedStaticPipetteData,
        serial_number: str,
    ) -> Self:
        """Update a pipette's config. See `PipetteConfigUpdate`."""
        self.pipette_config = PipetteConfigUpdate(
            pipette_id=pipette_id, config=config, serial_number=serial_number
        )
        return self

    def update_pipette_nozzle(
        self: Self, pipette_id: str, nozzle_map: NozzleMap
    ) -> Self:
        """Update a pipette's nozzle map. See `PipetteNozzleMapUpdate`."""
        self.pipette_nozzle_map = PipetteNozzleMapUpdate(
            pipette_id=pipette_id, nozzle_map=nozzle_map
        )
        return self

    def update_pipette_tip_state(
        self: Self,
        pipette_id: str,
        tip_geometry: TipGeometry | None,
        tip_source: LabwareWellId | None,
    ) -> Self:
        """Update a pipette's tip state. See `PipetteTipStateUpdate`."""
        self.pipette_tip_state = PipetteTipStateUpdate(
            pipette_id=pipette_id,
            tip_geometry=tip_geometry,
            tip_source=tip_source,
        )
        return self

    def mark_tips_as_used(self: Self, labware_id: str, well_names: list[str]) -> Self:
        """Mark tips in a tip rack as used. See `TipsUsedUpdate`."""
        self.tips_used = TipsUsedUpdate(labware_id=labware_id, well_names=well_names)
        return self

    def set_liquid_loaded(
        self: Self,
        labware_id: str,
        volumes: typing.Dict[str, float],
        last_loaded: datetime,
    ) -> Self:
        """Add liquid volumes to well state. See `LoadLiquidUpdate`."""
        self.liquid_loaded = LiquidLoadedUpdate(
            labware_id=labware_id,
            volumes=volumes,
            last_loaded=last_loaded,
        )
        return self

    def set_liquid_probed(
        self: Self,
        labware_id: str,
        well_name: str,
        last_probed: datetime,
        height: LiquidTrackingType | ClearType,
        volume: LiquidTrackingType | ClearType,
    ) -> Self:
        """Add a liquid height and volume to well state. See `ProbeLiquidUpdate`."""
        self.liquid_probed = LiquidProbedUpdate(
            labware_id=labware_id,
            well_name=well_name,
            height=height,
            volume=volume,
            last_probed=last_probed,
        )
        return self

    def set_liquid_operated(
        self: Self,
        labware_id: str,
        well_names: list[str],
        volume_added: float | ClearType,
    ) -> Self:
        """Update liquid volumes in well state. See `OperateLiquidUpdate`."""
        self.liquid_operated = LiquidOperatedUpdate(
            labware_id=labware_id,
            well_names=well_names,
            volume_added=volume_added,
        )
        return self

    def set_fluid_aspirated(self: Self, pipette_id: str, fluid: AspiratedFluid) -> Self:
        """Update record of fluid held inside a pipette. See `PipetteAspiratedFluidUpdate`."""
        self.pipette_aspirated_fluid = PipetteAspiratedFluidUpdate(
            type="aspirated", pipette_id=pipette_id, fluid=fluid
        )
        return self

    def set_fluid_ejected(self: Self, pipette_id: str, volume: float) -> Self:
        """Update record of fluid held inside a pipette. See `PipetteEjectedFluidUpdate`."""
        self.pipette_aspirated_fluid = PipetteEjectedFluidUpdate(
            type="ejected", pipette_id=pipette_id, volume=volume
        )
        return self

    def set_fluid_unknown(self: Self, pipette_id: str) -> Self:
        """Update record of fluid held inside a pipette. See `PipetteUnknownFluidUpdate`."""
        self.pipette_aspirated_fluid = PipetteUnknownFluidUpdate(
            type="unknown", pipette_id=pipette_id
        )
        return self

    def set_fluid_empty(self: Self, pipette_id: str, clean_tip: bool = False) -> Self:
        """Update record of fluid held inside a pipette. See `PipetteEmptyFluidUpdate`."""
        self.pipette_aspirated_fluid = PipetteEmptyFluidUpdate(
            type="empty", pipette_id=pipette_id, clean_tip=clean_tip
        )
        return self

    def set_absorbance_reader_lid(self: Self, module_id: str, is_lid_on: bool) -> Self:
        """Update an absorbance reader's lid location. See `AbsorbanceReaderLidUpdate`."""
        assert self.absorbance_reader_state_update == NO_CHANGE
        self.absorbance_reader_state_update = AbsorbanceReaderStateUpdate(
            module_id=module_id,
            absorbance_reader_lid=AbsorbanceReaderLidUpdate(is_lid_on=is_lid_on),
        )
        return self

    def set_absorbance_reader_data(
        self, module_id: str, read_result: typing.Dict[int, typing.Dict[str, float]]
    ) -> Self:
        """Update an absorbance reader's read data. See `AbsorbanceReaderReadDataUpdate`."""
        assert self.absorbance_reader_state_update == NO_CHANGE
        self.absorbance_reader_state_update = AbsorbanceReaderStateUpdate(
            module_id=module_id,
            absorbance_reader_data=AbsorbanceReaderDataUpdate(read_result=read_result),
        )
        return self

    def initialize_absorbance_reader(
        self,
        module_id: str,
        measure_mode: ABSMeasureMode,
        sample_wave_lengths: typing.List[int],
        reference_wave_length: typing.Optional[int],
    ) -> Self:
        """Initialize absorbance reader."""
        assert self.absorbance_reader_state_update == NO_CHANGE
        self.absorbance_reader_state_update = AbsorbanceReaderStateUpdate(
            module_id=module_id,
            initialize_absorbance_reader_update=AbsorbanceReaderInitializeUpdate(
                measure_mode=measure_mode,
                sample_wave_lengths=sample_wave_lengths,
                reference_wave_length=reference_wave_length,
            ),
        )
        return self

    def set_addressable_area_used(self: Self, addressable_area_name: str) -> Self:
        """Mark that an addressable area has been used. See `AddressableAreaUsedUpdate`."""
        self.addressable_area_used = AddressableAreaUsedUpdate(
            addressable_area_name=addressable_area_name
        )
        return self

    def update_flex_stacker_labware_pool_definition(
        self,
        module_id: str,
        max_count: int,
        pool_overlap: float,
        pool_height: float,
        primary_definition: LabwareDefinition,
        adapter_definition: LabwareDefinition | None,
        lid_definition: LabwareDefinition | None,
    ) -> Self:
        """Constrain the labware pool to a specific definition."""
        self.flex_stacker_state_update = dataclasses.replace(
            FlexStackerStateUpdate.create_or_override(
                self.flex_stacker_state_update, module_id
            ),
            pool_constraint=FlexStackerPoolConstraint(
                max_pool_count=max_count,
                pool_overlap=pool_overlap,
                pool_height=pool_height,
                primary_definition=primary_definition,
                lid_definition=lid_definition,
                adapter_definition=adapter_definition,
            ),
        )
        return self

    def update_flex_stacker_contained_labware(
        self,
        module_id: str,
        contained_labware_bottom_first: list[StackerStoredLabwareGroup],
    ) -> Self:
        """Set the labware pool to a specific count."""
        self.flex_stacker_state_update = dataclasses.replace(
            FlexStackerStateUpdate.create_or_override(
                self.flex_stacker_state_update, module_id
            ),
            contained_labware_bottom_first=contained_labware_bottom_first,
        )
        return self

    def set_pipette_ready_to_aspirate(
        self, pipette_id: str, ready_to_aspirate: bool
    ) -> Self:
        """Set the ready to aspirate state for a pipette."""
        self.ready_to_aspirate = PipetteAspirateReadyUpdate(
            pipette_id=pipette_id, ready_to_aspirate=ready_to_aspirate
        )
        return self
