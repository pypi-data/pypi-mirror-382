from __future__ import annotations

import logging
from typing import List, Dict, Optional, Union, cast, Iterator, Sequence

from opentrons_shared_data.errors.exceptions import CommandPreconditionViolated

from opentrons.protocol_engine.types import ABSMeasureMode
from opentrons_shared_data.labware.types import LabwareDefinition
from opentrons_shared_data.module.types import ModuleModel, ModuleType

from opentrons.legacy_broker import LegacyBroker
from opentrons.legacy_commands import module_commands as cmds
from opentrons.legacy_commands.publisher import CommandPublisher, publish
from opentrons.protocols.api_support.types import APIVersion, ThermocyclerStep
from opentrons.protocols.api_support.util import (
    APIVersionError,
    requires_version,
    UnsupportedAPIError,
)

from .core.common import (
    ProtocolCore,
    LabwareCore,
    ModuleCore,
    TemperatureModuleCore,
    MagneticModuleCore,
    ThermocyclerCore,
    HeaterShakerCore,
    MagneticBlockCore,
    AbsorbanceReaderCore,
    FlexStackerCore,
)
from .core.core_map import LoadedCoreMap
from .core.engine import ENGINE_CORE_API_VERSION
from .core.legacy.legacy_module_core import LegacyModuleCore
from .core.legacy.module_geometry import ModuleGeometry as LegacyModuleGeometry
from .core.legacy.legacy_labware_core import LegacyLabwareCore as LegacyLabwareCore

from .module_validation_and_errors import (
    validate_heater_shaker_temperature,
    validate_heater_shaker_speed,
)
from .labware import Labware
from . import validation


_MAGNETIC_MODULE_HEIGHT_PARAM_REMOVED_IN = APIVersion(2, 14)


_log = logging.getLogger(__name__)


