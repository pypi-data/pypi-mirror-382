from __future__ import annotations
import os
import pybind11_stubgen.typing_ext
import typing
import weompy
__all__: list[str] = ['ADAPTIVE', 'ADC_1', 'ALL', 'ANALOG', 'AUTO', 'AUTO_GAIN_CONTROL', 'Averaging', 'BRIGHT', 'B_115200', 'B_3000000', 'B_921600', 'Baudrate', 'CINT_1_5_GAIN_4_30', 'CINT_2_5_GAIN_2_60', 'CINT_3_5_GAIN_1_86', 'CINT_4_5_GAIN_1_44', 'CINT_5_5_GAIN_1_18', 'CINT_6_5_GAIN_1_00', 'CLEAN_DP', 'CLOSED', 'CMOS', 'CMOS_GIGE', 'CVBS', 'CommonTrigger', 'Core', 'CoreManager', 'DARK', 'DELTA_T_0_0625', 'DELTA_T_0_1250', 'DELTA_T_0_1875', 'DELTA_T_0_2500', 'DELTA_T_0_3125', 'DELTA_T_0_3750', 'DELTA_T_0_4375', 'DELTA_T_0_5000', 'DELTA_T_0_5625', 'DELTA_T_0_6250', 'DELTA_T_0_6875', 'DELTA_T_0_7500', 'DELTA_T_0_8125', 'DELTA_T_0_8750', 'DELTA_T_0_9375', 'DISABLED', 'DeadPixel', 'DeadPixels', 'DeltaTemperatureShutter', 'DetectorSensitivity', 'FPS_30', 'FPS_60', 'FPS_8_57', 'FRAMES_2', 'FRAMES_4', 'FRAME_CAPTURE_START', 'FirmwareType', 'Focus', 'Framerate', 'GIGE', 'HDMI', 'HIGH_GAIN', 'IFD', 'INVERTED', 'Image', 'ImageData', 'ImageDataType', 'ImageEqualizationType', 'ImageGenerator', 'InternalShutterState', 'LOW_GAIN', 'Lens', 'MANUAL_FOCUS', 'MANUAL_GAIN_CONTROL', 'MANUAL_H25', 'MANUAL_H34', 'MFD', 'MOTORFOCUS_CALIBRATION', 'MOTORIC_E25', 'MOTORIC_E34', 'MOTORIC_WITH_BAYONET_B25', 'MOTORIC_WITH_BAYONET_B34', 'MotorFocusMode', 'NFD', 'NON_RADIOMETRIC', 'NOT_DEFINED', 'NUC_OFFSET_UPDATE', 'OFF', 'ONVIF', 'OPEN', 'PERFORMANCE_NETD_50MK', 'PERIODIC', 'POST_COLORING', 'POST_COLORING_RGB', 'POST_IGC', 'PRE_IGC', 'Palette', 'PixelCoordinates', 'Plugin', 'PresetId', 'R1', 'R2', 'R3', 'RADIOMETRIC', 'REMOTE_FOCUS', 'RESET_TO_FACTORY_DEFAULT', 'RESET_TO_LOADER', 'Range', 'ResetTrigger', 'ReticleMode', 'SENSOR', 'SET_SELECTED_PRESET', 'SOFTWARE_RESET', 'STAY_IN_LOADER', 'SUPERIOR_NETD_30MK', 'SUPER_GAIN', 'Sensor', 'SensorCint', 'ShutterUpdateMode', 'TEST_PATTERN_DYNAMIC', 'USB', 'USER_1', 'USER_2', 'VideoFormat', 'WTC640', 'WTC_14', 'WTC_25', 'WTC_35', 'WTC_50', 'WTC_7', 'WTC_7_5', 'WZB', 'gigeDevice']
class Averaging:
    """
    Members:
    
      OFF
    
      FRAMES_2
    
      FRAMES_4
    """
    FRAMES_2: typing.ClassVar[Averaging]  # value = <Averaging.FRAMES_2: 1>
    FRAMES_4: typing.ClassVar[Averaging]  # value = <Averaging.FRAMES_4: 2>
    OFF: typing.ClassVar[Averaging]  # value = <Averaging.OFF: 0>
    __members__: typing.ClassVar[dict[str, weompy.Averaging]]  # value = {'OFF': <Averaging.OFF: 0>, 'FRAMES_2': <Averaging.FRAMES_2: 1>, 'FRAMES_4': <Averaging.FRAMES_4: 2>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class Baudrate:
    """
    Members:
    
      B_115200
    
      B_921600
    
      B_3000000
    """
    B_115200: typing.ClassVar[Baudrate]  # value = <Baudrate.B_115200: 4>
    B_3000000: typing.ClassVar[Baudrate]  # value = <Baudrate.B_3000000: 9>
    B_921600: typing.ClassVar[Baudrate]  # value = <Baudrate.B_921600: 7>
    __members__: typing.ClassVar[dict[str, weompy.Baudrate]]  # value = {'B_115200': <Baudrate.B_115200: 4>, 'B_921600': <Baudrate.B_921600: 7>, 'B_3000000': <Baudrate.B_3000000: 9>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class CommonTrigger:
    """
    Members:
    
      NUC_OFFSET_UPDATE
    
      CLEAN_DP
    
      SET_SELECTED_PRESET
    
      MOTORFOCUS_CALIBRATION
    
      FRAME_CAPTURE_START
    """
    CLEAN_DP: typing.ClassVar[CommonTrigger]  # value = <CommonTrigger.CLEAN_DP: 1>
    FRAME_CAPTURE_START: typing.ClassVar[CommonTrigger]  # value = <CommonTrigger.FRAME_CAPTURE_START: 4>
    MOTORFOCUS_CALIBRATION: typing.ClassVar[CommonTrigger]  # value = <CommonTrigger.MOTORFOCUS_CALIBRATION: 3>
    NUC_OFFSET_UPDATE: typing.ClassVar[CommonTrigger]  # value = <CommonTrigger.NUC_OFFSET_UPDATE: 0>
    SET_SELECTED_PRESET: typing.ClassVar[CommonTrigger]  # value = <CommonTrigger.SET_SELECTED_PRESET: 2>
    __members__: typing.ClassVar[dict[str, weompy.CommonTrigger]]  # value = {'NUC_OFFSET_UPDATE': <CommonTrigger.NUC_OFFSET_UPDATE: 0>, 'CLEAN_DP': <CommonTrigger.CLEAN_DP: 1>, 'SET_SELECTED_PRESET': <CommonTrigger.SET_SELECTED_PRESET: 2>, 'MOTORFOCUS_CALIBRATION': <CommonTrigger.MOTORFOCUS_CALIBRATION: 3>, 'FRAME_CAPTURE_START': <CommonTrigger.FRAME_CAPTURE_START: 4>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class Core:
    """
    Members:
    
      RADIOMETRIC
    
      NON_RADIOMETRIC
    """
    NON_RADIOMETRIC: typing.ClassVar[Core]  # value = <Core.NON_RADIOMETRIC: 1>
    RADIOMETRIC: typing.ClassVar[Core]  # value = <Core.RADIOMETRIC: 0>
    __members__: typing.ClassVar[dict[str, weompy.Core]]  # value = {'RADIOMETRIC': <Core.RADIOMETRIC: 0>, 'NON_RADIOMETRIC': <Core.NON_RADIOMETRIC: 1>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class CoreManager:
    def __init__(self) -> None:
        ...
    @typing.overload
    def activateCommonTrigger(self, trigger: weompy.CommonTrigger) -> None:
        """
        Activate a predefined common trigger.
        
        Parameters
        ----------
        trigger
        """
    @typing.overload
    def activateCommonTrigger(self, trigger: str) -> None:
        """
        Activate a predefined common trigger.
        
        Parameters
        ----------
        trigger
        """
    @typing.overload
    def activateResetTriggerAndReconnect(self, trigger: weompy.ResetTrigger) -> None:
        """
        Reset and reconnect after activating a trigger.
        
        Parameters
        ----------
        trigger
        """
    @typing.overload
    def activateResetTriggerAndReconnect(self, trigger: str) -> None:
        """
        Reset and reconnect after activating a trigger.
        
        Parameters
        ----------
        trigger
        """
    def captureImage(self) -> weompy.Image:
        """
        Capture a single image frame.
        
        Parameters
        ----------
        None
        """
    def captureImages(self, count: int) -> list[weompy.Image]:
        """
        Capture multiple images in sequence.
        
        Parameters
        ----------
        count
        """
    @typing.overload
    def colorizeImageDataToArgb(self, palette: weompy.Palette, imageData: weompy.ImageData, alpha: int) -> bytes:
        """
        Colorize image data to ARGB format with alpha transparency.
        
        Parameters
        ----------
        palette
        imageData
        alpha
        """
    @typing.overload
    def colorizeImageDataToArgb(self, palette: weompy.Palette, imageData: weompy.ImageData) -> bytes:
        """
        Colorize image data to ARGB format.
        
        Parameters
        ----------
        palette
        imageData
        """
    @typing.overload
    def colorizeImageDataToBgra(self, palette: weompy.Palette, imageData: weompy.ImageData, alpha: int) -> bytes:
        """
        Colorize image data to BGRA format with alpha transparency.
        
        Parameters
        ----------
        palette
        imageData
        alpha
        """
    @typing.overload
    def colorizeImageDataToBgra(self, palette: weompy.Palette, imageData: weompy.ImageData) -> bytes:
        """
        Colorize image data to BGRA format.
        
        Parameters
        ----------
        palette
        imageData
        """
    def connectGigeWithDevice(self, gigeDevice: weompy.gigeDevice) -> None:
        """
        Connect to a GigE Vision device by object.
        
        Parameters
        ----------
        gigeDevice
        """
    def connectGigeWithID(self, connectionID: str) -> None:
        """
        Connect to a GigE Vision device by ID.
        
        Parameters
        ----------
        connectionID
        """
    @typing.overload
    def connectUart(self, port: str) -> None:
        """
        Connect to a UART device using a port.
        
        Parameters
        ----------
        port
        """
    @typing.overload
    def connectUart(self, port: str, baudrate: weompy.Baudrate) -> None:
        """
        Connect to a UART device using a port and baudrate.
        
        Parameters
        ----------
        port
        baudrate
        """
    @typing.overload
    def connectUart(self, port: str, baudrate: str) -> None:
        """
        Connect to a UART device using a port and baudrate.
        
        Parameters
        ----------
        port
        baudrate
        """
    def connectUartAuto(self) -> None:
        """
        Automatically connect to the first available UART port.
        
        Parameters
        ----------
        None
        """
    def connectWzb(self, address: str, communicationPort: int, videoPort: int) -> None:
        """
        Connect to a Zoomblock camera using the address and ports.
        
        Parameters
        ----------
        address
        communicationPort
        videoPort
        """
    def disconnect(self) -> None:
        """
        Disconnect from the current device.
        
        Parameters
        ----------
        None
        """
    def findGigeDevices(self) -> list[weompy.gigeDevice]:
        """
        Find all GigE Vision devices on the network.
        
        Parameters
        ----------
        None
        """
    def getImageDataFromStream(self) -> weompy.ImageData:
        """
        Get image data from the video stream.
        
        Parameters
        ----------
        None
        """
    def getPortName(self) -> str:
        """
        Returns the portname of the currently connected UART port or an empty string.
        
        Parameters
        ----------
        None
        """
    def getPropertyDescription(self, property: str) -> str:
        """
        Get a description of the specified property.
        
        Parameters
        ----------
        property
        """
    def getPropertyIds(self) -> list[str]:
        """
        Retrieve a list of available property IDs.
        
        Parameters
        ----------
        None
        """
    def getPropertyValue(self, property: str) -> typing.Any:
        """
        Get the value of a given property.
        
        Parameters
        ----------
        property
        """
    def hasProperty(self, property: str) -> bool:
        """
        Check if a given property exists.
        
        Parameters
        ----------
        property
        """
    def isAnyTriggerActive(self) -> bool:
        """
        Returns if camera is currently performing a trigger.
        
        Parameters
        ----------
        None
        """
    def isCameraInLoader(self) -> bool:
        """
        Returns whether the camera is in loader.
        
        Parameters
        ----------
        None
        """
    def isCameraInMain(self) -> bool:
        """
        Returns whether the camera is in main.
        
        Parameters
        ----------
        None
        """
    def isCameraNotReady(self) -> bool:
        """
        Returns if camera is not ready to perform an operation.
        
        Parameters
        ----------
        None
        """
    def isNucActive(self) -> bool:
        """
        Returns if NUC is currently being performed.
        
        Parameters
        ----------
        None
        """
    def isPropertyReadable(self, property: str) -> bool:
        """
        Check if the property is readable.
        
        Parameters
        ----------
        property
        """
    def isPropertyWritable(self, property: str) -> bool:
        """
        Check if the property is writable.
        
        Parameters
        ----------
        property
        """
    def isValidVideoFormat(self, videoformat: weompy.VideoFormat, firmwareType: weompy.Plugin) -> bool:
        """
        Check if the video format is valid for a given firmware type.
        
        Parameters
        ----------
        videoformat
        firmwareType
        """
    def resetCore(self) -> None:
        """
        Perform a soft reset of the core system.
        
        Parameters
        ----------
        None
        """
    def resetToFactoryDefault(self) -> None:
        """
        Reset the device to factory settings.
        
        Parameters
        ----------
        None
        """
    def runMotorfocusCalibration(self) -> None:
        """
        Run the motor focus calibration procedure.
        
        Parameters
        ----------
        None
        """
    def runNucOffsetUpdate(self) -> None:
        """
        Run a NUC offset calibration.
        
        Parameters
        ----------
        None
        """
    def setPropertyValue(self, property: str, value: typing.Any) -> None:
        """
        Set the value of a given property.
        
        Parameters
        ----------
        property
        value
        """
    def startStream(self, videoFormat: weompy.VideoFormat) -> None:
        """
        Start video streaming with the specified format.
        
        Parameters
        ----------
        videoFormat
        """
    def stopStream(self) -> None:
        """
        Stop the video stream.
        
        Parameters
        ----------
        None
        """
    def updateFirmware(self, firmwarePath: str) -> None:
        """
        Update the device firmware using a given file path.
        
        Parameters
        ----------
        firmwarePath
        """
