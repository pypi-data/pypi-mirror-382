"""Union types of concrete command definitions."""

from collections.abc import Collection
from typing import Annotated, Type, Union, get_type_hints

from pydantic import Field, TypeAdapter

from opentrons.util.get_union_elements import get_union_elements

from .command import DefinedErrorData
from .pipetting_common import (
    OverpressureError,
    LiquidNotFoundError,
    TipPhysicallyAttachedError,
)
from .movement_common import StallOrCollisionError
from .flex_stacker.common import (
    FlexStackerStallOrCollisionError,
    FlexStackerShuttleError,
    FlexStackerHopperError,
    FlexStackerLabwareRetrieveError,
    FlexStackerShuttleOccupiedError,
    FlexStackerLabwareStoreError,
)

from . import absorbance_reader
from . import flex_stacker
from . import heater_shaker
from . import magnetic_module
from . import temperature_module
from . import thermocycler

from . import calibration
from . import unsafe
from . import robot

from .set_rail_lights import (
    SetRailLights,
    SetRailLightsCommandType,
    SetRailLightsCreate,
    SetRailLightsParams,
    SetRailLightsResult,
)

from .air_gap_in_place import (
    AirGapInPlace,
    AirGapInPlaceParams,
    AirGapInPlaceCreate,
    AirGapInPlaceResult,
    AirGapInPlaceCommandType,
)

from .aspirate import (
    Aspirate,
    AspirateParams,
    AspirateCreate,
    AspirateResult,
    AspirateCommandType,
)

from .aspirate_in_place import (
    AspirateInPlace,
    AspirateInPlaceParams,
    AspirateInPlaceCreate,
    AspirateInPlaceResult,
    AspirateInPlaceCommandType,
)

from .aspirate_while_tracking import (
    AspirateWhileTracking,
    AspirateWhileTrackingParams,
    AspirateWhileTrackingCreate,
    AspirateWhileTrackingResult,
    AspirateWhileTrackingCommandType,
)

from .comment import (
    Comment,
    CommentParams,
    CommentCreate,
    CommentResult,
    CommentCommandType,
)

from .custom import (
    Custom,
    CustomParams,
    CustomCreate,
    CustomResult,
    CustomCommandType,
)

from .dispense import (
    Dispense,
    DispenseParams,
    DispenseCreate,
    DispenseResult,
    DispenseCommandType,
)

from .dispense_while_tracking import (
    DispenseWhileTracking,
    DispenseWhileTrackingParams,
    DispenseWhileTrackingCreate,
    DispenseWhileTrackingResult,
    DispenseWhileTrackingCommandType,
)

from .dispense_in_place import (
    DispenseInPlace,
    DispenseInPlaceParams,
    DispenseInPlaceCreate,
    DispenseInPlaceResult,
    DispenseInPlaceCommandType,
)

from .drop_tip import (
    DropTip,
    DropTipParams,
    DropTipCreate,
    DropTipResult,
    DropTipCommandType,
)

from .drop_tip_in_place import (
    DropTipInPlace,
    DropTipInPlaceParams,
    DropTipInPlaceCreate,
    DropTipInPlaceResult,
    DropTipInPlaceCommandType,
)

from .home import (
    Home,
    HomeParams,
    HomeCreate,
    HomeResult,
    HomeCommandType,
)

from .load_labware import (
    LoadLabware,
    LoadLabwareParams,
    LoadLabwareCreate,
    LoadLabwareResult,
    LoadLabwareCommandType,
)

from .reload_labware import (
    ReloadLabware,
    ReloadLabwareParams,
    ReloadLabwareCreate,
    ReloadLabwareResult,
    ReloadLabwareCommandType,
)

from .load_liquid import (
    LoadLiquid,
    LoadLiquidParams,
    LoadLiquidCreate,
    LoadLiquidResult,
    LoadLiquidCommandType,
)

from .load_liquid_class import (
    LoadLiquidClass,
    LoadLiquidClassParams,
    LoadLiquidClassCreate,
    LoadLiquidClassResult,
    LoadLiquidClassCommandType,
)

