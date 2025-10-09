from dataclasses import dataclass
from numpy import interp
from typing import Optional, Dict, Sequence, Tuple, List, Union

from opentrons_shared_data.liquid_classes.liquid_class_definition import (
    TransferProperties as SharedDataTransferProperties,
    AspirateProperties as SharedDataAspirateProperties,
    SingleDispenseProperties as SharedDataSingleDispenseProperties,
    MultiDispenseProperties as SharedDataMultiDispenseProperties,
    TipPosition as SharedDataTipPosition,
    DelayProperties as SharedDataDelayProperties,
    DelayParams as SharedDataDelayParams,
    TouchTipProperties as SharedDataTouchTipProperties,
    LiquidClassTouchTipParams as SharedDataTouchTipParams,
    MixProperties as SharedDataMixProperties,
    MixParams as SharedDataMixParams,
    BlowoutProperties as SharedDataBlowoutProperties,
    BlowoutParams as SharedDataBlowoutParams,
    ByTipTypeSetting as SharedByTipTypeSetting,
    Submerge as SharedDataSubmerge,
    RetractAspirate as SharedDataRetractAspirate,
    RetractDispense as SharedDataRetractDispense,
    BlowoutLocation,
    PositionReference,
    Coordinate,
)
from . import validation


class LiquidHandlingPropertyByVolume:
    def __init__(self, by_volume_property: Sequence[Tuple[float, float]]) -> None:
        self._initial_properties_by_volume = by_volume_property
        self._properties_by_volume: Dict[float, float] = {
            float(volume): value for volume, value in by_volume_property
        }
        # Volumes need to be sorted for proper interpolation of non-defined volumes, and the
        # corresponding values need to be in the same order for them to be interpolated correctly
        self._sorted_volumes: Tuple[float, ...] = ()
        self._sorted_values: Tuple[float, ...] = ()
        self._sort_volume_and_values()

    def as_dict(self) -> Dict[float, float]:
        """Get a dictionary representation of all set volumes and values along with the default."""
        return self._properties_by_volume

    def as_list_of_tuples(self) -> List[Tuple[float, float]]:
        """Get as list of tuples."""
        return list(self._properties_by_volume.items())

    def get_for_volume(self, volume: float) -> float:
        """Get a value by volume for this property. Volumes not defined will be interpolated between set volumes."""
        validated_volume = validation.ensure_positive_float(volume)
        if len(self._properties_by_volume) == 0:
            raise ValueError(
                "No properties found for any volumes. Cannot interpolate for the given volume."
            )
        try:
            return self._properties_by_volume[validated_volume]
        except KeyError:
            # If volume is not defined in dictionary, do a piecewise interpolation with existing sorted values
            return float(
                interp(validated_volume, self._sorted_volumes, self._sorted_values)
            )

    def set_for_all_volumes(self, value: float) -> None:
        """Override all existing volume-dependent values with the given value."""
        self.clear_values()
        self.set_for_volume(0, value)

    def set_for_volume(self, volume: float, value: float) -> None:
        """Add a new volume and value for the property for the interpolation curve."""
        validated_volume = validation.ensure_positive_float(volume)
        self._properties_by_volume[validated_volume] = value
        self._sort_volume_and_values()

    def delete_for_volume(self, volume: float) -> None:
        """Remove an existing volume and value from the property."""
        try:
            del self._properties_by_volume[volume]
        except KeyError:
            raise KeyError(f"No value set for volume {volume} uL")
        self._sort_volume_and_values()

    def clear_values(self) -> None:
        """Removes all existing volume and value pairs from the curve."""
        self._properties_by_volume = {}

    def reset_values(self) -> None:
        """Resets volumes and values to the default."""
        self._properties_by_volume = {
            float(volume): value for volume, value in self._initial_properties_by_volume
        }
        self._sort_volume_and_values()

    def _sort_volume_and_values(self) -> None:
        """Sort volume in increasing order along with corresponding values in matching order."""
        self._sorted_volumes, self._sorted_values = (
            zip(*sorted(self._properties_by_volume.items()))
            if len(self._properties_by_volume) > 0
            else [(), ()]
        )


