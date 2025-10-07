"""
Utilities for setting up logging in modules
"""

import datetime
import fnmatch
import logging
import os
import sys
import threading
import time
from typing import Callable, List, Optional, Union

import structlog

from . import PACKAGE_NAME, get_bool_env_variable

PROPAGATE = get_bool_env_variable(f"{PACKAGE_NAME}_LOG_PROPAGATE", False)


TELEMETRY_PROCESSORS: List[Callable] = []


def telemetry_runner(target_logger, method_name, event_dict):
    """
    Runs processors for telemetry events or events where logger is enabled for event level.
    Drops telemetry events after processing
    """
    is_telemetry_event = event_dict.get("event_type") == "telemetry"
    if is_telemetry_event:
        run_telemetry_processors(target_logger, method_name, event_dict)
        raise structlog.DropEvent
    event_level = event_dict.get("level")
    numeric_level = getattr(logging, event_level.upper(), None)
    if target_logger.isEnabledFor(numeric_level):
        run_telemetry_processors(target_logger, method_name, event_dict)
    return event_dict


def run_telemetry_processors(target_logger, method_name, event_dict):
    for processor in TELEMETRY_PROCESSORS:
        processor(target_logger, method_name, event_dict)
        return event_dict


def format_console_time(target_logger, method_name, event_dict):
    event_dict["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return event_dict


def configure(use_colors=False):
    # maya doesn't seem to play nice with colors, and once structlog is configured to use colors it seems to
    # cause problems when reconfiguring without

    if not structlog.is_configured():
        logging.basicConfig(level=logging.INFO)
        logging.Logger.propagate = bool(PROPAGATE)

    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso", utc=False),
            structlog.processors.CallsiteParameterAdder(
                {
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.PATHNAME,
                    structlog.processors.CallsiteParameter.MODULE,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                    structlog.processors.CallsiteParameter.LINENO,
                }
            ),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.UnicodeDecoder(),
            telemetry_runner,
            format_console_time,
            structlog.dev.ConsoleRenderer(colors=use_colors),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


class LogLevelContextManager:
    def __init__(self, target_logger, level):
        self.logger = target_logger
        self.level = level
        self.previous_level = target_logger.getEffectiveLevel()

    def __enter__(self):
        self.logger.setLevel(self.level)

    def __call__(self, func):
        """Allow class to be used as decorator"""

        def decorator(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return decorator

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.setLevel(self.previous_level)


class LogAllLevelsContextManager:
    def __init__(self, min_level=logging.CRITICAL):
        self.min_level = min_level

    def __enter__(self):
        logging.disable(self.min_level)

    def __call__(self, func):
        """Allow class to be used as decorator"""

        def decorator(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return decorator

    def __exit__(self, exit_type, exit_value, exit_traceback):
        logging.disable(logging.NOTSET)


class SuppressStdOutStdErr:
    """
    A context manager for doing a "deep suppression" of stdout and stderr in
    Python, i.e. will suppress all print, even if the print originates in a
    compiled C/Fortran sub-function.
       This will not suppress raised exceptions, since exceptions are printed
    to stderr just before a script exits, and after the context manager has
    exited (at least, I think that is why it lets exceptions through).

    """

    def __init__(
        self, filter_list: Optional[Union[List[str], str]] = None, enable=True
    ) -> None:
        self.enable = enable
        if self.enable:
            if filter_list is None:
                self.filter_words = []
            elif isinstance(filter_list, str):
                self.filter_words = [filter_list]
            else:
                self.filter_words = filter_list

    def __enter__(self):
        if self.enable:
            self._stdout = sys.stdout
            self._stderr = sys.stderr
            self._stdout_pipe = os.pipe()
            self._stderr_pipe = os.pipe()
            self._stdout_fd = os.dup(1)
            self._stderr_fd = os.dup(2)
            os.dup2(self._stdout_pipe[1], 1)
            os.dup2(self._stderr_pipe[1], 2)
            self._stdout_thread = self._start_thread(self._stdout_pipe[0], self._stdout)
            self._stderr_thread = self._start_thread(self._stderr_pipe[0], self._stderr)
            os.close(self._stdout_pipe[1])
            os.close(self._stderr_pipe[1])
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.enable:
            os.dup2(self._stdout_fd, 1)
            os.dup2(self._stderr_fd, 2)

            os.close(self._stdout_fd)
            os.close(self._stderr_fd)

            if self._stdout_thread.is_alive():
                self._stdout_thread.join()
            if self._stderr_thread.is_alive():
                self._stderr_thread.join()

    def _should_filter(self, line) -> bool:
        if not self.filter_words:
            return True
        line = line.strip()
        for pattern in self.filter_words:
            pattern = pattern
            if "*" in pattern:
                if fnmatch.fnmatch(line, pattern):
                    return True
            else:
                if pattern in line:
                    return True
        return False

    def _start_thread(self, read_fd, write_stream):
        def _filter_output():
            read_file = os.fdopen(read_fd)
            try:
                for line in read_file:
                    if not self._should_filter(line):
                        write_stream.write(line)
                        write_stream.flush()
            finally:
                read_file.close()

        thread = threading.Thread(target=_filter_output)
        thread.daemon = True
        thread.start()
        return thread


class ExecutionTimer:
    def __init__(self):
        self.elapsed_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, type, value, traceback):
        end_time = time.time()
        self.elapsed_time = end_time - self.start_time


class SilenceContextManager(SuppressStdOutStdErr):
    pass


class SingleLevelFilter(logging.Filter):
    def __init__(self, passlevel, reject):
        super(SingleLevelFilter, self).__init__()
        self.passlevel = passlevel
        self.reject = reject

    def filter(self, record):
        if self.reject:
            return record.levelno != self.passlevel
        else:
            return record.levelno == self.passlevel


class CustomLogger(structlog.stdlib.BoundLogger):
    timer: ExecutionTimer
    info_handler: logging.StreamHandler

    @staticmethod
    def all_log_levels(min_level=logging.CRITICAL):
        return LogAllLevelsContextManager(min_level)

    @staticmethod
    def silence(filter_list: Optional[List[str]] = None, enable=True):
        return SilenceContextManager(filter_list=filter_list, enable=enable)

    @staticmethod
    def at_level(target_logger, level):
        return LogLevelContextManager(target_logger, level)

    @staticmethod
    def info_to_stdout(target_logger=None):
        h1 = logging.StreamHandler(sys.stdout)
        f1 = SingleLevelFilter(logging.INFO, False)
        h1.addFilter(f1)
        target_logger.addHandler(h1)

    @staticmethod
    def send_telemetry(*args, **kwargs):
        """Sends message to any telemetry handlers on logger"""
        raise NotImplementedError

    def setLevel(self, level: Union[int, str]) -> None:
        super().setLevel(level)  # type: ignore[arg-type]


class TelemetryHandler:
    """Abstract class for logging handlers to send telemetry data"""

    pass


def get_logger(name) -> CustomLogger:
    """
    Simple stream-logger that can also be used as a context manager.
    Be aware of the hacky adding of methods to existing logger,
    but overriding return type to get correct inspection in IDEs
    """
    logger = structlog.stdlib.get_logger(name)  # noqa

    # Hacks since current versions of pytest doesn't allow subclassing
    # of logging.getLogger
    setattr(logger, "all_log_levels", CustomLogger.all_log_levels)

    def _silence(*args, **kwargs):
        return CustomLogger.silence(*args, **kwargs)  # noqa

    setattr(logger, "silence", _silence)

    setattr(logger, "timer", ExecutionTimer)

    def _send_telemetry(*args, **kwargs):
        kwargs["event_type"] = "telemetry"
        logger.info(*args, **kwargs)

    setattr(logger, "send_telemetry", _send_telemetry)

    def _info_to_stdout():
        return CustomLogger.info_to_stdout(logger)

    setattr(logger, "info_to_stdout", _info_to_stdout)

    def at_level(level):
        return CustomLogger.at_level(logger, level)

    setattr(logger, "at_level", at_level)
    return logger  # type: ignore[return-value]


def mock_telemetry_processor(logger, method_name, event_dict):
    print(f"Sending to some telemetry service: {event_dict}")
    return event_dict


configure()

if __name__ == "__main__":
    TELEMETRY_PROCESSORS.append(mock_telemetry_processor)
    configure(use_colors=True)
    example_logger = get_logger(__name__)
    example_logger.info("Logging configured")
    example_logger.debug(
        "This is a debug message and shouldn't be displayed as logging level is set to info"
    )
    example_logger.setLevel("DEBUG")
    with example_logger.silence(filter_list=["filtered"]):
        example_logger.info("this should be filtered out")
        example_logger.info("this should not be silenced!")
    example_logger.debug(
        "This is a debug message and should be displayed as logging level is set to debug"
    )
