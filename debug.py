import logging
import config
import os
from time_manager import TimeManager
from typing import Union
from io import BytesIO

tm = TimeManager()

class Debug:
    prefix = 'log_'
    log_file_path = os.path.join(config.LOG_DIR, f"{prefix}{tm.strftime(tm.get_now().timestamp(), tm.debugger_format)}.txt")
    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")

    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging.INFO)

    fileHandler = logging.FileHandler(log_file_path, encoding="utf-8")
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)

    logging.info("========= STARTED =========")

    def exception(self, e: BaseException):
        return self.rootLogger.exception(e)

    def debug(self, *args, **kwargs):
        return self.rootLogger.debug(*args, **kwargs)

    def info(self, *args, **kwargs):
        return self.rootLogger.info(*args, **kwargs)

    def parse_log_date(self, log_path: Union[str, os.PathLike]):
        if not log_path or not self.is_log_exists(log_path):
            return "???"

        if isinstance(log_path, str):
            log_path = os.path.join(config.LOG_PATH, log_path)

        dirs, filename = os.path.split(log_path)
        date_title = os.path.splitext(filename)[0]
        date_title = date_title.replace(self.prefix, '')
        date = tm.strptime(tm.debugger_format, date_title)
        return date

    @property
    def log_files(self):
        return [filename for filename in os.listdir(config.LOG_PATH)]

    def is_log_exists(self, log_path: Union[str, os.PathLike]):
        if isinstance(log_path, str):
            log_path = os.path.join(config.LOG_PATH, log_path)
        return os.path.exists(log_path)

    def read_log_binary(self, log_path: Union[str, os.PathLike]):
        if not self.is_log_exists(log_path):
            return
        if isinstance(log_path, str):
            log_path = os.path.join(config.LOG_PATH, log_path)

        with open(log_path, 'rb') as f:
            data = f.read()
        return data

    def read_log(self, log_path: Union[str, os.PathLike]):
        if not self.is_log_exists(log_path):
            return

        if isinstance(log_path, str):
            log_path = os.path.join(config.LOG_PATH, log_path)

        data = ""
        with open(log_path, 'rb', encoding='utf-8') as f:
            data = f.read()
        return data