from .load_module import (
    LoadModule,
    LoadModuleParams,
    LoadModuleCreate,
    LoadModuleResult,
    LoadModuleCommandType,
)

from .load_pipette import (
    LoadPipette,
    LoadPipetteParams,
    LoadPipetteCreate,
    LoadPipetteResult,
    LoadPipetteCommandType,
)

from .load_lid_stack import (
    LoadLidStack,
    LoadLidStackParams,
    LoadLidStackCreate,
    LoadLidStackResult,
    LoadLidStackCommandType,
)

from .load_lid import (
    LoadLid,
    LoadLidParams,
    LoadLidCreate,
    LoadLidResult,
    LoadLidCommandType,
)

from .move_labware import (
    GripperMovementError,
    MoveLabware,
    MoveLabwareParams,
    MoveLabwareCreate,
    MoveLabwareResult,
    MoveLabwareCommandType,
)

from .move_relative import (
    MoveRelative,
    MoveRelativeParams,
    MoveRelativeCreate,
    MoveRelativeResult,
    MoveRelativeCommandType,
)

from .move_to_coordinates import (
    MoveToCoordinates,
    MoveToCoordinatesParams,
    MoveToCoordinatesCreate,
    MoveToCoordinatesResult,
    MoveToCoordinatesCommandType,
)

from .move_to_well import (
    MoveToWell,
    MoveToWellParams,
    MoveToWellCreate,
    MoveToWellResult,
    MoveToWellCommandType,
)

from .move_to_addressable_area import (
    MoveToAddressableArea,
    MoveToAddressableAreaParams,
    MoveToAddressableAreaCreate,
    MoveToAddressableAreaResult,
    MoveToAddressableAreaCommandType,
)

from .move_to_addressable_area_for_drop_tip import (
    MoveToAddressableAreaForDropTip,
    MoveToAddressableAreaForDropTipParams,
    MoveToAddressableAreaForDropTipCreate,
    MoveToAddressableAreaForDropTipResult,
    MoveToAddressableAreaForDropTipCommandType,
)

from .wait_for_resume import (
    WaitForResume,
    WaitForResumeParams,
    WaitForResumeCreate,
    WaitForResumeResult,
    WaitForResumeCommandType,
)

from .wait_for_duration import (
    WaitForDuration,
    WaitForDurationParams,
    WaitForDurationCreate,
    WaitForDurationResult,
    WaitForDurationCommandType,
)

from .pick_up_tip import (
    PickUpTip,
    PickUpTipParams,
    PickUpTipCreate,
    PickUpTipResult,
    PickUpTipCommandType,
    TipPhysicallyMissingError,
)

from .touch_tip import (
    TouchTip,
    TouchTipParams,
    TouchTipCreate,
    TouchTipResult,
    TouchTipCommandType,
)

from .save_position import (
    SavePosition,
    SavePositionParams,
    SavePositionCreate,
    SavePositionResult,
    SavePositionCommandType,
)

from .blow_out import (
    BlowOutParams,
    BlowOut,
    BlowOutCreate,
    BlowOutCommandType,
    BlowOutResult,
)

from .blow_out_in_place import (
    BlowOutInPlaceParams,
    BlowOutInPlace,
    BlowOutInPlaceCreate,
    BlowOutInPlaceCommandType,
    BlowOutInPlaceResult,
)

from .set_status_bar import (
    SetStatusBar,
    SetStatusBarParams,
    SetStatusBarCreate,
    SetStatusBarResult,
    SetStatusBarCommandType,
)

from .retract_axis import (
    RetractAxis,
    RetractAxisParams,
    RetractAxisCreate,
    RetractAxisResult,
    RetractAxisCommandType,
)

from .configure_for_volume import (
    ConfigureForVolume,
    ConfigureForVolumeParams,
    ConfigureForVolumeCreate,
    ConfigureForVolumeResult,
    ConfigureForVolumeCommandType,
)

from .prepare_to_aspirate import (
    PrepareToAspirate,
    PrepareToAspirateParams,
    PrepareToAspirateCreate,
    PrepareToAspirateResult,
    PrepareToAspirateCommandType,
)

