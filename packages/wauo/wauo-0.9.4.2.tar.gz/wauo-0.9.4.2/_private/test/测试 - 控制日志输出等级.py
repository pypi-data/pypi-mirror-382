import sys

from loguru import logger


class Loger:
    def __init__(self, level="INFO", file=None):
        self.logger = logger
        self.remove()
        self.logger.add(file or sys.stdout, level=level)  # 设置日志级别

    def test(self):
        self.logger.debug("Ok")
        self.logger.info("OK")
        self.logger.warning("OK")
        self.logger.error("Care")
        self.logger.critical("Oh My God")

    def __getattr__(self, item):
        return getattr(self.logger, item)


def test():
    loger = Loger(level="INFO")
    loger.test()


if __name__ == '__main__':
    test()