# We use slots for this dataclass (and the rest of liquid properties) to prevent dynamic creation of attributes
# not defined in the class, not for any performance reasons. This is so that mistyping properties when overriding
# values will cause the protocol to fail analysis, rather than silently passing.
@dataclass(slots=True)
class TipPosition:

    _position_reference: PositionReference
    _offset: Coordinate

    @property
    def position_reference(self) -> PositionReference:
        return self._position_reference

    @position_reference.setter
    def position_reference(self, new_position: Union[str, PositionReference]) -> None:
        self._position_reference = (
            new_position
            if isinstance(new_position, PositionReference)
            else PositionReference(new_position)
        )

    @property
    def offset(self) -> Coordinate:
        return self._offset

    @offset.setter
    def offset(self, new_offset: Union[Sequence[float], Coordinate]) -> None:
        if isinstance(new_offset, Coordinate):
            new_coordinate: Sequence[Union[int, float]] = [
                new_offset.x,
                new_offset.y,
                new_offset.z,
            ]
        else:
            new_coordinate = new_offset
        x, y, z = validation.validate_coordinates(new_coordinate)
        self._offset = Coordinate(x=x, y=y, z=z)

    def as_shared_data_model(self) -> SharedDataTipPosition:
        return SharedDataTipPosition(
            positionReference=self._position_reference,
            offset=self.offset,
        )


@dataclass(slots=True)
class DelayProperties:

    _enabled: bool
    _duration: Optional[float]

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, enable: bool) -> None:
        validated_enable = validation.ensure_boolean(enable)
        if validated_enable and self._duration is None:
            raise ValueError("duration must be set before enabling delay.")
        self._enabled = validated_enable

    @property
    def duration(self) -> Optional[float]:
        return self._duration

    @duration.setter
    def duration(self, new_duration: float) -> None:
        validated_duration = validation.ensure_positive_float(new_duration)
        self._duration = validated_duration

    def as_shared_data_model(self) -> SharedDataDelayProperties:
        return SharedDataDelayProperties(
            enable=self._enabled,
            params=SharedDataDelayParams(duration=self.duration)
            if self.duration is not None
            else None,
        )


@dataclass(slots=True)
class TouchTipProperties:

    _enabled: bool
    _z_offset: Optional[float]
    _mm_from_edge: Optional[float]
    _speed: Optional[float]

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, enable: bool) -> None:
        validated_enable = validation.ensure_boolean(enable)
        if validated_enable and (
            self._z_offset is None or self._mm_from_edge is None or self._speed is None
        ):
            raise ValueError(
                "z_offset, mm_from_edge and speed must be set before enabling touch tip."
            )
        self._enabled = validated_enable

    @property
    def z_offset(self) -> Optional[float]:
        return self._z_offset

    @z_offset.setter
    def z_offset(self, new_offset: float) -> None:
        validated_offset = validation.ensure_float(new_offset)
        self._z_offset = validated_offset

    @property
    def mm_from_edge(self) -> Optional[float]:
        return self._mm_from_edge

    @mm_from_edge.setter
    def mm_from_edge(self, new_mm: float) -> None:
        validated_mm = validation.ensure_float(new_mm)
        self._mm_from_edge = validated_mm

    @property
    def speed(self) -> Optional[float]:
        return self._speed

    @speed.setter
    def speed(self, new_speed: float) -> None:
        validated_speed = validation.ensure_greater_than_zero_float(new_speed)
        self._speed = validated_speed

    def _get_shared_data_params(self) -> Optional[SharedDataTouchTipParams]:
        """Get the touch tip params in schema v1 shape."""
        if (
            self._z_offset is not None
            and self._mm_from_edge is not None
            and self._speed is not None
        ):
            return SharedDataTouchTipParams(
                zOffset=self._z_offset,
                mmFromEdge=self._mm_from_edge,
                speed=self._speed,
            )
        else:
            return None

    def as_shared_data_model(self) -> SharedDataTouchTipProperties:
        return SharedDataTouchTipProperties(
            enable=self._enabled,
            params=self._get_shared_data_params(),
        )