class DeadPixel:
    @typing.overload
    def __init__(self, x: int, y: int) -> None:
        ...
    @typing.overload
    def __init__(self, coordinates: weompy.PixelCoordinates) -> None:
        ...
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def addReplacement(self, replacementCoordinates: weompy.PixelCoordinates) -> bool:
        ...
    def clearReplacements(self) -> None:
        ...
    def getCoordinates(self) -> weompy.PixelCoordinates:
        ...
    def getReplacements(self) -> list[weompy.PixelCoordinates]:
        ...
    def removeReplacement(self, replacementCoordinates: weompy.PixelCoordinates) -> bool:
        ...
class DeadPixels:
    def __init__(self) -> None:
        ...
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def eraseDeadPixel(self, deadPixelCoordinates: weompy.PixelCoordinates) -> bool:
        ...
    def getDeadPixelsList(self) -> list[weompy.DeadPixel]:
        ...
    def insertDeadPixel(self, deadPixel: weompy.DeadPixel) -> None:
        ...
    def recomputeReplacements(self) -> None:
        ...
class DeltaTemperatureShutter:
    """
    Members:
    
      DELTA_T_0_0625
    
      DELTA_T_0_1250
    
      DELTA_T_0_1875
    
      DELTA_T_0_2500
    
      DELTA_T_0_3125
    
      DELTA_T_0_3750
    
      DELTA_T_0_4375
    
      DELTA_T_0_5000
    
      DELTA_T_0_5625
    
      DELTA_T_0_6250
    
      DELTA_T_0_6875
    
      DELTA_T_0_7500
    
      DELTA_T_0_8125
    
      DELTA_T_0_8750
    
      DELTA_T_0_9375
    """
    DELTA_T_0_0625: typing.ClassVar[DeltaTemperatureShutter]  # value = <DeltaTemperatureShutter.DELTA_T_0_0625: 0>
    DELTA_T_0_1250: typing.ClassVar[DeltaTemperatureShutter]  # value = <DeltaTemperatureShutter.DELTA_T_0_1250: 1>
    DELTA_T_0_1875: typing.ClassVar[DeltaTemperatureShutter]  # value = <DeltaTemperatureShutter.DELTA_T_0_1875: 2>
    DELTA_T_0_2500: typing.ClassVar[DeltaTemperatureShutter]  # value = <DeltaTemperatureShutter.DELTA_T_0_2500: 3>
    DELTA_T_0_3125: typing.ClassVar[DeltaTemperatureShutter]  # value = <DeltaTemperatureShutter.DELTA_T_0_3125: 4>
    DELTA_T_0_3750: typing.ClassVar[DeltaTemperatureShutter]  # value = <DeltaTemperatureShutter.DELTA_T_0_3750: 5>
    DELTA_T_0_4375: typing.ClassVar[DeltaTemperatureShutter]  # value = <DeltaTemperatureShutter.DELTA_T_0_4375: 6>
    DELTA_T_0_5000: typing.ClassVar[DeltaTemperatureShutter]  # value = <DeltaTemperatureShutter.DELTA_T_0_5000: 7>
    DELTA_T_0_5625: typing.ClassVar[DeltaTemperatureShutter]  # value = <DeltaTemperatureShutter.DELTA_T_0_5625: 8>
    DELTA_T_0_6250: typing.ClassVar[DeltaTemperatureShutter]  # value = <DeltaTemperatureShutter.DELTA_T_0_6250: 9>
    DELTA_T_0_6875: typing.ClassVar[DeltaTemperatureShutter]  # value = <DeltaTemperatureShutter.DELTA_T_0_6875: 10>
    DELTA_T_0_7500: typing.ClassVar[DeltaTemperatureShutter]  # value = <DeltaTemperatureShutter.DELTA_T_0_7500: 11>
    DELTA_T_0_8125: typing.ClassVar[DeltaTemperatureShutter]  # value = <DeltaTemperatureShutter.DELTA_T_0_8125: 12>
    DELTA_T_0_8750: typing.ClassVar[DeltaTemperatureShutter]  # value = <DeltaTemperatureShutter.DELTA_T_0_8750: 13>
    DELTA_T_0_9375: typing.ClassVar[DeltaTemperatureShutter]  # value = <DeltaTemperatureShutter.DELTA_T_0_9375: 14>
    __members__: typing.ClassVar[dict[str, weompy.DeltaTemperatureShutter]]  # value = {'DELTA_T_0_0625': <DeltaTemperatureShutter.DELTA_T_0_0625: 0>, 'DELTA_T_0_1250': <DeltaTemperatureShutter.DELTA_T_0_1250: 1>, 'DELTA_T_0_1875': <DeltaTemperatureShutter.DELTA_T_0_1875: 2>, 'DELTA_T_0_2500': <DeltaTemperatureShutter.DELTA_T_0_2500: 3>, 'DELTA_T_0_3125': <DeltaTemperatureShutter.DELTA_T_0_3125: 4>, 'DELTA_T_0_3750': <DeltaTemperatureShutter.DELTA_T_0_3750: 5>, 'DELTA_T_0_4375': <DeltaTemperatureShutter.DELTA_T_0_4375: 6>, 'DELTA_T_0_5000': <DeltaTemperatureShutter.DELTA_T_0_5000: 7>, 'DELTA_T_0_5625': <DeltaTemperatureShutter.DELTA_T_0_5625: 8>, 'DELTA_T_0_6250': <DeltaTemperatureShutter.DELTA_T_0_6250: 9>, 'DELTA_T_0_6875': <DeltaTemperatureShutter.DELTA_T_0_6875: 10>, 'DELTA_T_0_7500': <DeltaTemperatureShutter.DELTA_T_0_7500: 11>, 'DELTA_T_0_8125': <DeltaTemperatureShutter.DELTA_T_0_8125: 12>, 'DELTA_T_0_8750': <DeltaTemperatureShutter.DELTA_T_0_8750: 13>, 'DELTA_T_0_9375': <DeltaTemperatureShutter.DELTA_T_0_9375: 14>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class DetectorSensitivity:
    """
    Members:
    
      PERFORMANCE_NETD_50MK
    
      SUPERIOR_NETD_30MK
    """
    PERFORMANCE_NETD_50MK: typing.ClassVar[DetectorSensitivity]  # value = <DetectorSensitivity.PERFORMANCE_NETD_50MK: 0>
    SUPERIOR_NETD_30MK: typing.ClassVar[DetectorSensitivity]  # value = <DetectorSensitivity.SUPERIOR_NETD_30MK: 1>
    __members__: typing.ClassVar[dict[str, weompy.DetectorSensitivity]]  # value = {'PERFORMANCE_NETD_50MK': <DetectorSensitivity.PERFORMANCE_NETD_50MK: 0>, 'SUPERIOR_NETD_30MK': <DetectorSensitivity.SUPERIOR_NETD_30MK: 1>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class FirmwareType:
    """
    Members:
    
      CMOS_GIGE
    
      HDMI
    
      ANALOG
    
      USB
    
      ALL
    """
    ALL: typing.ClassVar[FirmwareType]  # value = <FirmwareType.ALL: 4>
    ANALOG: typing.ClassVar[FirmwareType]  # value = <FirmwareType.ANALOG: 2>
    CMOS_GIGE: typing.ClassVar[FirmwareType]  # value = <FirmwareType.CMOS_GIGE: 0>
    HDMI: typing.ClassVar[FirmwareType]  # value = <FirmwareType.HDMI: 1>
    USB: typing.ClassVar[FirmwareType]  # value = <FirmwareType.USB: 3>
    __members__: typing.ClassVar[dict[str, weompy.FirmwareType]]  # value = {'CMOS_GIGE': <FirmwareType.CMOS_GIGE: 0>, 'HDMI': <FirmwareType.HDMI: 1>, 'ANALOG': <FirmwareType.ANALOG: 2>, 'USB': <FirmwareType.USB: 3>, 'ALL': <FirmwareType.ALL: 4>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class Focus:
    """
    Members:
    
      MANUAL_H25
    
      MANUAL_H34
    
      MOTORIC_E25
    
      MOTORIC_E34
    
      MOTORIC_WITH_BAYONET_B25
    
      MOTORIC_WITH_BAYONET_B34
    """
    MANUAL_H25: typing.ClassVar[Focus]  # value = <Focus.MANUAL_H25: 0>
    MANUAL_H34: typing.ClassVar[Focus]  # value = <Focus.MANUAL_H34: 1>
    MOTORIC_E25: typing.ClassVar[Focus]  # value = <Focus.MOTORIC_E25: 2>
    MOTORIC_E34: typing.ClassVar[Focus]  # value = <Focus.MOTORIC_E34: 3>
    MOTORIC_WITH_BAYONET_B25: typing.ClassVar[Focus]  # value = <Focus.MOTORIC_WITH_BAYONET_B25: 4>
    MOTORIC_WITH_BAYONET_B34: typing.ClassVar[Focus]  # value = <Focus.MOTORIC_WITH_BAYONET_B34: 5>
    __members__: typing.ClassVar[dict[str, weompy.Focus]]  # value = {'MANUAL_H25': <Focus.MANUAL_H25: 0>, 'MANUAL_H34': <Focus.MANUAL_H34: 1>, 'MOTORIC_E25': <Focus.MOTORIC_E25: 2>, 'MOTORIC_E34': <Focus.MOTORIC_E34: 3>, 'MOTORIC_WITH_BAYONET_B25': <Focus.MOTORIC_WITH_BAYONET_B25: 4>, 'MOTORIC_WITH_BAYONET_B34': <Focus.MOTORIC_WITH_BAYONET_B34: 5>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class Framerate:
    """
    Members:
    
      FPS_8_57
    
      FPS_30
    
      FPS_60
    """
    FPS_30: typing.ClassVar[Framerate]  # value = <Framerate.FPS_30: 1>
    FPS_60: typing.ClassVar[Framerate]  # value = <Framerate.FPS_60: 2>
    FPS_8_57: typing.ClassVar[Framerate]  # value = <Framerate.FPS_8_57: 0>
    __members__: typing.ClassVar[dict[str, weompy.Framerate]]  # value = {'FPS_8_57': <Framerate.FPS_8_57: 0>, 'FPS_30': <Framerate.FPS_30: 1>, 'FPS_60': <Framerate.FPS_60: 2>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class Image:
    @staticmethod
    def getPixelValue(*args, **kwargs) -> int:
        ...
    @staticmethod
    def load(path: os.PathLike) -> weompy.Image:
        ...
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def getData(self) -> list[int]:
        ...
    def getFpaTemperature(self) -> float:
        ...
    def getFpgaTemperature(self) -> float:
        ...
    def getHeight(self) -> int:
        ...
    def getSensorFrameRate(self) -> float:
        ...
    def getSensorHorizontalFlip(self) -> bool:
        ...
    def getSensorName(self) -> str:
        ...
    def getSensorSerial(self) -> str:
        ...
    def getSensorSerialNumber(self) -> typing.Annotated[list[int], pybind11_stubgen.typing_ext.FixedSize(3)]:
        ...
    def getSensorVerticalFlip(self) -> bool:
        ...
    def getShutterTemperature(self) -> float:
        ...
    def getTimestamp(self) -> int:
        ...
    def getWidth(self) -> int:
        ...
    def save(self, path: os.PathLike) -> None:
        ...