class ModuleContext(CommandPublisher):
    """A connected module in the protocol.

    .. versionadded:: 2.0
    """

    def __init__(
        self,
        core: ModuleCore,
        protocol_core: ProtocolCore,
        core_map: LoadedCoreMap,
        api_version: APIVersion,
        broker: LegacyBroker,
    ) -> None:
        super().__init__(broker=broker)
        self._core = core
        self._protocol_core = protocol_core
        self._core_map = core_map
        self._api_version = api_version

    @property
    @requires_version(2, 0)
    def api_version(self) -> APIVersion:
        return self._api_version

    @property
    @requires_version(2, 14)
    def model(self) -> ModuleModel:
        """Get the module's model identifier."""
        return cast(ModuleModel, self._core.get_model().value)

    @property
    @requires_version(2, 14)
    def type(self) -> ModuleType:
        """Get the module's general type identifier."""
        return self._get_type()

    def _get_type(self) -> ModuleType:
        return cast(ModuleType, self._core.MODULE_TYPE.value)

    @requires_version(2, 0)
    def load_labware_object(self, labware: Labware) -> Labware:
        """Specify the presence of a piece of labware on the module.

        :param labware: The labware object. This object should be already
                        initialized and its parent should be set to this
                        module's geometry. To initialize and load a labware
                        onto the module in one step, see
                        :py:meth:`load_labware`.
        :returns: The properly-linked labware object

        .. deprecated:: 2.14
            Use :py:meth:`load_labware` or :py:meth:`load_labware_by_definition`.
        """
        if not isinstance(self._core, LegacyModuleCore):
            raise UnsupportedAPIError(
                api_element="`ModuleContext.load_labware_object`",
                since_version="2.14",
                extra_message="Use `ModuleContext.load_labware` or `load_labware_by_definition` instead.",
            )

        _log.warning(
            "`ModuleContext.load_labware_object` is an internal, deprecated method. Use `ModuleContext.load_labware` or `load_labware_by_definition` instead."
        )
        core = cast(LegacyModuleCore, self._core)

        assert (
            labware.parent == core.geometry
        ), "Labware is not configured with this module as its parent"

        return core.geometry.add_labware(labware)

    def load_labware(  # noqa: C901
        self,
        name: str,
        label: Optional[str] = None,
        namespace: Optional[str] = None,
        version: Optional[int] = None,
        adapter: Optional[str] = None,
        lid: Optional[str] = None,
        *,
        adapter_namespace: Optional[str] = None,
        adapter_version: Optional[int] = None,
        lid_namespace: Optional[str] = None,
        lid_version: Optional[int] = None,
    ) -> Labware:
        """Load a labware onto the module using its load parameters.

        The parameters of this function behave like those of
        :py:obj:`ProtocolContext.load_labware` (which loads labware directly
        onto the deck). Note that the parameter ``name`` here corresponds to
        ``load_name`` on the ``ProtocolContext`` function.

        :returns: The initialized and loaded labware object.

        .. versionadded:: 2.1
            The ``label``, ``namespace``, and ``version`` parameters.

        .. versionadded:: 2.26
            The ``adapter_namespace``, ``adapter_version``,
            ``lid_namespace``, and ``lid_version`` parameters.
        """
        if self._api_version < APIVersion(2, 1) and (
            label is not None or namespace is not None or version != 1
        ):
            _log.warning(
                f"You have specified API {self.api_version}, but you "
                "are trying to utilize new load_labware parameters in 2.1"
            )

        if self._api_version < validation.NAMESPACE_VERSION_ADAPTER_LID_VERSION_GATE:
            if adapter_namespace is not None:
                raise APIVersionError(
                    api_element="The `adapter_namespace` parameter",
                    until_version=str(
                        validation.NAMESPACE_VERSION_ADAPTER_LID_VERSION_GATE
                    ),
                    current_version=str(self._api_version),
                )
            if adapter_version is not None:
                raise APIVersionError(
                    api_element="The `adapter_version` parameter",
                    until_version=str(
                        validation.NAMESPACE_VERSION_ADAPTER_LID_VERSION_GATE
                    ),
                    current_version=str(self._api_version),
                )
            if lid_namespace is not None:
                raise APIVersionError(
                    api_element="The `lid_namespace` parameter",
                    until_version=str(
                        validation.NAMESPACE_VERSION_ADAPTER_LID_VERSION_GATE
                    ),
                    current_version=str(self._api_version),
                )
            if lid_version is not None:
                raise APIVersionError(
                    api_element="The `lid_version` parameter",
                    until_version=str(
                        validation.NAMESPACE_VERSION_ADAPTER_LID_VERSION_GATE
                    ),
                    current_version=str(self._api_version),
                )

        load_location: Union[ModuleCore, LabwareCore]
        if adapter is not None:
            if self._api_version < APIVersion(2, 15):
                raise APIVersionError(
                    api_element="Loading a labware on an adapter",
                    until_version="2.15",
                    current_version=f"{self._api_version}",
                )

            if (
                self._api_version
                < validation.NAMESPACE_VERSION_ADAPTER_LID_VERSION_GATE
            ):
                checked_adapter_namespace = namespace
                checked_adapter_version = None
            else:
                checked_adapter_namespace = adapter_namespace
                checked_adapter_version = adapter_version

            loaded_adapter = self.load_adapter(
                name=adapter,
                namespace=checked_adapter_namespace,
                version=checked_adapter_version,
            )
            load_location = loaded_adapter._core
        else:
            load_location = self._core

        name = validation.ensure_lowercase_name(name)

        # todo(mm, 2024-11-08): This check belongs in opentrons.protocol_api.core.engine.deck_conflict.
        # We're currently doing it here, at the ModuleContext level, for consistency with what
        # ProtocolContext.load_labware() does. (It should also be moved to the deck_conflict module.)
        if self._get_type() == "absorbanceReaderType":
            if cast(AbsorbanceReaderCore, self._core).is_lid_on():
                raise CommandPreconditionViolated(
                    f"Cannot load {name} onto the Absorbance Reader Module when its lid is closed."
                )

        labware_core = self._protocol_core.load_labware(
            load_name=name,
            label=label if label is None else str(label),
            namespace=namespace,
            version=version,
            location=load_location,
        )
        if lid is not None:
            if self._api_version < validation.LID_STACK_VERSION_GATE:
                raise APIVersionError(
                    api_element="Loading a lid on a Labware",
                    until_version="2.23",
                    current_version=f"{self._api_version}",
                )

            if (
                self._api_version
                < validation.NAMESPACE_VERSION_ADAPTER_LID_VERSION_GATE
            ):
                checked_lid_namespace = namespace
                checked_lid_version = None
            else:
                checked_lid_namespace = lid_namespace
                checked_lid_version = lid_version

            self._protocol_core.load_lid(
                load_name=lid,
                location=labware_core,
                namespace=checked_lid_namespace,
                version=checked_lid_version,
            )

        if isinstance(self._core, LegacyModuleCore):
            labware = cast(LegacyModuleCore, self._core).add_labware_core(
                cast(LegacyLabwareCore, labware_core)
            )
        else:
            labware = Labware(
                core=labware_core,
                api_version=self._api_version,
                protocol_core=self._protocol_core,
                core_map=self._core_map,
            )

        self._core_map.add(labware_core, labware)

        return labware

    @requires_version(2, 0)
    def load_labware_from_definition(
        self, definition: LabwareDefinition, label: Optional[str] = None
    ) -> Labware:
        """Load a labware onto the module using an inline definition.

        :param definition: The labware definition.
        :param str label: An optional special name to give the labware. If
                          specified, this is the name the labware will appear
                          as in the run log and the calibration view in the
                          Opentrons app.
        :returns: The initialized and loaded labware object.
        """
        load_params = self._protocol_core.add_labware_definition(definition)

        return self.load_labware(
            name=load_params.load_name,
            namespace=load_params.namespace,
            version=load_params.version,
            label=label,
        )

    @requires_version(2, 1)
    def load_labware_by_name(
        self,
        name: str,
        label: Optional[str] = None,
        namespace: Optional[str] = None,
        version: Optional[int] = None,
    ) -> Labware:
        """
        .. deprecated:: 2.0
            Use ``load_labware`` instead.
        """
        _log.warning("load_labware_by_name is deprecated. Use load_labware instead.")
        return self.load_labware(
            name=name,
            label=label,
            namespace=namespace,
            version=version,
        )

    @requires_version(2, 15)
    def load_adapter(
        self,
        name: str,
        namespace: Optional[str] = None,
        version: Optional[int] = None,
    ) -> Labware:
        """Load an adapter onto the module using its load parameters.

        The parameters of this function behave like those of
        :py:obj:`ProtocolContext.load_adapter` (which loads adapters directly
        onto the deck). Note that the parameter ``name`` here corresponds to
        ``load_name`` on the ``ProtocolContext`` function.

        :returns: The initialized and loaded adapter object.
        """
        labware_core = self._protocol_core.load_adapter(
            load_name=name,
            namespace=namespace,
            version=version,
            location=self._core,
        )

        if isinstance(self._core, LegacyModuleCore):
            adapter = cast(LegacyModuleCore, self._core).add_labware_core(
                cast(LegacyLabwareCore, labware_core)
            )
        else:
            adapter = Labware(
                core=labware_core,
                api_version=self._api_version,
                protocol_core=self._protocol_core,
                core_map=self._core_map,
            )

        self._core_map.add(labware_core, adapter)

        return adapter

    @requires_version(2, 15)
    def load_adapter_from_definition(self, definition: LabwareDefinition) -> Labware:
        """Load an adapter onto the module using an inline definition.

        :param definition: The labware definition.
        :returns: The initialized and loaded labware object.
        """
        load_params = self._protocol_core.add_labware_definition(definition)

        return self.load_adapter(
            name=load_params.load_name,
            namespace=load_params.namespace,
            version=load_params.version,
        )

    @property
    @requires_version(2, 0)
    def labware(self) -> Optional[Labware]:
        """The labware (if any) present on this module."""
        labware_core = self._protocol_core.get_labware_on_module(self._core)
        return self._core_map.get(labware_core)

    @property
    @requires_version(2, 14)
    def parent(self) -> str:
        """The name of the slot the module is on.

        On a Flex, this will be like ``"D1"``. On an OT-2, this will be like ``"1"``.
        See :ref:`deck-slots`.
        """
        return self._core.get_deck_slot_id()

    @property
    @requires_version(2, 0)
    def geometry(self) -> LegacyModuleGeometry:
        """The object representing the module as an item on the deck.

        .. deprecated:: 2.14
            Use properties of the :py:class:`ModuleContext` instead,
            like :py:meth:`model` and :py:meth:`type`
        """
        if isinstance(self._core, LegacyModuleCore):
            return cast(LegacyModuleCore, self._core).geometry

        raise UnsupportedAPIError(
            api_element="`ModuleContext.geometry`",
            since_version="2.14",
            extra_message="Use properties of the `ModuleContext` itself.",
        )

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        display_name = self._core.get_display_name()
        location = self._core.get_deck_slot().id

        return f"{class_name} at {display_name} on {location} lw {self.labware}"


