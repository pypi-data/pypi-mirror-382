"""Basic addressable area data state and store."""

from dataclasses import dataclass
from functools import cached_property
from typing import Dict, List, Optional, Set

from opentrons_shared_data.robot.types import RobotType, RobotDefinition
from opentrons_shared_data.deck.types import (
    DeckDefinitionV5,
    SlotDefV3,
    CutoutFixture,
)

from opentrons.types import Point, DeckSlotName

from ..errors import (
    IncompatibleAddressableAreaError,
    AreaNotInDeckConfigurationError,
    SlotDoesNotExistError,
    AddressableAreaDoesNotExistError,
    CutoutDoesNotExistError,
)
from ..resources import deck_configuration_provider
from ..types import (
    AddressableArea,
    PotentialCutoutFixture,
    DeckConfigurationType,
    Dimensions,
)
from ..actions.get_state_update import get_state_updates
from ..actions import (
    Action,
    SetDeckConfigurationAction,
    AddAddressableAreaAction,
)
from . import update_types
from .config import Config
from ._abstract_store import HasState, HandlesActions


@dataclass
class AddressableAreaState:
    """State of all loaded addressable area resources."""

    loaded_addressable_areas_by_name: Dict[str, AddressableArea]
    """The addressable areas that have been loaded so far.

    When `use_simulated_deck_config` is `False`, these are the addressable areas that the
    deck configuration provided.

    When `use_simulated_deck_config` is `True`, these are the addressable areas that have been
    referenced by the protocol so far.
    """

    potential_cutout_fixtures_by_cutout_id: Dict[str, Set[PotentialCutoutFixture]]

    deck_definition: DeckDefinitionV5

    deck_configuration: Optional[DeckConfigurationType]
    """The host robot's full deck configuration.

    If `use_simulated_deck_config` is `True`, this is meaningless and this value is undefined.
    In practice it will probably be `None` or `[]`.

    If `use_simulated_deck_config` is `False`, this will be non-`None`.
    """

    robot_type: RobotType

    use_simulated_deck_config: bool
    """See `Config.use_simulated_deck_config`."""

    """Information about the current robot model."""
    robot_definition: RobotDefinition


_OT2_ORDERED_SLOTS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
_FLEX_ORDERED_SLOTS = [
    "D1",
    "D2",
    "D3",
    "C1",
    "C2",
    "C3",
    "B1",
    "B2",
    "B3",
    "A1",
    "A2",
    "A3",
]
_FLEX_ORDERED_STAGING_SLOTS = ["D4", "C4", "B4", "A4"]


def _get_conflicting_addressable_areas_error_string(
    potential_cutout_fixtures: Set[PotentialCutoutFixture],
    loaded_addressable_areas: Dict[str, AddressableArea],
    deck_definition: DeckDefinitionV5,
) -> str:
    loaded_areas_on_cutout = set()
    for fixture in potential_cutout_fixtures:
        loaded_areas_on_cutout.update(
            deck_configuration_provider.get_provided_addressable_area_names(
                fixture.cutout_fixture_id,
                fixture.cutout_id,
                deck_definition,
            )
        )
    loaded_areas_on_cutout.intersection_update(loaded_addressable_areas)
    display_names = {
        loaded_addressable_areas[area].display_name for area in loaded_areas_on_cutout
    }
    return ", ".join(display_names)