from .configure_nozzle_layout import (
    ConfigureNozzleLayout,
    ConfigureNozzleLayoutCreate,
    ConfigureNozzleLayoutParams,
    ConfigureNozzleLayoutResult,
    ConfigureNozzleLayoutCommandType,
)

from .verify_tip_presence import (
    VerifyTipPresence,
    VerifyTipPresenceCreate,
    VerifyTipPresenceParams,
    VerifyTipPresenceResult,
    VerifyTipPresenceCommandType,
)

from .get_tip_presence import (
    GetTipPresence,
    GetTipPresenceCreate,
    GetTipPresenceParams,
    GetTipPresenceResult,
    GetTipPresenceCommandType,
)

from .get_next_tip import (
    GetNextTip,
    GetNextTipCreate,
    GetNextTipParams,
    GetNextTipResult,
    GetNextTipCommandType,
)

from .liquid_probe import (
    LiquidProbe,
    LiquidProbeParams,
    LiquidProbeCreate,
    LiquidProbeResult,
    LiquidProbeCommandType,
    TryLiquidProbe,
    TryLiquidProbeParams,
    TryLiquidProbeCreate,
    TryLiquidProbeResult,
    TryLiquidProbeCommandType,
)

from .seal_pipette_to_tip import (
    SealPipetteToTip,
    SealPipetteToTipParams,
    SealPipetteToTipCreate,
    SealPipetteToTipResult,
    SealPipetteToTipCommandType,
)

from .pressure_dispense import (
    PressureDispense,
    PressureDispenseParams,
    PressureDispenseCreate,
    PressureDispenseResult,
    PressureDispenseCommandType,
)

from .unseal_pipette_from_tip import (
    UnsealPipetteFromTip,
    UnsealPipetteFromTipParams,
    UnsealPipetteFromTipCreate,
    UnsealPipetteFromTipResult,
    UnsealPipetteFromTipCommandType,
)

from .identify_module import (
    IdentifyModule,
    IdentifyModuleParams,
    IdentifyModuleCreate,
    IdentifyModuleResult,
    IdentifyModuleCommandType,
)

Command = Annotated[
    Union[
        AirGapInPlace,
        Aspirate,
        AspirateInPlace,
        AspirateWhileTracking,
        Comment,
        Custom,
        Dispense,
        DispenseInPlace,
        DispenseWhileTracking,
        BlowOut,
        BlowOutInPlace,
        ConfigureForVolume,
        ConfigureNozzleLayout,
        DropTip,
        DropTipInPlace,
        Home,
        RetractAxis,
        LoadLabware,
        ReloadLabware,
        LoadLiquid,
        LoadLiquidClass,
        LoadModule,
        IdentifyModule,
        LoadPipette,
        LoadLidStack,
        LoadLid,
        MoveLabware,
        MoveRelative,
        MoveToCoordinates,
        MoveToWell,
        MoveToAddressableArea,
        MoveToAddressableAreaForDropTip,
        PrepareToAspirate,
        WaitForResume,
        WaitForDuration,
        PickUpTip,
        SavePosition,
        SetRailLights,
        TouchTip,
        SetStatusBar,
        VerifyTipPresence,
        GetTipPresence,
        GetNextTip,
        LiquidProbe,
        TryLiquidProbe,
        SealPipetteToTip,
        PressureDispense,
        UnsealPipetteFromTip,
        heater_shaker.WaitForTemperature,
        heater_shaker.SetTargetTemperature,
        heater_shaker.DeactivateHeater,
        heater_shaker.SetAndWaitForShakeSpeed,
        heater_shaker.DeactivateShaker,
        heater_shaker.OpenLabwareLatch,
        heater_shaker.CloseLabwareLatch,
        magnetic_module.Disengage,
        magnetic_module.Engage,
        temperature_module.SetTargetTemperature,
        temperature_module.WaitForTemperature,
        temperature_module.DeactivateTemperature,
        thermocycler.SetTargetBlockTemperature,
        thermocycler.WaitForBlockTemperature,
        thermocycler.SetTargetLidTemperature,
        thermocycler.WaitForLidTemperature,
        thermocycler.DeactivateBlock,
        thermocycler.DeactivateLid,
        thermocycler.OpenLid,
        thermocycler.CloseLid,
        thermocycler.RunProfile,
        thermocycler.RunExtendedProfile,
        absorbance_reader.CloseLid,
        absorbance_reader.OpenLid,
        absorbance_reader.Initialize,
        absorbance_reader.ReadAbsorbance,
        flex_stacker.Retrieve,
        flex_stacker.Store,
        flex_stacker.SetStoredLabware,
        flex_stacker.Fill,
        flex_stacker.Empty,
        calibration.CalibrateGripper,
        calibration.CalibratePipette,
        calibration.CalibrateModule,
        calibration.MoveToMaintenancePosition,
        unsafe.UnsafeBlowOutInPlace,
        unsafe.UnsafeDropTipInPlace,
        unsafe.UpdatePositionEstimators,
        unsafe.UnsafeEngageAxes,
        unsafe.UnsafeUngripLabware,
        unsafe.UnsafePlaceLabware,
        unsafe.UnsafeFlexStackerManualRetrieve,
        unsafe.UnsafeFlexStackerCloseLatch,
        unsafe.UnsafeFlexStackerOpenLatch,
        unsafe.UnsafeFlexStackerPrepareShuttle,
        robot.MoveTo,
        robot.MoveAxesRelative,
        robot.MoveAxesTo,
        robot.OpenGripperJaw,
        robot.CloseGripperJaw,
    ],
    Field(discriminator="commandType"),
]

