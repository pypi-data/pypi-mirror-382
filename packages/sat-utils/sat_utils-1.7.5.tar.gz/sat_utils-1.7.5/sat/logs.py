import logging
import os


class SATLogger:
    def __init__(self, name: str = __name__, level: int = logging.INFO) -> None:
        self.logger = logging.getLogger(name)
        if os.getenv("DEBUG"):
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(level)
        self.formatter = ExtraTextFormatter()
        self.handler = logging.StreamHandler()
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)

    def add_handlers(self, handlers: list[(logging.Handler, logging.Formatter)]) -> None:
        """
        Add additional handlers to the logger.
        Handlers should be a list of tuples with a logging.Handler and an
        optional logging.Formatter.
        """
        for tup in handlers:
            handler, formatter = tup
            if formatter:
                handler.setFormatter(formatter)
            else:
                handler.setFormatter(self.formatter)
            self.logger.addHandler(handler)

    def debug(self, msg: str, *args, **kwargs) -> None:
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs) -> None:
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs) -> None:
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs) -> None:
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs) -> None:
        self.logger.critical(msg, args, kwargs)


class DjangoSATLogger:
    """
    Just a wrapper class around the default logger

    This exists just to keep the client side implementation of logging similar between the
    django/celery applications and the other python services in our stack.

    The default SATLogger implementation doesn't play nicely with UWSGI/Django/Celery altogether;
    Django manages logging configuration through it's built in settings module.
    The desired extra-argument formatter should be passed to
    """

    def __init__(self, name: str = __name__, level: int = logging.INFO) -> None:
        self.logger = logging.getLogger(name)

    def debug(self, msg: str, *args, **kwargs) -> None:
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs) -> None:
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs) -> None:
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs) -> None:
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs) -> None:
        self.logger.critical(msg, args, kwargs)


class ExtraTextFormatter(logging.Formatter):
    """
    Modifies the log format used based on the presence of extra variables in the log message

    Some log messages contain additional data to help track processes across multiple services.
    If a normal static formatter were used, then log messages without these extra args
    would contain blank formatting for those parameters,
    making the logs more difficult to read.

    The format method here dynamically builds out a text formatted addition to the log line,
    only including keys that were provided in the extra argument for the logger call.
    The appended output will look like
    ```
    asctime module.name This is the log message cid=8675309 first_name=Tommy last_name=TwoTone
    ```
    """

    def format(self, record):
        log_format = "%(asctime)s %(levelname)s %(name)s %(message)s "

        # Convert attribute style extra args on the log record into optional values in a dictionary
        existing_extra_args = dict()
        extra_to_check = ["cid", "first_name", "last_name"]
        for extra_arg in extra_to_check:
            try:
                existing_extra_args[extra_arg] = getattr(record, extra_arg)
            except AttributeError:
                pass

        if existing_extra_args:
            # Iterate through extra args and add argument name and value template to output format
            for existing_extra in existing_extra_args.keys():
                log_format += f"{existing_extra}=%({existing_extra})s "

        return logging.Formatter(fmt=log_format).format(record)