class TemperatureModuleContext(ModuleContext):
    """An object representing a connected Temperature Module.

    It should not be instantiated directly; instead, it should be
    created through :py:meth:`.ProtocolContext.load_module`.

    .. versionadded:: 2.0

    """

    _core: TemperatureModuleCore

    @property
    @requires_version(2, 14)
    def serial_number(self) -> str:
        """Get the module's unique hardware serial number."""
        return self._core.get_serial_number()

    @publish(command=cmds.tempdeck_set_temp)
    @requires_version(2, 0)
    def set_temperature(self, celsius: float) -> None:
        """Set a target temperature and wait until the module reaches the target.

        No other protocol commands will execute while waiting for the temperature.

        :param celsius: A value between 4 and 95, representing the target temperature in °C.
        """
        self._core.set_target_temperature(celsius)
        self._core.wait_for_target_temperature()

    @publish(command=cmds.tempdeck_set_temp)
    @requires_version(2, 3)
    def start_set_temperature(self, celsius: float) -> None:
        """Set the target temperature without waiting for the target to be hit.

        :param celsius: A value between 4 and 95, representing the target temperature in °C.
        """
        self._core.set_target_temperature(celsius)

    @publish(command=cmds.tempdeck_await_temp)
    @requires_version(2, 3)
    def await_temperature(self, celsius: float) -> None:
        """Wait until module reaches temperature.

        :param celsius: A value between 4 and 95, representing the target temperature in °C.
        """
        self._core.wait_for_target_temperature(celsius)

    @publish(command=cmds.tempdeck_deactivate)
    @requires_version(2, 0)
    def deactivate(self) -> None:
        """Stop heating or cooling, and turn off the fan."""
        self._core.deactivate()

    @property
    @requires_version(2, 0)
    def temperature(self) -> float:
        """The current temperature of the Temperature Module's deck in °C.

        Returns ``0`` in simulation if no target temperature has been set.
        """
        return self._core.get_current_temperature()

    @property
    @requires_version(2, 0)
    def target(self) -> Optional[float]:
        """The target temperature of the Temperature Module's deck in °C.

        Returns ``None`` if no target has been set.
        """
        return self._core.get_target_temperature()

    @property
    @requires_version(2, 3)
    def status(self) -> str:
        """One of four possible temperature statuses:

        - ``holding at target`` – The module has reached its target temperature
          and is actively maintaining that temperature.
        - ``cooling`` – The module is cooling to a target temperature.
        - ``heating`` – The module is heating to a target temperature.
        - ``idle`` – The module has been deactivated.
        """
        return self._core.get_status().value


class MagneticModuleContext(ModuleContext):
    """An object representing a connected Magnetic Module.

    It should not be instantiated directly; instead, it should be
    created through :py:meth:`.ProtocolContext.load_module`.

    .. versionadded:: 2.0
    """

    _core: MagneticModuleCore

    @property
    @requires_version(2, 14)
    def serial_number(self) -> str:
        """Get the module's unique hardware serial number."""
        return self._core.get_serial_number()

    @publish(command=cmds.magdeck_calibrate)
    @requires_version(2, 0)
    def calibrate(self) -> None:
        """Calibrate the Magnetic Module.

        .. deprecated:: 2.14
            This method is unnecessary; remove any usage.
        """
        if self._api_version < ENGINE_CORE_API_VERSION:
            _log.warning(
                "`MagneticModuleContext.calibrate` doesn't do anything useful"
                " and will be removed in Protocol API version 2.14 and higher."
            )
            self._core._sync_module_hardware.calibrate()  # type: ignore[attr-defined]
        else:
            raise UnsupportedAPIError(
                api_element="`MagneticModuleContext.calibrate`",
                since_version="2.14",
            )

    @publish(command=cmds.magdeck_engage)
    @requires_version(2, 0)
    def engage(
        self,
        height: Optional[float] = None,
        offset: Optional[float] = None,
        height_from_base: Optional[float] = None,
    ) -> None:
        """Raise the Magnetic Module's magnets.  You can specify how high the magnets
        should move:

           - No parameter: Move to the default height for the loaded labware. If
             the loaded labware has no default, or if no labware is loaded, this will
             raise an error.

           - ``height_from_base`` – Move this many millimeters above the bottom
             of the labware. Acceptable values are between ``0`` and ``25``.

             This is the recommended way to adjust the magnets' height.

             .. versionadded:: 2.2

           - ``offset`` – Move this many millimeters above (positive value) or below
             (negative value) the default height for the loaded labware. The sum of
             the default height and ``offset`` must be between 0 and 25.

           - ``height`` – Intended to move this many millimeters above the magnets'
             home position. However, depending on the generation of module and the loaded
             labware, this may produce unpredictable results. You should normally use
             ``height_from_base`` instead.

             .. versionchanged:: 2.14
                This parameter has been removed.

        You shouldn't specify more than one of these parameters. However, if you do,
        their order of precedence is ``height``, then ``height_from_base``, then ``offset``.
        """
        if height is not None:
            if self._api_version >= _MAGNETIC_MODULE_HEIGHT_PARAM_REMOVED_IN:
                raise UnsupportedAPIError(
                    api_element="The height parameter of MagneticModuleContext.engage()",
                    since_version=f"{_MAGNETIC_MODULE_HEIGHT_PARAM_REMOVED_IN}",
                    current_version=f"{self._api_version}",
                    extra_message="Use offset or height_from_base.",
                )
            self._core.engage(height_from_home=height)

        # This version check has a bug:
        # if the caller sets height_from_base in an API version that's too low,
        # we will silently ignore it instead of raising APIVersionError.
        # Leaving this unfixed because we haven't thought through
        # how to do backwards-compatible fixes to our version checking itself.
        elif height_from_base is not None and self._api_version >= APIVersion(2, 2):
            self._core.engage(height_from_base=height_from_base)

        else:
            self._core.engage_to_labware(
                offset=offset or 0,
                preserve_half_mm=self._api_version < APIVersion(2, 3),
            )

    @publish(command=cmds.magdeck_disengage)
    @requires_version(2, 0)
    def disengage(self) -> None:
        """Lower the magnets back into the Magnetic Module."""
        self._core.disengage()

    @property
    @requires_version(2, 0)
    def status(self) -> str:
        """The status of the module, either ``engaged`` or ``disengaged``."""
        return self._core.get_status().value


