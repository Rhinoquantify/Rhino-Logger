import logging
import logging.handlers
import os
import sys
import traceback
from typing import NoReturn

from RhinoLogger.RhinoLoggerObject.RhinoLoggerObject import LoggerConfig


class ColoredFormatter(logging.Formatter):

    def __init__(self, fmt=None, datefmt=None):
        logging.Formatter.__init__(self, fmt, datefmt)

    def format(self, record):
        # Color escape string
        COLOR_RED = '\033[1;31m'
        COLOR_GREEN = '\033[1;32m'
        COLOR_YELLOW = '\033[1;33m'
        COLOR_BLUE = '\033[1;34m'
        COLOR_PURPLE = '\033[1;35m'
        COLOR_CYAN = '\033[1;36m'
        COLOR_GRAY = '\033[1;37m'
        COLOR_WHITE = '\033[1;38m'
        COLOR_RESET = '\033[1;0m'
        # Define log color
        LOG_COLORS = {
            'DEBUG': COLOR_BLUE + '%s' + COLOR_RESET,
            'INFO': COLOR_GREEN + '%s' + COLOR_RESET,
            'WARNING': COLOR_YELLOW + '%s' + COLOR_RESET,
            'ERROR': COLOR_RED + '%s' + COLOR_RESET,
            'CRITICAL': COLOR_RED + '%s' + COLOR_RESET,
            'EXCEPTION': COLOR_RED + '%s' + COLOR_RESET,
        }
        level_name = record.levelname
        msg = logging.Formatter.format(self, record)
        return LOG_COLORS.get(level_name, '%s') % msg


class RhinoLogger(object):
    __logger = None

    def __init__(self, logger_config: LoggerConfig) -> NoReturn:
        self.filename = logger_config.filename
        self.loggername = logger_config.loggername

        # 创建 logger 日志文件夹等
        if self.filename is None:
            self.filename = getattr(sys.modules['__main__'], '__file__', 'log.py')
            self.filename = os.path.basename(self.filename.replace('.py', '.log'))
        if not os.path.exists(os.path.abspath(os.path.dirname(self.filename))):
            os.makedirs(os.path.abspath(os.path.dirname(self.filename)))

        self.mode = logger_config.mode
        self.cmdlevel = logger_config.cmdlevel
        self.filelevel = logger_config.filelevel

        if isinstance(self.cmdlevel, str):
            self.cmdlevel = getattr(logging, self.cmdlevel.upper(), logging.DEBUG)

        if isinstance(self.filelevel, str):
            self.filelevel = getattr(logging, self.filelevel.upper(), logging.DEBUG)

        self.filefmt = logger_config.filefmt
        self.cmdfmt = logger_config.cmdfmt
        self.filedatefmt = logger_config.filedatefmt
        self.cmddatefmt = logger_config.cmddatefmt
        self.backup_count = logger_config.backup_count
        self.limit = logger_config.limit
        self.when = logger_config.when
        self.colorful = logger_config.colorful
        self.logger = None
        self.streamhandler = None
        self.filehandler = None
        if self.cmdlevel > 10:
            self.filefmt = '[%(asctime)s.%(msecs)03d] %(levelname)-8s%(message)s'
            self.cmdfmt = '[%(asctime)s.%(msecs)03d] %(levelname)-8s%(message)s'
            self.cmddatefmt = '%Y-%m-%d %H:%M:%S'
        self.set_logger(cmdlevel=self.cmdlevel)

    @classmethod
    def get_instance(cls, logger_config: LoggerConfig):
        if not cls.__logger:
            cls.__logger = RhinoLogger(logger_config)
        return cls.__logger

    def init_logger(self):
        if self.logger is None:
            self.logger = logging.getLogger(self.loggername)
        else:
            logging.shutdown()
            self.logger.handlers = []
        self.streamhandler = None
        self.filehandler = None
        self.logger.setLevel(logging.DEBUG)

    def add_streamhandler(self):
        self.streamhandler = logging.StreamHandler()
        self.streamhandler.setLevel(self.cmdlevel)
        if self.colorful:
            formatter = ColoredFormatter(self.cmdfmt, self.cmddatefmt)
        else:
            formatter = logging.Formatter(self.cmdfmt, self.cmddatefmt, )
        self.streamhandler.setFormatter(formatter)
        self.logger.addHandler(self.streamhandler)

    def add_filehandler(self):
        # Choose the filehandler based on the passed arguments
        if self.backup_count == 0:  # Use FileHandler
            self.filehandler = logging.FileHandler(self.filename, self.mode)
        elif self.when is None:  # Use RotatingFileHandler
            self.filehandler = logging.handlers.RotatingFileHandler(self.filename,
                                                                    self.mode, self.limit, self.backup_count)
        else:  # Use TimedRotatingFileHandler
            self.filehandler = logging.handlers.TimedRotatingFileHandler(self.filename,
                                                                         self.when, 1, self.backup_count)
        self.filehandler.setLevel(self.filelevel)
        formatter = logging.Formatter(self.filefmt, self.filedatefmt, )
        self.filehandler.setFormatter(formatter)
        self.logger.addHandler(self.filehandler)

    def set_logger(self, **kwargs):
        keys = ['mode', 'cmdlevel', 'filelevel', 'filefmt', 'cmdfmt', \
                'filedatefmt', 'cmddatefmt', 'backup_count', 'limit', \
                'when', 'colorful']
        for (key, value) in kwargs.items():
            if not (key in keys):
                return False
            setattr(self, key, value)
        if isinstance(self.cmdlevel, str):
            self.cmdlevel = getattr(logging, self.cmdlevel.upper(), logging.DEBUG)
        if isinstance(self.filelevel, str):
            self.filelevel = getattr(logging, self.filelevel.upper(), logging.DEBUG)
        if not "cmdfmt" in kwargs:
            self.filefmt = '[%(asctime)s.%(msecs)03d] %(filename)s line:%(lineno)d %(levelname)-8s%(message)s'
            self.filedatefmt = '%Y-%m-%d %H:%M:%S'
            self.cmdfmt = '[%(asctime)s].%(msecs)03d %(filename)s line:%(lineno)d %(levelname)-8s%(message)s'
            self.cmddatefmt = '%H:%M:%S'
            if self.cmdlevel > 10:
                self.filefmt = '[%(asctime)s.%(msecs)03d] %(levelname)-8s%(message)s'
                self.cmdfmt = '[%(asctime)s.%(msecs)03d] %(levelname)-8s%(message)s'
                self.cmddatefmt = '%Y-%m-%d %H:%M:%S'
        self.init_logger()
        self.add_streamhandler()
        self.add_filehandler()
        # Import the common log functions for convenient
        self.import_log_funcs()
        return True

    def addFileLog(self, log):
        self.logger.addHandler(log.filehandler)
        return self

    def import_log_funcs(self):
        log_funcs = ['debug', 'info', 'warning', 'error', 'critical',
                     'exception']
        for func_name in log_funcs:
            func = getattr(self.logger, func_name)
            setattr(self, func_name, func)

    def trace(self):
        info = sys.exc_info()
        for file, lineno, function, text in traceback.extract_tb(info[2]):
            self.error('%s line:%s in %s:%s' % (file, lineno, function, text))
        self.error('%s: %s' % info[:2])
