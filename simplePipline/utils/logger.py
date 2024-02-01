import logging


class Logger:
    def __init__(self, name, filepath, console=True, level=logging.INFO):
        # Create a custom logger
        self.logger = logging.getLogger(name)
        # Set the default log level
        self.logger.setLevel(level)

        # Create handlers
        if console:
            c_handler = logging.StreamHandler()  # Console handler
            c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
            c_handler.setFormatter(c_format)
            self.logger.addHandler(c_handler)
        if filepath is not None:
            f_handler = logging.FileHandler(filepath)  # File handler
            f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            f_handler.setFormatter(f_format)
            self.logger.addHandler(f_handler)

    def get_logger(self):
        return self.logger


