"""Geometry state getters."""

from logging import getLogger
import enum
from numpy import array, dot, double as npdouble
from numpy.typing import NDArray
from typing import Optional, List, Tuple, Union, cast, TypeVar, Dict, Set
from dataclasses import dataclass
from functools import cached_property

from opentrons.types import (
    Point,
    DeckSlotName,
    StagingSlotName,
    MountType,
    MeniscusTrackingTarget,
)

from opentrons_shared_data.errors.exceptions import (
    InvalidStoredData,
    PipetteLiquidNotFoundError,
)
from opentrons_shared_data.labware.constants import WELL_NAME_PATTERN
from opentrons_shared_data.labware.labware_definition import (
    LabwareDefinition,
    LabwareDefinition2,
    InnerWellGeometry,
)
from opentrons_shared_data.deck.types import CutoutFixture
from opentrons_shared_data.pipette import PIPETTE_X_SPAN
from opentrons_shared_data.pipette.types import ChannelCount, LabwareUri

from .. import errors
from ..errors import (
    LabwareNotLoadedError,
    LabwareNotLoadedOnLabwareError,
    LabwareNotLoadedOnModuleError,
    LabwareMovementNotAllowedError,
    InvalidLabwarePositionError,
    LabwareNotOnDeckError,
)
from ..errors.exceptions import (
    InvalidLiquidHeightFound,
)
from ..resources import (
    fixture_validation,
    labware_validation,
    deck_configuration_provider,
)
from ..types import (
    OFF_DECK_LOCATION,
    SYSTEM_LOCATION,
    LoadedLabware,
    LoadedModule,
    WellLocation,
    LiquidHandlingWellLocation,
    DropTipWellLocation,
    PickUpTipWellLocation,
    WellOrigin,
    DropTipWellOrigin,
    WellOffset,
    DeckSlotLocation,
    ModuleLocation,
    OnLabwareLocation,
    LabwareLocation,
    LabwareOffsetVector,
    ModuleOffsetData,
    CurrentWell,
    CurrentPipetteLocation,
    TipGeometry,
    LabwareMovementOffsetData,
    InStackerHopperLocation,
    OnDeckLabwareLocation,
    AddressableAreaLocation,
    AddressableOffsetVector,
    StagingSlotLocation,
    LabwareOffsetLocationSequence,
    OnModuleOffsetLocationSequenceComponent,
    OnAddressableAreaOffsetLocationSequenceComponent,
    OnLabwareOffsetLocationSequenceComponent,
    OnLabwareLocationSequenceComponent,
    ModuleModel,
    PotentialCutoutFixture,
    LabwareLocationSequence,
    OnModuleLocationSequenceComponent,
    OnAddressableAreaLocationSequenceComponent,
    OnCutoutFixtureLocationSequenceComponent,
    NotOnDeckLocationSequenceComponent,
    AreaType,
    labware_location_is_off_deck,
    labware_location_is_system,
    WellLocationType,
    WellLocationFunction,
    LabwareParentDefinition,
    AddressableArea,
)
from ..types.liquid_level_detection import SimulatedProbeResult, LiquidTrackingType
from .config import Config
from .labware import LabwareView
from .wells import WellView
from .modules import ModuleView
from .pipettes import PipetteView
from .addressable_areas import AddressableAreaView
from .inner_well_math_utils import (
    find_height_inner_well_geometry,
    find_volume_inner_well_geometry,
    find_height_user_defined_volumes,
    find_volume_user_defined_volumes,
)
from ._well_math import wells_covered_by_pipette_configuration, nozzles_per_well
from ._labware_origin_math import get_parent_placement_origin_to_lw_origin


_LOG = getLogger(__name__)
SLOT_WIDTH = 128
_PIPETTE_HOMED_POSITION_Z = (
    248.0  # Height of the bottom of the nozzle without the tip attached when homed
)


class _TipDropSection(enum.Enum):
    """Well sections to drop tips in."""

    LEFT = "left"
    RIGHT = "right"


class _GripperMoveType(enum.Enum):
    """Types of gripper movement."""

    PICK_UP_LABWARE = enum.auto()
    DROP_LABWARE = enum.auto()


@dataclass
class _AbsoluteRobotExtents:
    front_left: Dict[MountType, Point]
    back_right: Dict[MountType, Point]
    deck_extents: Point
    padding_rear: float
    padding_front: float
    padding_left_side: float
    padding_right_side: float


_LabwareLocation = TypeVar("_LabwareLocation", bound=LabwareLocation)


