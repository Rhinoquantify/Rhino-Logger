from dataclasses import dataclass
from typing import Union, Dict, List
from RhinoLogger.RhinoLoggerObject.RhinoLoggerEnum import LoggerLevel, LoggerTime


@dataclass
class LoggerConfig:
    loggername: str = ''
    filename: str = None
    mode: str = 'a'
    cmdlevel: Union[LoggerLevel] = LoggerLevel.DEBUG.value
    filelevel: Union[LoggerLevel] = LoggerLevel.INFO.value
    cmdfmt: str = '[%(asctime)s] %(filename)s line:%(lineno)d %(levelname)-8s%(message)s'
    filefmt: str = '[%(asctime)s] %(levelname)-8s%(message)s'
    cmddatefmt: str = '%H:%M:%S',
    filedatefmt: str = '%Y-%m-%d %H:%M:%S',
    backup_count: int = 5
    limit: int = 20480
    when: Union[LoggerTime] = LoggerTime.D.value
    colorful: bool = True