@dataclass(slots=True)
class MixProperties:

    _enabled: bool
    _repetitions: Optional[int]
    _volume: Optional[float]

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, enable: bool) -> None:
        validated_enable = validation.ensure_boolean(enable)
        if validated_enable and (self._repetitions is None or self._volume is None):
            raise ValueError("repetitions and volume must be set before enabling mix.")
        self._enabled = validated_enable

    @property
    def repetitions(self) -> Optional[int]:
        return self._repetitions

    @repetitions.setter
    def repetitions(self, new_repetitions: int) -> None:
        validated_repetitions = validation.ensure_positive_int(new_repetitions)
        self._repetitions = validated_repetitions

    @property
    def volume(self) -> Optional[float]:
        return self._volume

    @volume.setter
    def volume(self, new_volume: float) -> None:
        validated_volume = validation.ensure_greater_than_zero_float(new_volume)
        self._volume = validated_volume

    def _get_shared_data_params(self) -> Optional[SharedDataMixParams]:
        """Get the mix params in schema v1 shape."""
        if self._repetitions is not None and self._volume is not None:
            return SharedDataMixParams(
                repetitions=self._repetitions,
                volume=self._volume,
            )
        else:
            return None

    def as_shared_data_model(self) -> SharedDataMixProperties:
        return SharedDataMixProperties(
            enable=self._enabled,
            params=self._get_shared_data_params(),
        )


@dataclass(slots=True)
class BlowoutProperties:

    _enabled: bool
    _location: Optional[BlowoutLocation]
    _flow_rate: Optional[float]

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, enable: bool) -> None:
        validated_enable = validation.ensure_boolean(enable)
        if validated_enable and (self._location is None or self._flow_rate is None):
            raise ValueError(
                "location and flow_rate must be set before enabling blowout."
            )
        self._enabled = validated_enable

    @property
    def location(self) -> Optional[BlowoutLocation]:
        return self._location

    @location.setter
    def location(self, new_location: str) -> None:
        self._location = BlowoutLocation(new_location)

    @property
    def flow_rate(self) -> Optional[float]:
        return self._flow_rate

    @flow_rate.setter
    def flow_rate(self, new_flow_rate: float) -> None:
        validated_flow_rate = validation.ensure_greater_than_zero_float(new_flow_rate)
        self._flow_rate = validated_flow_rate

    def _get_shared_data_params(self) -> Optional[SharedDataBlowoutParams]:
        """Get the mix params in schema v1 shape."""
        if self._location is not None and self._flow_rate is not None:
            return SharedDataBlowoutParams(
                location=self._location,
                flowRate=self._flow_rate,
            )
        else:
            return None

    def as_shared_data_model(self) -> SharedDataBlowoutProperties:
        return SharedDataBlowoutProperties(
            enable=self._enabled,
            params=self._get_shared_data_params(),
        )


@dataclass(slots=True)
class _SubmergeRetractCommon:

    _speed: float
    _delay: DelayProperties

    @property
    def speed(self) -> float:
        return self._speed

    @speed.setter
    def speed(self, new_speed: float) -> None:
        validated_speed = validation.ensure_positive_float(new_speed)
        self._speed = validated_speed

    @property
    def delay(self) -> DelayProperties:
        return self._delay


@dataclass(slots=True)
class Submerge(_SubmergeRetractCommon):

    _start_position: TipPosition

    @property
    def start_position(self) -> TipPosition:
        return self._start_position

    def as_shared_data_model(self) -> SharedDataSubmerge:
        return SharedDataSubmerge(
            startPosition=self._start_position.as_shared_data_model(),
            speed=self._speed,
            delay=self._delay.as_shared_data_model(),
        )


@dataclass(slots=True)
class RetractAspirate(_SubmergeRetractCommon):

    _end_position: TipPosition
    _air_gap_by_volume: LiquidHandlingPropertyByVolume
    _touch_tip: TouchTipProperties

    @property
    def end_position(self) -> TipPosition:
        return self._end_position

    @property
    def air_gap_by_volume(self) -> LiquidHandlingPropertyByVolume:
        return self._air_gap_by_volume

    @property
    def touch_tip(self) -> TouchTipProperties:
        return self._touch_tip

    def as_shared_data_model(self) -> SharedDataRetractAspirate:
        return SharedDataRetractAspirate(
            endPosition=self._end_position.as_shared_data_model(),
            speed=self._speed,
            airGapByVolume=self._air_gap_by_volume.as_list_of_tuples(),
            touchTip=self._touch_tip.as_shared_data_model(),
            delay=self._delay.as_shared_data_model(),
        )