class AddressableAreaStore(HasState[AddressableAreaState], HandlesActions):
    """Addressable area state container."""

    _state: AddressableAreaState

    def __init__(
        self,
        deck_configuration: DeckConfigurationType,
        config: Config,
        deck_definition: DeckDefinitionV5,
        robot_definition: RobotDefinition,
    ) -> None:
        """Initialize an addressable area store and its state."""
        if config.use_simulated_deck_config:
            loaded_addressable_areas_by_name = {}
        else:
            loaded_addressable_areas_by_name = (
                self._get_addressable_areas_from_deck_configuration(
                    deck_configuration,
                    deck_definition,
                )
            )

        self._state = AddressableAreaState(
            deck_configuration=deck_configuration,
            loaded_addressable_areas_by_name=loaded_addressable_areas_by_name,
            potential_cutout_fixtures_by_cutout_id={},
            deck_definition=deck_definition,
            robot_type=config.robot_type,
            use_simulated_deck_config=config.use_simulated_deck_config,
            robot_definition=robot_definition,
        )

    def handle_action(self, action: Action) -> None:
        """Modify state in reaction to an action."""
        for state_update in get_state_updates(action):
            if state_update.addressable_area_used != update_types.NO_CHANGE:
                self._add_addressable_area(
                    state_update.addressable_area_used.addressable_area_name
                )

        if isinstance(action, AddAddressableAreaAction):
            self._add_addressable_area(action.addressable_area_name)
        elif isinstance(action, SetDeckConfigurationAction):
            current_state = self._state
            if (
                action.deck_configuration is not None
                and not self._state.use_simulated_deck_config
            ):
                self._state.deck_configuration = action.deck_configuration
                self._state.loaded_addressable_areas_by_name = (
                    self._get_addressable_areas_from_deck_configuration(
                        deck_config=action.deck_configuration,
                        deck_definition=current_state.deck_definition,
                    )
                )

    @staticmethod
    def _get_addressable_areas_from_deck_configuration(
        deck_config: DeckConfigurationType, deck_definition: DeckDefinitionV5
    ) -> Dict[str, AddressableArea]:
        """Return all addressable areas provided by the given deck configuration."""
        addressable_areas = []
        for cutout_id, cutout_fixture_id, opentrons_module_serial_number in deck_config:
            provided_addressable_areas = (
                deck_configuration_provider.get_provided_addressable_area_names(
                    cutout_fixture_id, cutout_id, deck_definition
                )
            )
            cutout_position = deck_configuration_provider.get_cutout_position(
                cutout_id, deck_definition
            )
            for addressable_area_name in provided_addressable_areas:
                addressable_areas.append(
                    deck_configuration_provider.get_addressable_area_from_name(
                        addressable_area_name=addressable_area_name,
                        cutout_position=cutout_position,
                        deck_definition=deck_definition,
                    )
                )
        return {area.area_name: area for area in addressable_areas}

    def _add_addressable_area(self, addressable_area_name: str) -> None:
        if addressable_area_name not in self._state.loaded_addressable_areas_by_name:
            cutout_id = self._validate_addressable_area_for_simulation(
                addressable_area_name
            )

            cutout_position = deck_configuration_provider.get_cutout_position(
                cutout_id, self._state.deck_definition
            )
            addressable_area = (
                deck_configuration_provider.get_addressable_area_from_name(
                    addressable_area_name=addressable_area_name,
                    cutout_position=cutout_position,
                    deck_definition=self._state.deck_definition,
                )
            )
            self._state.loaded_addressable_areas_by_name[
                addressable_area.area_name
            ] = addressable_area

    def _validate_addressable_area_for_simulation(
        self, addressable_area_name: str
    ) -> str:
        """Given an addressable area name, validate it can exist on the deck and return cutout id associated with it."""
        (
            cutout_id,
            potential_fixtures,
        ) = deck_configuration_provider.get_potential_cutout_fixtures(
            addressable_area_name, self._state.deck_definition
        )

        if cutout_id in self._state.potential_cutout_fixtures_by_cutout_id:
            # Get the existing potential cutout fixtures for the addressable area already loaded on this cutout
            existing_potential_fixtures = (
                self._state.potential_cutout_fixtures_by_cutout_id[cutout_id]
            )
            # Get common cutout fixture that supplies existing addressable areas and the one being loaded
            remaining_fixtures = existing_potential_fixtures.intersection(
                set(potential_fixtures)
            )

            self._state.potential_cutout_fixtures_by_cutout_id[
                cutout_id
            ] = remaining_fixtures
        else:
            self._state.potential_cutout_fixtures_by_cutout_id[cutout_id] = set(
                potential_fixtures
            )

        return cutout_id


