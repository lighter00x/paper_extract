import logging
import datetime

class Log:
    def __init__(self, log_file="app.log"):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)  # 设置 logger 的总级别为 DEBUG，以便所有级别的消息都能被处理

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # 创建文件处理器（File Handler）并将 DEBUG 级别及以上的日志写入文件
        self.file_handler = logging.FileHandler(log_file, encoding='utf-8')
        self.file_handler.setLevel(logging.DEBUG)
        self.file_handler.setFormatter(formatter)
        self.logger.addHandler(self.file_handler)

        # 创建控制台处理器（Stream Handler）并将 INFO 级别及以上的日志输出到控制台
        self.stream_handler = logging.StreamHandler()
        self.stream_handler.setLevel(logging.INFO)
        self.stream_handler.setFormatter(formatter)
        self.logger.addHandler(self.stream_handler)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)

if __name__ == '__main__':
    # 示例用法
    log = Log(log_file="my_app.log")

    log.debug("这是一个调试信息 (仅在文件中)")
    log.info("这是一个普通信息 (在文件和控制台)")
    log.warning("这是一个警告信息 (在文件和控制台)")
    log.error("这是一个错误信息 (在文件和控制台)")
    log.critical("这是一个严重错误信息 (在文件和控制台)")

    print("日志信息已输出到控制台 (INFO 及以上) 和 my_app.log 文件 (DEBUG 及以上) 中。")