class ThermocyclerContext(ModuleContext):
    """An object representing a connected Thermocycler Module.

    It should not be instantiated directly; instead, it should be
    created through :py:meth:`.ProtocolContext.load_module`.

    .. versionadded:: 2.0
    """

    _core: ThermocyclerCore

    @property
    @requires_version(2, 14)
    def serial_number(self) -> str:
        """Get the module's unique hardware serial number."""
        return self._core.get_serial_number()

    @publish(command=cmds.thermocycler_open)
    @requires_version(2, 0)
    def open_lid(self) -> str:
        """Open the lid."""
        return self._core.open_lid().value

    @publish(command=cmds.thermocycler_close)
    @requires_version(2, 0)
    def close_lid(self) -> str:
        """Close the lid."""
        return self._core.close_lid().value

    @publish(command=cmds.thermocycler_set_block_temp)
    @requires_version(2, 0)
    def set_block_temperature(
        self,
        temperature: float,
        hold_time_seconds: Optional[float] = None,
        hold_time_minutes: Optional[float] = None,
        ramp_rate: Optional[float] = None,
        block_max_volume: Optional[float] = None,
    ) -> None:
        """Set the target temperature for the well block, in °C.

        :param temperature: A value between 4 and 99, representing the target
                            temperature in °C.
        :param hold_time_minutes: The number of minutes to hold, after reaching
                                  ``temperature``, before proceeding to the
                                  next command. If ``hold_time_seconds`` is also
                                  specified, the times are added together.
        :param hold_time_seconds: The number of seconds to hold, after reaching
                                  ``temperature``, before proceeding to the
                                  next command. If ``hold_time_minutes`` is also
                                  specified, the times are added together.
        :param block_max_volume: The greatest volume of liquid contained in any
                                 individual well of the loaded labware, in µL.
                                 If not specified, the default is 25 µL.

        .. note::

            If ``hold_time_minutes`` and ``hold_time_seconds`` are not
            specified, the Thermocycler will proceed to the next command
            immediately after ``temperature`` is reached.
        """
        seconds = validation.ensure_hold_time_seconds(
            seconds=hold_time_seconds, minutes=hold_time_minutes
        )
        self._core.set_target_block_temperature(
            celsius=temperature,
            hold_time_seconds=seconds,
            block_max_volume=block_max_volume,
        )
        self._core.wait_for_block_temperature()

    @publish(command=cmds.thermocycler_set_lid_temperature)
    @requires_version(2, 0)
    def set_lid_temperature(self, temperature: float) -> None:
        """Set the target temperature for the heated lid, in °C.

        :param temperature: A value between 37 and 110, representing the target
                            temperature in °C.

        .. note::

            The Thermocycler will proceed to the next command immediately after
            ``temperature`` is reached.

        """
        self._core.set_target_lid_temperature(celsius=temperature)
        self._core.wait_for_lid_temperature()

    @publish(command=cmds.thermocycler_execute_profile)
    @requires_version(2, 0)
    def execute_profile(
        self,
        steps: List[ThermocyclerStep],
        repetitions: int,
        block_max_volume: Optional[float] = None,
    ) -> None:
        """Execute a Thermocycler profile, defined as a cycle of
        ``steps``, for a given number of ``repetitions``.

        :param steps: List of steps that make up a single cycle.
                      Each list item should be a dictionary that maps to the parameters
                      of the :py:meth:`set_block_temperature` method. The dictionary's
                      keys must be ``temperature`` and one or both of
                      ``hold_time_seconds`` and ``hold_time_minutes``.
        :param repetitions: The number of times to repeat the cycled steps.
        :param block_max_volume: The greatest volume of liquid contained in any
                                 individual well of the loaded labware, in µL.
                                 If not specified, the default is 25 µL.

        .. versionchanged:: 2.21
            Fixed run log listing number of steps instead of number of repetitions.

        """
        repetitions = validation.ensure_thermocycler_repetition_count(repetitions)
        validated_steps = validation.ensure_thermocycler_profile_steps(steps)
        self._core.execute_profile(
            steps=validated_steps,
            repetitions=repetitions,
            block_max_volume=block_max_volume,
        )

    @publish(command=cmds.thermocycler_deactivate_lid)
    @requires_version(2, 0)
    def deactivate_lid(self) -> None:
        """Turn off the lid heater."""
        self._core.deactivate_lid()

    @publish(command=cmds.thermocycler_deactivate_block)
    @requires_version(2, 0)
    def deactivate_block(self) -> None:
        """Turn off the well block temperature controller."""
        self._core.deactivate_block()

    @publish(command=cmds.thermocycler_deactivate)
    @requires_version(2, 0)
    def deactivate(self) -> None:
        """Turn off both the well block temperature controller and the lid heater."""
        self._core.deactivate()

    @property
    @requires_version(2, 0)
    def lid_position(self) -> Optional[str]:
        """One of these possible lid statuses:

        - ``closed`` – The lid is closed.
        - ``in_between`` – The lid is neither open nor closed.
        - ``open`` – The lid is open.
        - ``unknown`` – The lid position can't be determined.
        """
        status = self._core.get_lid_position()
        return status.value if status is not None else None

    @property
    @requires_version(2, 0)
    def block_temperature_status(self) -> str:
        """One of five possible temperature statuses:

        - ``holding at target`` – The block has reached its target temperature
          and is actively maintaining that temperature.
        - ``cooling`` – The block is cooling to a target temperature.
        - ``heating`` – The block is heating to a target temperature.
        - ``idle`` – The block is not currently heating or cooling.
        - ``error`` – The temperature status can't be determined.
        """
        return self._core.get_block_temperature_status().value

    @property
    @requires_version(2, 0)
    def lid_temperature_status(self) -> Optional[str]:
        """One of five possible temperature statuses:

        - ``holding at target`` – The lid has reached its target temperature
          and is actively maintaining that temperature.
        - ``cooling`` – The lid has previously heated and is now passively cooling.
            `The Thermocycler lid does not have active cooling.`
        - ``heating`` – The lid is heating to a target temperature.
        - ``idle`` – The lid has not heated since the beginning of the protocol.
        - ``error`` – The temperature status can't be determined.
        """
        status = self._core.get_lid_temperature_status()
        return status.value if status is not None else None

    @property
    @requires_version(2, 0)
    def block_temperature(self) -> Optional[float]:
        """The current temperature of the well block in °C."""
        return self._core.get_block_temperature()

    @property
    @requires_version(2, 0)
    def block_target_temperature(self) -> Optional[float]:
        """The target temperature of the well block in °C."""
        return self._core.get_block_target_temperature()

    @property
    @requires_version(2, 0)
    def lid_temperature(self) -> Optional[float]:
        """The current temperature of the lid in °C."""
        return self._core.get_lid_temperature()

    @property
    @requires_version(2, 0)
    def lid_target_temperature(self) -> Optional[float]:
        """The target temperature of the lid in °C."""
        return self._core.get_lid_target_temperature()

    @property
    @requires_version(2, 0)
    def ramp_rate(self) -> Optional[float]:
        """The current ramp rate in °C/s."""
        return self._core.get_ramp_rate()

    @property
    @requires_version(2, 0)
    def hold_time(self) -> Optional[float]:
        """Remaining hold time in seconds."""
        return self._core.get_hold_time()

    @property
    @requires_version(2, 0)
    def total_cycle_count(self) -> Optional[int]:
        """Number of repetitions for current set cycle"""
        return self._core.get_total_cycle_count()

    @property
    @requires_version(2, 0)
    def current_cycle_index(self) -> Optional[int]:
        """Index of the current set cycle repetition"""
        return self._core.get_current_cycle_index()

    @property
    @requires_version(2, 0)
    def total_step_count(self) -> Optional[int]:
        """Number of steps within the current cycle"""
        return self._core.get_total_step_count()

    @property
    @requires_version(2, 0)
    def current_step_index(self) -> Optional[int]:
        """Index of the current step within the current cycle"""
        return self._core.get_current_step_index()


