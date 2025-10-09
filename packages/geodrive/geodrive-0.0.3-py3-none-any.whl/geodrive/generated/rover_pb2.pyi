from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class VelocityCommand(_message.Message):
    __slots__ = ("linear", "angular")
    LINEAR_FIELD_NUMBER: _ClassVar[int]
    ANGULAR_FIELD_NUMBER: _ClassVar[int]
    linear: float
    angular: float
    def __init__(self, linear: _Optional[float] = ..., angular: _Optional[float] = ...) -> None: ...

class DifferentialCommand(_message.Message):
    __slots__ = ("left", "right")
    LEFT_FIELD_NUMBER: _ClassVar[int]
    RIGHT_FIELD_NUMBER: _ClassVar[int]
    left: float
    right: float
    def __init__(self, left: _Optional[float] = ..., right: _Optional[float] = ...) -> None: ...

class GotoCommand(_message.Message):
    __slots__ = ("target_x", "target_y", "target_yaw")
    TARGET_X_FIELD_NUMBER: _ClassVar[int]
    TARGET_Y_FIELD_NUMBER: _ClassVar[int]
    TARGET_YAW_FIELD_NUMBER: _ClassVar[int]
    target_x: float
    target_y: float
    target_yaw: float
    def __init__(self, target_x: _Optional[float] = ..., target_y: _Optional[float] = ..., target_yaw: _Optional[float] = ...) -> None: ...

class GotoAck(_message.Message):
    __slots__ = ("accepted", "estimated_time")
    ACCEPTED_FIELD_NUMBER: _ClassVar[int]
    ESTIMATED_TIME_FIELD_NUMBER: _ClassVar[int]
    accepted: bool
    estimated_time: float
    def __init__(self, accepted: bool = ..., estimated_time: _Optional[float] = ...) -> None: ...

class GotoProgress(_message.Message):
    __slots__ = ("progress", "distance_to_goal", "angle_to_goal", "current_x", "current_y", "current_yaw")
    PROGRESS_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_TO_GOAL_FIELD_NUMBER: _ClassVar[int]
    ANGLE_TO_GOAL_FIELD_NUMBER: _ClassVar[int]
    CURRENT_X_FIELD_NUMBER: _ClassVar[int]
    CURRENT_Y_FIELD_NUMBER: _ClassVar[int]
    CURRENT_YAW_FIELD_NUMBER: _ClassVar[int]
    progress: float
    distance_to_goal: float
    angle_to_goal: float
    current_x: float
    current_y: float
    current_yaw: float
    def __init__(self, progress: _Optional[float] = ..., distance_to_goal: _Optional[float] = ..., angle_to_goal: _Optional[float] = ..., current_x: _Optional[float] = ..., current_y: _Optional[float] = ..., current_yaw: _Optional[float] = ...) -> None: ...

class RCChannelsCommand(_message.Message):
    __slots__ = ("channel1", "channel2", "channel3", "channel4")
    CHANNEL1_FIELD_NUMBER: _ClassVar[int]
    CHANNEL2_FIELD_NUMBER: _ClassVar[int]
    CHANNEL3_FIELD_NUMBER: _ClassVar[int]
    CHANNEL4_FIELD_NUMBER: _ClassVar[int]
    channel1: int
    channel2: int
    channel3: int
    channel4: int
    def __init__(self, channel1: _Optional[int] = ..., channel2: _Optional[int] = ..., channel3: _Optional[int] = ..., channel4: _Optional[int] = ...) -> None: ...

class LedCommand(_message.Message):
    __slots__ = ("r", "g", "b")
    R_FIELD_NUMBER: _ClassVar[int]
    G_FIELD_NUMBER: _ClassVar[int]
    B_FIELD_NUMBER: _ClassVar[int]
    r: int
    g: int
    b: int
    def __init__(self, r: _Optional[int] = ..., g: _Optional[int] = ..., b: _Optional[int] = ...) -> None: ...

class LedCustomCommand(_message.Message):
    __slots__ = ("color1", "color2", "mode")
    COLOR1_FIELD_NUMBER: _ClassVar[int]
    COLOR2_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    color1: _containers.RepeatedScalarFieldContainer[int]
    color2: _containers.RepeatedScalarFieldContainer[int]
    mode: int
    def __init__(self, color1: _Optional[_Iterable[int]] = ..., color2: _Optional[_Iterable[int]] = ..., mode: _Optional[int] = ...) -> None: ...

class TelemetryData(_message.Message):
    __slots__ = ("position", "velocity", "attitude")
    POSITION_FIELD_NUMBER: _ClassVar[int]
    VELOCITY_FIELD_NUMBER: _ClassVar[int]
    ATTITUDE_FIELD_NUMBER: _ClassVar[int]
    position: _containers.RepeatedScalarFieldContainer[float]
    velocity: _containers.RepeatedScalarFieldContainer[float]
    attitude: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, position: _Optional[_Iterable[float]] = ..., velocity: _Optional[_Iterable[float]] = ..., attitude: _Optional[_Iterable[float]] = ...) -> None: ...

class RoverStatus(_message.Message):
    __slots__ = ("is_connected", "mode", "state", "uptime", "firmware_version", "errors")
    IS_CONNECTED_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    UPTIME_FIELD_NUMBER: _ClassVar[int]
    FIRMWARE_VERSION_FIELD_NUMBER: _ClassVar[int]
    ERRORS_FIELD_NUMBER: _ClassVar[int]
    is_connected: bool
    mode: str
    state: str
    uptime: int
    firmware_version: str
    errors: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, is_connected: bool = ..., mode: _Optional[str] = ..., state: _Optional[str] = ..., uptime: _Optional[int] = ..., firmware_version: _Optional[str] = ..., errors: _Optional[_Iterable[str]] = ...) -> None: ...

class BatteryData(_message.Message):
    __slots__ = ("voltage", "percentage")
    VOLTAGE_FIELD_NUMBER: _ClassVar[int]
    PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    voltage: float
    percentage: int
    def __init__(self, voltage: _Optional[float] = ..., percentage: _Optional[int] = ...) -> None: ...

class CommandAck(_message.Message):
    __slots__ = ("success", "message", "error_code")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    ERROR_CODE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    error_code: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ..., error_code: _Optional[str] = ...) -> None: ...

class Empty(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