CommandParams = Union[
    AirGapInPlaceParams,
    AspirateParams,
    AspirateWhileTrackingParams,
    AspirateInPlaceParams,
    CommentParams,
    ConfigureForVolumeParams,
    ConfigureNozzleLayoutParams,
    CustomParams,
    DispenseParams,
    DispenseInPlaceParams,
    DispenseWhileTrackingParams,
    BlowOutParams,
    BlowOutInPlaceParams,
    DropTipParams,
    DropTipInPlaceParams,
    HomeParams,
    RetractAxisParams,
    LoadLabwareParams,
    LoadLidStackParams,
    LoadLidParams,
    ReloadLabwareParams,
    LoadLiquidParams,
    LoadLiquidClassParams,
    LoadModuleParams,
    IdentifyModuleParams,
    LoadPipetteParams,
    MoveLabwareParams,
    MoveRelativeParams,
    MoveToCoordinatesParams,
    MoveToWellParams,
    MoveToAddressableAreaParams,
    MoveToAddressableAreaForDropTipParams,
    PrepareToAspirateParams,
    WaitForResumeParams,
    WaitForDurationParams,
    PickUpTipParams,
    SavePositionParams,
    SetRailLightsParams,
    TouchTipParams,
    SetStatusBarParams,
    VerifyTipPresenceParams,
    GetTipPresenceParams,
    GetNextTipParams,
    LiquidProbeParams,
    TryLiquidProbeParams,
    SealPipetteToTipParams,
    PressureDispenseParams,
    UnsealPipetteFromTipParams,
    heater_shaker.WaitForTemperatureParams,
    heater_shaker.SetTargetTemperatureParams,
    heater_shaker.DeactivateHeaterParams,
    heater_shaker.SetAndWaitForShakeSpeedParams,
    heater_shaker.DeactivateShakerParams,
    heater_shaker.OpenLabwareLatchParams,
    heater_shaker.CloseLabwareLatchParams,
    magnetic_module.DisengageParams,
    magnetic_module.EngageParams,
    temperature_module.SetTargetTemperatureParams,
    temperature_module.WaitForTemperatureParams,
    temperature_module.DeactivateTemperatureParams,
    thermocycler.SetTargetBlockTemperatureParams,
    thermocycler.WaitForBlockTemperatureParams,
    thermocycler.SetTargetLidTemperatureParams,
    thermocycler.WaitForLidTemperatureParams,
    thermocycler.DeactivateBlockParams,
    thermocycler.DeactivateLidParams,
    thermocycler.OpenLidParams,
    thermocycler.CloseLidParams,
    thermocycler.RunProfileParams,
    thermocycler.RunExtendedProfileParams,
    absorbance_reader.CloseLidParams,
    absorbance_reader.OpenLidParams,
    absorbance_reader.InitializeParams,
    absorbance_reader.ReadAbsorbanceParams,
    flex_stacker.RetrieveParams,
    flex_stacker.StoreParams,
    flex_stacker.SetStoredLabwareParams,
    flex_stacker.FillParams,
    flex_stacker.EmptyParams,
    calibration.CalibrateGripperParams,
    calibration.CalibratePipetteParams,
    calibration.CalibrateModuleParams,
    calibration.MoveToMaintenancePositionParams,
    unsafe.UnsafeBlowOutInPlaceParams,
    unsafe.UnsafeDropTipInPlaceParams,
    unsafe.UpdatePositionEstimatorsParams,
    unsafe.UnsafeEngageAxesParams,
    unsafe.UnsafeUngripLabwareParams,
    unsafe.UnsafePlaceLabwareParams,
    unsafe.UnsafeFlexStackerManualRetrieveParams,
    unsafe.UnsafeFlexStackerCloseLatchParams,
    unsafe.UnsafeFlexStackerOpenLatchParams,
    unsafe.UnsafeFlexStackerPrepareShuttleParams,
    robot.MoveAxesRelativeParams,
    robot.MoveAxesToParams,
    robot.MoveToParams,
    robot.OpenGripperJawParams,
    robot.CloseGripperJawParams,
]

