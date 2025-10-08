"""Load lid command request, result, and implementation models."""

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import TYPE_CHECKING, Optional, Type
from typing_extensions import Literal

from opentrons_shared_data.labware.labware_definition import LabwareDefinition

from ..errors import LabwareCannotBeStackedError, LabwareIsNotAllowedInLocationError
from ..resources import labware_validation
from ..types import (
    LoadableLabwareLocation,
    OnLabwareLocation,
    OnLabwareLocationSequenceComponent,
)

from .labware_handling_common import LabwareHandlingResultMixin
from .command import AbstractCommandImpl, BaseCommand, BaseCommandCreate, SuccessData
from ..errors.error_occurrence import ErrorOccurrence
from ..state.update_types import StateUpdate

if TYPE_CHECKING:
    from ..state.state import StateView
    from ..execution import EquipmentHandler


LoadLidCommandType = Literal["loadLid"]


class LoadLidParams(BaseModel):
    """Payload required to load a lid onto a labware."""

    location: LoadableLabwareLocation = Field(
        ...,
        description="Labware the lid should be loaded onto.",
    )
    loadName: str = Field(
        ...,
        description="Name used to reference a lid labware definition.",
    )
    namespace: str = Field(
        ...,
        description="The namespace the lid labware definition belongs to.",
    )
    version: int = Field(
        ...,
        description="The lid labware definition version.",
    )


class LoadLidResult(LabwareHandlingResultMixin):
    """Result data from the execution of a LoadLabware command."""

    definition: LabwareDefinition = Field(
        ...,
        description="The full definition data for this lid labware.",
    )


class LoadLidImplementation(
    AbstractCommandImpl[LoadLidParams, SuccessData[LoadLidResult]]
):
    """Load lid command implementation."""

    def __init__(
        self, equipment: EquipmentHandler, state_view: StateView, **kwargs: object
    ) -> None:
        self._equipment = equipment
        self._state_view = state_view

    async def execute(self, params: LoadLidParams) -> SuccessData[LoadLidResult]:
        """Load definition and calibration data necessary for a lid."""
        if not isinstance(params.location, OnLabwareLocation):
            raise LabwareIsNotAllowedInLocationError(
                "Lid Labware is only allowed to be loaded on top of a labware. Try `load_lid_stack(...)` to load lids without parent labware."
            )

        verified_location = self._state_view.geometry.ensure_location_not_occupied(
            params.location
        )
        loaded_labware = await self._equipment.load_labware(
            load_name=params.loadName,
            namespace=params.namespace,
            version=params.version,
            location=verified_location,
            labware_id=None,
        )

        if not labware_validation.validate_definition_is_lid(loaded_labware.definition):
            raise LabwareCannotBeStackedError(
                f"Labware {params.loadName} is not a Lid and cannot be loaded onto {self._state_view.labware.get_display_name(params.location.labwareId)}."
            )

        state_update = StateUpdate()

        # In the case of lids being loaded on top of other labware, set the parent labware's lid
        state_update.set_lids(
            parent_labware_ids=[params.location.labwareId],
            lid_ids=[loaded_labware.labware_id],
        )

        state_update.set_loaded_labware(
            labware_id=loaded_labware.labware_id,
            offset_id=loaded_labware.offsetId,
            definition=loaded_labware.definition,
            location=verified_location,
            display_name=None,
        )

        if isinstance(verified_location, OnLabwareLocation):
            self._state_view.labware.raise_if_labware_cannot_be_stacked(
                top_labware_definition=loaded_labware.definition,
                bottom_labware_id=verified_location.labwareId,
            )

        return SuccessData(
            public=LoadLidResult(
                labwareId=loaded_labware.labware_id,
                definition=loaded_labware.definition,
                # Note: the lid is not yet loaded and therefore won't be found as the lid id for the
                # labware onto which we're loading it, so build that part of the location sequence
                # here and then build the rest of the sequence from the parent labware
                locationSequence=[
                    OnLabwareLocationSequenceComponent(
                        labwareId=params.location.labwareId,
                        lidId=loaded_labware.labware_id,
                    )
                ]
                + self._state_view.geometry.get_location_sequence(
                    params.location.labwareId
                ),
            ),
            state_update=state_update,
        )


class LoadLid(BaseCommand[LoadLidParams, LoadLidResult, ErrorOccurrence]):
    """Load lid command resource model."""

    commandType: LoadLidCommandType = "loadLid"
    params: LoadLidParams
    result: Optional[LoadLidResult] = None

    _ImplementationCls: Type[LoadLidImplementation] = LoadLidImplementation


class LoadLidCreate(BaseCommandCreate[LoadLidParams]):
    """Load lid command creation request."""

    commandType: LoadLidCommandType = "loadLid"
    params: LoadLidParams

    _CommandCls: Type[LoadLid] = LoadLid
