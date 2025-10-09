"""
Common utilities
"""

import logging
import os

from pythonjsonlogger import jsonlogger

main_logger_name = ""


def configure_pyro5_logging(log_path: str = "."):
    """Configures Pyro5 logging.

    Must be before any Pyro5 import to configure logging"""

    # for info see https://pyro5.readthedocs.io/en/latest/tipstricks.html#logging

    file_handler = logging.FileHandler(os.path.join(log_path, "pyro.log"))
    file_handler.setFormatter(
        jsonlogger.JsonFormatter(
            "%(asctime) [%(levelname)8s] %(message)s %(filename)s:%(lineno)d "
        )
    )
    pyro_logger_names = [  # pyro5 packages/modules
        "Pyro5",
        "Pyro5.compatibility",
        "Pyro5.Pyro4",
        "Pyro5.utils",
        "Pyro5.utils.echoserver",
        "Pyro5.utils.httpgateway",
        "Pyro5.api",
        "Pyro5.callcontext",
        "Pyro5.client",
        "Pyro5.configure",
        "Pyro5.core",
        "Pyro5.errors",
        "Pyro5.nameserver",
        "Pyro5.nsc",
        "Pyro5.protocol",
        "Pyro5.serializers",
        "Pyro5.server",
        "Pyro5.socketutil",
        "Pyro5.svr_existingconn",
        "Pyro5.svr_multiplex",
        "Pyro5.svr_threads",
    ]

    for logger_name in pyro_logger_names:
        l = logging.getLogger(logger_name)
        l.addHandler(file_handler)
        l.setLevel(logging.INFO)


def configure_main_logger(name: str, log_level, log_path: str = "."):
    """Run-once setup of main logger that should be used by all/some modules to log into the same logger

    The main logger is logs into file in JSON format and into console in non-JSON format.
    """

    if not name:
        raise ValueError("name for main logger must be non-empty")

    # setup new main logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    file_handler = logging.FileHandler(os.path.join(log_path, f"{name}.log"))
    file_handler.setLevel(log_level)
    file_handler.setFormatter(
        jsonlogger.JsonFormatter(
            "%(asctime) [%(levelname)8s] %(message)s %(filename)s:%(lineno)d "
        )
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(log_level)
    stream_handler.setFormatter(
        logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
    )

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    # remember name for get_main_logger(...) method calls
    global main_logger_name
    main_logger_name = name

    return logger


def get_main_logger():
    """Get main logger that was already created by configure_main_logger(...) method call"""

    global main_logger_name
    if not main_logger_name:
        raise ValueError(
            "configure_main_logger must be called before this method and proper name of main logger must "
            "be set there"
        )
    return logging.getLogger(main_logger_name)


def configure_module_logger(module_name, log_level):
    """Configures logger for module"""

    logger = logging.getLogger(module_name)
    logger.setLevel(log_level)
    handler = logging.StreamHandler()
    handler.setLevel(log_level)
    logger.addHandler(handler)
    return logger
