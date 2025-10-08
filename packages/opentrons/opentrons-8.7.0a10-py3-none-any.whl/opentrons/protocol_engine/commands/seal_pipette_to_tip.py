"""Seal tips to pipette command request, result, and implementation models."""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Type, Union

from typing_extensions import Literal
from pydantic import Field, BaseModel

from opentrons_shared_data.errors.exceptions import PositionUnknownError

from opentrons.types import MountType
from opentrons.protocol_engine.types import MotorAxis
from ..resources import ModelUtils, ensure_ot3_hardware
from ..types import PickUpTipWellLocation, FluidKind, AspiratedFluid, LabwareWellId
from .pipetting_common import (
    PipetteIdMixin,
)
from .movement_common import (
    DestinationPositionResult,
    StallOrCollisionError,
    move_to_well,
)
from .command import (
    AbstractCommandImpl,
    BaseCommand,
    BaseCommandCreate,
    DefinedErrorData,
    SuccessData,
)

from opentrons.hardware_control import HardwareControlAPI
from opentrons.hardware_control.types import Axis

if TYPE_CHECKING:
    from ..state.state import StateView
    from ..execution import (
        MovementHandler,
        TipHandler,
        GantryMover,
        PipettingHandler,
    )


SealPipetteToTipCommandType = Literal["sealPipetteToTip"]
_CAM_PREP_DISTANCE_DEFAULT = 8.25
_CAM_PRESS_DISTANCE_DEFAULT = 3.5
_CAM_EJECTOR_PUSH_MM_DEFAULT = 7.0
_PRESS_FIT_PREP_DISTANCE_DEFAULT = 0
_PRESS_FIT_PRESS_DISTANCE_DEFAULT = -11.0
_PRESS_FIT_EJECTOR_PUSH_MM_DEFAULT = 0
_SAFE_TOP_VOLUME = 1000


class TipPickUpParams(BaseModel):
    """Payload used to specify press-tip parameters for a seal command."""

    prepDistance: float = Field(
        default=0, description="The distance to move down to fit the tips on."
    )
    pressDistance: float = Field(
        default=0, description="The distance to press on tips."
    )
    ejectorPushMm: float = Field(
        default=0,
        description="The distance to back off to ensure that the tip presence sensors are not triggered.",
    )


class SealPipetteToTipParams(PipetteIdMixin):
    """Payload needed to seal resin tips to a pipette."""

    labwareId: str = Field(..., description="Identifier of labware to use.")
    wellName: str = Field(..., description="Name of well to use in labware.")
    wellLocation: PickUpTipWellLocation = Field(
        default_factory=PickUpTipWellLocation,
        description="Relative well location at which to pick up the tip.",
    )
    tipPickUpParams: Optional[TipPickUpParams] = Field(
        default=None, description="Specific parameters for "
    )


class SealPipetteToTipResult(DestinationPositionResult):
    """Result data from the execution of a SealPipetteToTip."""

    tipVolume: float = Field(
        0.0,
        description="Maximum volume of liquid that the picked up tip can hold, in µL.",
        ge=0.0,
    )

    tipLength: float = Field(
        0.0,
        description="The length of the tip in mm.",
        ge=0.0,
    )

    tipDiameter: float = Field(
        0.0,
        description="The diameter of the tip in mm.",
        ge=0.0,
    )


_ExecuteReturn = Union[
    SuccessData[SealPipetteToTipResult],
    DefinedErrorData[StallOrCollisionError],
]


