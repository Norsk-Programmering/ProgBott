import os
from logging import Formatter, StreamHandler, getLogger
from logging.handlers import RotatingFileHandler


class Logger(object):
    def __init__(self, location, to_file, level="info"):
        self.log_location = location + "/logs/"
        self.log_level = level
        log_dir = f"{self.log_location}/bot.log"

        self.logger = getLogger("logger")
        self.logger.setLevel(self.log_level)

        log_formatter = Formatter("%(asctime)s : %(levelname)s : %(module)s : %(message)s", "%Y-%m-%d %H:%M:%S")

        if to_file:
            if not os.path.isdir(self.log_location):
                os.makedirs(self.log_location)
                self.logger.info("Creating logging directory: %s", self.log_location)
            self.logger.debug("Logging directory: %s" % log_dir)
            file_handler = RotatingFileHandler(log_dir, mode="a", maxBytes=5000,
                                               encoding="UTF-8", delay=0, backupCount=5)
            file_handler.setLevel(self.log_level)
            file_handler.setFormatter(log_formatter)
            self.logger.addHandler(file_handler)

        console_handler = StreamHandler()
        console_handler.setFormatter(log_formatter)
        console_handler.setLevel(self.log_level)

        self.logger.addHandler(console_handler)
