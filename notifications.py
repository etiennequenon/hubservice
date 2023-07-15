"""
    By Etienne Quenon
"""
import abc


class AbstractNotifications(abc.ABC):
    @abc.abstractmethod
    def send(self, to, message: str):
        raise NotImplementedError