class SealPipetteToTipImplementation(
    AbstractCommandImpl[SealPipetteToTipParams, _ExecuteReturn]
):
    """Seal pipette command implementation."""

    def __init__(
        self,
        state_view: StateView,
        tip_handler: TipHandler,
        model_utils: ModelUtils,
        movement: MovementHandler,
        hardware_api: HardwareControlAPI,
        gantry_mover: GantryMover,
        pipetting: PipettingHandler,
        **kwargs: object,
    ) -> None:
        self._state_view = state_view
        self._tip_handler = tip_handler
        self._model_utils = model_utils
        self._movement = movement
        self._gantry_mover = gantry_mover
        self._pipetting = pipetting
        self._hardware_api = hardware_api

    async def relative_pickup_tip(
        self,
        tip_pick_up_params: TipPickUpParams,
        mount: MountType,
    ) -> None:
        """A relative press-fit pick up command using gantry moves."""
        prep_distance = tip_pick_up_params.prepDistance
        press_distance = tip_pick_up_params.pressDistance
        retract_distance = -1 * (press_distance) / 2

        mount_axis = MotorAxis.LEFT_Z if mount == MountType.LEFT else MotorAxis.RIGHT_Z
        ot3_hardware_api = ensure_ot3_hardware(self._hardware_api)
        # TODO chb, 2025-01-29): Factor out the movement constants and relocate this logic into the hardware controller
        try:
            await self._gantry_mover.move_axes(
                axis_map={mount_axis: prep_distance},
                speed=10,
                relative_move=True,
                expect_stalls=True,
            )
        except PositionUnknownError:
            # if this happens it's from the get position after the move and we can ignore it
            pass

        await ot3_hardware_api.update_axis_position_estimations(
            self._gantry_mover.motor_axes_to_present_hardware_axes([mount_axis])
        )

        # Drive mount down for press-fit
        try:
            await self._gantry_mover.move_axes(
                axis_map={mount_axis: press_distance},
                speed=10.0,
                relative_move=True,
                expect_stalls=True,
            )
        except PositionUnknownError:
            # if this happens it's from the get position after the move and we can ignore it
            pass

        await ot3_hardware_api.update_axis_position_estimations(
            self._gantry_mover.motor_axes_to_present_hardware_axes([mount_axis])
        )

        try:
            await self._gantry_mover.move_axes(
                axis_map={mount_axis: retract_distance}, speed=5.5, relative_move=True
            )
        except PositionUnknownError:
            # if this happens it's from the get position after the move and we can ignore it
            pass

        await ot3_hardware_api.update_axis_position_estimations(
            self._gantry_mover.motor_axes_to_present_hardware_axes([mount_axis])
        )

    async def cam_action_relative_pickup_tip(
        self,
        tip_pick_up_params: TipPickUpParams,
        mount: MountType,
    ) -> None:
        """A cam action pick up command using gantry moves."""
        prep_distance = tip_pick_up_params.prepDistance
        press_distance = tip_pick_up_params.pressDistance
        ejector_push_mm = tip_pick_up_params.ejectorPushMm
        retract_distance = -1 * (prep_distance + press_distance)

        mount_axis = MotorAxis.LEFT_Z if mount == MountType.LEFT else MotorAxis.RIGHT_Z

        # TODO chb, 2025-01-29): Factor out the movement constants and relocate this logic into the hardware controller
        await self._gantry_mover.move_axes(
            axis_map={mount_axis: -6}, speed=10, relative_move=True
        )

        # Drive Q down 3mm at fast speed - look into the pick up tip fuinction to find slow and fast: 10.0
        await self._gantry_mover.move_axes(
            axis_map={MotorAxis.AXIS_96_CHANNEL_CAM: prep_distance},
            speed=10.0,
            relative_move=True,
        )
        # 2.8mm at slow speed - cam action pickup speed: 5.5
        await self._gantry_mover.move_axes(
            axis_map={MotorAxis.AXIS_96_CHANNEL_CAM: press_distance},
            speed=5.5,
            relative_move=True,
        )
        # retract cam : 11.05
        await self._gantry_mover.move_axes(
            axis_map={MotorAxis.AXIS_96_CHANNEL_CAM: retract_distance},
            speed=5.5,
            relative_move=True,
        )

        # Lower tip presence
        await self._gantry_mover.move_axes(
            axis_map={mount_axis: 2}, speed=10, relative_move=True
        )
        await self._gantry_mover.move_axes(
            axis_map={MotorAxis.AXIS_96_CHANNEL_CAM: ejector_push_mm},
            speed=5.5,
            relative_move=True,
        )
        await self._gantry_mover.move_axes(
            axis_map={MotorAxis.AXIS_96_CHANNEL_CAM: -1 * ejector_push_mm},
            speed=5.5,
            relative_move=True,
        )

    async def execute(
        self, params: SealPipetteToTipParams
    ) -> Union[SuccessData[SealPipetteToTipResult], _ExecuteReturn]:
        """Move to and pick up a tip using the requested pipette."""
        pipette_id = params.pipetteId
        labware_id = params.labwareId
        well_name = params.wellName

        well_location = self._state_view.geometry.convert_pick_up_tip_well_location(
            well_location=params.wellLocation
        )
        move_result = await move_to_well(
            movement=self._movement,
            model_utils=self._model_utils,
            pipette_id=pipette_id,
            labware_id=labware_id,
            well_name=well_name,
            well_location=well_location,
        )
        if isinstance(move_result, DefinedErrorData):
            return move_result

        # Aspirate to move plunger to a maximum volume position per pipette type
        tip_geometry = self._state_view.geometry.get_nominal_tip_geometry(
            pipette_id, labware_id, well_name
        )
        if self._state_view.pipettes.get_mount(pipette_id) == MountType.LEFT:
            await self._hardware_api.home(axes=[Axis.P_L])
        else:
            await self._hardware_api.home(axes=[Axis.P_R])

        # Begin relative pickup steps for the resin tips

        channels = self._state_view.pipettes.get_active_channels(pipette_id)
        mount = self._state_view.pipettes.get_mount(pipette_id)
        tip_pick_up_params = params.tipPickUpParams

        if channels == 96:
            if tip_pick_up_params is None:
                tip_pick_up_params = TipPickUpParams(
                    prepDistance=_CAM_PREP_DISTANCE_DEFAULT,
                    pressDistance=_CAM_PRESS_DISTANCE_DEFAULT,
                    ejectorPushMm=_CAM_EJECTOR_PUSH_MM_DEFAULT,
                )
            await self.cam_action_relative_pickup_tip(
                tip_pick_up_params=tip_pick_up_params,
                mount=mount,
            )
        else:
            if tip_pick_up_params is None:
                tip_pick_up_params = TipPickUpParams(
                    prepDistance=_PRESS_FIT_PREP_DISTANCE_DEFAULT,
                    pressDistance=_PRESS_FIT_PRESS_DISTANCE_DEFAULT,
                    ejectorPushMm=_PRESS_FIT_EJECTOR_PUSH_MM_DEFAULT,
                )
            await self.relative_pickup_tip(
                tip_pick_up_params=tip_pick_up_params,
                mount=mount,
            )

        # cache_tip
        if self._state_view.config.use_virtual_pipettes is False:
            self._tip_handler.cache_tip(pipette_id, tip_geometry)
            hw_instr = self._hardware_api.hardware_instruments[mount.to_hw_mount()]
            if hw_instr is not None:
                hw_instr.set_current_volume(_SAFE_TOP_VOLUME)

        state_update = move_result.state_update.update_pipette_tip_state(
            pipette_id=pipette_id,
            tip_geometry=tip_geometry,
            tip_source=LabwareWellId(labware_id=labware_id, well_name=well_name),
        ).set_fluid_aspirated(
            pipette_id=pipette_id,
            fluid=AspiratedFluid(kind=FluidKind.LIQUID, volume=_SAFE_TOP_VOLUME),
        )
        return SuccessData(
            public=SealPipetteToTipResult(
                tipVolume=tip_geometry.volume,
                tipLength=tip_geometry.length,
                tipDiameter=tip_geometry.diameter,
                position=move_result.public.position,
            ),
            state_update=state_update,
        )


class SealPipetteToTip(
    BaseCommand[
        SealPipetteToTipParams,
        SealPipetteToTipResult,
        StallOrCollisionError,
    ]
):
    """Seal tip command model."""

    commandType: SealPipetteToTipCommandType = "sealPipetteToTip"
    params: SealPipetteToTipParams
    result: Optional[SealPipetteToTipResult] = None

    _ImplementationCls: Type[
        SealPipetteToTipImplementation
    ] = SealPipetteToTipImplementation


class SealPipetteToTipCreate(BaseCommandCreate[SealPipetteToTipParams]):
    """Seal tip command creation request model."""

    commandType: SealPipetteToTipCommandType = "sealPipetteToTip"
    params: SealPipetteToTipParams

    _CommandCls: Type[SealPipetteToTip] = SealPipetteToTip
