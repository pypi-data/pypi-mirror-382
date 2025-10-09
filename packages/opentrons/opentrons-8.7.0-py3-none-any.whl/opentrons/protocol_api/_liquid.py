from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Union, TYPE_CHECKING, Tuple

from opentrons_shared_data.liquid_classes.liquid_class_definition import (
    LiquidClassSchemaV1,
)

from opentrons.protocols.advanced_control.transfers.common import (
    NoLiquidClassPropertyError,
)

from ._liquid_properties import (
    TransferProperties,
    build_transfer_properties,
)

if TYPE_CHECKING:
    from . import InstrumentContext, Labware


@dataclass(frozen=True)
class Liquid:
    """A liquid to load into a well.

    Attributes:
        name: A human-readable name for the liquid.
        description: An optional description.
        display_color: An optional display color for the liquid.

    .. versionadded:: 2.14
    """

    _id: str
    name: str
    description: Optional[str]
    display_color: Optional[str]


@dataclass
class LiquidClass:
    """A data class that contains properties of a specific class of liquids."""

    _name: str
    _display_name: str
    _by_pipette_setting: Dict[str, Dict[str, TransferProperties]]

    @classmethod
    def create(cls, liquid_class_definition: LiquidClassSchemaV1) -> "LiquidClass":
        """Liquid class factory method."""

        by_pipette_settings: Dict[str, Dict[str, TransferProperties]] = {}
        for by_pipette in liquid_class_definition.byPipette:
            tip_settings: Dict[str, TransferProperties] = {}
            for tip_type in by_pipette.byTipType:
                tip_settings[tip_type.tiprack] = build_transfer_properties(tip_type)
            by_pipette_settings[by_pipette.pipetteModel] = tip_settings

        return cls(
            _name=liquid_class_definition.liquidClassName,
            _display_name=liquid_class_definition.displayName,
            _by_pipette_setting=by_pipette_settings,
        )

    @classmethod
    def create_from(
        cls,
        name: str,
        display_name: str,
        by_pipette_setting: Dict[str, Dict[str, TransferProperties]],
    ) -> "LiquidClass":
        """Create a liquid class from the passed in args."""
        return cls(
            _name=name,
            _display_name=display_name,
            _by_pipette_setting=by_pipette_setting,
        )

    @property
    def name(self) -> str:
        return self._name

    @property
    def display_name(self) -> str:
        return self._display_name

    def update_for(
        self,
        pipette: Union[str, InstrumentContext],
        tip_rack: Union[str, Labware],
        transfer_properties: TransferProperties,
    ) -> None:
        """Update the transfer properties for the given pipette and tip combo.

        If an entry does not exist, it will be created.
        """
        pipette_name, tiprack_uri = self._get_pipette_and_tiprack_names(
            pipette, tip_rack
        )
        try:
            self._by_pipette_setting[pipette_name].update(
                {tiprack_uri: transfer_properties}
            )
        except KeyError:
            self._by_pipette_setting[pipette_name] = {tiprack_uri: transfer_properties}

    def get_for(
        self, pipette: Union[str, InstrumentContext], tip_rack: Union[str, Labware]
    ) -> TransferProperties:
        """Get liquid class transfer properties for the specified pipette and tip."""
        pipette_name, tiprack_uri = self._get_pipette_and_tiprack_names(
            pipette, tip_rack
        )

        try:
            settings_for_pipette = self._by_pipette_setting[pipette_name]
        except KeyError:
            raise NoLiquidClassPropertyError(
                f"No properties found for {pipette_name} in {self._name} liquid class"
            )
        try:
            transfer_properties = settings_for_pipette[tiprack_uri]
        except KeyError:
            raise NoLiquidClassPropertyError(
                f"No properties found for {tiprack_uri} for {pipette_name} in {self._name} liquid class"
            )
        return transfer_properties

    @staticmethod
    def _get_pipette_and_tiprack_names(
        pipette: Union[str, InstrumentContext],
        tip_rack: Union[str, Labware],
    ) -> Tuple[str, str]:
        """Return the pipette and tip rack name strings from the given pipette and tip rack."""
        from . import InstrumentContext, Labware

        if isinstance(pipette, InstrumentContext):
            pipette_name = pipette.name
        elif isinstance(pipette, str):
            pipette_name = pipette
        else:
            raise ValueError(
                f"{pipette} should either be an InstrumentContext object"
                f" or a pipette name string."
            )

        if isinstance(tip_rack, Labware):
            tiprack_uri = tip_rack.uri
        elif isinstance(tip_rack, str):
            tiprack_uri = tip_rack
        else:
            raise ValueError(
                f"{tip_rack} should either be a tiprack Labware object"
                f" or a tiprack URI string."
            )
        return pipette_name, tiprack_uri