CommandType = Union[
    AirGapInPlaceCommandType,
    AspirateCommandType,
    AspirateWhileTrackingCommandType,
    AspirateInPlaceCommandType,
    CommentCommandType,
    ConfigureForVolumeCommandType,
    ConfigureNozzleLayoutCommandType,
    CustomCommandType,
    DispenseCommandType,
    DispenseInPlaceCommandType,
    DispenseWhileTrackingCommandType,
    BlowOutCommandType,
    BlowOutInPlaceCommandType,
    DropTipCommandType,
    DropTipInPlaceCommandType,
    HomeCommandType,
    RetractAxisCommandType,
    LoadLabwareCommandType,
    ReloadLabwareCommandType,
    LoadLiquidCommandType,
    LoadLiquidClassCommandType,
    LoadModuleCommandType,
    IdentifyModuleCommandType,
    LoadPipetteCommandType,
    LoadLidStackCommandType,
    LoadLidCommandType,
    MoveLabwareCommandType,
    MoveRelativeCommandType,
    MoveToCoordinatesCommandType,
    MoveToWellCommandType,
    MoveToAddressableAreaCommandType,
    MoveToAddressableAreaForDropTipCommandType,
    PrepareToAspirateCommandType,
    WaitForResumeCommandType,
    WaitForDurationCommandType,
    PickUpTipCommandType,
    SavePositionCommandType,
    SetRailLightsCommandType,
    TouchTipCommandType,
    SetStatusBarCommandType,
    VerifyTipPresenceCommandType,
    GetTipPresenceCommandType,
    GetNextTipCommandType,
    LiquidProbeCommandType,
    TryLiquidProbeCommandType,
    SealPipetteToTipCommandType,
    PressureDispenseCommandType,
    UnsealPipetteFromTipCommandType,
    heater_shaker.WaitForTemperatureCommandType,
    heater_shaker.SetTargetTemperatureCommandType,
    heater_shaker.DeactivateHeaterCommandType,
    heater_shaker.SetAndWaitForShakeSpeedCommandType,
    heater_shaker.DeactivateShakerCommandType,
    heater_shaker.OpenLabwareLatchCommandType,
    heater_shaker.CloseLabwareLatchCommandType,
    magnetic_module.DisengageCommandType,
    magnetic_module.EngageCommandType,
    temperature_module.SetTargetTemperatureCommandType,
    temperature_module.WaitForTemperatureCommandType,
    temperature_module.DeactivateTemperatureCommandType,
    thermocycler.SetTargetBlockTemperatureCommandType,
    thermocycler.WaitForBlockTemperatureCommandType,
    thermocycler.SetTargetLidTemperatureCommandType,
    thermocycler.WaitForLidTemperatureCommandType,
    thermocycler.DeactivateBlockCommandType,
    thermocycler.DeactivateLidCommandType,
    thermocycler.OpenLidCommandType,
    thermocycler.CloseLidCommandType,
    thermocycler.RunProfileCommandType,
    thermocycler.RunExtendedProfileCommandType,
    absorbance_reader.CloseLidCommandType,
    absorbance_reader.OpenLidCommandType,
    absorbance_reader.InitializeCommandType,
    absorbance_reader.ReadAbsorbanceCommandType,
    flex_stacker.RetrieveCommandType,
    flex_stacker.StoreCommandType,
    flex_stacker.SetStoredLabwareCommandType,
    flex_stacker.FillCommandType,
    flex_stacker.EmptyCommandType,
    calibration.CalibrateGripperCommandType,
    calibration.CalibratePipetteCommandType,
    calibration.CalibrateModuleCommandType,
    calibration.MoveToMaintenancePositionCommandType,
    unsafe.UnsafeBlowOutInPlaceCommandType,
    unsafe.UnsafeDropTipInPlaceCommandType,
    unsafe.UpdatePositionEstimatorsCommandType,
    unsafe.UnsafeEngageAxesCommandType,
    unsafe.UnsafeUngripLabwareCommandType,
    unsafe.UnsafePlaceLabwareCommandType,
    unsafe.UnsafeFlexStackerManualRetrieveCommandType,
    unsafe.UnsafeFlexStackerCloseLatchCommandType,
    unsafe.UnsafeFlexStackerOpenLatchCommandType,
    unsafe.UnsafeFlexStackerPrepareShuttleCommandType,
    robot.MoveAxesRelativeCommandType,
    robot.MoveAxesToCommandType,
    robot.MoveToCommandType,
    robot.OpenGripperJawCommandType,
    robot.CloseGripperJawCommandType,
]

