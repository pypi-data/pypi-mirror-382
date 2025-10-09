"""
Copy this file into your project
to manage your logging configuration there.
Don't forget to change the name of your app and the names of your loggers here!

Use it like this:

    from logging import getLogger
    from logging.config import dictConfig as configure_logging

    from .logging_conf import logging_configuration


    configure_logging(logging_configuration)

    logger = getLogger(__name__)
"""

from pathlib import Path

from platformdirs import user_log_dir

MY_APP_NAME = "ci-starter".replace("-", "_")

logging_dir = Path(user_log_dir(MY_APP_NAME))
logging_dir.mkdir(parents=True, exist_ok=True)
logfile = logging_dir / "debug.log"


def create_dict_config(logfile: Path) -> dict[str, str]:
    custom_file_formatter_conf = {
        "format": "{message:<50s} {levelname:>9s} {asctime}.{msecs:03.0f} {module}({lineno}) {funcName}",
        "style": "{",
        "datefmt": "%a %H:%M:%S",
    }

    custom_console_formatter_conf = {
        "format": "{message:<50s} {levelname:>9s} {module}({lineno}) {funcName}",
        "style": "{",
        "datefmt": "%a %H:%M:%S",
    }

    root_file_formatter_conf = {
        "format": f"[ROOT LOG] {custom_file_formatter_conf['format']}",
        "style": "{",
        "datefmt": "%a %H:%M:%S",
    }

    root_console_formatter_conf = {
        "format": f"[ROOT LOG] {custom_console_formatter_conf['format']}",
        "style": "{",
        "datefmt": "%a %H:%M:%S",
    }

    formatters_dict = {
        "custom_file_formatter": custom_file_formatter_conf,
        "custom_console_formatter": custom_console_formatter_conf,
        "root_file_formatter": root_file_formatter_conf,
        "root_console_formatter": root_console_formatter_conf,
    }

    custom_console_handler_conf = {
        "class": "logging.StreamHandler",
        "level": "DEBUG",
        "formatter": "custom_console_formatter",
        "stream": "ext://sys.stderr",
    }

    custom_file_handler_conf = {
        "class": "logging.FileHandler",
        "level": "DEBUG",
        "formatter": "custom_file_formatter",
        "filename": logfile,
        "mode": "w",
        "encoding": "utf-8",
    }

    root_console_handler_conf = {
        "class": "logging.StreamHandler",
        "level": "DEBUG",
        "formatter": "root_console_formatter",
        "stream": "ext://sys.stderr",
    }

    root_file_handler_conf = {
        "class": "logging.FileHandler",
        "level": "DEBUG",
        "formatter": "root_file_formatter",
        "filename": logfile.with_stem(f"{logfile.stem}_root"),
        "mode": "w",
        "encoding": "utf-8",
    }

    handlers_dict = {
        "custom_console_handler": custom_console_handler_conf,
        "custom_file_handler": custom_file_handler_conf,
        "root_console_handler": root_console_handler_conf,
        "root_file_handler": root_file_handler_conf,
    }

    custom_logger_conf = {
        "propagate": False,
        "handlers": ["custom_file_handler", "custom_console_handler"],
        "level": "DEBUG",
    }

    root_logger_conf = {
        "handlers": ["root_file_handler", "root_console_handler"],
        "level": "WARNING",
    }

    loggers_dict = {
        MY_APP_NAME: custom_logger_conf,
        "__main__": custom_logger_conf,
    }

    dict_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": formatters_dict,
        "handlers": handlers_dict,
        "loggers": loggers_dict,
        "root": root_logger_conf,
        "incremental": False,
    }

    return dict_config


logging_configuration = create_dict_config(logfile)