class HeaterShakerContext(ModuleContext):
    """An object representing a connected Heater-Shaker Module.

    It should not be instantiated directly; instead, it should be
    created through :py:meth:`.ProtocolContext.load_module`.

    .. versionadded:: 2.13
    """

    _core: HeaterShakerCore

    @property
    @requires_version(2, 14)
    def serial_number(self) -> str:
        """Get the module's unique hardware serial number."""
        return self._core.get_serial_number()

    @property
    @requires_version(2, 13)
    def target_temperature(self) -> Optional[float]:
        """The target temperature of the Heater-Shaker's plate in °C.

        Returns ``None`` if no target has been set.
        """
        return self._core.get_target_temperature()

    @property
    @requires_version(2, 13)
    def current_temperature(self) -> float:
        """The current temperature of the Heater-Shaker's plate in °C.

        Returns ``23`` in simulation if no target temperature has been set.
        """
        return self._core.get_current_temperature()

    @property
    @requires_version(2, 13)
    def current_speed(self) -> int:
        """The current speed of the Heater-Shaker's plate in rpm."""
        return self._core.get_current_speed()

    @property
    @requires_version(2, 13)
    def target_speed(self) -> Optional[int]:
        """Target speed of the Heater-Shaker's plate in rpm."""
        return self._core.get_target_speed()

    @property
    @requires_version(2, 13)
    def temperature_status(self) -> str:
        """One of five possible temperature statuses:

        - ``holding at target`` – The module has reached its target temperature
          and is actively maintaining that temperature.
        - ``cooling`` – The module has previously heated and is now passively cooling.
          `The Heater-Shaker does not have active cooling.`
        - ``heating`` – The module is heating to a target temperature.
        - ``idle`` – The module has not heated since the beginning of the protocol.
        - ``error`` – The temperature status can't be determined.
        """
        return self._core.get_temperature_status().value

    @property
    @requires_version(2, 13)
    def speed_status(self) -> str:
        """One of five possible shaking statuses:

        - ``holding at target`` – The module has reached its target shake speed
          and is actively maintaining that speed.
        - ``speeding up`` – The module is increasing its shake speed towards a target.
        - ``slowing down`` – The module was previously shaking at a faster speed
          and is currently reducing its speed to a lower target or to deactivate.
        - ``idle`` – The module is not shaking.
        - ``error`` – The shaking status can't be determined.
        """
        return self._core.get_speed_status().value

    @property
    @requires_version(2, 13)
    def labware_latch_status(self) -> str:
        """One of six possible latch statuses:

        - ``opening`` – The latch is currently opening (in motion).
        - ``idle_open`` – The latch is open and not moving.
        - ``closing`` – The latch is currently closing (in motion).
        - ``idle_closed`` – The latch is closed and not moving.
        - ``idle_unknown`` – The default status upon reset, regardless of physical latch position.
          Use :py:meth:`~HeaterShakerContext.close_labware_latch` before other commands
          requiring confirmation that the latch is closed.
        - ``unknown`` – The latch status can't be determined.
        """
        return self._core.get_labware_latch_status().value

    @requires_version(2, 13)
    def set_and_wait_for_temperature(self, celsius: float) -> None:
        """Set a target temperature and wait until the module reaches the target.

        No other protocol commands will execute while waiting for the temperature.

        .. versionchanged:: 2.25
            Removed the minimum temperature limit of 37 °C. Note that temperatures under ambient are
            not achievable.

        :param celsius: A value under 95, representing the target temperature in °C.
                        Values are automatically truncated to two decimal places,
                        and the Heater-Shaker module has a temperature accuracy of ±0.5 °C.
        """
        self.set_target_temperature(celsius=celsius)
        self.wait_for_temperature()

    @requires_version(2, 13)
    @publish(command=cmds.heater_shaker_set_target_temperature)
    def set_target_temperature(self, celsius: float) -> None:
        """Set target temperature and return immediately.

        Sets the Heater-Shaker's target temperature and returns immediately without
        waiting for the target to be reached. Does not delay the protocol until
        target temperature has reached.
        Use :py:meth:`~.HeaterShakerContext.wait_for_temperature` to delay
        protocol execution.

        .. versionchanged:: 2.25
            Removed the minimum temperature limit of 37 °C. Note that temperatures under ambient are
            not achievable.

        :param celsius: A value under 95, representing the target temperature in °C.
                        Values are automatically truncated to two decimal places,
                        and the Heater-Shaker module has a temperature accuracy of ±0.5 °C.
        """
        validated_temp = validate_heater_shaker_temperature(
            celsius=celsius, api_version=self.api_version
        )
        self._core.set_target_temperature(celsius=validated_temp)

    @requires_version(2, 13)
    @publish(command=cmds.heater_shaker_wait_for_temperature)
    def wait_for_temperature(self) -> None:
        """Delays protocol execution until the Heater-Shaker has reached its target
        temperature.

        Raises an error if no target temperature was previously set.
        """
        self._core.wait_for_target_temperature()

    @requires_version(2, 13)
    @publish(command=cmds.heater_shaker_set_and_wait_for_shake_speed)
    def set_and_wait_for_shake_speed(self, rpm: int) -> None:
        """Set a shake speed in rpm and block execution of further commands until the module reaches the target.

        Reaching a target shake speed typically only takes a few seconds.

        .. note::

            Before shaking, this command will retract the pipettes upward if they are parked adjacent to the Heater-Shaker.

        :param rpm: A value between 200 and 3000, representing the target shake speed in revolutions per minute.
        """
        validated_speed = validate_heater_shaker_speed(rpm=rpm)
        self._core.set_and_wait_for_shake_speed(rpm=validated_speed)

    @requires_version(2, 13)
    @publish(command=cmds.heater_shaker_open_labware_latch)
    def open_labware_latch(self) -> None:
        """Open the Heater-Shaker's labware latch.

        The labware latch needs to be closed before:
            * Shaking
            * Pipetting to or from the labware on the Heater-Shaker
            * Pipetting to or from labware to the left or right of the Heater-Shaker

        Attempting to open the latch while the Heater-Shaker is shaking will raise an error.

        .. note::

            Before opening the latch, this command will retract the pipettes upward
            if they are parked adjacent to the left or right of the Heater-Shaker.
        """
        self._core.open_labware_latch()

    @requires_version(2, 13)
    @publish(command=cmds.heater_shaker_close_labware_latch)
    def close_labware_latch(self) -> None:
        """Closes the labware latch.

        The labware latch needs to be closed using this method before sending a shake command,
        even if the latch was manually closed before starting the protocol.
        """
        self._core.close_labware_latch()

    @requires_version(2, 13)
    @publish(command=cmds.heater_shaker_deactivate_shaker)
    def deactivate_shaker(self) -> None:
        """Stops shaking.

        Decelerating to 0 rpm typically only takes a few seconds.
        """
        self._core.deactivate_shaker()

    @requires_version(2, 13)
    @publish(command=cmds.heater_shaker_deactivate_heater)
    def deactivate_heater(self) -> None:
        """Stops heating.

        The module will passively cool to room temperature.
        The Heater-Shaker does not have active cooling.
        """
        self._core.deactivate_heater()


