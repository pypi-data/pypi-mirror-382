import logging
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, List
# import locals

class Logger:
    debug_level : int = logging.INFO
    std_logger  : logging.Logger   = logging.getLogger("std_logger")
    file_logger : Optional[logging.Logger] = None

    @staticmethod
    def InitializeLogger(level:int, use_logfile:bool):
        """Function to set up the stdout and file loggers of the Logging package.

        :param level: The logging level, which must be one of the levels defined by the Python `logging` package (`ERROR`, `WARN`, `INFO`, or `DEBUG`)
        :type level: int
        :param use_logfile: Bool for whether to use file output for logging or not.
        :type use_logfile: bool
        """
        # Set up loggers. First, the std out logger
        if not Logger.std_logger.hasHandlers():
            stdout_handler = logging.StreamHandler()
            Logger.std_logger.addHandler(stdout_handler)
            print("Added handler to std_logger")
        else:
            Logger.std_logger.warning(f"Trying to add a handler to std_logger, when handlers ({Logger.std_logger.handlers}) already exist!")
        _valid_levels = {logging.ERROR, logging.WARN, logging.WARNING, logging.INFO, logging.DEBUG}
        if level in _valid_levels:
            Logger.std_logger.setLevel(level=level)
        else:
            Logger.std_logger.setLevel(level=logging.INFO)
            Logger.std_logger.info("No valid logging level given, defaulting to INFO.")
        Logger.std_logger.info("Initialized standard out logger")

        # Then, set up the file logger. Check for permissions errors.
        if use_logfile:
            Logger.file_logger = logging.getLogger("file_logger")
            Logger.file_logger.setLevel(level=logging.DEBUG)
            # file_logger.setLevel(level=logging.DEBUG)
            try:
                err_handler = logging.FileHandler("./ExportErrorReport.log", encoding="utf-8")
                debug_handler = logging.FileHandler("./ExportDebugReport.log", encoding="utf-8")
            except PermissionError as err:
                Logger.std_logger.exception(f"Failed permissions check for log files. No file logging on server.")
            else:
                Logger.std_logger.info("Successfully set up logging files.")
                err_handler.setLevel(level=logging.WARNING)
                Logger.file_logger.addHandler(err_handler)
                debug_handler.setLevel(level=logging.DEBUG)
                Logger.file_logger.addHandler(debug_handler)
            finally:
                Logger.file_logger.debug("Initialized file logger")
    
    @staticmethod
    def Log(message:str, level:int=logging.INFO, depth:int=0, whitespace_adjust:Optional[str]=None) -> None:
        """Function to print a method to both the standard out and file logs.

        Useful for "general" errors where you just want to print out the exception from a "backstop" try-catch block.

        :param message: The log message to display.
            Some additional formatting, such as displaying the log level, is automatically added.
        :type message: str
        :param level: Logging level at which to output the message, defaults to logging.INFO
        :type level: _type_, optional
        :param depth: The number of levels to indent the message (indent width=2).
            This allows for nice indentation of logging messages, useful for complex programs with multiple levels of "nested" behaviors to log.
            Defaults to 0
        :type depth: int, optional
        :param whitespace_adjust: how to handle leading whitespace in the message.
            If set to 'dedent', shared indentation will be removed, but relative indentation in the message will be preserved.
            If set to 'lstrip', all leading whitespace on each line will be removed, and relative indentation will be lost.
            Otherwise, all leading whitespace, including relative indentation, is preserved.
            Defaults to None
        :type whitespace_adjust: Optional[str], optional
        """
        now = datetime.now().strftime("%y-%m-%d %H:%M:%S")
        INDENT_WIDTH = 2
        base_indent = ' '*9
        user_indent = ' '*INDENT_WIDTH*depth
        line_indent = f"\n{base_indent}{user_indent}"
        indented_msg : str
        match whitespace_adjust:
            case "lstrip":
                indented_msg = line_indent.join(line.lstrip() for line in message.split("\n"))
            case "dedent":
                indented_msg = textwrap.dedent(message).replace("\n", line_indent)
            case _:
                indented_msg = message.replace("\n", line_indent)
        if Logger.file_logger is not None:
            match level:
                case logging.DEBUG:
                    Logger.file_logger.debug(   f"DEBUG:   {now} {user_indent}{indented_msg}")
                case logging.INFO:
                    Logger.file_logger.info(    f"INFO:    {now} {user_indent}{indented_msg}")
                case logging.WARNING:
                    Logger.file_logger.warning( f"WARNING: {now} {user_indent}{indented_msg}")
                case logging.ERROR:
                    Logger.file_logger.error(   f"ERROR:   {now} {user_indent}{indented_msg}")
        if Logger.std_logger is not None:
            match level:
                case logging.DEBUG:
                    Logger.std_logger.debug(   f"DEBUG:   {user_indent}{indented_msg}")
                case logging.INFO:
                    Logger.std_logger.info(    f"INFO:    {user_indent}{indented_msg}")
                case logging.WARNING:
                    Logger.std_logger.warning( f"WARNING: {user_indent}{indented_msg}")
                case logging.ERROR:
                    Logger.std_logger.error(   f"ERROR:   {user_indent}{indented_msg}")

    @staticmethod
    def debug(message:str, depth:int=0, whitespace_adjust:Optional[str]=None) -> None:
        Logger.Log(message=message, level=logging.DEBUG, depth=depth, whitespace_adjust=whitespace_adjust)

    @staticmethod
    def info(message:str, depth:int=0, whitespace_adjust:Optional[str]=None) -> None:
        Logger.Log(message=message, level=logging.INFO, depth=depth, whitespace_adjust=whitespace_adjust)

    @staticmethod
    def warning(message:str, depth:int=0, whitespace_adjust:Optional[str]=None) -> None:
        Logger.Log(message=message, level=logging.WARNING, depth=depth, whitespace_adjust=whitespace_adjust)

    @staticmethod
    def error(message:str, depth:int=0, whitespace_adjust:Optional[str]=None) -> None:
        Logger.Log(message=message, level=logging.ERROR, depth=depth, whitespace_adjust=whitespace_adjust)

    @staticmethod
    def Print(message:str, level=logging.DEBUG) -> None:
        match level:
            case logging.DEBUG:
                print(f"debug:   {message}")
            case logging.INFO:
                print(f"info:    {message}")
            case logging.WARNING:
                print(f"warning: {message}")
            case logging.ERROR:
                print(f"error:   {message}")
