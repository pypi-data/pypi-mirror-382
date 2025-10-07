# © Copyright Databand.ai, an IBM Company 2022

from __future__ import print_function

import logging
import os
import sys

from logging.config import DictConfigurator
from typing import Callable, List, Optional

from dbnd._core.log.config import configure_logging_dictConfig
from dbnd._core.log.logging_utils import (
    find_handler,
    safe_is_typeof,
    setup_log_file,
    try_init_sentry,
)
from dbnd._core.parameter.parameter_builder import parameter
from dbnd._core.task import config
from dbnd._core.utils.project.project_fs import databand_system_path


logger = logging.getLogger(__name__)


class RunLoggingConfig(config.Config):
    """Databand's logger configuration"""

    _conf__task_family = "run_log"
    disabled = parameter(
        description="Determine whether logging should be disabled."
    ).value(False)
    debug_log_config = parameter(
        description="Enable debugging our logging configuration system."
    ).value(False)

    override_airflow_logging_on_task_run = parameter(
        description="Enable replacing airflow logger with databand logger."
    ).value(True)
    support_jupyter = parameter(
        description="Support logging output to Jupiter UI."
    ).value(False)

    level = parameter(
        description="Set which logging level will be used. This could be DEBUG, INFO, WARN, or ERROR"
    ).value("INFO")
    formatter = parameter(
        description="Set the log formatting string, using the logging library convention."
    )[str]
    formatter_colorlog = parameter(
        description="Set the log formatting string, using the logging library convention."
    )[str]
    formatter_simple = parameter(
        description="Set the log formatting string, using the logging library convention."
    )[str]

    console_formatter_name = parameter(
        description="Set the name of the formatter logging to console output."
    )[str]
    file_formatter_name = parameter(
        description="Set the name of the formatter logging to file output."
    )[str]

    # sentry config
    sentry_url = parameter(
        default=None,
        description="Set the URL for setting up sentry logger. Make sure the url is exposed to dbnd run environment",
    )[str]
    sentry_env = parameter(
        default="dev", description="Set the environment for sentry logger."
    )[str]
    sentry_release = parameter(default="", description="Release for sentry logger")[str]
    sentry_debug = parameter(default=False, description="Enable debug flag for sentry")[
        bool
    ]

    file_log = parameter(
        default=None,
        description="Determine whether logger should log to a file. This is off by default",
    )[str]

    stream_stdout = parameter(
        description="Should Databand's logger stream stdout instead of stderr."
    ).value(False)

    custom_dict_config = parameter(
        default=None, description="Set customized logging configuration."
    )[Callable]

    at_warn = parameter.help("Set name of loggers to put in WARNING mode.").c[List[str]]
    at_debug = parameter.help("Set name of loggers to put in DEBUG mode.").c[List[str]]

    capture_task_run_log = parameter(
        default=True, description="Enable capturing task output into log."
    )

    send_body_to_server = parameter(
        default=True, description="Enable or disable sending log file to server."
    )[bool]

    remote_logging_disabled = parameter.help(
        "For tasks using a cloud environment, don't copy the task log to cloud storage."
    ).value(False)

    targets_log_level = parameter(
        default="DEBUG",
        description="Should log the time it takes for marshalling and unmarshalling targets.",
    )[str]

    disable_colors = parameter(default=False, description="Disable any colored logs.")

    sqlalchemy_print = parameter(description="Enable sqlalchemy logger.").value(False)
    sqlalchemy_trace = parameter(
        description="Enable tracing sqlalchemy queries."
    ).value(False)

    def _initialize(self):
        super(RunLoggingConfig, self)._initialize()
        self.task_log_file_formatter = None

    def get_dbnd_logging_config(self, filename=None):
        if self.custom_dict_config:
            logger.info("Using user provided logging config")
            return self.settings.log.custom_dict_config()

        return self.get_dbnd_logging_config_base(filename=filename)

    def get_dbnd_logging_config_base(self, filename=None):
        # type: (RunLoggingConfig, Optional[str]) -> Optional[dict]
        self.log_debug("Using log.get_dbnd_logging_config_base")
        log_settings = self
        log_level = log_settings.level
        # we want to have "real" output, so nothing can catch our handler
        # in opposite to what airflow is doing
        console_stream = (
            sys.__stdout__ if log_settings.stream_stdout else sys.__stderr__
        )

        if "ipykernel" in sys.modules and self.support_jupyter:
            # we can not use __stdout__ or __stderr__ as it will not be printed into jupyter web UI
            # at the same time  using sys.stdout when airflow is active is very dangerous
            # as it can create dangerous loop from airflow redirection into root logger

            self.log_debug("ipykernel: checking on console_stream again")
            console_stream = sys.stdout if log_settings.stream_stdout else sys.stderr

        # dummy path, we will not write to this file
        task_file_handler_file = databand_system_path("logs", "task.log")

        self.log_debug("task_file_handler_file: %s", task_file_handler_file)
        setup_log_file(task_file_handler_file)

        config = {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {
                "task_context_filter": {
                    "()": "dbnd._core.log.logging_utils.TaskContextFilter"
                }
            },
            "formatters": {
                "formatter": {"format": log_settings.formatter},
                "formatter_simple": {"format": log_settings.formatter_simple},
                "formatter_colorlog": {
                    "()": "dbnd._vendor.colorlog.ColoredFormatter",
                    "format": log_settings.formatter_colorlog,
                    "reset": True,
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "stream": console_stream,
                    "formatter": log_settings.console_formatter_name,
                    "filters": ["task_context_filter"],
                }
            },
            "root": {"handlers": ["console"], "level": log_level},
        }
        if filename:
            setup_log_file(filename)
            config["handlers"]["file"] = {
                "class": "logging.FileHandler",
                "formatter": log_settings.file_formatter_name,
                "filename": filename,
                "encoding": "utf-8",
            }
            config["root"]["handlers"].append("file")

        loggers = config.setdefault("loggers", {})
        for logger_warn in log_settings.at_warn:
            loggers[logger_warn] = {"level": logging.WARNING, "propagate": True}

        for logger_debug in log_settings.at_debug:
            loggers[logger_debug] = {"level": logging.DEBUG, "propagate": True}

        if log_settings.sqlalchemy_print:
            loggers["sqlalchemy.engine"] = {"level": logging.INFO, "propagate": True}

        self.log_debug("Log config: %s", config)
        return config

    def configure_dbnd_logging(self):
        if self.disabled:
            self.log_debug("Log is disabled, skipping configure_dbnd_logging")
            return

        # start by trying to initiate Sentry setup - has side effect of changing the logging config
        self.log_debug("Initialize Sentry setup")
        try_init_sentry(self)

        if self.disable_colors:
            self.log_debug("Colors are disabled")
            self.disable_color_logs()

        dict_config = self.get_dbnd_logging_config(filename=self.file_log)

        airflow_task_log_handler = None
        if self.override_airflow_logging_on_task_run:
            airflow_task_log_handler = self.dbnd_override_airflow_logging_on_task_run()

        try:
            self.log_debug("configure_logging_dictConfig: %s", dict_config)
            configure_logging_dictConfig(dict_config=dict_config)
        except Exception as e:
            # we print it this way, as it could be that now "logging" is down!
            print(
                "Failed to load reload logging configuration with dbnd settings! Exception: %s"
                % (e,),
                file=sys.__stderr__,
            )
            raise
        if airflow_task_log_handler:
            self.log_debug("logging.root.handlers.append(airflow_task_log_handler)")
            logging.root.handlers.append(airflow_task_log_handler)
        self.log_debug("Databand logging is up!")

    def dbnd_override_airflow_logging_on_task_run(self):
        # EXISTING STATE:
        # root logger use Console handler -> prints to current sys.stdout
        # on `airflow run` without interactive -> we have `redirect_stderr` applied that will redirect sys.stdout
        # into logger `airflow.task`, that will save everything into file.
        #  EVERY output of root logger will go through CONSOLE handler into AIRFLOW.TASK without being printed to screen

        self.log_debug("dbnd_override_airflow_logging_on_task_run")
        if not sys.stderr or not safe_is_typeof(sys.stderr, "StreamLogWriter"):
            self.log_debug(
                "Airflow logging is already replaced by dbnd stream log writer! sys.stderr=%s",
                sys.stderr,
            )
            return

        # NEW STATE
        # we will move airflow.task file handler to root level
        # we will set propogate
        # we will stop redirect of airflow logging

        # this will disable stdout ,stderr redirection
        sys.stderr = sys.__stderr__
        sys.stdout = sys.__stdout__

        airflow_root_console_handler = find_handler(logging.root, "console")

        self.log_debug("airflow_root_console_handler:%s", airflow_root_console_handler)
        if safe_is_typeof(airflow_root_console_handler, "RedirectStdHandler"):
            # we are removing this console logger
            # this is the logger that capable to create self loop
            # as it writes to "latest" sys.stdout,
            # if you have stdout redirection into any of loggers, that will propogate into root
            # you get very busy message loop that is really hard to debug

            self.log_debug("airflow_root_console_handler has been removed")
            logging.root.handlers.remove(airflow_root_console_handler)

        airflow_task_logger = logging.getLogger("airflow.task")

        self.log_debug("airflow_task_logger: %s", airflow_task_logger)
        airflow_task_log_handler = find_handler(airflow_task_logger, "task")
        if airflow_task_log_handler:
            self.log_debug("airflow_task_log_handler: %s", airflow_task_log_handler)
            logging.root.handlers.append(airflow_task_log_handler)
            airflow_task_logger.propagate = True
            airflow_task_logger.handlers = []
        self.log_debug(
            "dbnd_override_airflow_logging_on_task_run logging.root: %s", logging.root
        )
        return airflow_task_log_handler

    def get_task_log_file_handler(self, log_file):
        if not self.task_log_file_formatter:
            config = self.get_dbnd_logging_config()
            configurator = DictConfigurator(config)
            file_formatter_config = configurator.config.get("formatters").get(
                self.file_formatter_name
            )
            self.task_log_file_formatter = configurator.configure_formatter(
                file_formatter_config
            )

        log_file = str(log_file)
        setup_log_file(log_file)
        handler = logging.FileHandler(filename=log_file, encoding="utf-8")
        handler.setFormatter(self.task_log_file_formatter)
        handler.setLevel(self.level)
        return handler

    def disable_color_logs(self):
        """Removes colors from any console related config"""
        logger.debug("disabling color logs")

        os.environ["ANSI_COLORS_DISABLED"] = "True"  # disabling termcolor.colored
        self.exception_no_color = True
        if self.console_formatter_name == "formatter_colorlog":
            self.console_formatter_name = "formatter_simple"

    def log_debug(self, msg, *args):
        if not self.debug_log_config:
            if not self.disabled:
                # we don't want to print ANYTHING if we are disabled
                logger.debug(msg, *args)
            return

        try:
            # we print to stderr as well in case logging is broken
            print("DEBUG_LOG_CONFIG:" + msg % args, file=sys.__stderr__)
            logger.info("DEBUG_LOG_CONFIG:" + msg, *args)
        except Exception:
            pass