class MagneticBlockContext(ModuleContext):
    """An object representing a Magnetic Block.

    It should not be instantiated directly; instead, it should be
    created through :py:meth:`.ProtocolContext.load_module`.

    .. versionadded:: 2.15
    """

    _core: MagneticBlockCore


class AbsorbanceReaderContext(ModuleContext):
    """An object representing a connected Absorbance Plate Reader Module.

    It should not be instantiated directly; instead, it should be
    created through :py:meth:`.ProtocolContext.load_module`.

    .. versionadded:: 2.21
    """

    _core: AbsorbanceReaderCore

    @property
    @requires_version(2, 21)
    def serial_number(self) -> str:
        """Get the module's unique hardware serial number."""
        return self._core.get_serial_number()

    @requires_version(2, 21)
    def close_lid(self) -> None:
        """Use the Flex Gripper to close the lid of the Absorbance Plate Reader.

        You must call this method before initializing the reader, even if the reader was
        in the closed position at the start of the protocol.
        """
        self._core.close_lid()

    @requires_version(2, 21)
    def open_lid(self) -> None:
        """Use the Flex Gripper to open the lid of the Absorbance Plate Reader."""
        self._core.open_lid()

    @requires_version(2, 21)
    def is_lid_on(self) -> bool:
        """Return ``True`` if the Absorbance Plate Reader's lid is currently closed."""
        return self._core.is_lid_on()

    @requires_version(2, 21)
    def initialize(
        self,
        mode: ABSMeasureMode,
        wavelengths: List[int],
        reference_wavelength: Optional[int] = None,
    ) -> None:
        """Prepare the Absorbance Plate Reader to read a plate.

        See :ref:`absorbance-initialization` for examples.

        :param mode: Either ``"single"`` or ``"multi"``.

            - In single measurement mode, :py:meth:`.AbsorbanceReaderContext.read` uses
              one sample wavelength and an optional reference wavelength.
            - In multiple measurement mode, :py:meth:`.AbsorbanceReaderContext.read` uses
              a list of up to six sample wavelengths.
        :param wavelengths: A list of wavelengths, in nm, to measure.

            - In the default hardware configuration, each wavelength must be one of
              ``450`` (blue), ``562`` (green), ``600`` (orange), or ``650`` (red). In
              custom hardware configurations, the module may accept other integers
              between 350 and 1000.
            - The list must contain only one item when initializing a single measurement.
            - The list can contain one to six items when initializing a multiple measurement.
        :param reference_wavelength: An optional reference wavelength, in nm. If provided,
            :py:meth:`.AbsorbanceReaderContext.read` will read at the reference
            wavelength and then subtract the reference wavelength values from the
            measurement wavelength values. Can only be used with single measurements.
        """
        self._core.initialize(
            mode, wavelengths, reference_wavelength=reference_wavelength
        )

    @requires_version(2, 21)
    def read(
        self, export_filename: Optional[str] = None
    ) -> Dict[int, Dict[str, float]]:
        """Read a plate on the Absorbance Plate Reader.

        This method always returns a dictionary of measurement data. It optionally will
        save a CSV file of the results to the Flex filesystem, which you can access from
        the Recent Protocol Runs screen in the Opentrons App. These files are `only` saved
        if you specify ``export_filename``.

        In simulation, the values for each well key in the dictionary are set to zero, and
        no files are written.

        .. note::

            Avoid divide-by-zero errors when simulating and using the results of this
            method later in the protocol. If you divide by any of the measurement
            values, use :py:meth:`.ProtocolContext.is_simulating` to use alternate dummy
            data or skip the division step.

        :param export_filename: An optional file basename. If provided, this method
            will write a CSV file for each measurement in the read operation. File
            names will use the value of this parameter, the measurement wavelength
            supplied in :py:meth:`~.AbsorbanceReaderContext.initialize`, and a
            ``.csv`` extension. For example, when reading at wavelengths 450 and 562
            with ``export_filename="my_data"``, there will be two output files:
            ``my_data_450.csv`` and ``my_data_562.csv``.

            See :ref:`absorbance-csv` for information on working with these CSV files.

        :returns: A dictionary of wavelengths to dictionary of values ordered by well name.
        """
        return self._core.read(filename=export_filename)


