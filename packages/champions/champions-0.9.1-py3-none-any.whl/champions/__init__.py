import logging.config
import yaml

try:
    with open("logging.yaml", "r") as f:
        config = yaml.safe_load(f)
except FileNotFoundError:
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "simple",
                "level": "INFO",
            }
        },
        "root": {"handlers": ["console"], "level": "INFO"},
    }

logging.config.dictConfig(config)
