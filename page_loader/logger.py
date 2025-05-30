from datetime import datetime
import logging
from dotenv import load_dotenv
import os

LOGS_DIR = 'logs'
LOG_FILE_TEMPLATE = 'download_{formatted_page_content_filename}_{date_time}.log'
TIME_FORMAT = '%Y%m%d_%H%M%S'


class Logger:
    def __init__(self, page_content_filename):
        self.log_level = self.__get_level()
        self.log_path = self.__get_log_file_path(page_content_filename)
        self.__logger = logging.getLogger(__name__)
        self.__configure_logger()

    def debug(self, message):
        self.__logger.debug(message)

    def info(self, message):
        self.__logger.info(message)

    def error(self, message):
        self.__logger.error(message)

    def __configure_logger(self):
        self.__logger.setLevel(self.log_level)

        if self.log_level == logging.DEBUG:
            self.__formatter = logging.Formatter(
                fmt='[%(asctime)s %(levelname)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        else:
            self.__formatter = logging.Formatter(fmt='%(message)s')

        self.__add_console_handler()

        if self.log_level < logging.INFO:
            self.__add_file_handler()

    @staticmethod
    def __get_log_file_path(filename):
        log_file_dir = LOGS_DIR
        formatted_page_content_filename = filename.rstrip('.html')
        date_time = datetime.now().strftime(TIME_FORMAT)
        log_file_name = LOG_FILE_TEMPLATE.format(
            formatted_page_content_filename=formatted_page_content_filename,
            date_time=date_time)
        return os.path.join(log_file_dir, log_file_name)

    @staticmethod
    def __get_level():
        load_dotenv()
        env = os.environ.get('ENV', 'production')
        log_level = logging.DEBUG if env != 'production' else logging.INFO
        return log_level

    def __add_file_handler(self):
        file_handler = logging.FileHandler(self.log_path)
        file_handler.setFormatter(self.__formatter)
        self.__logger.addHandler(file_handler)

    def __add_console_handler(self):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self.__formatter)
        self.__logger.addHandler(console_handler)
