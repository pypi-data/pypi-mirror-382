# leafsdk/core/interfaces.py

from abc import ABC, abstractmethod

class IMavLinkProxy(ABC):
    def __init__(self):
        self.target_system: int

    @abstractmethod
    def send(self, key: str, msg, burst_count: int = 1, burst_interval: float = 0.0): ...
    @abstractmethod
    def register_handler(self, key: str, fn, duplicate_filter_interval: float = 0.0): ...
    @abstractmethod
    def unregister_handler(self, key: str, fn): ...

class IRedisProxy(ABC):
    @abstractmethod
    def publish(self, channel: str, message: str): ...
    @abstractmethod
    def register_pattern_channel_callback(self, pattern: str, callback): ...
    @abstractmethod
    def unregister_pattern_channel_callback(self, pattern: str): ...