# TODO(mc, 2021-06-03): continue evaluation of which selectors should go here
# vs which selectors should be in LabwareView
class GeometryView:
    """Geometry computed state getters."""

    def __init__(
        self,
        config: Config,
        labware_view: LabwareView,
        well_view: WellView,
        module_view: ModuleView,
        pipette_view: PipetteView,
        addressable_area_view: AddressableAreaView,
    ) -> None:
        """Initialize a GeometryView instance."""
        self._config = config
        self._labware = labware_view
        self._wells = well_view
        self._modules = module_view
        self._pipettes = pipette_view
        self._addressable_areas = addressable_area_view
        self._last_drop_tip_location_spot: Dict[str, _TipDropSection] = {}

    @cached_property
    def absolute_deck_extents(self) -> _AbsoluteRobotExtents:
        """The absolute deck extents for a given robot deck."""
        left_offset = self._addressable_areas.mount_offsets["left"]
        right_offset = self._addressable_areas.mount_offsets["right"]

        front_left_abs = {
            MountType.LEFT: Point(left_offset.x, -1 * left_offset.y, left_offset.z),
            MountType.RIGHT: Point(right_offset.x, -1 * right_offset.y, right_offset.z),
        }
        back_right_abs = {
            MountType.LEFT: self._addressable_areas.deck_extents + left_offset,
            MountType.RIGHT: self._addressable_areas.deck_extents + right_offset,
        }
        return _AbsoluteRobotExtents(
            front_left=front_left_abs,
            back_right=back_right_abs,
            deck_extents=self._addressable_areas.deck_extents,
            padding_rear=self._addressable_areas.padding_offsets["rear"],
            padding_front=self._addressable_areas.padding_offsets["front"],
            padding_left_side=self._addressable_areas.padding_offsets["left_side"],
            padding_right_side=self._addressable_areas.padding_offsets["right_side"],
        )

    def get_labware_highest_z(self, labware_id: str) -> float:
        """Get the highest Z-point of a labware."""
        labware_data = self._labware.get(labware_id)
        return self._get_highest_z_from_labware_data(labware_data)

    def _is_obstacle_labware(self, labware_id: str) -> bool:
        """Check if the labware is a deck obstacle."""
        for loc in self.get_location_sequence(labware_id):
            if isinstance(loc, InStackerHopperLocation) or isinstance(
                loc, NotOnDeckLocationSequenceComponent
            ):
                return False
        return True

    def _get_tallest_obstacle_labware(self) -> float:
        """Get the highest Z-point of all labware on the deck."""
        return max(
            (
                self._get_highest_z_from_labware_data(lw_data)
                for lw_data in self._labware.get_all()
                if self._is_obstacle_labware(lw_data.id)
            ),
            default=0.0,
        )

    def _get_tallest_obstacle_module(self) -> float:
        """Get the highest Z-point of all modules on the deck."""
        return max(
            (
                self._modules.get_module_highest_z(module.id, self._addressable_areas)
                for module in self._modules.get_all()
            ),
            default=0.0,
        )

    def _get_tallest_obstacle_fixture(self) -> float:
        """Get the highest Z-point of all fixtures on the deck."""
        all_fixtures = self._addressable_areas.get_all_cutout_fixtures()
        if all_fixtures is None:
            # We're using a simulated deck config (see `Config.use_simulated_deck_config`).
            # We only know the addressable areas referenced by the protocol, not the fixtures
            # providing them. And there is more than one possible configuration of fixtures
            # to provide them. So, we can't know what the highest fixture is. Default to 0.
            #
            # Defaulting to 0 may not be the right thing to do here.
            # For example, suppose a protocol references an addressable area that implies a tall
            # fixture must be on the deck, and then it uses long tips that wouldn't be able to
            # clear the top of that fixture. We should perhaps raise an analysis error for that,
            # but defaulting to 0 here means we won't.
            return 0.0
        return max(
            (
                self._addressable_areas.get_fixture_height(cutout_fixture_name)
                for cutout_fixture_name in all_fixtures
            ),
            default=0.0,
        )

    def get_all_obstacle_highest_z(self) -> float:
        """Get the highest Z-point across all obstacles that the instruments need to fly over."""
        return max(
            self._get_tallest_obstacle_labware(),
            self._get_tallest_obstacle_module(),
            self._get_tallest_obstacle_fixture(),
        )

    def get_highest_z_in_slot(
        self, slot: Union[DeckSlotLocation, StagingSlotLocation]
    ) -> float:
        """Get the highest Z-point of all items stacked in the given deck slot.

        This height includes the height of any module that occupies the given slot
        even if it wasn't loaded in that slot (e.g., thermocycler).
        """
        slot_item = self.get_slot_item(slot.slotName)
        if isinstance(slot_item, LoadedModule):
            # get height of module + all labware on it
            module_id = slot_item.id
            try:
                labware_id = self._labware.get_id_by_module(module_id=module_id)
            except LabwareNotLoadedOnModuleError:
                # For the time being we will ignore column 4 modules in this check to avoid conflating results
                if self._modules.is_column_4_module(slot_item.model) is False:
                    return self._modules.get_module_highest_z(
                        module_id=module_id,
                        addressable_areas=self._addressable_areas,
                    )
            else:
                # For the time being we will ignore column 4 modules in this check to avoid conflating results
                if self._modules.is_column_4_module(slot_item.model) is False:
                    return self.get_highest_z_of_labware_stack(labware_id)
            # todo (cb, 2025-09-15): For now we skip column 4 modules and handle them seperately in
            # get_highest_z_of_column_4_module, so this will return 0. In the future we may want to consolidate
            # this to make it more apparently at this point in the query process.
            return 0
        elif isinstance(slot_item, LoadedLabware):
            # get stacked heights of all labware in the slot
            return self.get_highest_z_of_labware_stack(slot_item.id)
        elif type(slot_item) is dict:
            # TODO (cb, 2024-02-05): Eventually this logic should become the responsibility of bounding box
            # conflict checking, as fixtures may not always be considered as items from slots.
            return self._addressable_areas.get_fixture_height(slot_item["id"])
        else:
            return 0

    def get_highest_z_of_labware_stack(self, labware_id: str) -> float:
        """Get the highest Z-point of the topmost labware in the stack of labware on the given labware.

        If there is no labware on the given labware, returns highest z of the given labware.
        """
        try:
            stacked_labware_id = self._labware.get_id_by_labware(labware_id)
        except LabwareNotLoadedOnLabwareError:
            return self.get_labware_highest_z(labware_id)
        return self.get_highest_z_of_labware_stack(stacked_labware_id)

    def get_highest_z_of_column_4_module(self, module: LoadedModule) -> float:
        """Get the highest Z-point of the topmost labware in the stack of labware on the given column 4 module.

        If there is no labware on the given module, returns highest z of the module.
        """
        if self._modules.is_column_4_module(module.model):
            try:
                labware_id = self._labware.get_id_by_module(module_id=module.id)
            except LabwareNotLoadedOnModuleError:
                return self._modules.get_module_highest_z(
                    module_id=module.id,
                    addressable_areas=self._addressable_areas,
                )
            else:
                return self.get_highest_z_of_labware_stack(labware_id)
        else:
            raise ValueError(
                "Module must be a Column 4 Module to determine maximum z height."
            )

    def get_min_travel_z(
        self,
        pipette_id: str,
        labware_id: str,
        location: Optional[CurrentPipetteLocation],
        minimum_z_height: Optional[float],
    ) -> float:
        """Get the minimum allowed travel height of an arc move."""
        if (
            isinstance(location, CurrentWell)
            and pipette_id == location.pipette_id
            and labware_id == location.labware_id
        ):
            min_travel_z = self.get_labware_highest_z(labware_id)
        else:
            min_travel_z = self.get_all_obstacle_highest_z()
        if minimum_z_height:
            min_travel_z = max(min_travel_z, minimum_z_height)
        return min_travel_z

    def _normalize_module_calibration_offset(
        self,
        module_location: DeckSlotLocation,
        offset_data: Optional[ModuleOffsetData],
    ) -> Point:
        """Normalize the module calibration offset depending on the module location."""
        if not offset_data:
            return Point(x=0, y=0, z=0)
        offset = Point.from_xyz_attrs(offset_data.moduleOffsetVector)
        calibrated_slot = offset_data.location.slotName
        calibrated_slot_column = self.get_slot_column(calibrated_slot)
        current_slot_column = self.get_slot_column(module_location.slotName)
        # make sure that we have valid colums since we cant have modules in the middle of the deck
        assert set([calibrated_slot_column, current_slot_column]).issubset(
            {1, 3}
        ), f"Module calibration offset is an invalid slot {calibrated_slot}"

        # Check if the module has moved from one side of the deck to the other
        if calibrated_slot_column != current_slot_column:
            # Since the module was rotated, the calibration offset vector needs to be rotated by 180 degrees along the z axis
            saved_offset: NDArray[npdouble] = array([offset.x, offset.y, offset.z])
            rotation_matrix: NDArray[npdouble] = array(
                [[-1, 0, 0], [0, -1, 0], [0, 0, 1]]
            )
            new_offset = dot(saved_offset, rotation_matrix)
            offset = Point(x=new_offset[0], y=new_offset[1], z=new_offset[2])
        return offset

    def _get_calibrated_module_offset(self, location: LabwareLocation) -> Point:
        """Get a labware location's underlying calibrated module offset, if it is on a module."""
        if isinstance(location, ModuleLocation):
            module_id = location.moduleId
            module_location = self._modules.get_location(module_id)
            offset_data = self._modules.get_module_calibration_offset(module_id)
            return self._normalize_module_calibration_offset(
                module_location, offset_data
            )
        elif isinstance(location, (DeckSlotLocation, AddressableAreaLocation)):
            # TODO we might want to do a check here to make sure addressable area location is a standard deck slot
            #   and raise if its not (or maybe we don't actually care since modules will never be loaded elsewhere)
            return Point(x=0, y=0, z=0)
        elif isinstance(location, OnLabwareLocation):
            labware_data = self._labware.get(location.labwareId)
            return self._get_calibrated_module_offset(labware_data.location)
        elif (
            location == OFF_DECK_LOCATION
            or location == SYSTEM_LOCATION
            or isinstance(location, InStackerHopperLocation)
        ):
            raise errors.LabwareNotOnDeckError(
                "Labware does not have a slot or module associated with it"
                " since it is no longer on the deck."
            )

    def get_labware_origin_position(self, labware_id: str) -> Point:
        """Get the deck coordinates of a labware's origin.

        This includes module calibration but excludes the calibration of the given labware.
        """
        location = self._labware.get(labware_id).location
        definition = self._labware.get_definition(labware_id)

        slot_front_left = self._get_labware_ancestor_position(labware_id)
        stackup_origin_to_lw_origin = self._get_stackup_placement_origin_to_lw_origin(
            location=location, definition=definition, is_topmost_labware=True
        )
        module_cal_offset = self._get_calibrated_module_offset(location)

        return slot_front_left + stackup_origin_to_lw_origin + module_cal_offset

    def _get_labware_ancestor_position(self, labware_id: str) -> Point:
        """Get the position of the labware's underlying ancestor."""
        slot_name = self._get_underlying_addressable_area_name(
            self._labware.get(labware_id).location
        )
        parent_pos = self._addressable_areas.get_addressable_area_position(slot_name)

        return parent_pos

    def _get_stackup_placement_origin_to_lw_origin(
        self,
        location: LabwareLocation,
        definition: LabwareDefinition,
        is_topmost_labware: bool,
    ) -> Point:
        """Get the offset vector from the lowest entity in a stackup to the labware."""
        if isinstance(
            location, (AddressableAreaLocation, DeckSlotLocation, ModuleLocation)
        ):
            return self._get_parent_placement_origin_to_lw_origin(
                labware_location=location,
                labware_definition=definition,
                is_topmost_labware=is_topmost_labware,
            )
        elif isinstance(location, OnLabwareLocation):
            parent_id = location.labwareId
            parent_location = self._labware.get(parent_id).location
            parent_definition = self._labware.get_definition(parent_id)

            parent_placement_origin_to_lw_origin = (
                self._get_parent_placement_origin_to_lw_origin(
                    labware_location=location,
                    labware_definition=definition,
                    is_topmost_labware=is_topmost_labware,
                )
            )

            return (
                parent_placement_origin_to_lw_origin
                + self._get_stackup_placement_origin_to_lw_origin(
                    location=parent_location,
                    definition=parent_definition,
                    is_topmost_labware=False,
                )
            )
        else:
            raise errors.LabwareNotOnDeckError(
                "Cannot access labware since it is not on the deck. "
                "Either it has been loaded off-deck or its been moved off-deck."
            )

    def _get_parent_placement_origin_to_lw_origin(
        self,
        labware_location: LabwareLocation,
        labware_definition: LabwareDefinition,
        is_topmost_labware: bool,
    ) -> Point:
        parent_deck_item = self._get_parent_definition(labware_location)

        if isinstance(labware_location, ModuleLocation):
            module_parent_to_child_offset = (
                self._modules.get_nominal_offset_to_child_from_addressable_area(
                    module_id=labware_location.moduleId,
                )
            )
            return get_parent_placement_origin_to_lw_origin(
                child_labware=labware_definition,
                parent_deck_item=parent_deck_item,  # type: ignore[arg-type]
                module_parent_to_child_offset=module_parent_to_child_offset,
                deck_definition=self._addressable_areas.deck_definition,
                is_topmost_labware=is_topmost_labware,
                labware_location=labware_location,
            )
        elif isinstance(labware_location, OnLabwareLocation):
            return get_parent_placement_origin_to_lw_origin(
                child_labware=labware_definition,
                parent_deck_item=parent_deck_item,  # type: ignore[arg-type]
                module_parent_to_child_offset=None,
                deck_definition=self._addressable_areas.deck_definition,
                is_topmost_labware=is_topmost_labware,
                labware_location=labware_location,
            )
        elif isinstance(labware_location, (DeckSlotLocation, AddressableAreaLocation)):
            return get_parent_placement_origin_to_lw_origin(
                child_labware=labware_definition,
                parent_deck_item=parent_deck_item,  # type: ignore[arg-type]
                module_parent_to_child_offset=None,
                deck_definition=self._addressable_areas.deck_definition,
                is_topmost_labware=is_topmost_labware,
                labware_location=labware_location,
            )
        else:
            raise ValueError(f"Invalid labware location: {labware_location}")

    def _get_parent_definition(
        self, location: LabwareLocation
    ) -> LabwareParentDefinition:
        """Get the parent's definition given the labware's location."""
        if isinstance(location, DeckSlotLocation):
            addressable_area_name = location.slotName.id
            return self._addressable_areas.get_slot_definition(addressable_area_name)

        elif isinstance(location, AddressableAreaLocation):
            addressable_area_name = location.addressableAreaName
            return self._addressable_areas.get_addressable_area(addressable_area_name)

        elif isinstance(location, ModuleLocation):
            module_id = location.moduleId
            return self._modules.get_definition(module_id)

        elif isinstance(location, OnLabwareLocation):
            below_labware_id = location.labwareId
            return self._labware.get_definition(below_labware_id)

        elif location == OFF_DECK_LOCATION or location == SYSTEM_LOCATION:
            raise errors.LabwareNotOnDeckError(
                f"Labware location {location} does not have a slot associated with it"
                f" since it is no longer on the deck."
            )

        elif isinstance(location, InStackerHopperLocation):
            raise errors.LabwareNotOnDeckError(
                "Labware does not have a slot or module associated with it"
                " since it is no longer on the deck."
            )

        else:
            raise errors.InvalidLabwarePositionError(
                f"Cannot get ancestor from location {location}"
            )

    def _get_underlying_addressable_area_name(self, location: LabwareLocation) -> str:
        if isinstance(location, DeckSlotLocation):
            return location.slotName.id
        elif isinstance(location, AddressableAreaLocation):
            return location.addressableAreaName
        elif isinstance(location, ModuleLocation):
            return self._modules.get_provided_addressable_area(location.moduleId)
        elif isinstance(location, OnLabwareLocation):
            return self.get_ancestor_addressable_area_name(location.labwareId)
        else:
            raise errors.InvalidLabwarePositionError(
                f"Cannot get ancestor slot of location {location}"
            )

    def get_labware_position(self, labware_id: str) -> Point:
        """Get the calibrated origin of the labware."""
        origin_pos = self.get_labware_origin_position(labware_id)
        cal_offset = self._labware.get_labware_offset_vector(labware_id)
        return Point(
            x=origin_pos.x + cal_offset.x,
            y=origin_pos.y + cal_offset.y,
            z=origin_pos.z + cal_offset.z,
        )

    def _validate_well_position(
        self,
        target_height: LiquidTrackingType,  # height in mm inside a well relative to the bottom
        well_max_height: float,
        pipette_id: str,
    ) -> LiquidTrackingType:
        """If well offset would be outside the bounds of a well, silently bring it back to the boundary."""
        if isinstance(target_height, SimulatedProbeResult):
            return target_height
        lld_min_height = self._pipettes.get_current_tip_lld_settings(
            pipette_id=pipette_id
        )
        if target_height < lld_min_height:
            target_height = lld_min_height
        elif target_height > well_max_height:
            target_height = well_max_height
        return target_height

    def validate_probed_height(
        self,
        labware_id: str,
        well_name: str,
        pipette_id: str,
        probed_height: LiquidTrackingType,
    ) -> None:
        """Raise an error if a probed liquid height is not within well bounds."""
        if isinstance(probed_height, SimulatedProbeResult):
            return
        lld_min_height = self._pipettes.get_current_tip_lld_settings(
            pipette_id=pipette_id
        )
        well_def = self._labware.get_well_definition(labware_id, well_name)
        well_depth = well_def.depth
        if probed_height < lld_min_height:
            raise PipetteLiquidNotFoundError(
                f"Liquid Height of {probed_height} mm is lower minumum allowed lld height {lld_min_height} mm."
            )
        if probed_height > well_depth:
            raise PipetteLiquidNotFoundError(
                f"Liquid Height of {probed_height} mm is greater than maximum well height {well_depth} mm."
            )

    def get_well_position(
        self,
        labware_id: str,
        well_name: str,
        well_location: Optional[WellLocationType] = None,
        operation_volume: Optional[float] = None,
        pipette_id: Optional[str] = None,
    ) -> Point:
        """Given relative well location in a labware, get absolute position."""
        labware_pos = self.get_labware_position(labware_id)
        well_def = self._labware.get_well_definition(labware_id, well_name)
        well_depth = well_def.depth

        offset = WellOffset(x=0, y=0, z=well_depth)
        if well_location is not None:
            offset = well_location.offset  # location of the bottom of the well
            offset_adjustment = self.get_well_offset_adjustment(
                labware_id=labware_id,
                well_name=well_name,
                well_location=well_location,
                well_depth=well_depth,
                operation_volume=operation_volume,
                pipette_id=pipette_id,
            )
            if not isinstance(offset_adjustment, SimulatedProbeResult):
                offset = offset.model_copy(update={"z": offset.z + offset_adjustment})
        return Point(
            x=labware_pos.x + offset.x + well_def.x,
            y=labware_pos.y + offset.y + well_def.y,
            z=labware_pos.z + offset.z + well_def.z,
        )

    def _get_relative_liquid_handling_well_location(
        self,
        labware_id: str,
        well_name: str,
        absolute_point: Point,
        delta: Point,
        meniscus_tracking: Optional[MeniscusTrackingTarget] = None,
    ) -> Tuple[WellLocationType, bool]:
        """Given absolute position, get relative location of a well in a labware."""
        dynamic_liquid_tracking = False
        if meniscus_tracking:
            location = LiquidHandlingWellLocation(
                origin=WellOrigin.MENISCUS,
                offset=WellOffset(x=0, y=0, z=absolute_point.z),
            )
            # TODO(cm): handle operationVolume being a float other than 0
            if meniscus_tracking == MeniscusTrackingTarget.END:
                location.volumeOffset = "operationVolume"
            elif meniscus_tracking == MeniscusTrackingTarget.DYNAMIC:
                dynamic_liquid_tracking = True
        else:
            location = LiquidHandlingWellLocation(
                offset=WellOffset(x=delta.x, y=delta.y, z=delta.z)
            )
        return location, dynamic_liquid_tracking

    def get_relative_well_location(
        self,
        labware_id: str,
        well_name: str,
        absolute_point: Point,
        location_type: WellLocationFunction,
        meniscus_tracking: Optional[MeniscusTrackingTarget] = None,
    ) -> Tuple[WellLocationType, bool]:
        """Given absolute position, get relative location of a well in a labware."""
        well_absolute_point = self.get_well_position(labware_id, well_name)
        delta = absolute_point - well_absolute_point
        match location_type:
            case WellLocationFunction.BASE | WellLocationFunction.DROP_TIP:
                return (
                    WellLocation(offset=WellOffset(x=delta.x, y=delta.y, z=delta.z)),
                    False,
                )
            case WellLocationFunction.PICK_UP_TIP:
                return (
                    PickUpTipWellLocation(
                        offset=WellOffset(x=delta.x, y=delta.y, z=delta.z)
                    ),
                    False,
                )
            case WellLocationFunction.LIQUID_HANDLING:
                return self._get_relative_liquid_handling_well_location(
                    labware_id=labware_id,
                    well_name=well_name,
                    absolute_point=absolute_point,
                    delta=delta,
                    meniscus_tracking=meniscus_tracking,
                )

    def get_well_height(
        self,
        labware_id: str,
        well_name: str,
    ) -> float:
        """Get the height of a specified well for a labware."""
        well_def = self._labware.get_well_definition(labware_id, well_name)
        return well_def.depth

    def _get_highest_z_from_labware_data(self, lw_data: LoadedLabware) -> float:
        labware_pos = self.get_labware_position(lw_data.id)
        z_dim = self._labware.get_dimensions(labware_id=lw_data.id).z
        height_over_labware: float = 0
        if isinstance(lw_data.location, ModuleLocation):
            # Note: when calculating highest z of stacked labware, height-over-labware
            # gets accounted for only if the top labware is directly on the module.
            # So if there's a labware on an adapter on a module, then this
            # over-module-height gets ignored. We currently do not have any modules
            # that use an adapter and has height over labware so this doesn't cause
            # any issues yet. But if we add one in the future then this calculation
            # should be updated.
            module_id = lw_data.location.moduleId
            height_over_labware = self._modules.get_height_over_labware(module_id)
        # todo(mm, 2025-07-31): This math needs updating for schema 2:
        # labware_pos.z is not necessarily the bottom of the labware.
        return labware_pos.z + z_dim + height_over_labware

    def get_nominal_effective_tip_length(
        self,
        pipette_id: str,
        labware_id: str,
    ) -> float:
        """Given a labware and a pipette's config, get the nominal effective tip length.

        Effective tip length is the nominal tip length less the distance the
        tip overlaps with the pipette nozzle. This does not take calibrated
        tip lengths into account.
        """
        labware_uri = self._labware.get_definition_uri(labware_id)
        nominal_overlap = self._pipettes.get_nominal_tip_overlap(
            pipette_id=pipette_id, labware_uri=labware_uri
        )

        return self._labware.get_tip_length(
            labware_id=labware_id, overlap=nominal_overlap
        )

    def get_nominal_tip_geometry(
        self,
        pipette_id: str,
        labware_id: str,
        well_name: Optional[str],
    ) -> TipGeometry:
        """Given a labware, well, and hardware pipette config, get the tip geometry.

        Tip geometry includes effective tip length, tip diameter, and tip volume,
        which is all data required by the hardware controller for proper tip handling.

        This geometry data is based solely on labware and pipette definitions and
        does not take calibrated tip lengths into account.
        """
        effective_length = self.get_nominal_effective_tip_length(
            pipette_id=pipette_id,
            labware_id=labware_id,
        )
        well_def = self._labware.get_well_definition(labware_id, well_name)

        if well_def.shape != "circular":
            raise errors.LabwareIsNotTipRackError(
                f"Well {well_name} in labware {labware_id} is not circular."
            )

        return TipGeometry(
            length=effective_length,
            diameter=well_def.diameter,
            # TODO(mc, 2020-11-12): WellDefinition type says totalLiquidVolume
            #  is a float, but hardware controller expects an int
            volume=int(well_def.totalLiquidVolume),
        )

    def get_checked_tip_drop_location(
        self,
        pipette_id: str,
        labware_id: str,
        well_location: DropTipWellLocation,
        partially_configured: bool = False,
        override_default_offset: float | None = None,
    ) -> WellLocation:
        """Get tip drop location given labware and hardware pipette.

        This makes sure that the well location has an appropriate origin & offset
        if one is not already set previously.
        """
        if (
            self._labware.get_definition(labware_id).parameters.isTiprack
            and partially_configured
        ):
            raise errors.UnexpectedProtocolError(
                "Cannot return tip to a tiprack while the pipette is configured for partial tip."
            )
        if well_location.origin != DropTipWellOrigin.DEFAULT:
            return WellLocation(
                origin=WellOrigin(well_location.origin.value),
                offset=well_location.offset,
            )
        if override_default_offset is not None:
            z_offset = override_default_offset
        elif self._labware.get_definition(labware_id).parameters.isTiprack:
            z_offset = self._labware.get_tip_drop_z_offset(
                labware_id=labware_id,
                length_scale=self._pipettes.get_return_tip_scale(pipette_id),
                additional_offset=well_location.offset.z,
            )
        else:
            # return to top if labware is not tip rack
            z_offset = well_location.offset.z

        return WellLocation(
            origin=WellOrigin.TOP,
            offset=WellOffset(
                x=well_location.offset.x,
                y=well_location.offset.y,
                z=z_offset,
            ),
        )

    def convert_pick_up_tip_well_location(
        self, well_location: PickUpTipWellLocation
    ) -> WellLocation:
        """Convert PickUpTipWellLocation to WellLocation."""
        return WellLocation(
            origin=WellOrigin(well_location.origin.value), offset=well_location.offset
        )

    def get_ancestor_slot_name(
        self, labware_id: str
    ) -> Union[DeckSlotName, StagingSlotName]:
        """Get the slot name of the labware or the module that the labware is on."""
        labware = self._labware.get(labware_id)
        slot_name: Union[DeckSlotName, StagingSlotName]
        if isinstance(labware.location, DeckSlotLocation):
            slot_name = labware.location.slotName
        elif isinstance(labware.location, ModuleLocation):
            module_id = labware.location.moduleId
            slot_name = self._modules.get_location(module_id).slotName
        elif isinstance(labware.location, OnLabwareLocation):
            below_labware_id = labware.location.labwareId
            slot_name = self.get_ancestor_slot_name(below_labware_id)
        elif isinstance(labware.location, AddressableAreaLocation):
            area_name = labware.location.addressableAreaName
            if self._labware.is_absorbance_reader_lid(labware_id):
                raise errors.LocationIsLidDockSlotError(
                    "Cannot get ancestor slot name for labware on lid dock slot."
                )
            elif fixture_validation.is_staging_slot(area_name):
                slot_name = StagingSlotName.from_primitive(area_name)
            else:
                slot_name = DeckSlotName.from_primitive(area_name)
        elif labware.location == OFF_DECK_LOCATION:
            raise errors.LabwareNotOnDeckError(
                f"Labware {labware_id} does not have a slot associated with it"
                f" since it is no longer on the deck."
            )
        else:
            _LOG.error(
                f"Unhandled location type in get_ancestor_slot_name: {labware.location}"
            )
            raise errors.InvalidLabwarePositionError(
                f"Cannot get ancestor slot of {self._labware.get_display_name(labware_id)} with location {labware.location}"
            )

        return slot_name

    def get_ancestor_addressable_area_name(self, labware_id: str) -> str:
        """Get the name of the addressable area the labware is eventually on."""
        labware = self._labware.get(labware_id)
        original_display_name = self._labware.get_display_name(labware_id)
        seen: Set[str] = set((labware_id,))
        while isinstance(labware.location, OnLabwareLocation):
            labware = self._labware.get(labware.location.labwareId)
            if labware.id in seen:
                raise InvalidLabwarePositionError(
                    f"Cycle detected in labware positioning for {original_display_name}"
                )
            seen.add(labware.id)
        if isinstance(labware.location, DeckSlotLocation):
            return labware.location.slotName.id
        elif isinstance(labware.location, AddressableAreaLocation):
            return labware.location.addressableAreaName
        elif isinstance(labware.location, ModuleLocation):
            return self._modules.get_provided_addressable_area(
                labware.location.moduleId
            )
        else:
            raise LabwareNotOnDeckError(
                f"Labware {original_display_name} is not loaded on deck",
                details={"eventual-location": repr(labware.location)},
            )

    def ensure_location_not_occupied(
        self,
        location: _LabwareLocation,
        desired_addressable_area: Optional[str] = None,
    ) -> _LabwareLocation:
        """Ensure that the location does not already have either Labware or a Module in it."""
        # Collect set of existing fixtures, if any
        existing_fixtures = self._get_potential_fixtures_for_location_occupation(
            location
        )
        potential_fixtures = (
            self._get_potential_fixtures_for_location_occupation(
                AddressableAreaLocation(addressableAreaName=desired_addressable_area)
            )
            if desired_addressable_area is not None
            else None
        )

        # Handle the checking conflict on an incoming fixture
        if potential_fixtures is not None and isinstance(location, DeckSlotLocation):
            if (
                existing_fixtures is not None
                and not any(
                    location.slotName.id in fixture.provided_addressable_areas
                    for fixture in potential_fixtures[1].intersection(
                        existing_fixtures[1]
                    )
                )
            ) or (
                self._labware.get_by_slot(location.slotName) is not None
                and not any(
                    location.slotName.id in fixture.provided_addressable_areas
                    for fixture in potential_fixtures[1]
                )
            ):
                self._labware.raise_if_labware_in_location(location)

            else:
                self._modules.raise_if_module_in_location(location)

        # Otherwise handle standard conflict checking
        else:
            if isinstance(
                location,
                (
                    DeckSlotLocation,
                    ModuleLocation,
                    OnLabwareLocation,
                    AddressableAreaLocation,
                ),
            ):
                self._labware.raise_if_labware_in_location(location)

            area = (
                location.slotName.id
                if isinstance(location, DeckSlotLocation)
                else (
                    location.addressableAreaName
                    if isinstance(location, AddressableAreaLocation)
                    else None
                )
            )
            if area is not None and (
                existing_fixtures is None
                or not any(
                    area in fixture.provided_addressable_areas
                    for fixture in existing_fixtures[1]
                )
            ):
                if isinstance(location, DeckSlotLocation):
                    self._modules.raise_if_module_in_location(location)
                elif isinstance(location, AddressableAreaLocation):
                    self._modules.raise_if_module_in_location(
                        DeckSlotLocation(
                            slotName=self._addressable_areas.get_addressable_area_base_slot(
                                location.addressableAreaName
                            )
                        )
                    )

        return location

    def _get_potential_fixtures_for_location_occupation(
        self, location: _LabwareLocation
    ) -> Tuple[str, Set[PotentialCutoutFixture]] | None:
        loc: DeckSlotLocation | AddressableAreaLocation | None = None
        if isinstance(location, AddressableAreaLocation):
            # Convert the addressable area into a staging slot if applicable
            slots = StagingSlotName._value2member_map_
            for slot in slots:
                if location.addressableAreaName == slot:
                    loc = DeckSlotLocation(
                        slotName=DeckSlotName(location.addressableAreaName[0] + "3")
                    )
            if loc is None:
                loc = location
        elif isinstance(location, DeckSlotLocation):
            loc = location

        if isinstance(loc, DeckSlotLocation):
            module = self._modules.get_by_slot(loc.slotName)
            if module is not None and self._config.robot_type != "OT-2 Standard":
                fixtures = deck_configuration_provider.get_potential_cutout_fixtures(
                    addressable_area_name=self._modules.ensure_and_convert_module_fixture_location(
                        deck_slot=loc.slotName,
                        model=module.model,
                    ),
                    deck_definition=self._addressable_areas.deck_definition,
                )
            else:
                fixtures = None
        elif isinstance(loc, AddressableAreaLocation):
            fixtures = deck_configuration_provider.get_potential_cutout_fixtures(
                addressable_area_name=loc.addressableAreaName,
                deck_definition=self._addressable_areas.deck_definition,
            )
        else:
            fixtures = None
        return fixtures

    def _get_potential_disposal_location_cutout_fixtures(
        self, slot_name: DeckSlotName
    ) -> CutoutFixture | None:
        for area in self._addressable_areas.get_all():
            if (
                self._addressable_areas.get_addressable_area(area).area_type
                == AreaType.WASTE_CHUTE
                or self._addressable_areas.get_addressable_area(area).area_type
                == AreaType.MOVABLE_TRASH
            ) and slot_name == self._addressable_areas.get_addressable_area_base_slot(
                area
            ):
                # Given we only have one Waste Chute fixture and one type of Trash bin fixture it's
                # fine to return the first result of our potential fixtures here. This will need to
                # change in the future if there multiple trash fixtures that share the same area type.
                potential_fixture = (
                    deck_configuration_provider.get_potential_cutout_fixtures(
                        area, self._addressable_areas.deck_definition
                    )[1].pop()
                )
                return deck_configuration_provider.get_cutout_fixture(
                    potential_fixture.cutout_fixture_id,
                    self._addressable_areas.deck_definition,
                )
        return None

    def get_labware_grip_point(
        self,
        labware_definition: LabwareDefinition,
        location: Union[
            DeckSlotLocation, ModuleLocation, OnLabwareLocation, AddressableAreaLocation
        ],
    ) -> Point:
        """Get the grip point of the labware as placed on the given location.

        Returns the absolute position of the labware's gripping point as if
        it were placed on the specified location. Labware offset (LPC offset) not included.

        Grip point is the location where critical point of the gripper should move to
        in order to pick/drop the given labware in the specified location.
        It is calculated as the xy center of the slot with z as the point indicated by
        z-position of labware bottom + grip height from labware bottom.
        """
        grip_z_from_lw_origin = self._labware.get_grip_z(labware_definition)
        aa_name = self._get_underlying_addressable_area_name(location)
        parent_to_lw_offset = self._get_stackup_placement_origin_to_lw_origin(
            location=location,
            definition=labware_definition,
            is_topmost_labware=True,  # We aren't concerned with entities above the gripped labware.
        )
        addressable_area = self._addressable_areas.get_addressable_area(aa_name)
        lw_origin_to_parent = self._get_lw_origin_to_parent(
            labware_definition=labware_definition, addressable_area=addressable_area
        )
        mod_cal_offset = self._get_calibrated_module_offset(location)
        location_center = self._addressable_areas.get_addressable_area_center(aa_name)

        return (
            location_center
            + parent_to_lw_offset
            + lw_origin_to_parent
            + mod_cal_offset
            + Point(0, 0, grip_z_from_lw_origin)
        )

    def _get_lw_origin_to_parent(
        self, labware_definition: LabwareDefinition, addressable_area: AddressableArea
    ) -> Point:
        if isinstance(labware_definition, LabwareDefinition2):
            return Point(0, 0, 0)
        else:
            bb_y = addressable_area.bounding_box.y
            bb_z = addressable_area.bounding_box.z
            return (
                Point(
                    x=0,
                    y=bb_y,
                    z=bb_z,
                )
                * -1
            )

    def get_extra_waypoints(
        self,
        location: Optional[CurrentPipetteLocation],
        to_slot: Union[DeckSlotName, StagingSlotName],
    ) -> List[Tuple[float, float]]:
        """Get extra waypoints for movement if thermocycler needs to be dodged."""
        if location is not None:
            if isinstance(location, CurrentWell):
                from_slot = self.get_ancestor_slot_name(location.labware_id)
            else:
                from_slot = self._addressable_areas.get_addressable_area_base_slot(
                    location.addressable_area_name
                )
            if self._modules.should_dodge_thermocycler(
                from_slot=from_slot, to_slot=to_slot
            ):

                middle_slot_fixture = (
                    self._addressable_areas.get_fixture_by_deck_slot_name(
                        DeckSlotName.SLOT_C2.to_equivalent_for_robot_type(
                            self._config.robot_type
                        )
                    )
                )
                if middle_slot_fixture is None:
                    middle_slot = DeckSlotName.SLOT_5.to_equivalent_for_robot_type(
                        self._config.robot_type
                    )
                    middle_slot_center = (
                        self._addressable_areas.get_addressable_area_center(
                            addressable_area_name=middle_slot.id,
                        )
                    )
                else:
                    # todo(chb, 2025-07-30): For now we're defaulting to the first addressable area for these center slot fixtures, but
                    # if we ever introduce a fixture in the center slot with many addressable areas that aren't "centered" over the deck
                    # slot we will enter up generating a pretty whacky movement path (potentially dangerous).
                    middle_slot_center = self._addressable_areas.get_addressable_area_center(
                        addressable_area_name=middle_slot_fixture[
                            "providesAddressableAreas"
                        ][
                            deck_configuration_provider.get_cutout_id_by_deck_slot_name(
                                DeckSlotName.SLOT_C2.to_equivalent_for_robot_type(
                                    self._config.robot_type
                                )
                            )
                        ][
                            0
                        ],
                    )
                return [(middle_slot_center.x, middle_slot_center.y)]
        return []

    def get_slot_item(
        self, slot_name: Union[DeckSlotName, StagingSlotName]
    ) -> Union[LoadedLabware, LoadedModule, CutoutFixture, None]:
        """Get the top-most item present in a deck slot, if any.

        This includes any module that occupies the given slot even if it wasn't loaded
        in that slot (e.g., thermocycler).
        """
        maybe_labware = self._labware.get_by_slot(
            slot_name=slot_name,
        )

        if isinstance(slot_name, DeckSlotName):
            maybe_fixture = self._addressable_areas.get_fixture_by_deck_slot_name(
                slot_name
            )

            # Ignore generic single slot fixtures
            if maybe_fixture and maybe_fixture["id"] in {
                "singleLeftSlot",
                "singleCenterSlot",
                "singleRightSlot",
            }:
                maybe_fixture = None

            maybe_module = self._modules.get_by_slot(
                slot_name=slot_name,
            ) or self._modules.get_overflowed_module_in_slot(slot_name=slot_name)

            # For situations in which the deck config is none
            if maybe_fixture is None and maybe_labware is None and maybe_module is None:
                # todo(chb 2025-03-19): This can go away once we solve the problem of no deck config in analysis
                maybe_fixture = self._get_potential_disposal_location_cutout_fixtures(
                    slot_name
                )
        else:
            # Modules and fixtures can't be loaded on staging slots
            maybe_fixture = None
            maybe_module = None

        return maybe_labware or maybe_module or maybe_fixture or None

    @staticmethod
    def get_slot_column(slot_name: Union[DeckSlotName, StagingSlotName]) -> int:
        """Get the column number for the specified slot."""
        if isinstance(slot_name, StagingSlotName):
            return 4
        row_col_name = slot_name.to_ot3_equivalent()
        slot_name_match = WELL_NAME_PATTERN.match(row_col_name.value)
        assert (
            slot_name_match is not None
        ), f"Slot name {row_col_name} did not match required pattern; please check labware location."

        row_name, column_name = slot_name_match.group(1, 2)
        return int(column_name)

    def get_next_tip_drop_location(
        self, labware_id: str, well_name: str, pipette_id: str
    ) -> DropTipWellLocation:
        """Get the next location within the specified well to drop the tip into.

        In order to prevent tip stacking, we will alternate between two tip drop locations:
        1. location in left section: a safe distance from left edge of the well
        2. location in right section: a safe distance from right edge of the well

        This safe distance for most cases would be a location where all tips drop
        reliably inside the labware's well. This can be calculated based off of the
        span of a pipette, including all its tips, in the x-direction.

        But we also need to account for the not-so-uncommon case of a left pipette
        trying to drop tips in a labware in the rightmost deck column and vice versa.
        If this labware extends beyond a regular deck slot, like the Flex's default trash,
        then even after keeping a margin for x-span of a pipette, we will get
        a location that's unreachable for the pipette. In such cases, we try to drop tips
        at the rightmost location that a left pipette is able to reach,
        and leftmost location that a right pipette is able to reach respectively.

        In these calculations we assume that the critical point of a pipette
        is considered to be the midpoint of the pipette's tip for single channel,
        and the midpoint of the entire tip assembly for multi-channel pipettes.
        We also assume that the pipette_x_span includes any safety margins required.
        """
        if not self._labware.is_fixed_trash(labware_id=labware_id):
            # In order to avoid the complexity of finding tip drop locations for
            # variety of labware with different well configs, we will allow
            # location cycling only for fixed trash labware right now.
            # TODO (spp, 2023-09-12): update this to possibly a labware-width based check,
            #  or a 'trash' quirk check, once movable trash is implemented.
            return DropTipWellLocation(
                origin=DropTipWellOrigin.DEFAULT,
                offset=WellOffset(x=0, y=0, z=0),
            )

        well_x_dim = self._labware.get_well_size(
            labware_id=labware_id, well_name=well_name
        )[0]
        pipette_channels = self._pipettes.get_config(pipette_id).channels
        pipette_mount = self._pipettes.get_mount(pipette_id)

        labware_slot_column = self.get_slot_column(
            slot_name=self.get_ancestor_slot_name(labware_id)
        )

        if self._last_drop_tip_location_spot.get(labware_id) == _TipDropSection.RIGHT:
            # Drop tip in LEFT section
            x_offset = self._get_drop_tip_well_x_offset(
                tip_drop_section=_TipDropSection.LEFT,
                well_x_dim=well_x_dim,
                pipette_channels=pipette_channels,
                pipette_mount=pipette_mount,
                labware_slot_column=labware_slot_column,
            )
            self._last_drop_tip_location_spot[labware_id] = _TipDropSection.LEFT
        else:
            # Drop tip in RIGHT section
            x_offset = self._get_drop_tip_well_x_offset(
                tip_drop_section=_TipDropSection.RIGHT,
                well_x_dim=well_x_dim,
                pipette_channels=pipette_channels,
                pipette_mount=pipette_mount,
                labware_slot_column=labware_slot_column,
            )
            self._last_drop_tip_location_spot[labware_id] = _TipDropSection.RIGHT

        return DropTipWellLocation(
            origin=DropTipWellOrigin.TOP,
            offset=WellOffset(
                x=x_offset,
                y=0,
                z=0,
            ),
        )

    # TODO find way to combine this with above
    def get_next_tip_drop_location_for_addressable_area(
        self,
        addressable_area_name: str,
        pipette_id: str,
    ) -> AddressableOffsetVector:
        """Get the next location within the specified well to drop the tip into.

        See the doc-string for `get_next_tip_drop_location` for more info on execution.
        """
        area_x_dim = self._addressable_areas.get_addressable_area(
            addressable_area_name
        ).bounding_box.x

        pipette_channels = self._pipettes.get_config(pipette_id).channels
        pipette_mount = self._pipettes.get_mount(pipette_id)

        labware_slot_column = self.get_slot_column(
            slot_name=self._addressable_areas.get_addressable_area_base_slot(
                addressable_area_name
            )
        )

        if (
            self._last_drop_tip_location_spot.get(addressable_area_name)
            == _TipDropSection.RIGHT
        ):
            # Drop tip in LEFT section
            x_offset = self._get_drop_tip_well_x_offset(
                tip_drop_section=_TipDropSection.LEFT,
                well_x_dim=area_x_dim,
                pipette_channels=pipette_channels,
                pipette_mount=pipette_mount,
                labware_slot_column=labware_slot_column,
            )
            self._last_drop_tip_location_spot[
                addressable_area_name
            ] = _TipDropSection.LEFT
        else:
            # Drop tip in RIGHT section
            x_offset = self._get_drop_tip_well_x_offset(
                tip_drop_section=_TipDropSection.RIGHT,
                well_x_dim=area_x_dim,
                pipette_channels=pipette_channels,
                pipette_mount=pipette_mount,
                labware_slot_column=labware_slot_column,
            )
            self._last_drop_tip_location_spot[
                addressable_area_name
            ] = _TipDropSection.RIGHT

        return AddressableOffsetVector(x=x_offset, y=0, z=0)

    @staticmethod
    def _get_drop_tip_well_x_offset(
        tip_drop_section: _TipDropSection,
        well_x_dim: float,
        pipette_channels: int,
        pipette_mount: MountType,
        labware_slot_column: int,
    ) -> float:
        """Get the well x offset for DropTipWellLocation."""
        drop_location_margin_from_labware_edge = (
            PIPETTE_X_SPAN[cast(ChannelCount, pipette_channels)] / 2
        )
        if tip_drop_section == _TipDropSection.LEFT:
            if (
                well_x_dim > SLOT_WIDTH
                and pipette_channels != 96
                and pipette_mount == MountType.RIGHT
                and labware_slot_column == 1
            ):
                # Pipette might not reach the default left spot so use a different left spot
                x_well_offset = (
                    -well_x_dim / 2 + drop_location_margin_from_labware_edge * 2
                )
            else:
                x_well_offset = -well_x_dim / 2 + drop_location_margin_from_labware_edge
                if x_well_offset > 0:
                    x_well_offset = 0
        else:
            if (
                well_x_dim > SLOT_WIDTH
                and pipette_channels != 96
                and pipette_mount == MountType.LEFT
                and labware_slot_column == 3
            ):
                # Pipette might not reach the default right spot so use a different right spot
                x_well_offset = (
                    -well_x_dim / 2
                    + SLOT_WIDTH
                    - drop_location_margin_from_labware_edge
                )
            else:
                x_well_offset = well_x_dim / 2 - drop_location_margin_from_labware_edge
                if x_well_offset < 0:
                    x_well_offset = 0
        return x_well_offset

    def get_final_labware_movement_offset_vectors(
        self,
        from_location: OnDeckLabwareLocation,
        to_location: OnDeckLabwareLocation,
        additional_pick_up_offset: Point,
        additional_drop_offset: Point,
        current_labware: LabwareDefinition,
    ) -> LabwareMovementOffsetData:
        """Calculate the final labware offset vector to use in labware movement."""
        pick_up_offset = (
            self.get_total_nominal_gripper_offset_for_move_type(
                location=from_location,
                move_type=_GripperMoveType.PICK_UP_LABWARE,
                current_labware=current_labware,
            )
            + additional_pick_up_offset
        )
        drop_offset = (
            self.get_total_nominal_gripper_offset_for_move_type(
                location=to_location,
                move_type=_GripperMoveType.DROP_LABWARE,
                current_labware=current_labware,
            )
            + additional_drop_offset
        )

        return LabwareMovementOffsetData(
            pickUpOffset=LabwareOffsetVector(
                x=pick_up_offset.x, y=pick_up_offset.y, z=pick_up_offset.z
            ),
            dropOffset=LabwareOffsetVector(
                x=drop_offset.x, y=drop_offset.y, z=drop_offset.z
            ),
        )

    @staticmethod
    def ensure_valid_gripper_location(
        location: LabwareLocation,
    ) -> Union[
        DeckSlotLocation, ModuleLocation, OnLabwareLocation, AddressableAreaLocation
    ]:
        """Ensure valid on-deck location for gripper, otherwise raise error."""
        if not isinstance(
            location,
            (
                DeckSlotLocation,
                ModuleLocation,
                OnLabwareLocation,
                AddressableAreaLocation,
            ),
        ):
            raise errors.LabwareMovementNotAllowedError(
                "Off-deck labware movements are not supported using the gripper."
            )
        return location

    def get_total_nominal_gripper_offset_for_move_type(
        self,
        location: OnDeckLabwareLocation,
        move_type: _GripperMoveType,
        current_labware: LabwareDefinition,
    ) -> Point:
        """Get the total of the offsets to be used to pick up labware in its current location."""
        if move_type == _GripperMoveType.PICK_UP_LABWARE:
            if isinstance(
                location, (ModuleLocation, DeckSlotLocation, AddressableAreaLocation)
            ):
                return Point.from_xyz_attrs(
                    self._nominal_gripper_offsets_for_location(location).pickUpOffset
                )
            else:
                # If it's a labware on a labware (most likely an adapter),
                # we calculate the offset as sum of offsets for the direct parent labware
                # and the underlying non-labware parent location.
                direct_parent_offset = self._nominal_gripper_offsets_for_location(
                    location
                )
                ancestor = self._labware.get_parent_location(location.labwareId)
                extra_offset = Point(x=0, y=0, z=0)
                if (
                    isinstance(ancestor, ModuleLocation)
                    # todo(mm, 2025-06-20): Avoid this private attribute access.
                    and self._modules._state.requested_model_by_id[ancestor.moduleId]
                    == ModuleModel.THERMOCYCLER_MODULE_V2
                    and labware_validation.validate_definition_is_lid(current_labware)
                ):
                    if "lidOffsets" in current_labware.gripperOffsets.keys():
                        extra_offset = Point(
                            x=current_labware.gripperOffsets[
                                "lidOffsets"
                            ].pickUpOffset.x,
                            y=current_labware.gripperOffsets[
                                "lidOffsets"
                            ].pickUpOffset.y,
                            z=current_labware.gripperOffsets[
                                "lidOffsets"
                            ].pickUpOffset.z,
                        )
                    else:
                        raise errors.LabwareOffsetDoesNotExistError(
                            f"Labware Definition {current_labware.parameters.loadName} does not contain required field 'lidOffsets' of 'gripperOffsets'."
                        )

                assert isinstance(
                    ancestor,
                    (
                        DeckSlotLocation,
                        ModuleLocation,
                        OnLabwareLocation,
                        AddressableAreaLocation,
                    ),
                ), "No gripper offsets for off-deck labware"
                return (
                    Point.from_xyz_attrs(direct_parent_offset.pickUpOffset)
                    + Point.from_xyz_attrs(
                        self._nominal_gripper_offsets_for_location(
                            location=ancestor
                        ).pickUpOffset
                    )
                    + extra_offset
                )
        else:
            if isinstance(
                location, (ModuleLocation, DeckSlotLocation, AddressableAreaLocation)
            ):
                return Point.from_xyz_attrs(
                    self._nominal_gripper_offsets_for_location(location).dropOffset
                )
            else:
                # If it's a labware on a labware (most likely an adapter),
                # we calculate the offset as sum of offsets for the direct parent labware
                # and the underlying non-labware parent location.
                direct_parent_offset = self._nominal_gripper_offsets_for_location(
                    location
                )
                ancestor = self._labware.get_parent_location(location.labwareId)
                extra_offset = Point(x=0, y=0, z=0)
                if (
                    isinstance(ancestor, ModuleLocation)
                    # todo(mm, 2024-11-06): Do not access private module state; only use public ModuleView methods.
                    and self._modules._state.requested_model_by_id[ancestor.moduleId]
                    == ModuleModel.THERMOCYCLER_MODULE_V2
                    and labware_validation.validate_definition_is_lid(current_labware)
                ):
                    if "lidOffsets" in current_labware.gripperOffsets.keys():
                        extra_offset = Point(
                            x=current_labware.gripperOffsets[
                                "lidOffsets"
                            ].pickUpOffset.x,
                            y=current_labware.gripperOffsets[
                                "lidOffsets"
                            ].pickUpOffset.y,
                            z=current_labware.gripperOffsets[
                                "lidOffsets"
                            ].pickUpOffset.z,
                        )
                    else:
                        raise errors.LabwareOffsetDoesNotExistError(
                            f"Labware Definition {current_labware.parameters.loadName} does not contain required field 'lidOffsets' of 'gripperOffsets'."
                        )

                assert isinstance(
                    ancestor,
                    (
                        DeckSlotLocation,
                        ModuleLocation,
                        OnLabwareLocation,
                        AddressableAreaLocation,
                    ),
                ), "No gripper offsets for off-deck labware"
                return (
                    Point.from_xyz_attrs(direct_parent_offset.dropOffset)
                    + Point.from_xyz_attrs(
                        self._nominal_gripper_offsets_for_location(
                            location=ancestor
                        ).dropOffset
                    )
                    + extra_offset
                )

    # todo(mm, 2024-11-05): This may be incorrect because it does not take the following
    # offsets into account, which *are* taken into account for the actual gripper movement:
    #
    # * The pickup offset in the definition of the parent of the gripped labware.
    # * The "additional offset" or "user offset", e.g. the `pickUpOffset` and `dropOffset`
    #   params in the `moveLabware` command.
    #
    # For robustness, we should combine this with `get_gripper_labware_movement_waypoints()`.
    #
    # We should also be more explicit about which offsets act to move the gripper paddles
    # relative to the gripped labware, and which offsets act to change how the gripped
    # labware sits atop its parent. Those have different effects on how far the gripped
    # labware juts beyond the paddles while it's in transit.
    def check_gripper_labware_tip_collision(
        self,
        gripper_homed_position_z: float,
        labware_id: str,
        # todo(mm, 2025-07-31): arg unused, investigate or remove.
        current_location: OnDeckLabwareLocation,
    ) -> None:
        """Check for potential collision of tips against labware to be lifted."""
        labware_definition = self._labware.get_definition(labware_id)
        pipettes = self._pipettes.get_all()
        for pipette in pipettes:
            # TODO(cb, 2024-01-22): Remove the 1 and 8 channel special case once we are doing X axis validation
            if self._pipettes.get_channels(pipette.id) in [1, 8]:
                return

            tip = self._pipettes.get_attached_tip(pipette.id)
            if not tip:
                continue

            labware_origin_to_grip_point = self._labware.get_grip_z(labware_definition)
            grip_point_to_labware_origin = -labware_origin_to_grip_point
            height_above_labware_origin = self._labware.get_extents_around_lw_origin(
                labware_definition
            ).max_z
            labware_top_z_when_gripped = (
                gripper_homed_position_z
                + grip_point_to_labware_origin
                + height_above_labware_origin
            )

            # TODO(cb, 2024-01-18): Utilizing the nozzle map and labware X coordinates,
            # verify if collisions will occur on the X axis (analysis will use hard coded data
            # to measure from the gripper critical point to the pipette mount)
            if (_PIPETTE_HOMED_POSITION_Z - tip.length) < labware_top_z_when_gripped:
                raise LabwareMovementNotAllowedError(
                    f"Cannot move labware '{labware_definition.parameters.loadName}' when {int(tip.volume)} µL tips are attached."
                )

    def _nominal_gripper_offsets_for_location(
        self, location: OnDeckLabwareLocation
    ) -> LabwareMovementOffsetData:
        """Provide the default gripper offset data for the given location type."""
        if isinstance(location, (DeckSlotLocation, AddressableAreaLocation)):
            # TODO we might need a separate type of gripper offset for addressable areas but that also might just
            #   be covered by the drop labware offset/location
            offsets = self._labware.get_deck_default_gripper_offsets()
        elif isinstance(location, ModuleLocation):
            offsets = self._modules.get_default_gripper_offsets(location.moduleId)
        else:
            # Labware is on a labware/adapter
            offsets = self._labware_gripper_offsets(location.labwareId)
        return offsets or LabwareMovementOffsetData(
            pickUpOffset=LabwareOffsetVector(x=0, y=0, z=0),
            dropOffset=LabwareOffsetVector(x=0, y=0, z=0),
        )

    def _labware_gripper_offsets(
        self, labware_id: str
    ) -> Optional[LabwareMovementOffsetData]:
        """Provide the most appropriate gripper offset data for the specified labware.

        We check the types of gripper offsets available for the labware ("default" or slot-based)
        and return the most appropriate one for the overall location of the labware.
        Currently, only module adapters (specifically, the H/S universal flat adapter)
        have non-default offsets that are specific to location of the module on deck,
        so, this code only checks for the presence of those known offsets.
        """
        parent_location = self._labware.get_parent_location(labware_id)
        assert isinstance(
            parent_location,
            (
                DeckSlotLocation,
                ModuleLocation,
                AddressableAreaLocation,
                OnLabwareLocation,
            ),
        ), "No gripper offsets for off-deck labware"

        if isinstance(parent_location, DeckSlotLocation):
            slot_name = parent_location.slotName
        elif isinstance(parent_location, AddressableAreaLocation):
            slot_name = self._addressable_areas.get_addressable_area_base_slot(
                parent_location.addressableAreaName
            )
        else:
            module_loc = self._modules.get_location(parent_location.moduleId)
            slot_name = module_loc.slotName

        slot_based_offset = self._labware.get_child_gripper_offsets(
            labware_id=labware_id, slot_name=slot_name.to_ot3_equivalent()
        )

        return slot_based_offset or self._labware.get_child_gripper_offsets(
            labware_id=labware_id, slot_name=None
        )

    def get_location_sequence(self, labware_id: str) -> LabwareLocationSequence:
        """Provide the LocationSequence specifying the current position of the labware.

        Elements in this sequence contain instance IDs of things. The chain is valid only until the
        labware is moved.
        """
        return self.get_predicted_location_sequence(
            self._labware.get_location(labware_id)
        )

    def get_predicted_location_sequence(
        self,
        labware_location: LabwareLocation,
        labware_pending_load: dict[str, LoadedLabware] | None = None,
    ) -> LabwareLocationSequence:
        """Get the location sequence for this location. Useful for a labware that hasn't been loaded."""
        return self._recurse_labware_location(
            labware_location, [], labware_pending_load or {}
        )

    def _cutout_fixture_location_sequence_from_addressable_area(
        self, addressable_area_name: str
    ) -> OnCutoutFixtureLocationSequenceComponent:
        (
            cutout_id,
            potential_fixtures,
        ) = self._addressable_areas.get_current_potential_cutout_fixtures_for_addressable_area(
            addressable_area_name
        )
        return OnCutoutFixtureLocationSequenceComponent(
            possibleCutoutFixtureIds=sorted(
                [fixture.cutout_fixture_id for fixture in potential_fixtures]
            ),
            cutoutId=cutout_id,
        )

    def _recurse_labware_location_from_aa_component(
        self,
        labware_location: AddressableAreaLocation,
        building: LabwareLocationSequence,
    ) -> LabwareLocationSequence:
        cutout_location = self._cutout_fixture_location_sequence_from_addressable_area(
            labware_location.addressableAreaName
        )
        # If the labware is loaded on an AA that is a module, we want to respect the convention
        # of giving it an OnModuleLocation.
        possible_module = self._modules.get_by_addressable_area(
            labware_location.addressableAreaName
        )
        if possible_module is not None:
            return building + [
                OnAddressableAreaLocationSequenceComponent(
                    addressableAreaName=labware_location.addressableAreaName
                ),
                OnModuleLocationSequenceComponent(moduleId=possible_module.id),
                cutout_location,
            ]
        else:
            return building + [
                OnAddressableAreaLocationSequenceComponent(
                    addressableAreaName=labware_location.addressableAreaName,
                ),
                cutout_location,
            ]

    def _recurse_labware_location_from_module_component(
        self, labware_location: ModuleLocation, building: LabwareLocationSequence
    ) -> LabwareLocationSequence:
        module_id = labware_location.moduleId
        module_aa = self._modules.get_provided_addressable_area(module_id)
        base_location: (
            OnCutoutFixtureLocationSequenceComponent
            | NotOnDeckLocationSequenceComponent
        ) = self._cutout_fixture_location_sequence_from_addressable_area(module_aa)

        if self._modules.get_deck_supports_module_fixtures():
            # On a deck with modules as cutout fixtures, we want, in order,
            # - the addressable area of the module
            # - the module with its module id, which is what clients want
            # - the cutout
            loc = self._modules.get_location(module_id)
            model = self._modules.get_connected_model(module_id)
            module_aa = self._modules.ensure_and_convert_module_fixture_location(
                loc.slotName, model
            )
            return building + [
                OnAddressableAreaLocationSequenceComponent(
                    addressableAreaName=module_aa
                ),
                OnModuleLocationSequenceComponent(moduleId=module_id),
                base_location,
            ]
        else:
            # If the module isn't a cutout fixture, then we want
            # - the module
            # - the addressable area the module is loaded on
            # - the cutout
            location = self._modules.get_location(module_id)
            return building + [
                OnModuleLocationSequenceComponent(moduleId=module_id),
                OnAddressableAreaLocationSequenceComponent(
                    addressableAreaName=location.slotName.value
                ),
                base_location,
            ]

    def _recurse_labware_location_from_stacker_hopper(
        self,
        labware_location: InStackerHopperLocation,
        building: LabwareLocationSequence,
    ) -> LabwareLocationSequence:
        loc = self._modules.get_location(labware_location.moduleId)
        model = self._modules.get_connected_model(labware_location.moduleId)
        module_aa = self._modules.ensure_and_convert_module_fixture_location(
            loc.slotName, model
        )
        cutout_base = self._cutout_fixture_location_sequence_from_addressable_area(
            module_aa
        )
        return building + [labware_location, cutout_base]

    def _recurse_labware_location(
        self,
        labware_location: LabwareLocation,
        building: LabwareLocationSequence,
        labware_pending_load: dict[str, LoadedLabware],
    ) -> LabwareLocationSequence:
        if isinstance(labware_location, AddressableAreaLocation):
            return self._recurse_labware_location_from_aa_component(
                labware_location, building
            )
        elif labware_location_is_off_deck(
            labware_location
        ) or labware_location_is_system(labware_location):
            return building + [
                NotOnDeckLocationSequenceComponent(logicalLocationName=labware_location)
            ]

        elif isinstance(labware_location, OnLabwareLocation):
            labware = self._get_or_default_labware(
                labware_location.labwareId, labware_pending_load
            )
            return self._recurse_labware_location(
                labware.location,
                building
                + [
                    OnLabwareLocationSequenceComponent(
                        labwareId=labware_location.labwareId, lidId=labware.lid_id
                    )
                ],
                labware_pending_load,
            )
        elif isinstance(labware_location, ModuleLocation):
            return self._recurse_labware_location_from_module_component(
                labware_location, building
            )
        elif isinstance(labware_location, DeckSlotLocation):
            return building + [
                OnAddressableAreaLocationSequenceComponent(
                    addressableAreaName=labware_location.slotName.value,
                ),
                self._cutout_fixture_location_sequence_from_addressable_area(
                    labware_location.slotName.value
                ),
            ]
        elif isinstance(labware_location, InStackerHopperLocation):
            return self._recurse_labware_location_from_stacker_hopper(
                labware_location, building
            )
        else:
            _LOG.warn(f"Unhandled labware location kind: {labware_location}")
            return building

    def get_offset_location(
        self, labware_id: str
    ) -> Optional[LabwareOffsetLocationSequence]:
        """Provide the LegacyLabwareOffsetLocation specifying the current position of the labware.

        If the labware is in a location that cannot be specified by a LabwareOffsetLocationSequence
        (for instance, OFF_DECK) then return None.
        """
        parent_location = self._labware.get_location(labware_id)
        return self.get_projected_offset_location(parent_location)

    def get_projected_offset_location(
        self,
        labware_location: LabwareLocation,
        labware_pending_load: dict[str, LoadedLabware] | None = None,
    ) -> Optional[LabwareOffsetLocationSequence]:
        """Get the offset location that a labware loaded into this location would match.

        `None` indicates that the very concept of a labware offset would not make sense
        for the given location, such as if it's some kind of off-deck location. This
        is a difference from `get_predicted_location_sequence()`, where off-deck
        locations are still represented as lists, but with special final elements.
        """
        return self._recurse_labware_offset_location(
            labware_location, [], labware_pending_load or {}
        )

    def _recurse_labware_offset_location(
        self,
        labware_location: LabwareLocation,
        building: LabwareOffsetLocationSequence,
        labware_pending_load: dict[str, LoadedLabware],
    ) -> LabwareOffsetLocationSequence | None:
        if isinstance(labware_location, DeckSlotLocation):
            return building + [
                OnAddressableAreaOffsetLocationSequenceComponent(
                    addressableAreaName=labware_location.slotName.value
                )
            ]

        elif isinstance(labware_location, ModuleLocation):
            module_id = labware_location.moduleId
            # Allow ModuleNotLoadedError to propagate.
            # Note also that we match based on the module's requested model, not its
            # actual model, to implement robot-server's documented HTTP API semantics.
            module_model = self._modules.get_requested_model(module_id=module_id)

            # If `module_model is None`, it probably means that this module was added by
            # `ProtocolEngine.use_attached_modules()`, instead of an explicit
            # `loadModule` command.
            #
            # This assert should never raise in practice because:
            #   1. `ProtocolEngine.use_attached_modules()` is only used by
            #      robot-server's "stateless command" endpoints, under `/commands`.
            #   2. Those endpoints don't support loading labware, so this code will
            #      never run.
            #
            # Nevertheless, if it does happen somehow, we do NOT want to pass the
            # `None` value along to `LabwareView.find_applicable_labware_offset()`.
            # `None` means something different there, which will cause us to return
            # wrong results.
            assert module_model is not None, (
                "Can't find offsets for labware"
                " that are loaded on modules"
                " that were loaded with ProtocolEngine.use_attached_modules()."
            )

            module_location = self._modules.get_location(module_id=module_id)
            if self._modules.get_deck_supports_module_fixtures():
                module_aa = self._modules.ensure_and_convert_module_fixture_location(
                    module_location.slotName, module_model
                )
            else:
                module_aa = module_location.slotName.value
            return building + [
                OnModuleOffsetLocationSequenceComponent(moduleModel=module_model),
                OnAddressableAreaOffsetLocationSequenceComponent(
                    addressableAreaName=module_aa
                ),
            ]

        elif isinstance(labware_location, OnLabwareLocation):
            parent_labware_id = labware_location.labwareId
            parent_labware = self._get_or_default_labware(
                parent_labware_id, labware_pending_load
            )
            parent_labware_uri = LabwareUri(parent_labware.definitionUri)
            base_location = parent_labware.location
            return self._recurse_labware_offset_location(
                base_location,
                building
                + [
                    OnLabwareOffsetLocationSequenceComponent(
                        labwareUri=parent_labware_uri
                    )
                ],
                labware_pending_load,
            )

        else:  # Off deck
            return None

    def get_liquid_handling_z_change(
        self,
        labware_id: str,
        well_name: str,
        pipette_id: str,
        operation_volume: float,
    ) -> float:
        """Get the change in height from a liquid handling operation."""
        initial_handling_height = self.get_meniscus_height(
            labware_id=labware_id, well_name=well_name
        )
        final_height = self.get_well_height_after_liquid_handling(
            labware_id=labware_id,
            well_name=well_name,
            pipette_id=pipette_id,
            initial_height=initial_handling_height,
            volume=operation_volume,
        )
        # this function is only called by
        # HardwarePipetteHandler::aspirate/dispense while_tracking, and shouldn't
        # be reached in the case of a simulated liquid_probe
        assert not isinstance(
            initial_handling_height, SimulatedProbeResult
        ), "Initial handling height got SimulatedProbeResult"
        assert not isinstance(
            final_height, SimulatedProbeResult
        ), "final height is SimulatedProbeResult"
        return final_height - initial_handling_height

    def get_well_offset_adjustment(
        self,
        labware_id: str,
        well_name: str,
        well_location: WellLocationType,
        well_depth: float,
        pipette_id: Optional[str] = None,
        operation_volume: Optional[float] = None,
    ) -> LiquidTrackingType:
        """Return a z-axis distance that accounts for well handling height and operation volume.

        Distance is with reference to the well bottom.
        """
        # TODO(pbm, 10-23-24): refactor to smartly reduce height/volume conversions

        initial_handling_height = self.get_well_handling_height(
            labware_id=labware_id,
            well_name=well_name,
            well_location=well_location,
            well_depth=well_depth,
        )
        # if we're tracking a MENISCUS origin, and targeting either the beginning
        #   position of the liquid or doing dynamic tracking, return the initial height
        if (
            well_location.origin == WellOrigin.MENISCUS
            and not well_location.volumeOffset
        ):
            return initial_handling_height
        volume: Optional[float] = None
        if isinstance(well_location, PickUpTipWellLocation):
            volume = 0.0
        elif isinstance(well_location, LiquidHandlingWellLocation):
            if well_location.volumeOffset == "operationVolume":
                volume = operation_volume or 0.0
            else:
                if not isinstance(well_location.volumeOffset, float):
                    raise ValueError("Invalid volume offset.")
                volume = well_location.volumeOffset

        if volume:
            if pipette_id is None:
                raise ValueError(
                    "cannot get liquid handling offset without pipette id."
                )
            liquid_height_after = self.get_well_height_after_liquid_handling(
                labware_id=labware_id,
                well_name=well_name,
                pipette_id=pipette_id,
                initial_height=initial_handling_height,
                volume=volume,
            )
            return liquid_height_after
        else:
            return initial_handling_height

    def get_current_well_volume(
        self,
        labware_id: str,
        well_name: str,
    ) -> LiquidTrackingType:
        """Returns most recently updated volume in specified well."""
        last_updated = self._wells.get_last_liquid_update(labware_id, well_name)
        if last_updated is None:
            raise errors.LiquidHeightUnknownError(
                "Must LiquidProbe or LoadLiquid before specifying WellOrigin.MENISCUS."
            )

        well_liquid = self._wells.get_well_liquid_info(
            labware_id=labware_id, well_name=well_name
        )
        if (
            well_liquid.probed_height is not None
            and well_liquid.probed_height.height is not None
            and well_liquid.probed_height.last_probed == last_updated
        ):
            volume = self.get_well_volume_at_height(
                labware_id=labware_id,
                well_name=well_name,
                height=well_liquid.probed_height.height,
            )
            return volume
        elif (
            well_liquid.loaded_volume is not None
            and well_liquid.loaded_volume.volume is not None
            and well_liquid.loaded_volume.last_loaded == last_updated
        ):
            return well_liquid.loaded_volume.volume
        elif (
            well_liquid.probed_volume is not None
            and well_liquid.probed_volume.volume is not None
            and well_liquid.probed_volume.last_probed == last_updated
        ):
            return well_liquid.probed_volume.volume
        else:
            # This should not happen if there was an update but who knows
            raise errors.LiquidVolumeUnknownError(
                f"Unable to find liquid volume despite an update at {last_updated}."
            )

    def get_meniscus_height(
        self,
        labware_id: str,
        well_name: str,
    ) -> LiquidTrackingType:
        """Returns stored meniscus height in specified well."""
        last_updated = self._wells.get_last_liquid_update(labware_id, well_name)
        if last_updated is None:
            raise errors.LiquidHeightUnknownError(
                "Must LiquidProbe or LoadLiquid before specifying WellOrigin.MENISCUS."
            )

        well_liquid = self._wells.get_well_liquid_info(
            labware_id=labware_id, well_name=well_name
        )
        if (
            well_liquid.probed_height is not None
            and well_liquid.probed_height.height is not None
            and well_liquid.probed_height.last_probed == last_updated
        ):
            return well_liquid.probed_height.height
        elif (
            well_liquid.loaded_volume is not None
            and well_liquid.loaded_volume.volume is not None
            and well_liquid.loaded_volume.last_loaded == last_updated
        ):
            return self.get_well_height_at_volume(
                labware_id=labware_id,
                well_name=well_name,
                volume=well_liquid.loaded_volume.volume,
            )
        elif (
            well_liquid.probed_volume is not None
            and well_liquid.probed_volume.volume is not None
            and well_liquid.probed_volume.last_probed == last_updated
        ):
            return self.get_well_height_at_volume(
                labware_id=labware_id,
                well_name=well_name,
                volume=well_liquid.probed_volume.volume,
            )
        else:
            # This should not happen if there was an update but who knows
            raise errors.LiquidHeightUnknownError(
                f"Unable to find liquid height despite an update at {last_updated}."
            )

    def get_well_handling_height(
        self,
        labware_id: str,
        well_name: str,
        well_location: WellLocationType,
        well_depth: float,
    ) -> LiquidTrackingType:
        """Return the handling height for a labware well (with reference to the well bottom)."""
        handling_height: LiquidTrackingType = 0.0
        if well_location.origin == WellOrigin.TOP:
            handling_height = float(well_depth)
        elif well_location.origin == WellOrigin.CENTER:
            handling_height = float(well_depth / 2.0)
        elif well_location.origin == WellOrigin.MENISCUS:
            handling_height = self.get_meniscus_height(
                labware_id=labware_id, well_name=well_name
            )
        return handling_height

    def find_volume_at_well_height(
        self,
        labware_id: str,
        well_name: str,
        target_height: LiquidTrackingType,
    ) -> LiquidTrackingType:
        """Call the correct volume from height function based on well geoemtry type."""
        well_geometry = self._labware.get_well_geometry(
            labware_id=labware_id, well_name=well_name
        )
        if isinstance(well_geometry, InnerWellGeometry):
            return find_volume_inner_well_geometry(
                target_height=target_height, well_geometry=well_geometry
            )
        else:
            return find_volume_user_defined_volumes(
                target_height=target_height, well_geometry=well_geometry
            )

    def find_height_at_well_volume(
        self,
        labware_id: str,
        well_name: str,
        target_volume: LiquidTrackingType,
    ) -> LiquidTrackingType:
        """Call the correct height from volume function based on well geometry type."""
        well_geometry = self._labware.get_well_geometry(
            labware_id=labware_id, well_name=well_name
        )
        if isinstance(well_geometry, InnerWellGeometry):
            return find_height_inner_well_geometry(
                target_volume=target_volume, well_geometry=well_geometry
            )
        else:
            return find_height_user_defined_volumes(
                target_volume=target_volume, well_geometry=well_geometry
            )

    def get_well_height_after_liquid_handling(
        self,
        labware_id: str,
        well_name: str,
        pipette_id: str,
        initial_height: LiquidTrackingType,
        volume: float,
    ) -> LiquidTrackingType:
        """Return the height of liquid in a labware well after a given volume has been handled.

        This is given an initial handling height, with reference to the well bottom.
        """
        well_def = self._labware.get_well_definition(labware_id, well_name)
        well_depth = well_def.depth

        try:
            initial_volume = self.find_volume_at_well_height(
                labware_id=labware_id, well_name=well_name, target_height=initial_height
            )
            final_volume = initial_volume + (
                volume
                * self.get_nozzles_per_well(
                    labware_id=labware_id,
                    target_well_name=well_name,
                    pipette_id=pipette_id,
                )
            )
            # NOTE(cm): if final_volume is outside the bounds of the well, it will get
            # adjusted inside find_height_at_well_volume to accomodate well the height
            # calculation.
            height_inside_well = self.find_height_at_well_volume(
                labware_id=labware_id, well_name=well_name, target_volume=final_volume
            )
            return self._validate_well_position(
                target_height=height_inside_well,
                well_max_height=well_depth,
                pipette_id=pipette_id,
            )
        except InvalidLiquidHeightFound as _exception:
            raise InvalidLiquidHeightFound(
                message=_exception.message
                + f"for well {well_name} of {self._labware.get_display_name(labware_id)} on slot {self.get_ancestor_slot_name(labware_id)}"
            )

    def get_well_height_at_volume(
        self, labware_id: str, well_name: str, volume: LiquidTrackingType
    ) -> LiquidTrackingType:
        """Convert well volume to height."""
        try:
            return self.find_height_at_well_volume(
                labware_id=labware_id, well_name=well_name, target_volume=volume
            )
        except InvalidLiquidHeightFound as _exception:
            raise InvalidLiquidHeightFound(
                message=_exception.message
                + f"for well {well_name} of {self._labware.get_display_name(labware_id)} on slot {self.get_ancestor_slot_name(labware_id)}"
            )

    def get_well_volume_at_height(
        self,
        labware_id: str,
        well_name: str,
        height: LiquidTrackingType,
    ) -> LiquidTrackingType:
        """Convert well height to volume."""
        try:
            return self.find_volume_at_well_height(
                labware_id=labware_id, well_name=well_name, target_height=height
            )
        except InvalidLiquidHeightFound as _exception:
            raise InvalidLiquidHeightFound(
                message=_exception.message
                + f"for well {well_name} of {self._labware.get_display_name(labware_id)} on slot {self.get_ancestor_slot_name(labware_id)}"
            )

    def validate_dispense_volume_into_well(
        self,
        labware_id: str,
        well_name: str,
        well_location: WellLocationType,
        volume: float,
    ) -> None:
        """Raise InvalidDispenseVolumeError if planned dispense volume will overflow well."""
        well_def = self._labware.get_well_definition(labware_id, well_name)
        well_volumetric_capacity = float(well_def.totalLiquidVolume)
        if well_location.origin == WellOrigin.MENISCUS:
            # TODO(pbm, 10-23-24): refactor to smartly reduce height/volume conversions
            meniscus_height = self.get_meniscus_height(
                labware_id=labware_id, well_name=well_name
            )
            try:
                meniscus_volume = self.find_volume_at_well_height(
                    labware_id=labware_id,
                    well_name=well_name,
                    target_height=meniscus_height,
                )
            except InvalidLiquidHeightFound as _exception:
                raise InvalidLiquidHeightFound(
                    message=_exception.message
                    + f"for well {well_name} of {self._labware.get_display_name(labware_id)} on slot {self.get_ancestor_slot_name(labware_id)}"
                )
            # if meniscus volume is a simulated value, comparisons aren't meaningful
            if isinstance(meniscus_volume, SimulatedProbeResult):
                return
            remaining_volume = well_volumetric_capacity - meniscus_volume
            if volume > remaining_volume:
                raise errors.InvalidDispenseVolumeError(
                    f"Attempting to dispense {volume}µL of liquid into a well that can currently only hold {remaining_volume}µL (well {well_name} in labware_id: {labware_id})"
                )
        else:
            # TODO(pbm, 10-08-24): factor in well (LabwareStore) state volume
            if volume > well_volumetric_capacity:
                raise errors.InvalidDispenseVolumeError(
                    f"Attempting to dispense {volume}µL of liquid into a well that can only hold {well_volumetric_capacity}µL (well {well_name} in labware_id: {labware_id})"
                )

    def get_wells_covered_by_pipette_with_active_well(
        self, labware_id: str, target_well_name: str, pipette_id: str
    ) -> list[str]:
        """Get a flat list of wells that are covered by a pipette when moved to a specified well.

        When you move a pipette in a multichannel configuration  to a specific well - the target well -
        the pipette will operate on other wells as well.

        For instance, a pipette with a COLUMN configuration with well A1 of an SBS standard labware target
        will also "cover", under this definition, wells B1-H1. That same pipette, when C5 is the target well, will "cover"
        wells C5-H5.

        This math only works, and may only be applied, if one of the following is true:
        - The pipette is in a SINGLE configuration
        - The pipette is in a non-SINGLE configuration, and the labware is an SBS-format 96 or 384 well plate (and is so
          marked in its definition's parameters.format key, as 96Standard or 384Standard)

        If all of the following do not apply, regardless of the nozzle configuration of the pipette this function will
        return only the labware covered by the primary well.
        """
        pipette_nozzle_map = self._pipettes.get_nozzle_configuration(pipette_id)
        labware_columns = [
            column for column in self._labware.get_definition(labware_id).ordering
        ]
        try:
            return list(
                wells_covered_by_pipette_configuration(
                    pipette_nozzle_map, target_well_name, labware_columns
                )
            )
        except InvalidStoredData:
            return [target_well_name]

    def get_nozzles_per_well(
        self, labware_id: str, target_well_name: str, pipette_id: str
    ) -> int:
        """Get the number of nozzles that will interact with each well."""
        return nozzles_per_well(
            self._pipettes.get_nozzle_configuration(pipette_id),
            target_well_name,
            self._labware.get_definition(labware_id).ordering,
        )

    def get_height_of_labware_stack(
        self, definitions: list[LabwareDefinition]
    ) -> float:
        """Get the overall height of a stack of labware listed by definition in top-first order."""
        if len(definitions) == 0:
            return 0
        if len(definitions) == 1:
            return self._labware.get_dimensions(labware_definition=definitions[0]).z
        total_height = 0.0
        upper_def: LabwareDefinition = definitions[0]
        for lower_def in definitions[1:]:
            overlap = self._labware.get_labware_overlap_offsets(
                upper_def, lower_def.parameters.loadName
            ).z
            total_height += (
                self._labware.get_dimensions(labware_definition=upper_def).z - overlap
            )
            upper_def = lower_def
        return (
            total_height + self._labware.get_dimensions(labware_definition=upper_def).z
        )
        return total_height + upper_def.dimensions.zDimension

    def get_height_of_stacker_labware_pool(self, module_id: str) -> float:
        """Get the overall height of a stack of labware in a Stacker module."""
        stacker = self._modules.get_flex_stacker_substate(module_id)
        pool_list = stacker.get_pool_definition_ordered_list()
        if not pool_list:
            return 0.0
        return self.get_height_of_labware_stack(pool_list)

    def _get_or_default_labware(
        self, labware_id: str, pending_labware: dict[str, LoadedLabware]
    ) -> LoadedLabware:
        try:
            return self._labware.get(labware_id)
        except LabwareNotLoadedError as lnle:
            try:
                return pending_labware[labware_id]
            except KeyError as ke:
                raise lnle from ke

    def raise_if_labware_inaccessible_by_pipette(  # noqa: C901
        self, labware_id: str
    ) -> None:
        """Raise an error if the specified location cannot be reached via a pipette."""
        labware = self._labware.get(labware_id)
        labware_location = labware.location
        if isinstance(labware_location, OnLabwareLocation):
            return self.raise_if_labware_inaccessible_by_pipette(
                labware_location.labwareId
            )
        elif labware.lid_id is not None:
            raise errors.LocationNotAccessibleByPipetteError(
                f"Cannot move pipette to {labware.loadName} "
                "because labware is currently covered by a lid."
            )
        elif isinstance(labware_location, AddressableAreaLocation):
            if fixture_validation.is_staging_slot(labware_location.addressableAreaName):
                raise errors.LocationNotAccessibleByPipetteError(
                    f"Cannot move pipette to {labware.loadName},"
                    f" labware is on staging slot {labware_location.addressableAreaName}"
                )
            elif fixture_validation.is_stacker_shuttle(
                labware_location.addressableAreaName
            ):
                raise errors.LocationNotAccessibleByPipetteError(
                    f"Cannot move pipette to {labware.loadName} because it is on a stacker shuttle"
                )
        elif (
            labware_location == OFF_DECK_LOCATION or labware_location == SYSTEM_LOCATION
        ):
            raise errors.LocationNotAccessibleByPipetteError(
                f"Cannot move pipette to {labware.loadName}, labware is off-deck."
            )
        elif isinstance(labware_location, ModuleLocation):
            module = self._modules.get(labware_location.moduleId)
            if ModuleModel.is_flex_stacker(module.model):
                raise errors.LocationNotAccessibleByPipetteError(
                    f"Cannot move pipette to {labware.loadName}, labware is on a stacker shuttle"
                )

        elif isinstance(labware_location, InStackerHopperLocation):
            raise errors.LocationNotAccessibleByPipetteError(
                f"Cannot move pipette to {labware.loadName}, labware is in a stacker hopper"
            )
