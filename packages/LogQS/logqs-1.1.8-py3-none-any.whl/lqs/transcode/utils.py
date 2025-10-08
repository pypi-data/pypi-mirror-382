import os
import inspect
import logging
from typing import Optional

from pythonjsonlogger import jsonlogger


class ContextLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        kwargs["extra"] = self.extra
        return msg, kwargs

    def log(self, level, msg, *args, **kwargs):
        """
        Override the default 'log' method to inject custom contextual information into the LogRecord.
        """
        if self.isEnabledFor(level):
            frame = inspect.currentframe()
            # the frame is two levels up
            stack_info = inspect.getouterframes(frame)[3][0]
            if stack_info:
                # Extracting filename, line number, and function name from the frame
                filename = stack_info.f_code.co_filename
                lineno = stack_info.f_lineno
                func_name = stack_info.f_code.co_name
                record = self.logger.makeRecord(
                    self.logger.name,
                    level,
                    filename,
                    lineno,
                    msg,
                    args,
                    None,
                    func_name,
                    extra=self.extra,
                )
                self.logger.handle(record)


def get_logger(
    name,
    level: Optional[str] = None,
    log_to_file: bool = False,
    json_logging: bool = False,
    correlation_id: str | None = None,
):
    log_level = level or os.environ.get("LOG_LEVEL", "INFO")
    if isinstance(log_level, str):
        log_level = log_level.upper()
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    # logger.propagate = False
    if logger.hasHandlers():
        return ContextLoggerAdapter(logger, {"correlation_id": correlation_id})
    correlation_id_str = "%(correlation_id)s:" if correlation_id else ""
    if json_logging:
        formatter = jsonlogger.JsonFormatter(
            f"%(asctime)s %(levelname)s {correlation_id_str} %(name)s %(filename)s %(funcName)s %(lineno)s %(message)s"
        )
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    else:
        formatter = logging.Formatter(
            f"%(asctime)s  (%(levelname)s - %(name)s): {correlation_id_str} %(message)s"
        )
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        if log_to_file:
            handler = logging.FileHandler("lqs.log")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
    return ContextLoggerAdapter(logger, {"correlation_id": correlation_id})
