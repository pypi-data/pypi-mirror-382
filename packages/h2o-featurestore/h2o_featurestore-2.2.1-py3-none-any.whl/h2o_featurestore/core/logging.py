from logging import config


class LoggingConfiguration:
    def __init__(self):
        pass

    @staticmethod
    def apply_config(log_level):
        validated_log_level = log_level.upper()
        if validated_log_level not in ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]:
            print(f"Invalid log level {log_level}, falling back to INFO")
            validated_log_level = "INFO"

        log_config = {
            "version": 1,
            "root": {"handlers": ["console"], "level": validated_log_level},
            "handlers": {
                "console": {"formatter": "std_out", "class": "logging.StreamHandler", "level": validated_log_level}
            },
            "formatters": {
                "std_out": {
                    "format": "%(asctime)s : %(levelname)s : %(message)s",
                    "datefmt": "%d-%m-%Y %I:%M:%S",
                }
            },
        }
        config.dictConfig(log_config)