class ImageData:
    @staticmethod
    def getPixelValue(*args, **kwargs) -> int:
        ...
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def getData(self) -> list[int]:
        ...
    def getDataType(self) -> weompy.ImageDataType:
        ...
    def getHeight(self) -> int:
        ...
    def getWidth(self) -> int:
        ...
class ImageDataType:
    """
    Members:
    
      PRE_IGC
    
      POST_IGC
    
      POST_COLORING
    
      POST_COLORING_RGB
    """
    POST_COLORING: typing.ClassVar[ImageDataType]  # value = <ImageDataType.POST_COLORING: 2>
    POST_COLORING_RGB: typing.ClassVar[ImageDataType]  # value = <ImageDataType.POST_COLORING_RGB: 3>
    POST_IGC: typing.ClassVar[ImageDataType]  # value = <ImageDataType.POST_IGC: 1>
    PRE_IGC: typing.ClassVar[ImageDataType]  # value = <ImageDataType.PRE_IGC: 0>
    __members__: typing.ClassVar[dict[str, weompy.ImageDataType]]  # value = {'PRE_IGC': <ImageDataType.PRE_IGC: 0>, 'POST_IGC': <ImageDataType.POST_IGC: 1>, 'POST_COLORING': <ImageDataType.POST_COLORING: 2>, 'POST_COLORING_RGB': <ImageDataType.POST_COLORING_RGB: 3>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class ImageEqualizationType:
    """
    Members:
    
      AUTO_GAIN_CONTROL
    
      MANUAL_GAIN_CONTROL
    """
    AUTO_GAIN_CONTROL: typing.ClassVar[ImageEqualizationType]  # value = <ImageEqualizationType.AUTO_GAIN_CONTROL: 0>
    MANUAL_GAIN_CONTROL: typing.ClassVar[ImageEqualizationType]  # value = <ImageEqualizationType.MANUAL_GAIN_CONTROL: 1>
    __members__: typing.ClassVar[dict[str, weompy.ImageEqualizationType]]  # value = {'AUTO_GAIN_CONTROL': <ImageEqualizationType.AUTO_GAIN_CONTROL: 0>, 'MANUAL_GAIN_CONTROL': <ImageEqualizationType.MANUAL_GAIN_CONTROL: 1>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class ImageGenerator:
    """
    Members:
    
      SENSOR
    
      ADC_1
    
      TEST_PATTERN_DYNAMIC
    """
    ADC_1: typing.ClassVar[ImageGenerator]  # value = <ImageGenerator.ADC_1: 1>
    SENSOR: typing.ClassVar[ImageGenerator]  # value = <ImageGenerator.SENSOR: 0>
    TEST_PATTERN_DYNAMIC: typing.ClassVar[ImageGenerator]  # value = <ImageGenerator.TEST_PATTERN_DYNAMIC: 3>
    __members__: typing.ClassVar[dict[str, weompy.ImageGenerator]]  # value = {'SENSOR': <ImageGenerator.SENSOR: 0>, 'ADC_1': <ImageGenerator.ADC_1: 1>, 'TEST_PATTERN_DYNAMIC': <ImageGenerator.TEST_PATTERN_DYNAMIC: 3>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class InternalShutterState:
    """
    Members:
    
      OPEN
    
      CLOSED
    """
    CLOSED: typing.ClassVar[InternalShutterState]  # value = <InternalShutterState.CLOSED: 1>
    OPEN: typing.ClassVar[InternalShutterState]  # value = <InternalShutterState.OPEN: 0>
    __members__: typing.ClassVar[dict[str, weompy.InternalShutterState]]  # value = {'OPEN': <InternalShutterState.OPEN: 0>, 'CLOSED': <InternalShutterState.CLOSED: 1>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class Lens:
    """
    Members:
    
      NOT_DEFINED
    
      WTC_35
    
      WTC_25
    
      WTC_14
    
      WTC_7_5
    
      WTC_50
    
      WTC_7
    
      USER_1
    
      USER_2
    """
    NOT_DEFINED: typing.ClassVar[Lens]  # value = <Lens.NOT_DEFINED: 0>
    USER_1: typing.ClassVar[Lens]  # value = <Lens.USER_1: 7>
    USER_2: typing.ClassVar[Lens]  # value = <Lens.USER_2: 8>
    WTC_14: typing.ClassVar[Lens]  # value = <Lens.WTC_14: 3>
    WTC_25: typing.ClassVar[Lens]  # value = <Lens.WTC_25: 2>
    WTC_35: typing.ClassVar[Lens]  # value = <Lens.WTC_35: 1>
    WTC_50: typing.ClassVar[Lens]  # value = <Lens.WTC_50: 5>
    WTC_7: typing.ClassVar[Lens]  # value = <Lens.WTC_7: 6>
    WTC_7_5: typing.ClassVar[Lens]  # value = <Lens.WTC_7_5: 4>
    __members__: typing.ClassVar[dict[str, weompy.Lens]]  # value = {'NOT_DEFINED': <Lens.NOT_DEFINED: 0>, 'WTC_35': <Lens.WTC_35: 1>, 'WTC_25': <Lens.WTC_25: 2>, 'WTC_14': <Lens.WTC_14: 3>, 'WTC_7_5': <Lens.WTC_7_5: 4>, 'WTC_50': <Lens.WTC_50: 5>, 'WTC_7': <Lens.WTC_7: 6>, 'USER_1': <Lens.USER_1: 7>, 'USER_2': <Lens.USER_2: 8>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class MotorFocusMode:
    """
    Members:
    
      MANUAL_FOCUS
    
      REMOTE_FOCUS
    
      IFD
    
      NFD
    
      MFD
    """
    IFD: typing.ClassVar[MotorFocusMode]  # value = <MotorFocusMode.IFD: 2>
    MANUAL_FOCUS: typing.ClassVar[MotorFocusMode]  # value = <MotorFocusMode.MANUAL_FOCUS: 0>
    MFD: typing.ClassVar[MotorFocusMode]  # value = <MotorFocusMode.MFD: 4>
    NFD: typing.ClassVar[MotorFocusMode]  # value = <MotorFocusMode.NFD: 3>
    REMOTE_FOCUS: typing.ClassVar[MotorFocusMode]  # value = <MotorFocusMode.REMOTE_FOCUS: 1>
    __members__: typing.ClassVar[dict[str, weompy.MotorFocusMode]]  # value = {'MANUAL_FOCUS': <MotorFocusMode.MANUAL_FOCUS: 0>, 'REMOTE_FOCUS': <MotorFocusMode.REMOTE_FOCUS: 1>, 'IFD': <MotorFocusMode.IFD: 2>, 'NFD': <MotorFocusMode.NFD: 3>, 'MFD': <MotorFocusMode.MFD: 4>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class Palette:
    @staticmethod
    def load(path: str) -> weompy.Palette:
        ...
    def __init__(self, arg0: str, arg1: typing.Annotated[list[typing.Annotated[list[int], pybind11_stubgen.typing_ext.FixedSize(3)]], pybind11_stubgen.typing_ext.FixedSize(256)]) -> None:
        ...
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def getName(self) -> str:
        ...
    def getRgb(self) -> typing.Annotated[list[typing.Annotated[list[int], pybind11_stubgen.typing_ext.FixedSize(3)]], pybind11_stubgen.typing_ext.FixedSize(256)]:
        ...
    def getYCbCr(self) -> typing.Annotated[list[typing.Annotated[list[int], pybind11_stubgen.typing_ext.FixedSize(3)]], pybind11_stubgen.typing_ext.FixedSize(256)]:
        ...
    def save(self, path: str) -> None:
        ...
    def setName(self, name: str) -> None:
        ...
