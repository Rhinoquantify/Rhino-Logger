from enum import Enum, unique


@unique
class LoggerLevel(Enum):
    INFO = "INFO"
    DEBUG = "DEBUG"
    ERROR = "ERROR"

@unique
class LoggerTime(Enum):
    H = "H"
    D = "D"
