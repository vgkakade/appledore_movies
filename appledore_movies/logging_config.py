import logging
import json

# standard fields that are always present on every log record
STANDARD_FIELDS = {
    "name",
    "msg",
    "args",
    "levelname",
    "levelno",
    "pathname",
    "filename",
    "module",
    "exc_info",
    "exc_text",
    "stack_info",
    "lineno",
    "funcName",
    "created",
    "msecs",
    "relativeCreated",
    "thread",
    "threadName",
    "processName",
    "process",
    "message",
    "taskName",
}


def is_serializable(value):
    try:
        json.dumps(value)
        return True
    except (TypeError, ValueError):
        return False


class CustomFormatter(logging.Formatter):
    def format(self, record):
        # call parent to populate record.message and record.asctime
        super().format(record)

        # extract only the extra fields by filtering out standard ones
        extra_fields = {
            key: value
            for key, value in record.__dict__.items()
            if key not in STANDARD_FIELDS and is_serializable(value)
        }

        # build a structured log dict with standard fields + extras
        log_entry = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "process": record.process,
            "thread": record.thread,
            **extra_fields,  # spread all extra fields in
        }

        return json.dumps(log_entry)


def get_logging_config(debug):
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "custom": {
                "()": "appledore_movies.logging_config.CustomFormatter",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "custom",
            },
        },
        "loggers": {
            "django": {"handlers": ["console"], "level": "WARNING", "propagate": False},
            "django.request": {
                "handlers": ["console"],
                "level": "ERROR",
                "propagate": False,
            },
            "django.db.backends": {
                "handlers": ["console"],
                "level": "WARNING",
                "propagate": False,
            },
            "": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
        },
    }
