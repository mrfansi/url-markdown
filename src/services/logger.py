import logging
from typing import Optional, Protocol
import threading
import queue
import datetime
import os
from abc import ABC, abstractmethod

class LogObserver(Protocol):
    def on_log_message(self, level: str, message: str, timestamp: str) -> None:
        """Called when a new log message is available."""
        pass

class LoggerService:
    _instance = None
    _lock = threading.Lock()
    _log_queue = queue.Queue()
    _observers: list[LogObserver] = []

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._setup_logger()
            return cls._instance

    @classmethod
    def _setup_logger(cls):
        logger = logging.getLogger('URLMarkdown')
        logger.setLevel(logging.DEBUG)

        # Ensure logs directory exists
        logs_dir = 'logs'
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)

        # File handler
        file_handler = logging.FileHandler(os.path.join(logs_dir, 'url_markdown.log'))
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Queue handler
        queue_handler = logging.Handler()
        queue_handler.emit = lambda record: cls._handle_log_record(record)
        logger.addHandler(queue_handler)

        cls.logger = logger

    @classmethod
    def _handle_log_record(cls, record):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for observer in cls._observers:
            observer.on_log_message(record.levelname, record.message, timestamp)

    def add_observer(self, observer: LogObserver):
        self._observers.append(observer)

    def remove_observer(self, observer: LogObserver):
        if observer in self._observers:
            self._observers.remove(observer)

    def debug(self, message: str):
        self.logger.debug(message)

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)
    
    @classmethod
    def get_logger(cls) -> 'LoggerService':
        return LoggerService()