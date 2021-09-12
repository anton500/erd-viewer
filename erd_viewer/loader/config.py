import configparser

class Config():

    __FILENAME = 'erd_viewer/loader/config.ini'

    def __init__(self) -> None:
        self.config = configparser.ConfigParser(allow_no_value=True)
        self.__read_config(self.__FILENAME)
        return None

    def __read_config(self, filename: str) -> None:
        self.config.read(filename, encoding='utf-8')
        return None

config = Config().config