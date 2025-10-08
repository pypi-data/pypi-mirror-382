"""Basic labware data state and store."""

from __future__ import annotations

from dataclasses import dataclass
from typing import (
    Any,
    Dict,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    NamedTuple,
    Union,
    overload,
)
from typing_extensions import assert_never

from opentrons.protocol_engine.state import update_types
from opentrons_shared_data.deck.types import DeckDefinitionV5
from opentrons_shared_data.gripper.constants import LABWARE_GRIP_FORCE
from opentrons_shared_data.labware.labware_definition import (
    InnerWellGeometry,
    LabwareDefinition,
    LabwareDefinition2,
    LabwareRole,
    WellDefinition2,
    WellDefinition3,
    UserDefinedVolumes,
)
from opentrons_shared_data.pipette.types import LabwareUri

from opentrons.protocol_engine.state._axis_aligned_bounding_box import (
    AxisAlignedBoundingBox3D,
)
from opentrons.types import DeckSlotName, StagingSlotName, MountType, Point
from opentrons.protocols.api_support.constants import OPENTRONS_NAMESPACE
from opentrons.calibration_storage.helpers import uri_from_details

from .. import errors
from ..resources import DeckFixedLabware, labware_validation, fixture_validation
from ..types import (
    DeckSlotLocation,
    OnLabwareLocation,
    AddressableAreaLocation,
    NonStackedLocation,
    Dimensions,
    GripSpecs,
    LabwareOffset,
    LabwareOffsetVector,
    LabwareOffsetLocationSequence,
    LegacyLabwareOffsetLocation,
    InStackerHopperLocation,
    LabwareLocation,
    LoadedLabware,
    ModuleLocation,
    OverlapOffset,
    LabwareMovementOffsetData,
    OnDeckLabwareLocation,
    OFF_DECK_LOCATION,
)
from ..actions import (
    Action,
    AddLabwareOffsetAction,
    AddLabwareDefinitionAction,
    get_state_updates,
)
from ._abstract_store import HasState, HandlesActions
from ._move_types import EdgePathType


# URIs of labware whose definitions accidentally specify an engage height
# in units of half-millimeters instead of millimeters.
_MAGDECK_HALF_MM_LABWARE = {
    "opentrons/biorad_96_wellplate_200ul_pcr/1",
    "opentrons/nest_96_wellplate_100ul_pcr_full_skirt/1",
    "opentrons/usascientific_96_wellplate_2.4ml_deep/1",
}

_RIGHT_SIDE_SLOTS = {
    # OT-2:
    DeckSlotName.FIXED_TRASH,
    DeckSlotName.SLOT_9,
    DeckSlotName.SLOT_6,
    DeckSlotName.SLOT_3,
    # OT-3:
    DeckSlotName.SLOT_A3,
    DeckSlotName.SLOT_B3,
    DeckSlotName.SLOT_C3,
    DeckSlotName.SLOT_D3,
}


# The max height of the labware that can fit in a plate reader
_PLATE_READER_MAX_LABWARE_Z_MM = 16.0


_WellDefinition = WellDefinition2 | WellDefinition3


class LabwareLoadParams(NamedTuple):
    """Parameters required to load a labware in Protocol Engine."""

    load_name: str
    namespace: str
    version: int


@dataclass
class LabwareState:
    """State of all loaded labware resources."""

    # Indexed by LoadedLabware.id.
    # If a LoadedLabware here has a non-None offsetId,
    # it must point to an existing element of labware_offsets_by_id.
    labware_by_id: Dict[str, LoadedLabware]

    # Indexed by LabwareOffset.id.
    # We rely on Python 3.7+ preservation of dict insertion order.
    labware_offsets_by_id: Dict[str, LabwareOffset]

    definitions_by_uri: Dict[str, LabwareDefinition]
    deck_definition: DeckDefinitionV5