@dataclass(slots=True)
class RetractDispense(_SubmergeRetractCommon):
    _end_position: TipPosition
    _air_gap_by_volume: LiquidHandlingPropertyByVolume
    _touch_tip: TouchTipProperties
    _blowout: BlowoutProperties

    @property
    def end_position(self) -> TipPosition:
        return self._end_position

    @property
    def air_gap_by_volume(self) -> LiquidHandlingPropertyByVolume:
        return self._air_gap_by_volume

    @property
    def touch_tip(self) -> TouchTipProperties:
        return self._touch_tip

    @property
    def blowout(self) -> BlowoutProperties:
        return self._blowout

    def as_shared_data_model(self) -> SharedDataRetractDispense:
        return SharedDataRetractDispense(
            endPosition=self._end_position.as_shared_data_model(),
            speed=self._speed,
            airGapByVolume=self._air_gap_by_volume.as_list_of_tuples(),
            blowout=self._blowout.as_shared_data_model(),
            touchTip=self._touch_tip.as_shared_data_model(),
            delay=self._delay.as_shared_data_model(),
        )


@dataclass(slots=True)
class _BaseLiquidHandlingProperties:

    _submerge: Submerge
    _flow_rate_by_volume: LiquidHandlingPropertyByVolume
    _correction_by_volume: LiquidHandlingPropertyByVolume
    _delay: DelayProperties

    @property
    def submerge(self) -> Submerge:
        return self._submerge

    @property
    def flow_rate_by_volume(self) -> LiquidHandlingPropertyByVolume:
        return self._flow_rate_by_volume

    @property
    def correction_by_volume(self) -> LiquidHandlingPropertyByVolume:
        return self._correction_by_volume

    @property
    def delay(self) -> DelayProperties:
        return self._delay


@dataclass(slots=True)
class AspirateProperties(_BaseLiquidHandlingProperties):

    _aspirate_position: TipPosition
    _retract: RetractAspirate
    _pre_wet: bool
    _mix: MixProperties

    @property
    def aspirate_position(self) -> TipPosition:
        return self._aspirate_position

    @property
    def pre_wet(self) -> bool:
        return self._pre_wet

    @pre_wet.setter
    def pre_wet(self, new_setting: bool) -> None:
        validated_setting = validation.ensure_boolean(new_setting)
        self._pre_wet = validated_setting

    @property
    def retract(self) -> RetractAspirate:
        return self._retract

    @property
    def mix(self) -> MixProperties:
        return self._mix

    def as_shared_data_model(self) -> SharedDataAspirateProperties:
        return SharedDataAspirateProperties(
            submerge=self._submerge.as_shared_data_model(),
            retract=self._retract.as_shared_data_model(),
            aspiratePosition=self._aspirate_position.as_shared_data_model(),
            flowRateByVolume=self._flow_rate_by_volume.as_list_of_tuples(),
            preWet=self._pre_wet,
            mix=self._mix.as_shared_data_model(),
            delay=self._delay.as_shared_data_model(),
            correctionByVolume=self._correction_by_volume.as_list_of_tuples(),
        )


@dataclass(slots=True)
class SingleDispenseProperties(_BaseLiquidHandlingProperties):

    _dispense_position: TipPosition
    _retract: RetractDispense
    _push_out_by_volume: LiquidHandlingPropertyByVolume
    _mix: MixProperties

    @property
    def dispense_position(self) -> TipPosition:
        return self._dispense_position

    @property
    def push_out_by_volume(self) -> LiquidHandlingPropertyByVolume:
        return self._push_out_by_volume

    @property
    def retract(self) -> RetractDispense:
        return self._retract

    @property
    def mix(self) -> MixProperties:
        return self._mix

    def as_shared_data_model(self) -> SharedDataSingleDispenseProperties:
        return SharedDataSingleDispenseProperties(
            submerge=self._submerge.as_shared_data_model(),
            retract=self._retract.as_shared_data_model(),
            dispensePosition=self._dispense_position.as_shared_data_model(),
            flowRateByVolume=self._flow_rate_by_volume.as_list_of_tuples(),
            mix=self._mix.as_shared_data_model(),
            pushOutByVolume=self._push_out_by_volume.as_list_of_tuples(),
            delay=self._delay.as_shared_data_model(),
            correctionByVolume=self._correction_by_volume.as_list_of_tuples(),
        )