class PixelCoordinates:
    x: int
    y: int
    def __init__(self, x: int, y: int) -> None:
        ...
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
class Plugin:
    """
    Members:
    
      CMOS
    
      HDMI
    
      ANALOG
    
      USB
    
      GIGE
    
      CVBS
    
      WZB
    
      ONVIF
    """
    ANALOG: typing.ClassVar[Plugin]  # value = <Plugin.ANALOG: 2>
    CMOS: typing.ClassVar[Plugin]  # value = <Plugin.CMOS: 0>
    CVBS: typing.ClassVar[Plugin]  # value = <Plugin.CVBS: 5>
    GIGE: typing.ClassVar[Plugin]  # value = <Plugin.GIGE: 4>
    HDMI: typing.ClassVar[Plugin]  # value = <Plugin.HDMI: 1>
    ONVIF: typing.ClassVar[Plugin]  # value = <Plugin.ONVIF: 7>
    USB: typing.ClassVar[Plugin]  # value = <Plugin.USB: 3>
    WZB: typing.ClassVar[Plugin]  # value = <Plugin.WZB: 6>
    __members__: typing.ClassVar[dict[str, weompy.Plugin]]  # value = {'CMOS': <Plugin.CMOS: 0>, 'HDMI': <Plugin.HDMI: 1>, 'ANALOG': <Plugin.ANALOG: 2>, 'USB': <Plugin.USB: 3>, 'GIGE': <Plugin.GIGE: 4>, 'CVBS': <Plugin.CVBS: 5>, 'WZB': <Plugin.WZB: 6>, 'ONVIF': <Plugin.ONVIF: 7>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class PresetId:
    lens: weompy.Lens
    range: weompy.Range
    def __init__(self, arg0: weompy.Lens, arg1: weompy.Range) -> None:
        ...
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
class Range:
    """
    Members:
    
      NOT_DEFINED
    
      R1
    
      R2
    
      R3
    
      HIGH_GAIN
    
      LOW_GAIN
    
      SUPER_GAIN
    """
    HIGH_GAIN: typing.ClassVar[Range]  # value = <Range.HIGH_GAIN: 4>
    LOW_GAIN: typing.ClassVar[Range]  # value = <Range.LOW_GAIN: 5>
    NOT_DEFINED: typing.ClassVar[Range]  # value = <Range.NOT_DEFINED: 0>
    R1: typing.ClassVar[Range]  # value = <Range.R1: 1>
    R2: typing.ClassVar[Range]  # value = <Range.R2: 2>
    R3: typing.ClassVar[Range]  # value = <Range.R3: 3>
    SUPER_GAIN: typing.ClassVar[Range]  # value = <Range.SUPER_GAIN: 6>
    __members__: typing.ClassVar[dict[str, weompy.Range]]  # value = {'NOT_DEFINED': <Range.NOT_DEFINED: 0>, 'R1': <Range.R1: 1>, 'R2': <Range.R2: 2>, 'R3': <Range.R3: 3>, 'HIGH_GAIN': <Range.HIGH_GAIN: 4>, 'LOW_GAIN': <Range.LOW_GAIN: 5>, 'SUPER_GAIN': <Range.SUPER_GAIN: 6>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class ResetTrigger:
    """
    Members:
    
      STAY_IN_LOADER
    
      SOFTWARE_RESET
    
      RESET_TO_LOADER
    
      RESET_TO_FACTORY_DEFAULT
    """
    RESET_TO_FACTORY_DEFAULT: typing.ClassVar[ResetTrigger]  # value = <ResetTrigger.RESET_TO_FACTORY_DEFAULT: 4>
    RESET_TO_LOADER: typing.ClassVar[ResetTrigger]  # value = <ResetTrigger.RESET_TO_LOADER: 3>
    SOFTWARE_RESET: typing.ClassVar[ResetTrigger]  # value = <ResetTrigger.SOFTWARE_RESET: 2>
    STAY_IN_LOADER: typing.ClassVar[ResetTrigger]  # value = <ResetTrigger.STAY_IN_LOADER: 1>
    __members__: typing.ClassVar[dict[str, weompy.ResetTrigger]]  # value = {'STAY_IN_LOADER': <ResetTrigger.STAY_IN_LOADER: 1>, 'SOFTWARE_RESET': <ResetTrigger.SOFTWARE_RESET: 2>, 'RESET_TO_LOADER': <ResetTrigger.RESET_TO_LOADER: 3>, 'RESET_TO_FACTORY_DEFAULT': <ResetTrigger.RESET_TO_FACTORY_DEFAULT: 4>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class ReticleMode:
    """
    Members:
    
      DISABLED
    
      DARK
    
      BRIGHT
    
      AUTO
    
      INVERTED
    """
    AUTO: typing.ClassVar[ReticleMode]  # value = <ReticleMode.AUTO: 3>
    BRIGHT: typing.ClassVar[ReticleMode]  # value = <ReticleMode.BRIGHT: 2>
    DARK: typing.ClassVar[ReticleMode]  # value = <ReticleMode.DARK: 1>
    DISABLED: typing.ClassVar[ReticleMode]  # value = <ReticleMode.DISABLED: 0>
    INVERTED: typing.ClassVar[ReticleMode]  # value = <ReticleMode.INVERTED: 4>
    __members__: typing.ClassVar[dict[str, weompy.ReticleMode]]  # value = {'DISABLED': <ReticleMode.DISABLED: 0>, 'DARK': <ReticleMode.DARK: 1>, 'BRIGHT': <ReticleMode.BRIGHT: 2>, 'AUTO': <ReticleMode.AUTO: 3>, 'INVERTED': <ReticleMode.INVERTED: 4>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class Sensor:
    """
    Members:
    
      WTC640
    """
    WTC640: typing.ClassVar[Sensor]  # value = <Sensor.WTC640: 0>
    __members__: typing.ClassVar[dict[str, weompy.Sensor]]  # value = {'WTC640': <Sensor.WTC640: 0>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class SensorCint:
    """
    Members:
    
      CINT_6_5_GAIN_1_00
    
      CINT_5_5_GAIN_1_18
    
      CINT_4_5_GAIN_1_44
    
      CINT_3_5_GAIN_1_86
    
      CINT_2_5_GAIN_2_60
    
      CINT_1_5_GAIN_4_30
    """
    CINT_1_5_GAIN_4_30: typing.ClassVar[SensorCint]  # value = <SensorCint.CINT_1_5_GAIN_4_30: 5>
    CINT_2_5_GAIN_2_60: typing.ClassVar[SensorCint]  # value = <SensorCint.CINT_2_5_GAIN_2_60: 4>
    CINT_3_5_GAIN_1_86: typing.ClassVar[SensorCint]  # value = <SensorCint.CINT_3_5_GAIN_1_86: 3>
    CINT_4_5_GAIN_1_44: typing.ClassVar[SensorCint]  # value = <SensorCint.CINT_4_5_GAIN_1_44: 2>
    CINT_5_5_GAIN_1_18: typing.ClassVar[SensorCint]  # value = <SensorCint.CINT_5_5_GAIN_1_18: 1>
    CINT_6_5_GAIN_1_00: typing.ClassVar[SensorCint]  # value = <SensorCint.CINT_6_5_GAIN_1_00: 0>
    __members__: typing.ClassVar[dict[str, weompy.SensorCint]]  # value = {'CINT_6_5_GAIN_1_00': <SensorCint.CINT_6_5_GAIN_1_00: 0>, 'CINT_5_5_GAIN_1_18': <SensorCint.CINT_5_5_GAIN_1_18: 1>, 'CINT_4_5_GAIN_1_44': <SensorCint.CINT_4_5_GAIN_1_44: 2>, 'CINT_3_5_GAIN_1_86': <SensorCint.CINT_3_5_GAIN_1_86: 3>, 'CINT_2_5_GAIN_2_60': <SensorCint.CINT_2_5_GAIN_2_60: 4>, 'CINT_1_5_GAIN_4_30': <SensorCint.CINT_1_5_GAIN_4_30: 5>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class ShutterUpdateMode:
    """
    Members:
    
      PERIODIC
    
      ADAPTIVE
    """
    ADAPTIVE: typing.ClassVar[ShutterUpdateMode]  # value = <ShutterUpdateMode.ADAPTIVE: 1>
    PERIODIC: typing.ClassVar[ShutterUpdateMode]  # value = <ShutterUpdateMode.PERIODIC: 0>
    __members__: typing.ClassVar[dict[str, weompy.ShutterUpdateMode]]  # value = {'PERIODIC': <ShutterUpdateMode.PERIODIC: 0>, 'ADAPTIVE': <ShutterUpdateMode.ADAPTIVE: 1>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class VideoFormat:
    """
    Members:
    
      PRE_IGC
    
      POST_IGC
    
      POST_COLORING
    """
    POST_COLORING: typing.ClassVar[VideoFormat]  # value = <VideoFormat.POST_COLORING: 2>
    POST_IGC: typing.ClassVar[VideoFormat]  # value = <VideoFormat.POST_IGC: 1>
    PRE_IGC: typing.ClassVar[VideoFormat]  # value = <VideoFormat.PRE_IGC: 0>
    __members__: typing.ClassVar[dict[str, weompy.VideoFormat]]  # value = {'PRE_IGC': <VideoFormat.PRE_IGC: 0>, 'POST_IGC': <VideoFormat.POST_IGC: 1>, 'POST_COLORING': <VideoFormat.POST_COLORING: 2>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class gigeDevice:
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def getConnectionID(self) -> str:
        ...
    def getGateway(self) -> str:
        ...
    def getIp(self) -> str:
        ...
    def getMac(self) -> str:
        ...
    def getName(self) -> str:
        ...
    def getSerialNumber(self) -> str:
        ...
    def getSubnet(self) -> str:
        ...
    def getType(self) -> str:
        ...
