import logging


class Logger:
    def __init__(self, name, level=logging.INFO):
        # Create a custom logger
        self.logger = logging.getLogger(name)

        # Set the default log level
        self.logger.setLevel(level)


        # Create handlers
        c_handler = logging.StreamHandler()  # Console handler
        f_handler = logging.FileHandler('file.log')  # File handler

        # Create formatters and add them to the handlers
        c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        c_handler.setFormatter(c_format)
        f_handler.setFormatter(f_format)

        # Add handlers to the logger
        self.logger.addHandler(c_handler)
        self.logger.addHandler(f_handler)
    def get_logger(self):
        return self.logger


log =Logger("hi", logging.DEBUG ).get_logger()
log.warning("hi")
log.debug("hi")