CommandCreate = Annotated[
    Union[
        AirGapInPlaceCreate,
        AspirateCreate,
        AspirateWhileTrackingCreate,
        AspirateInPlaceCreate,
        CommentCreate,
        ConfigureForVolumeCreate,
        ConfigureNozzleLayoutCreate,
        CustomCreate,
        DispenseCreate,
        DispenseInPlaceCreate,
        DispenseWhileTrackingCreate,
        BlowOutCreate,
        BlowOutInPlaceCreate,
        DropTipCreate,
        DropTipInPlaceCreate,
        HomeCreate,
        RetractAxisCreate,
        LoadLabwareCreate,
        ReloadLabwareCreate,
        LoadLiquidCreate,
        LoadLiquidClassCreate,
        LoadModuleCreate,
        IdentifyModuleCreate,
        LoadPipetteCreate,
        LoadLidStackCreate,
        LoadLidCreate,
        MoveLabwareCreate,
        MoveRelativeCreate,
        MoveToCoordinatesCreate,
        MoveToWellCreate,
        MoveToAddressableAreaCreate,
        MoveToAddressableAreaForDropTipCreate,
        PrepareToAspirateCreate,
        WaitForResumeCreate,
        WaitForDurationCreate,
        PickUpTipCreate,
        SavePositionCreate,
        SetRailLightsCreate,
        TouchTipCreate,
        SetStatusBarCreate,
        VerifyTipPresenceCreate,
        GetTipPresenceCreate,
        GetNextTipCreate,
        LiquidProbeCreate,
        TryLiquidProbeCreate,
        SealPipetteToTipCreate,
        PressureDispenseCreate,
        UnsealPipetteFromTipCreate,
        heater_shaker.WaitForTemperatureCreate,
        heater_shaker.SetTargetTemperatureCreate,
        heater_shaker.DeactivateHeaterCreate,
        heater_shaker.SetAndWaitForShakeSpeedCreate,
        heater_shaker.DeactivateShakerCreate,
        heater_shaker.OpenLabwareLatchCreate,
        heater_shaker.CloseLabwareLatchCreate,
        magnetic_module.DisengageCreate,
        magnetic_module.EngageCreate,
        temperature_module.SetTargetTemperatureCreate,
        temperature_module.WaitForTemperatureCreate,
        temperature_module.DeactivateTemperatureCreate,
        thermocycler.SetTargetBlockTemperatureCreate,
        thermocycler.WaitForBlockTemperatureCreate,
        thermocycler.SetTargetLidTemperatureCreate,
        thermocycler.WaitForLidTemperatureCreate,
        thermocycler.DeactivateBlockCreate,
        thermocycler.DeactivateLidCreate,
        thermocycler.OpenLidCreate,
        thermocycler.CloseLidCreate,
        thermocycler.RunProfileCreate,
        thermocycler.RunExtendedProfileCreate,
        absorbance_reader.CloseLidCreate,
        absorbance_reader.OpenLidCreate,
        absorbance_reader.InitializeCreate,
        absorbance_reader.ReadAbsorbanceCreate,
        flex_stacker.RetrieveCreate,
        flex_stacker.StoreCreate,
        flex_stacker.SetStoredLabwareCreate,
        flex_stacker.FillCreate,
        flex_stacker.EmptyCreate,
        calibration.CalibrateGripperCreate,
        calibration.CalibratePipetteCreate,
        calibration.CalibrateModuleCreate,
        calibration.MoveToMaintenancePositionCreate,
        unsafe.UnsafeBlowOutInPlaceCreate,
        unsafe.UnsafeDropTipInPlaceCreate,
        unsafe.UpdatePositionEstimatorsCreate,
        unsafe.UnsafeEngageAxesCreate,
        unsafe.UnsafeUngripLabwareCreate,
        unsafe.UnsafePlaceLabwareCreate,
        unsafe.UnsafeFlexStackerManualRetrieveCreate,
        unsafe.UnsafeFlexStackerCloseLatchCreate,
        unsafe.UnsafeFlexStackerOpenLatchCreate,
        unsafe.UnsafeFlexStackerPrepareShuttleCreate,
        robot.MoveAxesRelativeCreate,
        robot.MoveAxesToCreate,
        robot.MoveToCreate,
        robot.OpenGripperJawCreate,
        robot.CloseGripperJawCreate,
    ],
    Field(discriminator="commandType"),
]