class AddressableAreaView:
    """Read-only addressable area state view."""

    _state: AddressableAreaState

    def __init__(self, state: AddressableAreaState) -> None:
        """Initialize the computed view of addressable area state.

        Arguments:
            state: Addressable area state dataclass used for all calculations.
        """
        self._state = state

    @cached_property
    def deck_definition(self) -> DeckDefinitionV5:
        """The full deck definition."""
        return self._state.deck_definition

    @cached_property
    def deck_extents(self) -> Point:
        """The maximum space on the deck."""
        extents = self._state.robot_definition["extents"]
        return Point(x=extents[0], y=extents[1], z=extents[2])

    @cached_property
    def mount_offsets(self) -> Dict[str, Point]:
        """The left and right mount offsets of the robot."""
        left_offset = self._state.robot_definition["mountOffsets"]["left"]
        right_offset = self._state.robot_definition["mountOffsets"]["right"]
        return {
            "left": Point(x=left_offset[0], y=left_offset[1], z=left_offset[2]),
            "right": Point(x=right_offset[0], y=right_offset[1], z=right_offset[2]),
        }

    @cached_property
    def padding_offsets(self) -> Dict[str, float]:
        """The padding offsets to be applied to the deck extents of the robot."""
        rear_offset = self._state.robot_definition["paddingOffsets"]["rear"]
        front_offset = self._state.robot_definition["paddingOffsets"]["front"]
        left_side_offset = self._state.robot_definition["paddingOffsets"]["leftSide"]
        right_side_offset = self._state.robot_definition["paddingOffsets"]["rightSide"]
        return {
            "rear": rear_offset,
            "front": front_offset,
            "left_side": left_side_offset,
            "right_side": right_side_offset,
        }

    def get_addressable_area(self, addressable_area_name: str) -> AddressableArea:
        """Get addressable area."""
        if not self._state.use_simulated_deck_config:
            return self._get_loaded_addressable_area(addressable_area_name)
        else:
            return self._get_addressable_area_from_deck_data(
                addressable_area_name=addressable_area_name,
                do_compatibility_check=True,
            )

    def get_all(self) -> List[str]:
        """Get a list of all loaded addressable area names."""
        return list(self._state.loaded_addressable_areas_by_name)

    def get_all_cutout_fixtures(self) -> Optional[List[str]]:
        """Get the names of all fixtures present in the host robot's deck configuration.

        If `use_simulated_deck_config` is `True` (see `Config`), we don't have a
        meaningful concrete layout of fixtures, so this will return `None`.
        """
        if self._state.use_simulated_deck_config:
            return None
        else:
            assert self._state.deck_configuration is not None
            return [
                cutout_fixture_id
                for _, cutout_fixture_id, _serial in self._state.deck_configuration
            ]

    def _get_loaded_addressable_area(
        self, addressable_area_name: str
    ) -> AddressableArea:
        """Get an addressable area that has been loaded into state. Will raise error if it does not exist."""
        try:
            return self._state.loaded_addressable_areas_by_name[addressable_area_name]
        except KeyError:
            raise AreaNotInDeckConfigurationError(
                f"{addressable_area_name} not provided by deck configuration."
            )

    def _check_if_area_is_compatible_with_potential_fixtures(
        self,
        area_name: str,
        cutout_id: str,
        potential_fixtures: Set[PotentialCutoutFixture],
    ) -> None:
        if cutout_id in self._state.potential_cutout_fixtures_by_cutout_id:
            if not self._state.potential_cutout_fixtures_by_cutout_id[
                cutout_id
            ].intersection(potential_fixtures):
                loaded_areas_on_cutout = (
                    _get_conflicting_addressable_areas_error_string(
                        self._state.potential_cutout_fixtures_by_cutout_id[cutout_id],
                        self._state.loaded_addressable_areas_by_name,
                        self._state.deck_definition,
                    )
                )
                area_display_name = (
                    deck_configuration_provider.get_addressable_area_display_name(
                        area_name, self._state.deck_definition
                    )
                )
                raise IncompatibleAddressableAreaError(
                    f"Cannot use {area_display_name}, not compatible with one or more of"
                    f" the following fixtures: {loaded_areas_on_cutout}"
                )

    def _get_addressable_area_from_deck_data(
        self,
        addressable_area_name: str,
        do_compatibility_check: bool,
    ) -> AddressableArea:
        """Get an addressable area that may not have been already loaded for a simulated run.

        Since this may be the first time this addressable area has been called, and it might not exist in the store
        yet (and if not won't until the result completes), we have to check if it is theoretically possible and then
        get the area data from the deck configuration provider.
        """
        if addressable_area_name in self._state.loaded_addressable_areas_by_name:
            return self._state.loaded_addressable_areas_by_name[addressable_area_name]

        (
            cutout_id,
            potential_fixtures,
        ) = deck_configuration_provider.get_potential_cutout_fixtures(
            addressable_area_name, self._state.deck_definition
        )

        if do_compatibility_check:
            self._check_if_area_is_compatible_with_potential_fixtures(
                addressable_area_name, cutout_id, potential_fixtures
            )

        cutout_position = deck_configuration_provider.get_cutout_position(
            cutout_id, self._state.deck_definition
        )
        return deck_configuration_provider.get_addressable_area_from_name(
            addressable_area_name=addressable_area_name,
            cutout_position=cutout_position,
            deck_definition=self._state.deck_definition,
        )

    def get_addressable_area_base_slot(
        self, addressable_area_name: str
    ) -> DeckSlotName:
        """Get the base slot the addressable area is associated with."""
        addressable_area = self.get_addressable_area(addressable_area_name)
        return addressable_area.base_slot

    def get_addressable_area_position(
        self,
        addressable_area_name: str,
        do_compatibility_check: bool = True,
    ) -> Point:
        """Get the position of an addressable area.

        This does not require the addressable area to be in the deck configuration.
        This is primarily used to support legacy fixed trash labware without
        modifying the deck layout to remove the similar, but functionally different,
        trashBinAdapter cutout fixture.

        Besides that instance, for movement purposes, this should only be called for
        areas that have been pre-validated, otherwise there could be the risk of collision.
        """
        addressable_area = self._get_addressable_area_from_deck_data(
            addressable_area_name=addressable_area_name,
            do_compatibility_check=False,  # This should probably not default to false
        )
        position = addressable_area.position
        return Point(x=position.x, y=position.y, z=position.z)

    def get_addressable_area_offsets_from_cutout(
        self,
        addressable_area_name: str,
    ) -> Point:
        """Get the offset form cutout fixture of an addressable area."""
        for addressable_area in self._state.deck_definition["locations"][
            "addressableAreas"
        ]:
            if addressable_area["id"] == addressable_area_name:
                area_offset = addressable_area["offsetFromCutoutFixture"]
                position = Point(
                    x=area_offset[0],
                    y=area_offset[1],
                    z=area_offset[2],
                )
                return Point(x=position.x, y=position.y, z=position.z)
        raise ValueError(
            f"No matching addressable area named {addressable_area_name} identified."
        )

    def get_addressable_area_bounding_box(
        self,
        addressable_area_name: str,
        do_compatibility_check: bool = True,
    ) -> Dimensions:
        """Get the bounding box of an addressable area.

        This does not require the addressable area to be in the deck configuration.
        For movement purposes, this should only be called for
        areas that have been pre-validated, otherwise there could be the risk of collision.
        """
        addressable_area = self._get_addressable_area_from_deck_data(
            addressable_area_name=addressable_area_name,
            do_compatibility_check=do_compatibility_check,
        )
        return addressable_area.bounding_box

    def get_addressable_area_move_to_location(
        self, addressable_area_name: str
    ) -> Point:
        """Get the move-to position (top center) for an addressable area."""
        addressable_area = self.get_addressable_area(addressable_area_name)
        position = addressable_area.position
        bounding_box = addressable_area.bounding_box
        return Point(
            x=position.x + bounding_box.x / 2,
            y=position.y + bounding_box.y / 2,
            z=position.z + bounding_box.z,
        )

    def get_addressable_area_center(self, addressable_area_name: str) -> Point:
        """Get the (x, y, z) position of the center of the area."""
        addressable_area = self.get_addressable_area(addressable_area_name)
        position = addressable_area.position
        bounding_box = addressable_area.bounding_box
        return Point(
            x=position.x + bounding_box.x / 2,
            y=position.y + bounding_box.y / 2,
            z=position.z,
        )

    def get_cutout_id_by_deck_slot_name(self, slot_name: DeckSlotName) -> str:
        """Get the Cutout ID of a given Deck Slot by Deck Slot Name."""
        return deck_configuration_provider.get_cutout_id_by_deck_slot_name(slot_name)

    def get_fixture_by_deck_slot_name(
        self, slot_name: DeckSlotName
    ) -> Optional[CutoutFixture]:
        """Get the Cutout Fixture currently loaded where a specific Deck Slot would be."""
        deck_config = self._state.deck_configuration
        if deck_config:
            slot_cutout_id = (
                deck_configuration_provider.get_cutout_id_by_deck_slot_name(slot_name)
            )
            slot_cutout_fixture = None
            # This will only ever be one under current assumptions
            for (
                cutout_id,
                cutout_fixture_id,
                opentrons_module_serial_number,
            ) in deck_config:
                if cutout_id == slot_cutout_id:
                    slot_cutout_fixture = (
                        deck_configuration_provider.get_cutout_fixture(
                            cutout_fixture_id, self._state.deck_definition
                        )
                    )
                    return slot_cutout_fixture
            if slot_cutout_fixture is None:
                # If this happens, it's a bug. Either DECK_SLOT_TO_CUTOUT_MAP
                # is missing an entry for the slot, or the deck configuration is missing
                # an entry for the cutout.
                raise CutoutDoesNotExistError(
                    f"No Cutout was found in the Deck that matched provided slot {slot_name}."
                )
        return None

    def get_fixture_height(self, cutout_fixture_name: str) -> float:
        """Get the z height of a cutout fixture."""
        cutout_fixture = deck_configuration_provider.get_cutout_fixture(
            cutout_fixture_name, self._state.deck_definition
        )
        return cutout_fixture["height"]

    def get_fixture_serial_from_deck_configuration_by_deck_slot(
        self, slot_name: DeckSlotName
    ) -> Optional[str]:
        """Get the serial number provided by the deck configuration for a Fixture at a given location."""
        deck_config = self._state.deck_configuration
        if deck_config:
            slot_cutout_id = (
                deck_configuration_provider.get_cutout_id_by_deck_slot_name(slot_name)
            )
            # This will only ever be one under current assumptions
            for (
                cutout_id,
                cutout_fixture_id,
                opentrons_module_serial_number,
            ) in deck_config:
                if cutout_id == slot_cutout_id:
                    return opentrons_module_serial_number
        return None

    def get_serial_number_by_cutout_id(self, slot_cutout_id: str) -> str | None:
        """Gets serial number from deck at a given cutout ID if one exists."""
        deck_config = self._state.deck_configuration
        if deck_config:
            for (
                cutout_id,
                cutout_fixture_id,
                opentrons_module_serial_number,
            ) in deck_config:
                if cutout_id == slot_cutout_id:
                    return opentrons_module_serial_number
        return None

    def get_fixture_serial_from_deck_configuration_by_addressable_area(
        self, addressable_area_name: str
    ) -> Optional[str]:
        """Get the serial number provided by the deck configuration for a Fixture that provides a given addressable area."""
        deck_config = self._state.deck_configuration
        if deck_config:
            potential_fixtures = (
                deck_configuration_provider.get_potential_cutout_fixtures(
                    addressable_area_name, self._state.deck_definition
                )
            )
            slot_cutout_id = potential_fixtures[0]
            fixture_ids = [
                fixture.cutout_fixture_id for fixture in potential_fixtures[1]
            ]
            # This will only ever be one under current assumptions
            for (
                cutout_id,
                cutout_fixture_id,
                opentrons_module_serial_number,
            ) in deck_config:
                if cutout_id == slot_cutout_id and cutout_fixture_id in fixture_ids:
                    return opentrons_module_serial_number
        return None

    def get_slot_definition(self, slot_id: str) -> SlotDefV3:
        """Get the definition of a slot in the deck.

        This does not require that the slot exist in deck configuration.
        """
        try:
            addressable_area = self._get_addressable_area_from_deck_data(
                addressable_area_name=slot_id,
                do_compatibility_check=True,  # From the description of get_slot_definition, this might have to be False.
            )
        except AddressableAreaDoesNotExistError:
            raise SlotDoesNotExistError(
                f"Slot ID {slot_id} does not exist in deck {self._state.deck_definition['otId']}"
            )
        position = addressable_area.position
        bounding_box = addressable_area.bounding_box
        return {
            "id": addressable_area.area_name,
            "position": [position.x, position.y, position.z],
            "boundingBox": {
                "xDimension": bounding_box.x,
                "yDimension": bounding_box.y,
                "zDimension": bounding_box.z,
            },
            "displayName": addressable_area.display_name,
            "compatibleModuleTypes": addressable_area.compatible_module_types,
            "features": addressable_area.features,
        }

    def get_deck_slot_definitions(self) -> Dict[str, SlotDefV3]:
        """Get all standard slot definitions available in the deck definition."""
        if self._state.robot_type == "OT-2 Standard":
            slots = _OT2_ORDERED_SLOTS
        else:
            slots = _FLEX_ORDERED_SLOTS
        return {slot_name: self.get_slot_definition(slot_name) for slot_name in slots}

    def get_staging_slot_definitions(self) -> Dict[str, SlotDefV3]:
        """Get all staging slot definitions available in the deck definition."""
        if self._state.robot_type == "OT-3 Standard":
            return {
                slot_name: self.get_slot_definition(slot_name)
                for slot_name in _FLEX_ORDERED_STAGING_SLOTS
            }
        else:
            return {}

    def raise_if_area_not_in_deck_configuration(
        self, addressable_area_name: str
    ) -> None:
        """Raise error if an addressable area is not compatible with or in the deck configuration.

        For simulated runs/analysis, this will raise if the given addressable area is not compatible with other
        previously referenced addressable areas, for example if a movable trash in A1 is in state, referencing the
        deck slot A1 will raise since those two can't exist in any deck configuration combination.

        For an on robot run, it will check if it is in the robot's deck configuration, if not it will raise an error.
        """
        if self._state.use_simulated_deck_config:
            (
                cutout_id,
                potential_fixtures,
            ) = deck_configuration_provider.get_potential_cutout_fixtures(
                addressable_area_name, self._state.deck_definition
            )

            self._check_if_area_is_compatible_with_potential_fixtures(
                addressable_area_name, cutout_id, potential_fixtures
            )
        else:
            if (
                addressable_area_name
                not in self._state.loaded_addressable_areas_by_name
            ):
                raise AreaNotInDeckConfigurationError(
                    f"{addressable_area_name} not provided by deck configuration."
                )

    def get_current_potential_cutout_fixtures_for_addressable_area(
        self, addressable_area_name: str
    ) -> tuple[str, Set[PotentialCutoutFixture]]:
        """Get the set of cutout fixtures that might provide a given addressable area.

        This takes into account the constraints already established by load commands or by a loaded deck
        configuration, and may therefore return different results for the same addressable area at
        different points in the protocol after deck configuration constraints have changed.

        This returns the common cutout id and the potential fixtures.
        """
        (
            cutout_id,
            base_potential_fixtures,
        ) = deck_configuration_provider.get_potential_cutout_fixtures(
            addressable_area_name, self._state.deck_definition
        )
        try:
            loaded_potential_fixtures = (
                self._state.potential_cutout_fixtures_by_cutout_id[cutout_id]
            )
            return cutout_id, loaded_potential_fixtures.intersection(
                base_potential_fixtures
            )
        except KeyError:
            # If there was a key error here, it's because this function was (eventually) called
            # from the body of a command implementation whose state update will load the
            # addressable area it's querying... but that state update has not been submitted
            # and processed, so nothing has created the entry for this cutout id yet. Do what
            # we'll do when we actually get to that state update, which is apply the base
            # potential fixtures from the deck def.
            return cutout_id, base_potential_fixtures
