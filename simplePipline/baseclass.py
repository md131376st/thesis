import logging

from simplePipline.utils.logger import Logger


class Baseclass:
    def __init__(self,name, loglevel=logging.INFO, filename=None, console=True):
        self.logger = Logger(name,
                             filename,
                             console,
                             level=loglevel).get_logger()