class LabwareStore(HasState[LabwareState], HandlesActions):
    """Labware state container."""

    _state: LabwareState

    def __init__(
        self,
        deck_definition: DeckDefinitionV5,
        deck_fixed_labware: Sequence[DeckFixedLabware],
    ) -> None:
        """Initialize a labware store and its state."""
        definitions_by_uri: Dict[str, LabwareDefinition] = {
            uri_from_details(
                load_name=fixed_labware.definition.parameters.loadName,
                namespace=fixed_labware.definition.namespace,
                version=fixed_labware.definition.version,
            ): fixed_labware.definition
            for fixed_labware in deck_fixed_labware
        }
        labware_by_id = {
            fixed_labware.labware_id: LoadedLabware.model_construct(
                id=fixed_labware.labware_id,
                location=fixed_labware.location,
                loadName=fixed_labware.definition.parameters.loadName,
                definitionUri=uri_from_details(
                    load_name=fixed_labware.definition.parameters.loadName,
                    namespace=fixed_labware.definition.namespace,
                    version=fixed_labware.definition.version,
                ),
                offsetId=None,
            )
            for fixed_labware in deck_fixed_labware
        }

        self._state = LabwareState(
            definitions_by_uri=definitions_by_uri,
            labware_offsets_by_id={},
            labware_by_id=labware_by_id,
            deck_definition=deck_definition,
        )

    def handle_action(self, action: Action) -> None:
        """Modify state in reaction to an action."""
        for state_update in get_state_updates(action):
            self._add_loaded_labware(state_update)
            self._add_batch_loaded_labwares(state_update)
            self._add_loaded_lid_stack(state_update)
            self._set_labware_location(state_update)
            self._set_batch_labware_location(state_update)
            self._set_labware_lid(state_update)

        if isinstance(action, AddLabwareOffsetAction):
            labware_offset = LabwareOffset.model_construct(
                id=action.labware_offset_id,
                createdAt=action.created_at,
                definitionUri=action.request.definitionUri,
                location=action.request.legacyLocation,
                locationSequence=action.request.locationSequence,
                vector=action.request.vector,
            )
            self._add_labware_offset(labware_offset)

        elif isinstance(action, AddLabwareDefinitionAction):
            uri = uri_from_details(
                namespace=action.definition.namespace,
                load_name=action.definition.parameters.loadName,
                version=action.definition.version,
            )
            self._state.definitions_by_uri[uri] = action.definition

    def _add_labware_offset(self, labware_offset: LabwareOffset) -> None:
        """Add a new labware offset to state.

        `labware_offset.id` must not match any existing labware offset ID.
        `LoadLabwareCommand`s retain references to their corresponding labware offsets
        and expect them to be immutable.
        """
        assert labware_offset.id not in self._state.labware_offsets_by_id

        self._state.labware_offsets_by_id[labware_offset.id] = labware_offset

    def _add_loaded_labware(self, state_update: update_types.StateUpdate) -> None:
        loaded_labware_update = state_update.loaded_labware
        if loaded_labware_update != update_types.NO_CHANGE:
            # If the labware load refers to an offset, that offset must actually exist.
            if loaded_labware_update.offset_id is not None:
                assert (
                    loaded_labware_update.offset_id in self._state.labware_offsets_by_id
                )

            definition_uri = uri_from_details(
                namespace=loaded_labware_update.definition.namespace,
                load_name=loaded_labware_update.definition.parameters.loadName,
                version=loaded_labware_update.definition.version,
            )

            self._state.definitions_by_uri[
                definition_uri
            ] = loaded_labware_update.definition

            location = loaded_labware_update.new_location

            display_name = loaded_labware_update.display_name

            self._state.labware_by_id[
                loaded_labware_update.labware_id
            ] = LoadedLabware.model_construct(
                id=loaded_labware_update.labware_id,
                location=location,
                loadName=loaded_labware_update.definition.parameters.loadName,
                definitionUri=definition_uri,
                offsetId=loaded_labware_update.offset_id,
                displayName=display_name,
            )

    def _add_batch_loaded_labwares(
        self, state_update: update_types.StateUpdate
    ) -> None:
        batch_loaded_labware_update = state_update.batch_loaded_labware
        if batch_loaded_labware_update == update_types.NO_CHANGE:
            return
        # If the labware load refers to an offset, that offset must actually exist.
        for labware_id in batch_loaded_labware_update.new_locations_by_id:
            if batch_loaded_labware_update.offset_ids_by_id[labware_id] is not None:
                assert (
                    batch_loaded_labware_update.offset_ids_by_id[labware_id]
                    in self._state.labware_offsets_by_id
                )

            definition_uri = uri_from_details(
                namespace=batch_loaded_labware_update.definitions_by_id[
                    labware_id
                ].namespace,
                load_name=batch_loaded_labware_update.definitions_by_id[
                    labware_id
                ].parameters.loadName,
                version=batch_loaded_labware_update.definitions_by_id[
                    labware_id
                ].version,
            )

            self._state.definitions_by_uri[
                definition_uri
            ] = batch_loaded_labware_update.definitions_by_id[labware_id]

            location = batch_loaded_labware_update.new_locations_by_id[labware_id]

            self._state.labware_by_id[labware_id] = LoadedLabware.model_construct(
                id=labware_id,
                location=location,
                loadName=batch_loaded_labware_update.definitions_by_id[
                    labware_id
                ].parameters.loadName,
                definitionUri=definition_uri,
                offsetId=batch_loaded_labware_update.offset_ids_by_id[labware_id],
                displayName=batch_loaded_labware_update.display_names_by_id[labware_id],
            )

    def _add_loaded_lid_stack(self, state_update: update_types.StateUpdate) -> None:
        loaded_lid_stack_update = state_update.loaded_lid_stack
        if loaded_lid_stack_update != update_types.NO_CHANGE:
            # Add the stack object
            stack_definition_uri = uri_from_details(
                namespace=loaded_lid_stack_update.stack_object_definition.namespace,
                load_name=loaded_lid_stack_update.stack_object_definition.parameters.loadName,
                version=loaded_lid_stack_update.stack_object_definition.version,
            )
            self.state.definitions_by_uri[
                stack_definition_uri
            ] = loaded_lid_stack_update.stack_object_definition
            self._state.labware_by_id[
                loaded_lid_stack_update.stack_id
            ] = LoadedLabware.construct(
                id=loaded_lid_stack_update.stack_id,
                location=loaded_lid_stack_update.stack_location,
                loadName=loaded_lid_stack_update.stack_object_definition.parameters.loadName,
                definitionUri=stack_definition_uri,
                offsetId=None,
                displayName=None,
            )

            # Add the Lids on top of the stack object
            for labware_id in loaded_lid_stack_update.new_locations_by_id:
                if loaded_lid_stack_update.definition is None:
                    raise ValueError(
                        "Lid Stack Labware Definition cannot be None when multiple lids are loaded."
                    )
                definition_uri = uri_from_details(
                    namespace=loaded_lid_stack_update.definition.namespace,
                    load_name=loaded_lid_stack_update.definition.parameters.loadName,
                    version=loaded_lid_stack_update.definition.version,
                )

                self._state.definitions_by_uri[
                    definition_uri
                ] = loaded_lid_stack_update.definition

                location = loaded_lid_stack_update.new_locations_by_id[labware_id]

                self._state.labware_by_id[labware_id] = LoadedLabware.construct(
                    id=labware_id,
                    location=location,
                    loadName=loaded_lid_stack_update.definition.parameters.loadName,
                    definitionUri=definition_uri,
                    offsetId=None,
                    displayName=None,
                )

    def _set_labware_lid(self, state_update: update_types.StateUpdate) -> None:
        labware_lid_update = state_update.labware_lid
        if labware_lid_update != update_types.NO_CHANGE:
            parent_labware_ids = labware_lid_update.parent_labware_ids
            for i in range(len(parent_labware_ids)):
                lid_id = labware_lid_update.lid_ids[i]
                self._state.labware_by_id[parent_labware_ids[i]].lid_id = lid_id

    def _do_update_labware_location(
        self, labware_id: str, new_location: LabwareLocation, new_offset_id: str | None
    ) -> None:
        self._state.labware_by_id[labware_id].offsetId = new_offset_id

        if isinstance(new_location, AddressableAreaLocation) and (
            fixture_validation.is_gripper_waste_chute(new_location.addressableAreaName)
            or fixture_validation.is_trash(new_location.addressableAreaName)
        ):
            # If a labware has been moved into a waste chute it's been chuted away and is now technically off deck
            new_location = OFF_DECK_LOCATION

        self._state.labware_by_id[labware_id].location = new_location

    def _set_labware_location(self, state_update: update_types.StateUpdate) -> None:
        labware_location_update = state_update.labware_location
        if labware_location_update == update_types.NO_CHANGE:
            return

        self._do_update_labware_location(
            labware_location_update.labware_id,
            labware_location_update.new_location,
            labware_location_update.offset_id,
        )

    def _set_batch_labware_location(
        self, state_update: update_types.StateUpdate
    ) -> None:
        batch_location_update = state_update.batch_labware_location
        if batch_location_update == update_types.NO_CHANGE:
            return
        for (
            labware_id,
            new_location,
        ) in batch_location_update.new_locations_by_id.items():
            self._do_update_labware_location(
                labware_id,
                new_location,
                batch_location_update.new_offset_ids_by_id.get(labware_id, None),
            )