ADAPTIVE: ShutterUpdateMode  # value = <ShutterUpdateMode.ADAPTIVE: 1>
ADC_1: ImageGenerator  # value = <ImageGenerator.ADC_1: 1>
ALL: FirmwareType  # value = <FirmwareType.ALL: 4>
ANALOG: FirmwareType  # value = <FirmwareType.ANALOG: 2>
AUTO: ReticleMode  # value = <ReticleMode.AUTO: 3>
AUTO_GAIN_CONTROL: ImageEqualizationType  # value = <ImageEqualizationType.AUTO_GAIN_CONTROL: 0>
BRIGHT: ReticleMode  # value = <ReticleMode.BRIGHT: 2>
B_115200: Baudrate  # value = <Baudrate.B_115200: 4>
B_3000000: Baudrate  # value = <Baudrate.B_3000000: 9>
B_921600: Baudrate  # value = <Baudrate.B_921600: 7>
CINT_1_5_GAIN_4_30: SensorCint  # value = <SensorCint.CINT_1_5_GAIN_4_30: 5>
CINT_2_5_GAIN_2_60: SensorCint  # value = <SensorCint.CINT_2_5_GAIN_2_60: 4>
CINT_3_5_GAIN_1_86: SensorCint  # value = <SensorCint.CINT_3_5_GAIN_1_86: 3>
CINT_4_5_GAIN_1_44: SensorCint  # value = <SensorCint.CINT_4_5_GAIN_1_44: 2>
CINT_5_5_GAIN_1_18: SensorCint  # value = <SensorCint.CINT_5_5_GAIN_1_18: 1>
CINT_6_5_GAIN_1_00: SensorCint  # value = <SensorCint.CINT_6_5_GAIN_1_00: 0>
CLEAN_DP: CommonTrigger  # value = <CommonTrigger.CLEAN_DP: 1>
CLOSED: InternalShutterState  # value = <InternalShutterState.CLOSED: 1>
CMOS: Plugin  # value = <Plugin.CMOS: 0>
CMOS_GIGE: FirmwareType  # value = <FirmwareType.CMOS_GIGE: 0>
CVBS: Plugin  # value = <Plugin.CVBS: 5>
DARK: ReticleMode  # value = <ReticleMode.DARK: 1>
DELTA_T_0_0625: DeltaTemperatureShutter  # value = <DeltaTemperatureShutter.DELTA_T_0_0625: 0>
DELTA_T_0_1250: DeltaTemperatureShutter  # value = <DeltaTemperatureShutter.DELTA_T_0_1250: 1>
DELTA_T_0_1875: DeltaTemperatureShutter  # value = <DeltaTemperatureShutter.DELTA_T_0_1875: 2>
DELTA_T_0_2500: DeltaTemperatureShutter  # value = <DeltaTemperatureShutter.DELTA_T_0_2500: 3>
DELTA_T_0_3125: DeltaTemperatureShutter  # value = <DeltaTemperatureShutter.DELTA_T_0_3125: 4>
DELTA_T_0_3750: DeltaTemperatureShutter  # value = <DeltaTemperatureShutter.DELTA_T_0_3750: 5>
DELTA_T_0_4375: DeltaTemperatureShutter  # value = <DeltaTemperatureShutter.DELTA_T_0_4375: 6>
DELTA_T_0_5000: DeltaTemperatureShutter  # value = <DeltaTemperatureShutter.DELTA_T_0_5000: 7>
DELTA_T_0_5625: DeltaTemperatureShutter  # value = <DeltaTemperatureShutter.DELTA_T_0_5625: 8>
DELTA_T_0_6250: DeltaTemperatureShutter  # value = <DeltaTemperatureShutter.DELTA_T_0_6250: 9>
DELTA_T_0_6875: DeltaTemperatureShutter  # value = <DeltaTemperatureShutter.DELTA_T_0_6875: 10>
DELTA_T_0_7500: DeltaTemperatureShutter  # value = <DeltaTemperatureShutter.DELTA_T_0_7500: 11>
DELTA_T_0_8125: DeltaTemperatureShutter  # value = <DeltaTemperatureShutter.DELTA_T_0_8125: 12>
DELTA_T_0_8750: DeltaTemperatureShutter  # value = <DeltaTemperatureShutter.DELTA_T_0_8750: 13>
DELTA_T_0_9375: DeltaTemperatureShutter  # value = <DeltaTemperatureShutter.DELTA_T_0_9375: 14>
DISABLED: ReticleMode  # value = <ReticleMode.DISABLED: 0>
FPS_30: Framerate  # value = <Framerate.FPS_30: 1>
FPS_60: Framerate  # value = <Framerate.FPS_60: 2>
FPS_8_57: Framerate  # value = <Framerate.FPS_8_57: 0>
FRAMES_2: Averaging  # value = <Averaging.FRAMES_2: 1>
FRAMES_4: Averaging  # value = <Averaging.FRAMES_4: 2>
FRAME_CAPTURE_START: CommonTrigger  # value = <CommonTrigger.FRAME_CAPTURE_START: 4>
GIGE: Plugin  # value = <Plugin.GIGE: 4>
HDMI: FirmwareType  # value = <FirmwareType.HDMI: 1>
HIGH_GAIN: Range  # value = <Range.HIGH_GAIN: 4>
IFD: MotorFocusMode  # value = <MotorFocusMode.IFD: 2>
INVERTED: ReticleMode  # value = <ReticleMode.INVERTED: 4>
LOW_GAIN: Range  # value = <Range.LOW_GAIN: 5>
MANUAL_FOCUS: MotorFocusMode  # value = <MotorFocusMode.MANUAL_FOCUS: 0>
MANUAL_GAIN_CONTROL: ImageEqualizationType  # value = <ImageEqualizationType.MANUAL_GAIN_CONTROL: 1>
MANUAL_H25: Focus  # value = <Focus.MANUAL_H25: 0>
MANUAL_H34: Focus  # value = <Focus.MANUAL_H34: 1>
MFD: MotorFocusMode  # value = <MotorFocusMode.MFD: 4>
MOTORFOCUS_CALIBRATION: CommonTrigger  # value = <CommonTrigger.MOTORFOCUS_CALIBRATION: 3>
MOTORIC_E25: Focus  # value = <Focus.MOTORIC_E25: 2>
MOTORIC_E34: Focus  # value = <Focus.MOTORIC_E34: 3>
MOTORIC_WITH_BAYONET_B25: Focus  # value = <Focus.MOTORIC_WITH_BAYONET_B25: 4>
MOTORIC_WITH_BAYONET_B34: Focus  # value = <Focus.MOTORIC_WITH_BAYONET_B34: 5>
NFD: MotorFocusMode  # value = <MotorFocusMode.NFD: 3>
NON_RADIOMETRIC: Core  # value = <Core.NON_RADIOMETRIC: 1>
NOT_DEFINED: Range  # value = <Range.NOT_DEFINED: 0>
NUC_OFFSET_UPDATE: CommonTrigger  # value = <CommonTrigger.NUC_OFFSET_UPDATE: 0>
OFF: Averaging  # value = <Averaging.OFF: 0>
ONVIF: Plugin  # value = <Plugin.ONVIF: 7>
OPEN: InternalShutterState  # value = <InternalShutterState.OPEN: 0>
PERFORMANCE_NETD_50MK: DetectorSensitivity  # value = <DetectorSensitivity.PERFORMANCE_NETD_50MK: 0>
PERIODIC: ShutterUpdateMode  # value = <ShutterUpdateMode.PERIODIC: 0>
POST_COLORING: VideoFormat  # value = <VideoFormat.POST_COLORING: 2>
POST_COLORING_RGB: ImageDataType  # value = <ImageDataType.POST_COLORING_RGB: 3>
POST_IGC: VideoFormat  # value = <VideoFormat.POST_IGC: 1>
PRE_IGC: VideoFormat  # value = <VideoFormat.PRE_IGC: 0>
R1: Range  # value = <Range.R1: 1>
R2: Range  # value = <Range.R2: 2>
R3: Range  # value = <Range.R3: 3>
RADIOMETRIC: Core  # value = <Core.RADIOMETRIC: 0>
REMOTE_FOCUS: MotorFocusMode  # value = <MotorFocusMode.REMOTE_FOCUS: 1>
RESET_TO_FACTORY_DEFAULT: ResetTrigger  # value = <ResetTrigger.RESET_TO_FACTORY_DEFAULT: 4>
RESET_TO_LOADER: ResetTrigger  # value = <ResetTrigger.RESET_TO_LOADER: 3>
SENSOR: ImageGenerator  # value = <ImageGenerator.SENSOR: 0>
SET_SELECTED_PRESET: CommonTrigger  # value = <CommonTrigger.SET_SELECTED_PRESET: 2>
SOFTWARE_RESET: ResetTrigger  # value = <ResetTrigger.SOFTWARE_RESET: 2>
STAY_IN_LOADER: ResetTrigger  # value = <ResetTrigger.STAY_IN_LOADER: 1>
SUPERIOR_NETD_30MK: DetectorSensitivity  # value = <DetectorSensitivity.SUPERIOR_NETD_30MK: 1>
SUPER_GAIN: Range  # value = <Range.SUPER_GAIN: 6>
TEST_PATTERN_DYNAMIC: ImageGenerator  # value = <ImageGenerator.TEST_PATTERN_DYNAMIC: 3>
USB: FirmwareType  # value = <FirmwareType.USB: 3>
USER_1: Lens  # value = <Lens.USER_1: 7>
USER_2: Lens  # value = <Lens.USER_2: 8>
WTC640: Sensor  # value = <Sensor.WTC640: 0>
WTC_14: Lens  # value = <Lens.WTC_14: 3>
WTC_25: Lens  # value = <Lens.WTC_25: 2>
WTC_35: Lens  # value = <Lens.WTC_35: 1>
WTC_50: Lens  # value = <Lens.WTC_50: 5>
WTC_7: Lens  # value = <Lens.WTC_7: 6>
WTC_7_5: Lens  # value = <Lens.WTC_7_5: 4>
WZB: Plugin  # value = <Plugin.WZB: 6>
__version__: str = '1.7.179'