# Each time a TypeAdapter is instantiated, it will construct a new validator and
# serializer. To improve performance, TypeAdapters are instantiated once.
# See https://docs.pydantic.dev/latest/concepts/performance/#typeadapter-instantiated-once
CommandCreateAdapter: TypeAdapter[CommandCreate] = TypeAdapter(CommandCreate)

CommandAdapter: TypeAdapter[Command] = TypeAdapter(Command)

CommandResult = Union[
    AirGapInPlaceResult,
    AspirateResult,
    AspirateWhileTrackingResult,
    AspirateInPlaceResult,
    CommentResult,
    ConfigureForVolumeResult,
    ConfigureNozzleLayoutResult,
    CustomResult,
    DispenseResult,
    DispenseInPlaceResult,
    DispenseWhileTrackingResult,
    BlowOutResult,
    BlowOutInPlaceResult,
    DropTipResult,
    DropTipInPlaceResult,
    HomeResult,
    RetractAxisResult,
    LoadLabwareResult,
    ReloadLabwareResult,
    LoadLiquidResult,
    LoadLiquidClassResult,
    LoadModuleResult,
    IdentifyModuleResult,
    LoadPipetteResult,
    LoadLidStackResult,
    LoadLidResult,
    MoveLabwareResult,
    MoveRelativeResult,
    MoveToCoordinatesResult,
    MoveToWellResult,
    MoveToAddressableAreaResult,
    MoveToAddressableAreaForDropTipResult,
    PrepareToAspirateResult,
    WaitForResumeResult,
    WaitForDurationResult,
    PickUpTipResult,
    SavePositionResult,
    SetRailLightsResult,
    TouchTipResult,
    SetStatusBarResult,
    VerifyTipPresenceResult,
    GetTipPresenceResult,
    GetNextTipResult,
    LiquidProbeResult,
    TryLiquidProbeResult,
    SealPipetteToTipResult,
    PressureDispenseResult,
    UnsealPipetteFromTipResult,
    heater_shaker.WaitForTemperatureResult,
    heater_shaker.SetTargetTemperatureResult,
    heater_shaker.DeactivateHeaterResult,
    heater_shaker.SetAndWaitForShakeSpeedResult,
    heater_shaker.DeactivateShakerResult,
    heater_shaker.OpenLabwareLatchResult,
    heater_shaker.CloseLabwareLatchResult,
    magnetic_module.DisengageResult,
    magnetic_module.EngageResult,
    temperature_module.SetTargetTemperatureResult,
    temperature_module.WaitForTemperatureResult,
    temperature_module.DeactivateTemperatureResult,
    thermocycler.SetTargetBlockTemperatureResult,
    thermocycler.WaitForBlockTemperatureResult,
    thermocycler.SetTargetLidTemperatureResult,
    thermocycler.WaitForLidTemperatureResult,
    thermocycler.DeactivateBlockResult,
    thermocycler.DeactivateLidResult,
    thermocycler.OpenLidResult,
    thermocycler.CloseLidResult,
    thermocycler.RunProfileResult,
    thermocycler.RunExtendedProfileResult,
    absorbance_reader.CloseLidResult,
    absorbance_reader.OpenLidResult,
    absorbance_reader.InitializeResult,
    absorbance_reader.ReadAbsorbanceResult,
    flex_stacker.RetrieveResult,
    flex_stacker.StoreResult,
    flex_stacker.SetStoredLabwareResult,
    flex_stacker.FillResult,
    flex_stacker.EmptyResult,
    calibration.CalibrateGripperResult,
    calibration.CalibratePipetteResult,
    calibration.CalibrateModuleResult,
    calibration.MoveToMaintenancePositionResult,
    unsafe.UnsafeBlowOutInPlaceResult,
    unsafe.UnsafeDropTipInPlaceResult,
    unsafe.UpdatePositionEstimatorsResult,
    unsafe.UnsafeEngageAxesResult,
    unsafe.UnsafeUngripLabwareResult,
    unsafe.UnsafePlaceLabwareResult,
    unsafe.UnsafeFlexStackerManualRetrieveResult,
    unsafe.UnsafeFlexStackerCloseLatchResult,
    unsafe.UnsafeFlexStackerOpenLatchResult,
    unsafe.UnsafeFlexStackerPrepareShuttleResult,
    robot.MoveAxesRelativeResult,
    robot.MoveAxesToResult,
    robot.MoveToResult,
    robot.OpenGripperJawResult,
    robot.CloseGripperJawResult,
]


