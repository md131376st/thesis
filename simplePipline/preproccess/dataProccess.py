from simplePipline.utils.logger import Logger


class DataPreprocess:
    def __init__(self, loglevel, content):
        self.logger = Logger("Data Cleaning",
                             None,
                             console=True,
                             level=loglevel).get_logger()
        self.content = content

    def preprocess(self):
        self.logger.info("correct_errors")
        self.correct_error()
        self.logger.info("remove duplicates and unwanted sections")
        self.remove_unwanted_data()
        self.logger.info("give data structure")
        self.structure_data()
        self.logger.info("extra steps for processing data")
        self.extra_steps()

    def correct_error(self):
        pass

    def remove_unwanted_data(self):
        pass

    def extra_steps(self):
        pass

    def structure_data(self):
        pass

    def get_content(self):
        return self.content

    def write_content(self, filepath):
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(self.content)


