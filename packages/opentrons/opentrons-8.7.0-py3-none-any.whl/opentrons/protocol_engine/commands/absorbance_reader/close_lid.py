"""Command models to close the lid on an Absorbance Reader."""
from __future__ import annotations
from typing import Optional, Literal, TYPE_CHECKING
from typing_extensions import Type

from pydantic import BaseModel, Field

from ..command import AbstractCommandImpl, BaseCommand, BaseCommandCreate, SuccessData
from ...errors.error_occurrence import ErrorOccurrence
from ...errors import CannotPerformModuleAction
from opentrons.protocol_engine.types import AddressableAreaLocation

from ...state.update_types import StateUpdate

from .common import LID_Z_CLEARANCE

from opentrons.types import Point

from opentrons.drivers.types import AbsorbanceReaderLidStatus


if TYPE_CHECKING:
    from opentrons.protocol_engine.state.state import StateView
    from opentrons.protocol_engine.execution import (
        EquipmentHandler,
        LabwareMovementHandler,
    )


CloseLidCommandType = Literal["absorbanceReader/closeLid"]


class CloseLidParams(BaseModel):
    """Input parameters to close the lid on an absorbance reading."""

    moduleId: str = Field(..., description="Unique ID of the absorbance reader.")


class CloseLidResult(BaseModel):
    """Result data from closing the lid on an aborbance reading."""


class CloseLidImpl(AbstractCommandImpl[CloseLidParams, SuccessData[CloseLidResult]]):
    """Execution implementation of closing the lid on an Absorbance Reader."""

    def __init__(
        self,
        state_view: StateView,
        equipment: EquipmentHandler,
        labware_movement: LabwareMovementHandler,
        **unused_dependencies: object,
    ) -> None:
        self._state_view = state_view
        self._equipment = equipment
        self._labware_movement = labware_movement

    async def execute(self, params: CloseLidParams) -> SuccessData[CloseLidResult]:
        """Execute the close lid command."""
        state_update = StateUpdate()
        mod_substate = self._state_view.modules.get_absorbance_reader_substate(
            module_id=params.moduleId
        )

        hardware_lid_status = AbsorbanceReaderLidStatus.OFF
        if not self._state_view.config.use_virtual_modules:
            abs_reader = self._equipment.get_module_hardware_api(mod_substate.module_id)
            if abs_reader is not None:
                hardware_lid_status = await abs_reader.get_current_lid_status()
            else:
                raise CannotPerformModuleAction(
                    "Could not reach the Hardware API for Opentrons Plate Reader Module."
                )

        if hardware_lid_status is AbsorbanceReaderLidStatus.ON:
            # The lid is already physically ON, so we can no-op physically closing it
            state_update.set_absorbance_reader_lid(
                module_id=mod_substate.module_id, is_lid_on=True
            )
        else:
            # Allow propagation of ModuleNotAttachedError.
            _ = self._equipment.get_module_hardware_api(mod_substate.module_id)

            lid_definition = (
                self._state_view.labware.get_absorbance_reader_lid_definition()
            )

            current_location = self._state_view.modules.absorbance_reader_dock_location(
                params.moduleId
            )

            # we need to move the lid onto the module reader
            absorbance_model = self._state_view.modules.get_requested_model(
                params.moduleId
            )
            assert absorbance_model is not None
            new_location = AddressableAreaLocation(
                addressableAreaName=self._state_view.modules.ensure_and_convert_module_fixture_location(
                    deck_slot=self._state_view.modules.get_location(
                        params.moduleId
                    ).slotName,
                    model=absorbance_model,
                )
            )

            # The lid's labware definition stores gripper offsets for itself in the
            # space normally meant for offsets for labware stacked atop it.
            lid_gripper_offsets = self._state_view.labware.get_child_gripper_offsets(
                labware_definition=lid_definition,
                slot_name=None,
            )
            if lid_gripper_offsets is None:
                raise ValueError(
                    "Gripper Offset values for Absorbance Reader Lid labware must not be None."
                )

            await self._labware_movement.move_labware_with_gripper(
                labware_definition=lid_definition,
                current_location=current_location,
                new_location=new_location,
                user_pick_up_offset=Point.from_xyz_attrs(
                    lid_gripper_offsets.pickUpOffset
                ),
                user_drop_offset=Point.from_xyz_attrs(lid_gripper_offsets.dropOffset),
                post_drop_slide_offset=None,
                gripper_z_offset=LID_Z_CLEARANCE,
            )
            state_update.set_absorbance_reader_lid(
                module_id=mod_substate.module_id,
                is_lid_on=True,
            )

        return SuccessData(
            public=CloseLidResult(),
            state_update=state_update,
        )


class CloseLid(BaseCommand[CloseLidParams, CloseLidResult, ErrorOccurrence]):
    """A command to close the lid on an Absorbance Reader."""

    commandType: CloseLidCommandType = "absorbanceReader/closeLid"
    params: CloseLidParams
    result: Optional[CloseLidResult] = None

    _ImplementationCls: Type[CloseLidImpl] = CloseLidImpl


class CloseLidCreate(BaseCommandCreate[CloseLidParams]):
    """A request to execute an Absorbance Reader close lid command."""

    commandType: CloseLidCommandType = "absorbanceReader/closeLid"
    params: CloseLidParams

    _CommandCls: Type[CloseLid] = CloseLid