@dataclass(slots=True)
class MultiDispenseProperties(_BaseLiquidHandlingProperties):

    _dispense_position: TipPosition
    _retract: RetractDispense
    _conditioning_by_volume: LiquidHandlingPropertyByVolume
    _disposal_by_volume: LiquidHandlingPropertyByVolume

    @property
    def dispense_position(self) -> TipPosition:
        return self._dispense_position

    @property
    def retract(self) -> RetractDispense:
        return self._retract

    @property
    def conditioning_by_volume(self) -> LiquidHandlingPropertyByVolume:
        return self._conditioning_by_volume

    @property
    def disposal_by_volume(self) -> LiquidHandlingPropertyByVolume:
        return self._disposal_by_volume

    def as_shared_data_model(self) -> SharedDataMultiDispenseProperties:
        return SharedDataMultiDispenseProperties(
            submerge=self._submerge.as_shared_data_model(),
            retract=self._retract.as_shared_data_model(),
            dispensePosition=self._dispense_position.as_shared_data_model(),
            flowRateByVolume=self._flow_rate_by_volume.as_list_of_tuples(),
            conditioningByVolume=self._conditioning_by_volume.as_list_of_tuples(),
            disposalByVolume=self._disposal_by_volume.as_list_of_tuples(),
            delay=self._delay.as_shared_data_model(),
            correctionByVolume=self._correction_by_volume.as_list_of_tuples(),
        )


@dataclass(slots=True)
class TransferProperties:
    _aspirate: AspirateProperties
    _dispense: SingleDispenseProperties
    _multi_dispense: Optional[MultiDispenseProperties]

    @property
    def aspirate(self) -> AspirateProperties:
        """Aspirate properties."""
        return self._aspirate

    @property
    def dispense(self) -> SingleDispenseProperties:
        """Single dispense properties."""
        return self._dispense

    @property
    def multi_dispense(self) -> Optional[MultiDispenseProperties]:
        """Multi dispense properties."""
        return self._multi_dispense


def _build_tip_position(tip_position: SharedDataTipPosition) -> TipPosition:
    return TipPosition(
        _position_reference=tip_position.positionReference, _offset=tip_position.offset
    )


def _build_delay_properties(
    delay_properties: SharedDataDelayProperties,
) -> DelayProperties:
    if delay_properties.params is not None:
        duration = delay_properties.params.duration
    else:
        duration = None
    return DelayProperties(_enabled=delay_properties.enable, _duration=duration)


def _build_touch_tip_properties(
    touch_tip_properties: SharedDataTouchTipProperties,
) -> TouchTipProperties:
    if touch_tip_properties.params is not None:
        z_offset = touch_tip_properties.params.zOffset
        mm_from_edge = touch_tip_properties.params.mmFromEdge
        speed = touch_tip_properties.params.speed
    else:
        z_offset = None
        mm_from_edge = None
        speed = None
    return TouchTipProperties(
        _enabled=touch_tip_properties.enable,
        _z_offset=z_offset,
        _mm_from_edge=mm_from_edge,
        _speed=speed,
    )


def _build_mix_properties(
    mix_properties: SharedDataMixProperties,
) -> MixProperties:
    if mix_properties.params is not None:
        repetitions = mix_properties.params.repetitions
        volume = mix_properties.params.volume
    else:
        repetitions = None
        volume = None
    return MixProperties(
        _enabled=mix_properties.enable, _repetitions=repetitions, _volume=volume
    )


def _build_blowout_properties(
    blowout_properties: SharedDataBlowoutProperties,
) -> BlowoutProperties:
    if blowout_properties.params is not None:
        location = blowout_properties.params.location
        flow_rate = blowout_properties.params.flowRate
    else:
        location = None
        flow_rate = None
    return BlowoutProperties(
        _enabled=blowout_properties.enable, _location=location, _flow_rate=flow_rate
    )


def _build_submerge(
    submerge_properties: SharedDataSubmerge,
) -> Submerge:
    return Submerge(
        _start_position=_build_tip_position(submerge_properties.startPosition),
        _speed=submerge_properties.speed,
        _delay=_build_delay_properties(submerge_properties.delay),
    )


def _build_retract_aspirate(
    retract_aspirate: SharedDataRetractAspirate,
) -> RetractAspirate:
    return RetractAspirate(
        _end_position=_build_tip_position(retract_aspirate.endPosition),
        _speed=retract_aspirate.speed,
        _air_gap_by_volume=LiquidHandlingPropertyByVolume(
            retract_aspirate.airGapByVolume
        ),
        _touch_tip=_build_touch_tip_properties(retract_aspirate.touchTip),
        _delay=_build_delay_properties(retract_aspirate.delay),
    )


