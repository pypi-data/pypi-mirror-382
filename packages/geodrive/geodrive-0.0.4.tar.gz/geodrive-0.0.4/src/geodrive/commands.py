from enum import Enum, auto


class RoverCommands(Enum):
    SET_VELOCITY = auto()
    SET_DIFF_SPEED = auto()
    LED_CONTROL = auto()
    LED_CUSTOM = auto()
    STOP = auto()
    EMERGENCY_STOP = auto()
    GET_TELEMETRY = auto()
    GET_BATTERY = auto()
    GET_STATUS = auto()
    GOTO = auto()
    GOTO_CANCEL = auto()
    MOO = auto()
    BEEP = auto()