class LabwareView:
    """Read-only labware state view."""

    _state: LabwareState

    def __init__(self, state: LabwareState) -> None:
        """Initialize the computed view of labware state.

        Arguments:
            state: Labware state dataclass used for all calculations.
        """
        self._state = state

    def get(self, labware_id: str) -> LoadedLabware:
        """Get labware data by the labware's unique identifier."""
        try:
            return self._state.labware_by_id[labware_id]
        except KeyError as e:
            raise errors.LabwareNotLoadedError(
                f"Labware {labware_id} not found."
            ) from e

    def known(self, labware_id: str) -> bool:
        """Check if the labware specified by labware_id has been loaded."""
        return labware_id in self._state.labware_by_id

    def get_id_by_module(self, module_id: str) -> str:
        """Return the ID of the labware loaded on the given module."""
        for labware_id, labware in self._state.labware_by_id.items():
            if (
                isinstance(labware.location, ModuleLocation)
                and labware.location.moduleId == module_id
            ):
                return labware_id

        raise errors.exceptions.LabwareNotLoadedOnModuleError(
            "There is no labware loaded on this Module"
        )

    def get_id_by_labware(self, labware_id: str) -> str:
        """Return the ID of the labware loaded on the given labware."""
        for labware in self._state.labware_by_id.values():
            if (
                isinstance(labware.location, OnLabwareLocation)
                and labware.location.labwareId == labware_id
            ):
                return labware.id
        raise errors.exceptions.LabwareNotLoadedOnLabwareError(
            f"There is not labware loaded onto labware {labware_id}"
        )

    def raise_if_labware_has_non_lid_labware_on_top(self, labware_id: str) -> None:
        """Raise if labware has another labware that is not its lid on top."""
        lid_id = self.get_lid_id_by_labware_id(labware_id)
        for candidate_id, candidate_labware in self._state.labware_by_id.items():
            if (
                isinstance(candidate_labware.location, OnLabwareLocation)
                and candidate_labware.location.labwareId == labware_id
                and candidate_id != lid_id
            ):
                raise errors.LabwareIsInStackError(
                    f"Cannot access labware {labware_id} because it has a non-lid labware stacked on top."
                )

    def raise_if_labware_has_labware_on_top(self, labware_id: str) -> None:
        """Raise if labware has another labware on top."""
        for labware in self._state.labware_by_id.values():
            if (
                isinstance(labware.location, OnLabwareLocation)
                and labware.location.labwareId == labware_id
            ):
                raise errors.LabwareIsInStackError(
                    f"Cannot access labware {labware_id} because it has another labware stacked on top."
                )

    def get_by_slot(
        self,
        slot_name: Union[DeckSlotName, StagingSlotName],
    ) -> Optional[LoadedLabware]:
        """Get the labware located in a given slot, if any."""
        loaded_labware = list(self._state.labware_by_id.values())

        for labware in loaded_labware:
            if (
                isinstance(labware.location, DeckSlotLocation)
                and labware.location.slotName.id == slot_name.id
            ) or (
                isinstance(labware.location, AddressableAreaLocation)
                and labware.location.addressableAreaName == slot_name.id
            ):
                return labware

        return None

    def get_by_addressable_area(
        self,
        addressable_area: str,
    ) -> Optional[LoadedLabware]:
        """Get the labware located in a given addressable area, if any."""
        loaded_labware = list(self._state.labware_by_id.values())

        for labware in loaded_labware:
            if (
                isinstance(labware.location, AddressableAreaLocation)
                and labware.location.addressableAreaName == addressable_area
            ):
                return labware

        return None

    def get_definition(self, labware_id: str) -> LabwareDefinition:
        """Get labware definition by the labware's unique identifier."""
        return self.get_definition_by_uri(
            LabwareUri(self.get(labware_id).definitionUri)
        )

    def get_user_specified_display_name(self, labware_id: str) -> Optional[str]:
        """Get the labware's user-specified display name, if set."""
        return self.get(labware_id).displayName

    def get_display_name(self, labware_id: str) -> str:
        """Get the labware's display name.

        If a user-specified display name exists, will return that, else will return
        display name from the definition.
        """
        return (
            self.get_user_specified_display_name(labware_id)
            or self.get_definition(labware_id).metadata.displayName
        )

    def get_deck_definition(self) -> DeckDefinitionV5:
        """Get the current deck definition."""
        return self._state.deck_definition

    def get_definition_by_uri(self, uri: LabwareUri) -> LabwareDefinition:
        """Get the labware definition matching loadName namespace and version."""
        try:
            return self._state.definitions_by_uri[uri]
        except KeyError as e:
            raise errors.LabwareDefinitionDoesNotExistError(
                f"Labware definition for matching {uri} not found."
            ) from e

    def get_loaded_labware_definitions(self) -> List[LabwareDefinition]:
        """Get all loaded labware definitions."""
        loaded_labware = self._state.labware_by_id.values()
        return [
            self.get_definition_by_uri(LabwareUri(labware.definitionUri))
            for labware in loaded_labware
        ]

    def find_custom_labware_load_params(self) -> List[LabwareLoadParams]:
        """Find all load labware parameters for custom labware definitions in state."""
        return [
            LabwareLoadParams(
                load_name=definition.parameters.loadName,
                namespace=definition.namespace,
                version=definition.version,
            )
            for definition in self._state.definitions_by_uri.values()
            if definition.namespace != OPENTRONS_NAMESPACE
        ]

    def get_location(self, labware_id: str) -> LabwareLocation:
        """Get labware location by the labware's unique identifier."""
        return self.get(labware_id).location

    def get_parent_location(self, labware_id: str) -> NonStackedLocation:
        """Get labware's non-labware parent location."""
        parent = self.get_location(labware_id)
        if isinstance(parent, OnLabwareLocation):
            return self.get_parent_location(parent.labwareId)
        elif isinstance(parent, InStackerHopperLocation):
            # TODO: This function really wants to return something like an "EventuallyOnDeckLocation"
            # and either raise or return None for labware that isn't traceable to a place on the robot
            # deck (i.e. not in a stacker hopper, not off-deck, not in system). We don't really have
            # that concept yet but should add it soon. In the meantime, other checks should prevent
            # this being called in those cases.
            return ModuleLocation(moduleId=parent.moduleId)
        return parent

    def get_highest_child_labware(self, labware_id: str) -> str:
        """Get labware's highest child labware returning the labware ID."""
        if (child_id := self.get_next_child_labware(labware_id)) is not None:
            return self.get_highest_child_labware(labware_id=child_id)
        return labware_id

    def get_next_child_labware(self, labware_id: str) -> str | None:
        """Get the labware that is on this labware, if any.

        This includes lids.
        """
        for labware in self._state.labware_by_id.values():
            if (
                isinstance(labware.location, OnLabwareLocation)
                and labware.location.labwareId == labware_id
            ):
                return labware.id
        return None

    def get_labware_stack_from_parent(self, labware_id: str) -> list[str]:
        """Get the stack of labware starting from the specified labware ID and moving up."""
        labware_ids = [labware_id]
        while (next_id := self.get_next_child_labware(labware_id)) is not None:
            labware_ids.append(next_id)
            labware_id = next_id
        return labware_ids

    def get_labware_stack(
        self, labware_stack: List[LoadedLabware]
    ) -> List[LoadedLabware]:
        """Get the a stack of labware starting from a given labware or existing stack."""
        parent = self.get_location(labware_stack[-1].id)
        if isinstance(parent, OnLabwareLocation):
            labware_stack.append(self.get(parent.labwareId))
            return self.get_labware_stack(labware_stack)
        return labware_stack

    def get_lid_id_by_labware_id(self, labware_id: str) -> str | None:
        """Get the ID of a lid labware on top of a given labware, if any."""
        return self._state.labware_by_id[labware_id].lid_id

    def get_lid_by_labware_id(self, labware_id: str) -> LoadedLabware | None:
        """Get the Lid Labware that is currently on top of a given labware, if there is one."""
        lid_id = self.get_lid_id_by_labware_id(labware_id)
        if lid_id:
            return self._state.labware_by_id[lid_id]
        else:
            return None

    def get_labware_by_lid_id(self, lid_id: str) -> LoadedLabware | None:
        """Get the labware that is currently covered by a given lid, if there is one."""
        loaded_labware = list(self._state.labware_by_id.values())
        for labware in loaded_labware:
            if labware.lid_id == lid_id:
                return labware
        return None

    def get_all(self) -> List[LoadedLabware]:
        """Get a list of all labware entries in state."""
        return list(self._state.labware_by_id.values())

    def get_has_quirk(self, labware_id: str, quirk: str) -> bool:
        """Get if a labware has a certain quirk."""
        return quirk in self.get_quirks(labware_id=labware_id)

    def get_quirks(self, labware_id: str) -> List[str]:
        """Get a labware's quirks."""
        definition = self.get_definition(labware_id)
        return definition.parameters.quirks or []

    def get_should_center_column_on_target_well(self, labware_id: str) -> bool:
        """True if a pipette moving to this labware should center its active column on the target.

        This is true for labware that have wells spanning entire columns.
        """
        has_quirk = self.get_has_quirk(labware_id, "centerMultichannelOnWells")
        return has_quirk and (
            len(self.get_definition(labware_id).wells) > 1
            and len(self.get_definition(labware_id).wells) < 96
        )

    def get_labware_stacking_maximum(self, labware: LabwareDefinition) -> int:
        """Returns the maximum number of labware allowed in a stack for a given labware definition.

        If not defined within a labware, defaults to one.
        """
        return labware.stackLimit if labware.stackLimit is not None else 1

    def get_should_center_pipette_on_target_well(self, labware_id: str) -> bool:
        """True if a pipette moving to a well of this labware should center its body on the target.

        This is true for 1-well reservoirs no matter the pipette, and for large plates.
        """
        has_quirk = self.get_has_quirk(labware_id, "centerMultichannelOnWells")
        return has_quirk and (
            len(self.get_definition(labware_id).wells) == 1
            or len(self.get_definition(labware_id).wells) >= 96
        )

    def get_well_definition(
        self,
        labware_id: str,
        well_name: Optional[str] = None,
    ) -> WellDefinition2 | WellDefinition3:
        """Get a well's definition by labware and well name.

        If `well_name` is omitted, the first well in the labware
        will be used.
        """
        definition = self.get_definition(labware_id)
        if well_name is None:
            well_name = definition.ordering[0][0]

        try:
            return definition.wells[well_name]
        except KeyError as e:
            raise errors.WellDoesNotExistError(
                f"{well_name} does not exist in {labware_id}."
            ) from e

    def get_well_geometry(
        self, labware_id: str, well_name: Optional[str] = None
    ) -> InnerWellGeometry | UserDefinedVolumes:
        """Get a well's inner geometry by labware and well name."""
        labware_def = self.get_definition(labware_id)
        if labware_def.innerLabwareGeometry is None:
            raise errors.IncompleteLabwareDefinitionError(
                message=f"No innerLabwareGeometry found in labware definition for labware_id: {labware_id}."
            )
        well_def = self.get_well_definition(labware_id, well_name)
        geometry_id = well_def.geometryDefinitionId
        if geometry_id is None:
            raise errors.IncompleteWellDefinitionError(
                message=f"No geometryDefinitionId found in well definition for well: {well_name} in labware_id: {labware_id}"
            )
        else:
            well_geometry = labware_def.innerLabwareGeometry.get(geometry_id)
            if well_geometry is None:
                raise errors.IncompleteLabwareDefinitionError(
                    message=f"No innerLabwareGeometry found in labware definition for well_id: {geometry_id} in labware_id: {labware_id}"
                )
            return well_geometry

    def get_well_size(
        self, labware_id: str, well_name: str
    ) -> Tuple[float, float, float]:
        """Get a well's size in x, y, z dimensions based on its shape.

        Args:
            labware_id: Labware identifier.
            well_name: Name of well in labware.

        Returns:
            A tuple of dimensions in x, y, and z. If well is circular,
            the x and y dimensions will both be set to the diameter.
        """
        well_definition = self.get_well_definition(labware_id, well_name)

        if well_definition.shape == "circular":
            x_size = y_size = well_definition.diameter
        elif well_definition.shape == "rectangular":
            x_size = well_definition.xDimension
            y_size = well_definition.yDimension
        else:
            assert_never(well_definition.shape)

        return x_size, y_size, well_definition.depth

    def get_well_radial_offsets(
        self, labware_id: str, well_name: str, radius_percentage: float
    ) -> Tuple[float, float]:
        """Get x and y radius offsets modified by radius percentage."""
        x_size, y_size, z_size = self.get_well_size(labware_id, well_name)
        return (x_size / 2.0) * radius_percentage, (y_size / 2.0) * radius_percentage

    def get_edge_path_type(
        self,
        labware_id: str,
        well_name: str,
        mount: MountType,
        labware_slot: DeckSlotName,
        next_to_module: bool,
    ) -> EdgePathType:
        """Get the recommended edge path type based on well column, labware position and any neighboring modules."""
        labware_definition = self.get_definition(labware_id)
        left_column = labware_definition.ordering[0]
        right_column = labware_definition.ordering[-1]

        left_path_criteria = mount is MountType.RIGHT and well_name in left_column
        right_path_criteria = mount is MountType.LEFT and well_name in right_column
        labware_right_side = labware_slot in _RIGHT_SIDE_SLOTS

        if left_path_criteria and (next_to_module or labware_right_side):
            return EdgePathType.LEFT
        elif right_path_criteria and next_to_module:
            return EdgePathType.RIGHT
        else:
            return EdgePathType.DEFAULT

    def validate_liquid_allowed_in_labware(
        self, labware_id: str, wells: Mapping[str, Any]
    ) -> List[str]:
        """Check if wells associated to a labware_id has well by name and that labware is not tiprack."""
        labware_definition = self.get_definition(labware_id)
        labware_wells = labware_definition.wells
        contains_wells = all(well_name in labware_wells for well_name in iter(wells))
        if labware_definition.parameters.isTiprack:
            raise errors.LabwareIsTipRackError(
                f"Given labware: {labware_id} is a tiprack. Can not load liquid."
            )
        if LabwareRole.adapter in labware_definition.allowedRoles:
            raise errors.LabwareIsAdapterError(
                f"Given labware: {labware_id} is an adapter. Can not load liquid."
            )
        if not contains_wells:
            raise errors.WellDoesNotExistError(
                f"Some of the supplied wells do not match the labwareId: {labware_id}."
            )
        return list(wells)

    def get_tip_length(self, labware_id: str, overlap: float = 0) -> float:
        """Get the nominal tip length of a tip rack."""
        definition = self.get_definition(labware_id)
        if definition.parameters.tipLength is None:
            raise errors.LabwareIsNotTipRackError(
                f"Labware {labware_id} has no tip length defined."
            )

        return definition.parameters.tipLength - overlap

    def get_tip_drop_z_offset(
        self, labware_id: str, length_scale: float, additional_offset: float
    ) -> float:
        """Get the tip drop offset from the top of the well."""
        tip_length = self.get_tip_length(labware_id)
        return -tip_length * length_scale + additional_offset

    def get_definition_uri(self, labware_id: str) -> LabwareUri:
        """Get a labware's definition URI."""
        return LabwareUri(self.get(labware_id).definitionUri)

    def get_uri_from_definition(
        self,
        labware_definition: LabwareDefinition,
    ) -> LabwareUri:
        """Get a definition URI from a full labware definition."""
        return uri_from_details(
            load_name=labware_definition.parameters.loadName,
            namespace=labware_definition.namespace,
            version=labware_definition.version,
        )

    @overload
    def get_uri_from_definition_unless_none(
        self, labware_definition: LabwareDefinition
    ) -> str:
        ...

    @overload
    def get_uri_from_definition_unless_none(self, labware_definition: None) -> None:
        ...

    def get_uri_from_definition_unless_none(
        self, labware_definition: LabwareDefinition | None
    ) -> str | None:
        """Get the URI from a labware definition, passing None through.

        Don't use unless you're sure you want to accept that the definition might be None.
        """
        if labware_definition is None:
            return None
        return self.get_uri_from_definition(labware_definition)

    def is_tiprack(self, labware_id: str) -> bool:
        """Get whether labware is a tiprack."""
        definition = self.get_definition(labware_id)
        return definition.parameters.isTiprack

    def get_load_name(self, labware_id: str) -> str:
        """Get the labware's load name."""
        definition = self.get_definition(labware_id)
        return definition.parameters.loadName

    @overload
    def get_dimensions(self, *, labware_definition: LabwareDefinition) -> Dimensions:
        pass

    @overload
    def get_dimensions(self, *, labware_id: str) -> Dimensions:
        pass

    def get_dimensions(
        self,
        *,
        labware_definition: LabwareDefinition | None = None,
        labware_id: str | None = None,
    ) -> Dimensions:
        """Get the labware's dimensions."""
        if labware_definition is None:
            assert labware_id is not None  # From our @overloads.
            labware_definition = self.get_definition(labware_id)

        extents = self.get_extents_around_lw_origin(labware_definition)
        return Dimensions(
            x=extents.x_dimension, y=extents.y_dimension, z=extents.z_dimension
        )

    def get_extents_around_lw_origin(
        self,
        labware_definition: LabwareDefinition,
    ) -> AxisAlignedBoundingBox3D:
        """Return a bounding box around all the space the labware occupies, all-encompassing.

        Returned coordinates are relative to the labware's local origin.
        """
        if labware_definition.schemaVersion == 2:
            x_dimension = labware_definition.dimensions.xDimension
            y_dimension = labware_definition.dimensions.yDimension
            z_dimension = labware_definition.dimensions.zDimension
            return AxisAlignedBoundingBox3D.from_corners(
                Point(0, 0, 0), Point(x_dimension, y_dimension, z_dimension)
            )
        else:
            return AxisAlignedBoundingBox3D.from_corners(
                Point.from_xyz_attrs(labware_definition.extents.total.backLeftBottom),
                Point.from_xyz_attrs(labware_definition.extents.total.frontRightTop),
            )

    def get_labware_overlap_offsets(
        self, definition: LabwareDefinition, below_labware_name: str
    ) -> OverlapOffset:
        """Get the labware's overlap with requested labware's load name."""
        if below_labware_name in definition.stackingOffsetWithLabware.keys():
            stacking_overlap = definition.stackingOffsetWithLabware.get(
                below_labware_name, OverlapOffset(x=0, y=0, z=0)
            )
        else:
            stacking_overlap = definition.stackingOffsetWithLabware.get(
                "default", OverlapOffset(x=0, y=0, z=0)
            )
        return OverlapOffset(
            x=stacking_overlap.x, y=stacking_overlap.y, z=stacking_overlap.z
        )

    def get_default_magnet_height(self, module_id: str, offset: float) -> float:
        """Return a labware's default Magnetic Module engage height with added offset, if supplied.

        The returned value is measured in millimeters above the labware base plane.
        """
        labware_id = self.get_id_by_module(module_id)
        parameters = self.get_definition(labware_id).parameters
        default_engage_height = parameters.magneticModuleEngageHeight
        if (
            parameters.isMagneticModuleCompatible is False
            or default_engage_height is None
        ):
            raise errors.exceptions.NoMagnetEngageHeightError(
                "The labware loaded on this Magnetic Module"
                " does not have a default engage height."
            )

        if self._is_magnetic_module_uri_in_half_millimeter(labware_id):
            # TODO(mc, 2022-09-26): this value likely _also_ needs a few mm subtracted
            # https://opentrons.atlassian.net/browse/RSS-111
            calculated_height = default_engage_height / 2.0
        else:
            calculated_height = default_engage_height

        return calculated_height + offset

    def get_labware_offset_vector(self, labware_id: str) -> LabwareOffsetVector:
        """Get the labware's calibration offset."""
        offset_id = self.get(labware_id=labware_id).offsetId
        if offset_id is None:
            return LabwareOffsetVector(x=0, y=0, z=0)
        else:
            return self._state.labware_offsets_by_id[offset_id].vector

    def get_labware_offset(self, labware_offset_id: str) -> LabwareOffset:
        """Get a labware offset by the offset's unique ID.

        Raises:
            LabwareOffsetDoesNotExistError: If the given ID does not match any
                                            previously added offset.
        """
        try:
            return self._state.labware_offsets_by_id[labware_offset_id]
        except KeyError as e:
            raise errors.LabwareOffsetDoesNotExistError(
                f"Labware offset {labware_offset_id} not found."
            ) from e

    def get_labware_offsets(self) -> List[LabwareOffset]:
        """Get all labware offsets, in the order they were added."""
        return list(self._state.labware_offsets_by_id.values())

    def find_applicable_labware_offset(
        self, definition_uri: str, location: LabwareOffsetLocationSequence
    ) -> Optional[LabwareOffset]:
        """Find a labware offset that applies to the given definition and location sequence.

        Returns the *most recently* added matching offset, so later ones can override earlier ones.
        Returns ``None`` if no loaded offset matches the location.

        An offset matches a labware instance if the sequence of locations formed by following the
        .location elements of the labware instance until you reach an addressable area has the same
        definition URIs as the sequence of definition URIs stored by the offset.
        """
        for candidate in reversed(list(self._state.labware_offsets_by_id.values())):
            if (
                candidate.definitionUri == definition_uri
                and candidate.locationSequence == location
            ):
                return candidate
        return None

    def find_applicable_labware_offset_by_legacy_location(
        self,
        definition_uri: str,
        location: LegacyLabwareOffsetLocation,
    ) -> Optional[LabwareOffset]:
        """Find a labware offset that applies to the given definition and legacy location.

        Returns the *most recently* added matching offset,
        so later offsets can override earlier ones.
        Or, ``None`` if no offsets match at all.

        An offset "matches"
        if its ``definition_uri`` and ``location`` *exactly* match what's provided.
        This implies that if the location involves a module,
        it will *not* match a module that's compatible but not identical.
        """
        for candidate in reversed(list(self._state.labware_offsets_by_id.values())):
            if (
                candidate.definitionUri == definition_uri
                and candidate.location == location
            ):
                return candidate

        return None

    def get_fixed_trash_id(self) -> Optional[str]:
        """Get the identifier of labware loaded into the fixed trash location.

        Raises:
            LabwareNotLoadedError: a fixed trash was not loaded by the deck definition
                that is currently in use for the protocol run.
        """
        for labware in self._state.labware_by_id.values():
            if isinstance(
                labware.location, DeckSlotLocation
            ) and labware.location.slotName in {
                DeckSlotName.FIXED_TRASH,
                DeckSlotName.SLOT_A3,
            }:
                return labware.id
        return None

    def is_fixed_trash(self, labware_id: str) -> bool:
        """Check if labware is fixed trash."""
        return self.get_has_quirk(labware_id, "fixedTrash")

    def is_absorbance_reader_lid(self, labware_id: str) -> bool:
        """Check if labware is an absorbance reader lid."""
        return labware_validation.is_absorbance_reader_lid(
            self.get(labware_id).loadName
        )

    def is_lid(self, labware_id: str) -> bool:
        """Check if labware is a lid."""
        return LabwareRole.lid in self.get_definition(labware_id).allowedRoles

    def raise_if_labware_in_location(
        self,
        location: OnDeckLabwareLocation,
    ) -> None:
        """Raise an error if the specified location has labware in it."""
        for labware in self.get_all():
            if labware.location == location:
                raise errors.LocationIsOccupiedError(
                    f"Labware {labware.loadName} is already present at {location}."
                )

    def raise_if_labware_cannot_be_ondeck(
        self,
        location: LabwareLocation,
        labware_definition: LabwareDefinition,
    ) -> None:
        """Raise an error if the labware cannot be in the specified location."""
        if isinstance(
            location, (DeckSlotLocation, AddressableAreaLocation)
        ) and not labware_validation.validate_labware_can_be_ondeck(labware_definition):
            raise errors.LabwareCannotSitOnDeckError(
                f"{labware_definition.parameters.loadName} cannot sit in a slot by itself."
            )

    def raise_if_labware_incompatible_with_plate_reader(
        self,
        labware_definition: LabwareDefinition,
    ) -> None:
        """Raise an error if the labware is not compatible with the plate reader."""
        load_name = labware_definition.parameters.loadName
        number_of_wells = len(labware_definition.wells)
        if number_of_wells != 96:
            raise errors.LabwareMovementNotAllowedError(
                f"Cannot move '{load_name}' into plate reader because the"
                f" labware contains {number_of_wells} wells where 96 wells is expected."
            )
        elif (
            self.get_dimensions(labware_definition=labware_definition).z
            > _PLATE_READER_MAX_LABWARE_Z_MM
        ):
            raise errors.LabwareMovementNotAllowedError(
                f"Cannot move '{load_name}' into plate reader because the"
                f" maximum allowed labware height is {_PLATE_READER_MAX_LABWARE_Z_MM}mm."
            )

    def raise_if_stacker_labware_pool_is_not_valid(
        self,
        primary_labware_definition: LabwareDefinition,
        lid_labware_definition: LabwareDefinition | None,
        adapter_labware_definition: LabwareDefinition | None,
    ) -> None:
        """Raise if the primary, lid, and adapter do not go together."""
        if lid_labware_definition:
            if not labware_validation.validate_definition_is_lid(
                lid_labware_definition
            ):
                raise errors.LabwareCannotBeStackedError(
                    f"Labware {lid_labware_definition.parameters.loadName} cannot be used as a lid in the Flex Stacker."
                )
            if not labware_validation.validate_labware_can_be_stacked(
                lid_labware_definition, primary_labware_definition.parameters.loadName
            ):
                raise errors.LabwareCannotBeStackedError(
                    f"Labware {lid_labware_definition.parameters.loadName} cannot be used as a lid for {primary_labware_definition.parameters.loadName}"
                )
        if adapter_labware_definition:
            if not labware_validation.validate_definition_is_adapter(
                adapter_labware_definition
            ):
                raise errors.LabwareCannotBeStackedError(
                    f"Labware {adapter_labware_definition.parameters.loadName} cannot be used as an adapter in the Flex Stacker."
                )
            if not labware_validation.validate_labware_can_be_stacked(
                primary_labware_definition,
                adapter_labware_definition.parameters.loadName,
            ):
                raise errors.LabwareCannotBeStackedError(
                    f"Labware {adapter_labware_definition.parameters.loadName} cannot be used as an adapter for {primary_labware_definition.parameters.loadName}"
                )

    def stacker_labware_pool_to_ordered_list(
        self,
        primary_labware_definition: LabwareDefinition,
        lid_labware_definition: LabwareDefinition | None,
        adapter_labware_definition: LabwareDefinition | None,
    ) -> List[LabwareDefinition]:
        """Get the pool definitions in the top-first order suitable for geometry calculations."""
        self.raise_if_stacker_labware_pool_is_not_valid(
            primary_labware_definition,
            lid_labware_definition,
            adapter_labware_definition,
        )
        return [
            x
            for x in [
                lid_labware_definition,
                primary_labware_definition,
                adapter_labware_definition,
            ]
            if x is not None
        ]

    def get_stacker_labware_overlap_offset(
        self, definitions: list[LabwareDefinition]
    ) -> OverlapOffset:
        """Get the overlap amount between each labware pool.

        The definitions must be in top-first order, ideally created by
        `stacker_labware_pool_to_ordered_list`.
        """
        return self.get_labware_overlap_offsets(
            definitions[-1], definitions[0].parameters.loadName
        )

    def raise_if_labware_cannot_be_stacked(  # noqa: C901
        self, top_labware_definition: LabwareDefinition, bottom_labware_id: str
    ) -> None:
        """Raise if the specified labware definition cannot be placed on top of the bottom labware."""
        if labware_validation.validate_definition_is_adapter(top_labware_definition):
            raise errors.LabwareCannotBeStackedError(
                f"Labware {top_labware_definition.parameters.loadName} is defined as an adapter and cannot be placed"
                " on other labware."
            )
        below_labware = self.get(bottom_labware_id)
        if isinstance(
            top_labware_definition, LabwareDefinition2
        ) and not labware_validation.validate_labware_can_be_stacked(
            top_labware_definition=top_labware_definition,
            below_labware_load_name=below_labware.loadName,
        ):
            raise errors.LabwareCannotBeStackedError(
                f"Labware {top_labware_definition.parameters.loadName} cannot be loaded onto labware {below_labware.loadName}"
            )
        elif (
            labware_validation.validate_definition_is_lid(top_labware_definition)
            and top_labware_definition.compatibleParentLabware is not None
            and self.get_load_name(bottom_labware_id)
            not in top_labware_definition.compatibleParentLabware
        ):
            # This parent is assumed to be compatible, unless the lid enumerates
            # all its compatible parents and this parent is missing from the list.
            raise ValueError(
                f"Labware Lid {top_labware_definition.parameters.loadName} may not be loaded on parent labware"
                f" {self.get_display_name(bottom_labware_id)}."
            )
        elif isinstance(below_labware.location, ModuleLocation):
            below_definition = self.get_definition(labware_id=below_labware.id)
            if not labware_validation.validate_definition_is_adapter(
                below_definition
            ) and not labware_validation.validate_definition_is_lid(
                top_labware_definition
            ):
                raise errors.LabwareCannotBeStackedError(
                    f"Labware {top_labware_definition.parameters.loadName} cannot be loaded"
                    f" onto a labware on top of a module"
                )
        elif isinstance(below_labware.location, OnLabwareLocation):
            labware_stack = self.get_labware_stack([below_labware])
            stack_without_adapters = []
            for lw in labware_stack:
                if not labware_validation.validate_definition_is_adapter(
                    self.get_definition(lw.id)
                ) and not labware_validation.is_lid_stack(self.get_load_name(lw.id)):
                    stack_without_adapters.append(lw)
            if len(stack_without_adapters) >= self.get_labware_stacking_maximum(
                top_labware_definition
            ):
                raise errors.LabwareCannotBeStackedError(
                    f"Labware {top_labware_definition.parameters.loadName} cannot be loaded to stack of more than {self.get_labware_stacking_maximum(top_labware_definition)} labware."
                )

            further_below_definition = self.get_definition(
                labware_id=below_labware.location.labwareId
            )
            if labware_validation.validate_definition_is_adapter(
                further_below_definition
            ) and not labware_validation.validate_definition_is_lid(
                top_labware_definition
            ):
                raise errors.LabwareCannotBeStackedError(
                    f"Labware {top_labware_definition.parameters.loadName} cannot be loaded"
                    f" onto labware on top of adapter"
                )

    def _is_magnetic_module_uri_in_half_millimeter(self, labware_id: str) -> bool:
        """Check whether the labware uri needs to be calculated in half a millimeter."""
        uri = self.get_uri_from_definition(self.get_definition(labware_id))
        return uri in _MAGDECK_HALF_MM_LABWARE

    def get_deck_default_gripper_offsets(self) -> Optional[LabwareMovementOffsetData]:
        """Get the deck's default gripper offsets."""
        parsed_offsets = (
            self.get_deck_definition().get("gripperOffsets", {}).get("default")
        )
        return (
            LabwareMovementOffsetData(
                pickUpOffset=LabwareOffsetVector(
                    x=parsed_offsets["pickUpOffset"]["x"],
                    y=parsed_offsets["pickUpOffset"]["y"],
                    z=parsed_offsets["pickUpOffset"]["z"],
                ),
                dropOffset=LabwareOffsetVector(
                    x=parsed_offsets["dropOffset"]["x"],
                    y=parsed_offsets["dropOffset"]["y"],
                    z=parsed_offsets["dropOffset"]["z"],
                ),
            )
            if parsed_offsets
            else None
        )

    def get_absorbance_reader_lid_definition(self) -> LabwareDefinition:
        """Return the special labware definition for the plate reader lid.

        See todo comments in `create_protocol_engine().
        """
        # NOTE: This needs to stay in sync with create_protocol_engine().
        return self._state.definitions_by_uri[
            "opentrons/opentrons_flex_lid_absorbance_plate_reader_module/1"
        ]

    @overload
    def get_child_gripper_offsets(
        self,
        *,
        labware_definition: LabwareDefinition,
        slot_name: Optional[DeckSlotName],
    ) -> Optional[LabwareMovementOffsetData]:
        pass

    @overload
    def get_child_gripper_offsets(
        self, *, labware_id: str, slot_name: Optional[DeckSlotName]
    ) -> Optional[LabwareMovementOffsetData]:
        pass

    def get_child_gripper_offsets(
        self,
        *,
        labware_definition: Optional[LabwareDefinition] = None,
        labware_id: Optional[str] = None,
        slot_name: Optional[DeckSlotName],
    ) -> Optional[LabwareMovementOffsetData]:
        """Get the grip offsets that a labware says should be applied to children stacked atop it.

        Params:
            labware_id: The ID of a parent labware (atop which another labware, the child, will be stacked).
            slot_name: The ancestor slot that the parent labware is ultimately loaded into,
                       perhaps after going through a module in the middle.

        Returns:
            If `slot_name` is provided, returns the gripper offsets that the parent labware definition
            specifies just for that slot, or `None` if the labware definition doesn't have an
            exact match.

            If `slot_name` is `None`, returns the gripper offsets that the parent labware
            definition designates as "default," or `None` if it doesn't designate any as such.
        """
        if labware_id is not None:
            labware_definition = self.get_definition(labware_id)
        else:
            # Should be ensured by our @overloads.
            assert labware_definition is not None

        parsed_offsets = labware_definition.gripperOffsets
        offset_key = slot_name.id if slot_name else "default"

        if parsed_offsets is None or offset_key not in parsed_offsets:
            return None
        else:
            return LabwareMovementOffsetData(
                pickUpOffset=LabwareOffsetVector.model_construct(
                    x=parsed_offsets[offset_key].pickUpOffset.x,
                    y=parsed_offsets[offset_key].pickUpOffset.y,
                    z=parsed_offsets[offset_key].pickUpOffset.z,
                ),
                dropOffset=LabwareOffsetVector.model_construct(
                    x=parsed_offsets[offset_key].dropOffset.x,
                    y=parsed_offsets[offset_key].dropOffset.y,
                    z=parsed_offsets[offset_key].dropOffset.z,
                ),
            )

    def get_grip_force(self, labware_definition: LabwareDefinition) -> float:
        """Get the recommended grip force for gripping labware using gripper."""
        recommended_force = labware_definition.gripForce
        return (
            recommended_force if recommended_force is not None else LABWARE_GRIP_FORCE
        )

    def get_grip_z(self, labware_definition: LabwareDefinition) -> float:
        """Get the place on the labware where the gripper should contact.

        The returned value is a z-offset relative to the labware origin.
        """

        def get_origin_to_mid_z(labware_definition: LabwareDefinition) -> float:
            """Return the z-coordinate of the middle of the labware, relative to the labware's origin."""
            extents = self.get_extents_around_lw_origin(labware_definition)
            return (extents.max_z + extents.min_z) / 2

        if labware_definition.schemaVersion == 2:
            # In schema 2, the bottom of the labware is at the z-origin by definition.
            defined_height_from_origin = labware_definition.gripHeightFromLabwareBottom
        else:
            defined_height_from_origin = labware_definition.gripHeightFromLabwareOrigin

        return (
            defined_height_from_origin
            if defined_height_from_origin is not None
            else get_origin_to_mid_z(labware_definition)
        )

    @staticmethod
    def _max_x_of_well(well_defn: _WellDefinition) -> float:
        if well_defn.shape == "rectangular":
            return well_defn.x + (well_defn.xDimension or 0) / 2
        elif well_defn.shape == "circular":
            return well_defn.x + (well_defn.diameter or 0) / 2
        else:
            return well_defn.x

    @staticmethod
    def _min_x_of_well(well_defn: _WellDefinition) -> float:
        if well_defn.shape == "rectangular":
            return well_defn.x - (well_defn.xDimension or 0) / 2
        elif well_defn.shape == "circular":
            return well_defn.x - (well_defn.diameter or 0) / 2
        else:
            return 0

    @staticmethod
    def _max_y_of_well(well_defn: _WellDefinition) -> float:
        if well_defn.shape == "rectangular":
            return well_defn.y + (well_defn.yDimension or 0) / 2
        elif well_defn.shape == "circular":
            return well_defn.y + (well_defn.diameter or 0) / 2
        else:
            return 0

    @staticmethod
    def _min_y_of_well(well_defn: _WellDefinition) -> float:
        if well_defn.shape == "rectangular":
            return well_defn.y - (well_defn.yDimension or 0) / 2
        elif well_defn.shape == "circular":
            return well_defn.y - (well_defn.diameter or 0) / 2
        else:
            return 0

    @staticmethod
    def _max_z_of_well(well_defn: _WellDefinition) -> float:
        return well_defn.z + well_defn.depth

    def get_well_bbox(self, labware_definition: LabwareDefinition) -> Dimensions:
        """Get the bounding box implied by the wells.

        The bounding box of the labware that is implied by the wells is that required
        to contain the bounds of the wells - the y-span from the min-y bound of the min-y
        well to the max-y bound of the max-y well, x ditto, z from labware 0 to the max-z
        well top.

        This is used for the specific purpose of finding the reasonable uncertainty bounds of
        where and how a gripper will interact with a labware.
        """
        max_x: Optional[float] = None
        min_x: Optional[float] = None
        max_y: Optional[float] = None
        min_y: Optional[float] = None
        max_z: Optional[float] = None

        for well in labware_definition.wells.values():
            well_max_x = self._max_x_of_well(well)
            well_min_x = self._min_x_of_well(well)
            well_max_y = self._max_y_of_well(well)
            well_min_y = self._min_y_of_well(well)
            well_max_z = self._max_z_of_well(well)
            if (max_x is None) or (well_max_x > max_x):
                max_x = well_max_x
            if (max_y is None) or (well_max_y > max_y):
                max_y = well_max_y
            if (min_x is None) or (well_min_x < min_x):
                min_x = well_min_x
            if (min_y is None) or (well_min_y < min_y):
                min_y = well_min_y
            if (max_z is None) or (well_max_z > max_z):
                max_z = well_max_z
        if (
            max_x is None
            or max_y is None
            or min_x is None
            or min_y is None
            or max_z is None
        ):
            return Dimensions(0, 0, 0)
        return Dimensions(max_x - min_x, max_y - min_y, max_z)

    def _gripper_uncertainty_narrower(
        self, labware_bbox: Dimensions, well_bbox: Dimensions, target_grip_width: float
    ) -> float:
        """Most narrower the gripper can be than the target while still likely gripping successfully.

        This number can't just be the 0, because that is not going to be accurate if the labware is
        skirted - the dimensions are a full bounding box including the skirt, and the labware is
        narrower than that at the point where it is gripped. The general heuristic is that we can't
        get to the wells; but some labware don't have wells, so we need alternate values.

        The number will be interpreted relative to the target width, which is (for now) the labware
        outer bounding box.

        TODO: This should be a number looked up from the definition.
        """
        if well_bbox.y == 0:
            # This labware has no wells; use a fixed minimum
            return 5
        if well_bbox.y > labware_bbox.y:
            # This labware has a very odd definition with wells outside its dimensions.
            # Return the smaller value.
            return 0
        # An ok heuristic for successful grip is if we don't get all the way to the wells.
        return target_grip_width - well_bbox.y

    def _gripper_uncertainty_wider(
        self, labware_bbox: Dimensions, well_bbox: Dimensions, target_grip_width: float
    ) -> float:
        """Most wider the gripper can be than the target while still likely gripping successfully.

        This can be a lot closer to 0, since the bounding box of the labware will certainly be the
        widest point (if it's defined without error), but since there might be error in the
        definition we allow some slop.

        The number will be interpreted relative to the target width, which is (for now) the labware
        outer bounding box.

        TODO: This should be a number looked up from the definition.
        """
        # This will be 0 unless the wells are wider than the labware
        return max(well_bbox.y - target_grip_width, 0)

    def get_gripper_width_specs(
        self, labware_definition: LabwareDefinition
    ) -> GripSpecs:
        """Get the target and bounds for a successful grip of this labware."""
        outer_bounds = self.get_dimensions(labware_definition=labware_definition)
        well_bounds = self.get_well_bbox(labware_definition=labware_definition)
        narrower = self._gripper_uncertainty_narrower(
            labware_bbox=outer_bounds,
            well_bbox=well_bounds,
            target_grip_width=outer_bounds.y,
        )
        wider = self._gripper_uncertainty_wider(
            labware_bbox=outer_bounds,
            well_bbox=well_bounds,
            target_grip_width=outer_bounds.y,
        )
        return GripSpecs(
            # TODO: This should be a number looked up from the definition.
            targetY=outer_bounds.y,
            uncertaintyNarrower=narrower,
            uncertaintyWider=wider,
        )