def _build_retract_dispense(
    retract_dispense: SharedDataRetractDispense,
) -> RetractDispense:
    return RetractDispense(
        _end_position=_build_tip_position(retract_dispense.endPosition),
        _speed=retract_dispense.speed,
        _air_gap_by_volume=LiquidHandlingPropertyByVolume(
            retract_dispense.airGapByVolume
        ),
        _blowout=_build_blowout_properties(retract_dispense.blowout),
        _touch_tip=_build_touch_tip_properties(retract_dispense.touchTip),
        _delay=_build_delay_properties(retract_dispense.delay),
    )


def build_aspirate_properties(
    aspirate_properties: SharedDataAspirateProperties,
) -> AspirateProperties:
    return AspirateProperties(
        _submerge=_build_submerge(aspirate_properties.submerge),
        _retract=_build_retract_aspirate(aspirate_properties.retract),
        _aspirate_position=_build_tip_position(aspirate_properties.aspiratePosition),
        _flow_rate_by_volume=LiquidHandlingPropertyByVolume(
            aspirate_properties.flowRateByVolume
        ),
        _correction_by_volume=LiquidHandlingPropertyByVolume(
            aspirate_properties.correctionByVolume
        ),
        _pre_wet=aspirate_properties.preWet,
        _mix=_build_mix_properties(aspirate_properties.mix),
        _delay=_build_delay_properties(aspirate_properties.delay),
    )


def build_single_dispense_properties(
    single_dispense_properties: SharedDataSingleDispenseProperties,
) -> SingleDispenseProperties:
    return SingleDispenseProperties(
        _submerge=_build_submerge(single_dispense_properties.submerge),
        _retract=_build_retract_dispense(single_dispense_properties.retract),
        _dispense_position=_build_tip_position(
            single_dispense_properties.dispensePosition
        ),
        _flow_rate_by_volume=LiquidHandlingPropertyByVolume(
            single_dispense_properties.flowRateByVolume
        ),
        _correction_by_volume=LiquidHandlingPropertyByVolume(
            single_dispense_properties.correctionByVolume
        ),
        _mix=_build_mix_properties(single_dispense_properties.mix),
        _push_out_by_volume=LiquidHandlingPropertyByVolume(
            single_dispense_properties.pushOutByVolume
        ),
        _delay=_build_delay_properties(single_dispense_properties.delay),
    )


def build_multi_dispense_properties(
    multi_dispense_properties: Optional[SharedDataMultiDispenseProperties],
) -> Optional[MultiDispenseProperties]:
    if multi_dispense_properties is None:
        return None
    return MultiDispenseProperties(
        _submerge=_build_submerge(multi_dispense_properties.submerge),
        _retract=_build_retract_dispense(multi_dispense_properties.retract),
        _dispense_position=_build_tip_position(
            multi_dispense_properties.dispensePosition
        ),
        _flow_rate_by_volume=LiquidHandlingPropertyByVolume(
            multi_dispense_properties.flowRateByVolume
        ),
        _correction_by_volume=LiquidHandlingPropertyByVolume(
            multi_dispense_properties.correctionByVolume
        ),
        _conditioning_by_volume=LiquidHandlingPropertyByVolume(
            multi_dispense_properties.conditioningByVolume
        ),
        _disposal_by_volume=LiquidHandlingPropertyByVolume(
            multi_dispense_properties.disposalByVolume
        ),
        _delay=_build_delay_properties(multi_dispense_properties.delay),
    )


def build_transfer_properties(
    transfer_properties: Union[SharedDataTransferProperties, SharedByTipTypeSetting],
) -> TransferProperties:
    if isinstance(transfer_properties, SharedByTipTypeSetting):
        _transfer_properties = SharedDataTransferProperties(
            aspirate=transfer_properties.aspirate,
            singleDispense=transfer_properties.singleDispense,
            multiDispense=transfer_properties.multiDispense,
        )
    else:
        _transfer_properties = transfer_properties
    return TransferProperties(
        _aspirate=build_aspirate_properties(_transfer_properties.aspirate),
        _dispense=build_single_dispense_properties(_transfer_properties.singleDispense),
        _multi_dispense=build_multi_dispense_properties(
            _transfer_properties.multiDispense
        ),
    )