class FlexStackerContext(ModuleContext):
    """An object representing a connected Flex Stacker module.

    It should not be instantiated directly; instead, it should be
    created through :py:meth:`.ProtocolContext.load_module`.

    .. versionadded:: 2.25
    """

    _core: FlexStackerCore

    @property
    @requires_version(2, 25)
    def serial_number(self) -> str:
        """Get the module's unique hardware serial number."""
        return self._core.get_serial_number()

    @requires_version(2, 25)
    @publish(command=cmds.flex_stacker_retrieve)
    def retrieve(self) -> Labware:
        """Retrieve a labware from the Flex Stacker and move it onto the shuttle.

        The Stacker will retrieve the bottom-most labware in the stack.

        :returns: The retrieved :py:class:`Labware` object. This will always be the main labware,
                  even if the Flex Stacker contains labware on an adapter. To get the adapter object,
                  call :py:class:`Labware.parent` on the returned labware.

        """
        labware_core = self._core.retrieve()

        return self._core_map.get_or_add(
            labware_core,
            Labware._builder_for_core_map(
                self._api_version, self._protocol_core, self._core_map
            ),
        )

    @requires_version(2, 25)
    @publish(command=cmds.flex_stacker_store)
    def store(self) -> None:
        """Move a labware currently on the Flex Stacker shuttle into the Flex Stacker.

        The labware must be the same type the Stacker is configured to store using :py:meth:`.set_stored_labware()`. If labware is currently stacked inside the module, this method moves the new labware to the bottom-most position of the stack.
        """
        self._core.store()

    def _labware_to_cores(self, labware: Sequence[Labware]) -> list[LabwareCore]:
        return [labware._core for labware in labware]

    def _cores_to_labware(self, cores: Sequence[LabwareCore]) -> list[Labware]:
        def _convert() -> Iterator[Labware]:
            for core in cores:
                yield self._core_map.get_or_add(
                    core,
                    Labware._builder_for_core_map(
                        self._api_version, self._protocol_core, self._core_map
                    ),
                )

        return list(_convert())

    @requires_version(2, 25)
    def get_max_storable_labware_from_list(
        self,
        labware: list[Labware],
        stacking_offset_z: float | None = None,
    ) -> list[Labware]:
        """Limit a list of labware instances to the number that can be stored in a Flex Stacker.
        Items will be taken from the head of the list.

        A Flex Stacker has a limited amount of internal space and computes the number of labware
        (or labware with lids or adapters) that it can store based on the ``z`` heights of the labware
        and the amount they overlap when stacked. To calculate how many of a given
        labware the Stacker can store, the labware type must be specified.

        Provide a list of labware to this function to return the maximum number of labware of the given type that the
        Stacker can store. The returned list is guaranteed to be suitable
        for passing to :py:meth:`.set_stored_labware_items`.

        This function limits the list of labware based on the overall maximum number the Stacker
        can hold and will not change as labware is added or removed. To limit a list of labware to
        the amount that will currently fit in the Flex Stacker, use
        :py:meth:`.get_current_storable_labware_from_list`.

        .. note::

            If a ``z`` stacking offset is provided, be sure to specify the same value when
            configuring the Flex Stacker with :py:meth:`.set_stored_labware_items`.

            See :py:meth:`.set_stored_labware_items` for more details on stacking offset.

        """
        return self._cores_to_labware(
            self._core.get_max_storable_labware_from_list(
                self._labware_to_cores(labware), stacking_offset_z
            ),
        )

    @requires_version(2, 25)
    def get_current_storable_labware_from_list(
        self, labware: list[Labware]
    ) -> list[Labware]:
        """Limit a list of labware instances to the number that the Flex Stacker currently has space for,
        based on the labware that is already stored in the Flex Stacker.
        Items will be taken from the head of the list.

        A Flex Stacker has a limited amount of internal space and computes the number of labware that it can store based on the ``z`` height of the labware and the amount they overlap when stacked.

        .. note::
            The number of elements in the returned list will change as labware is added or removed from
            the Flex Stacker. To get a list limited to the overall maximum number of labware the Flex Stacker
            can store, use :py:meth:`.get_max_storable_labware_from_list`.

        :param labware: A list of labware to limit. The returned list takes from the front of the provided list, and it is guaranteed to be suitable
            for passing to :py:meth:`.fill_items`.
        """
        return self._cores_to_labware(
            self._core.get_current_storable_labware_from_list(
                self._labware_to_cores(labware)
            )
        )

    @requires_version(2, 25)
    def get_max_storable_labware(self) -> int:
        """Get the maximum number of labware that the Flex Stacker can store.

        Use this function to return the total number of labware that the Flex Stacker can store. A Stacker has a limited amount of internal space and calculates the total number of labware that can be stored based on the ``z`` height of the labware and the amount they overlap when stacked.

        The total number is calculated based on the labware definition for the type of labware the Stacker is currently configured to store using :py:meth:`.set_stored_labware()`. This
        number is the overall maximum and will not change as labware is added or removed. To get the number of labware that can
        be stored in the Flex Stacker based on its current conditions, use :py:meth:`.get_current_storable_labware`.
        """
        return self._core.get_max_storable_labware()

    @requires_version(2, 25)
    def get_current_storable_labware(self) -> int:
        """Get the number of labware that the Flex Stacker currently has space for.

        Use this function to return the total number of labware that the Flex Stacker can store. A Stacker has a limited amount of internal space and calculates the number of labware that can be stored based on the ``z`` height of the labware and the amount they overlap when stacked.

        The number is calculated based on the labware definition for the type of labware the Stacker is currently configured to store using :py:meth:`.set_stored_labware()`. This function returns a number based on the current storage conditions of the Stacker, and will change as labware is added or removed. To get the overall maximum number of labware the
        Flex Stacker can store, use :py:meth:`.get_max_storable_labware`.
        """
        return self._core.get_current_storable_labware()

    @requires_version(2, 25)
    def set_stored_labware_items(
        self,
        labware: list[Labware],
        stacking_offset_z: float | None = None,
    ) -> None:
        """Configure the labware the Flex Stacker will store during a protocol by providing an initial list of stored labware objects. The start of the list represents the bottom of the Stacker,
        and the end of the list represents the top of the Stacker.

        The kind of labware stored by the Flex Stacker will be calculated from the list of labware
        specified here. You can use this to store labware objects that you have already created
        so that, for instance, you can set their liquid state or nicknames.


        :param labware: A list of labware to load into the Stacker.

            - The list must have at least one element.
            - All labware must be loaded :py:obj:`OFF_DECK`.
            - All labware must be of the same kind. If any of them have lids, they
              must all have lids, and the lids must be the same.
              If any of them are on adapters, they all
              must be on adapters, and the adapters must be the same.
              All lids and adapters must be compatible with the Stacker.
            - The number of labware objects must fit in the Stacker physically. To make sure the labware
              will fit, use the return value of :py:meth:`.get_max_storable_labware_from_list`.

        :param stacking_offset_z: Stacking ``z`` offset in mm of stored labware. If specified, this overrides the
            calculated value from labware definitions.

        .. note::

            The stacking offset is the amount of vertical overlap (in mm) between the bottom side of a
            labware unit and the top side of the unit below. This offset is used to determine how many
            units can fit in the stacker and calculates the ``z`` position of the shuttle when retrieving
            or storing labware.

            There are four possible stacking configurations, each with a different method of calculating
            the stacking offset:

                - Bare labware: labware (bottom side) overlaps with the top side of the labware below.
                - Labware on adapter: the adapter (bottom side) of the upper labware unit overlaps with the top side of the labware below.
                - Labware with lid: the labware (bottom side) of the upper unit overlaps with the lid (top side) of the unit below.
                - Labware with lid and adapter: the adapter (bottom side) of the upper unit overlaps with the
                  lid (top side) of the unit below.

        """
        self._core.set_stored_labware_items(
            self._labware_to_cores(labware),
            stacking_offset_z=stacking_offset_z,
        )

    @requires_version(2, 25)
    @publish(command=cmds.flex_stacker_set_stored_labware)
    def set_stored_labware(
        self,
        load_name: str,
        namespace: str | None = None,
        version: int | None = None,
        adapter: str | None = None,
        lid: str | None = None,
        count: int | None = None,
        stacking_offset_z: float | None = None,
        *,
        adapter_namespace: str | None = None,
        adapter_version: int | None = None,
        lid_namespace: str | None = None,
        lid_version: int | None = None,
    ) -> None:
        """Configure the type and starting quantity of labware the Flex Stacker will store during a protocol. This is the only type of labware you'll be able to store in the Stacker until it's reconfigured.

        You must use this method to load a labware stack stored inside the Stacker before you're able to ``retrieve()`` or ``store()`` additional labware.

        :param str load_name: A string to use for looking up a labware definition.
            You can find the ``load_name`` for any Opentrons-verified labware on the
            `Labware Library <https://labware.opentrons.com>`__.

        :param str namespace: The namespace that the labware definition belongs to.
            If unspecified, the API will automatically search two namespaces:

              - ``"opentrons"``, to load standard Opentrons labware definitions.
              - ``"custom_beta"``, to load custom labware definitions created with the
                `Custom Labware Creator <https://labware.opentrons.com/create>`__.

            You might need to specify an explicit ``namespace`` if you have a custom
            definition whose ``load_name`` is the same as an Opentrons-verified
            definition, and you want to explicitly choose one or the other.

        :param version: The version of the labware definition. You should normally
            leave this unspecified to let the method choose a version
            automatically.

        :param adapter: An adapter to load the labware on top of. Accepts the same
            values as the ``load_name`` parameter of :py:meth:`.load_adapter`.

        :param adapter_namespace: Applies to ``adapter`` the same way that ``namespace``
            applies to ``load_name``.

        :param adapter_version: Applies to ``adapter`` the same way that ``version``
            applies to ``load_name``.

        :param lid: A lid to load the on top of the main labware. Accepts the same
            values as the ``load_name`` parameter of :py:meth:`~.ProtocolContext.load_lid_stack`. The
            lid will use the same namespace as the labware, and the API will
            choose the lid's version automatically.

        :param lid_namespace: Applies to ``lid`` the same way that ``namespace``
            applies to ``load_name``.

        :param lid_version: Applies to ``lid`` the same way that ``version``
            applies to ``load_name``.

        :param count: The number of labware that the Flex Stacker should store. If not specified, this will be the maximum amount of this kind of
            labware that the Flex Stacker is capable of storing.

        :param stacking_offset_z: Stacking ``z`` offset in mm of stored labware. If specified, this overrides the
            calculated value in the labware definition.

        .. note::

            The stacking offset is the amount of vertical overlap (in mm) between the bottom side of a
            labware unit and the top side of the unit below. This offset is used to determine how many
            units can fit in the Stacker and calculates the ``z`` position of the shuttle when retrieving
            or storing labware.

            There are four possible stacking configurations, each with a different method of calculating
            the stacking offset:

              - Bare labware: labware (bottom side) overlaps with the top side of the labware below.
              - Labware on adapter: the adapter (bottom side) of the upper labware unit overlaps with the top side of the labware below.
              - Labware with lid: the labware (bottom side) of the upper labware unit overlaps with the lid (top side) of the unit below.
              - Labware with lid and adapter: the adapter (bottom side) of the upper labware unit overlaps with the lid (top side) of the unit below.
        """

        if self._api_version < validation.NAMESPACE_VERSION_ADAPTER_LID_VERSION_GATE:
            if adapter_namespace is not None:
                raise APIVersionError(
                    api_element="The `adapter_namespace` parameter",
                    until_version=str(
                        validation.NAMESPACE_VERSION_ADAPTER_LID_VERSION_GATE
                    ),
                    current_version=str(self._api_version),
                )
            if adapter_version is not None:
                raise APIVersionError(
                    api_element="The `adapter_version` parameter",
                    until_version=str(
                        validation.NAMESPACE_VERSION_ADAPTER_LID_VERSION_GATE
                    ),
                    current_version=str(self._api_version),
                )
            if lid_namespace is not None:
                raise APIVersionError(
                    api_element="The `lid_namespace` parameter",
                    until_version=str(
                        validation.NAMESPACE_VERSION_ADAPTER_LID_VERSION_GATE
                    ),
                    current_version=str(self._api_version),
                )
            if lid_version is not None:
                raise APIVersionError(
                    api_element="The `lid_version` parameter",
                    until_version=str(
                        validation.NAMESPACE_VERSION_ADAPTER_LID_VERSION_GATE
                    ),
                    current_version=str(self._api_version),
                )

        if self._api_version < validation.NAMESPACE_VERSION_ADAPTER_LID_VERSION_GATE:
            checked_adapter_namespace = namespace
            checked_adapter_version = version
            checked_lid_namespace = namespace
            checked_lid_version = version
        else:
            checked_adapter_namespace = adapter_namespace
            checked_adapter_version = adapter_version
            checked_lid_namespace = lid_namespace
            checked_lid_version = lid_version

        self._core.set_stored_labware(
            main_load_name=load_name,
            main_namespace=namespace,
            main_version=version,
            lid_load_name=lid,
            lid_namespace=checked_lid_namespace,
            lid_version=checked_lid_version,
            adapter_load_name=adapter,
            adapter_namespace=checked_adapter_namespace,
            adapter_version=checked_adapter_version,
            count=count,
            stacking_offset_z=stacking_offset_z,
        )

    @requires_version(2, 25)
    @publish(command=cmds.flex_stacker_fill)
    def fill(self, count: int | None = None, message: str | None = None) -> None:
        """Pause the protocol to add labware to the Flex Stacker.

        The labware must be the same type the Stacker is configured to store using :py:meth:`.set_stored_labware()`. If no labware type has been set, the API will raise an error.

        :param count: The amount of labware the Flex Stacker should hold after this command is executed.
                      If not specified, the Flex Stacker should be full after this command is executed.
        :param message: A message to display noting what kind of labware to fill the Stacker with.
        """
        self._core.fill(count, message)

    @requires_version(2, 25)
    def fill_items(self, labware: list[Labware], message: str | None = None) -> None:
        """Pause the protocol to add a specific list of labware to the Flex Stacker.

        :param labware: The list of labware to add. The list must:

          - Contain at least one labware.
          - Have labware of the same kind previously passed to
            :py:meth:`.set_stored_labware_items` or loaded by :py:meth:`.set_stored_labware`.
          - All labware should be loaded :py:obj:`OFF_DECK`.
        :param message: A message to display noting the labware to fill the Stacker with.
        """
        self._core.fill_items(self._labware_to_cores(labware), message)

    @requires_version(2, 25)
    @publish(command=cmds.flex_stacker_empty)
    def empty(self, message: str | None = None) -> None:
        """Pause the protocol to remove all labware stored in the Flex Stacker.

        This method sets the location of all labware currently in the stacker to :py:obj:`OFF_DECK`.

        :param message: A message to display to note what should be removed from
                        the Flex Stacker.
        """
        self._core.empty(
            message,
        )

    @requires_version(2, 25)
    def get_stored_labware(self) -> list[Labware]:
        """Get the list of labware currently stored inside the Stacker.

        This function returns a list of all labware stored in the Stacker based on the labware intially stored using :py:meth:`.set_stored_labware` and any labware added or removed during the protocol.

        The first element of the list occupies the bottom-most position in the labware stack and would be the labware retrieved by a call to
        :py:meth:`.retrieve`.
        """
        return self._cores_to_labware(self._core.get_stored_labware())