# All `DefinedErrorData`s that implementations will actually return in practice.
CommandDefinedErrorData = Union[
    DefinedErrorData[TipPhysicallyMissingError],
    DefinedErrorData[TipPhysicallyAttachedError],
    DefinedErrorData[OverpressureError],
    DefinedErrorData[LiquidNotFoundError],
    DefinedErrorData[GripperMovementError],
    DefinedErrorData[StallOrCollisionError],
    DefinedErrorData[FlexStackerStallOrCollisionError],
    DefinedErrorData[FlexStackerShuttleError],
    DefinedErrorData[FlexStackerHopperError],
    DefinedErrorData[FlexStackerLabwareRetrieveError],
    DefinedErrorData[FlexStackerShuttleOccupiedError],
    DefinedErrorData[FlexStackerLabwareStoreError],
]


def _map_create_types_by_params_type(
    create_types: Collection[Type[CommandCreate]],
) -> dict[Type[CommandParams], Type[CommandCreate]]:
    def get_params_type(create_type: Type[CommandCreate]) -> Type[CommandParams]:
        return get_type_hints(create_type)["params"]  # type: ignore[no-any-return]

    result = {get_params_type(create_type): create_type for create_type in create_types}

    # This isn't an inherent requirement of opentrons.protocol_engine,
    # but this mapping is only useful to higher-level code if this holds true.
    assert len(result) == len(
        create_types
    ), "Param models should map to create models 1:1."

    return result


CREATE_TYPES_BY_PARAMS_TYPE = _map_create_types_by_params_type(
    get_union_elements(CommandCreate)
)
"""A "reverse" mapping from each CommandParams type to its parent CommandCreate type."""
