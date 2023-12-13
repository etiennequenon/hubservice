"""
    By Etienne Quenon
"""

import abc


class AbstractDatabase(abc.ABC):
    @abc.abstractmethod
    def create(self, obj: object):
        raise NotImplementedError

    @abc.abstractmethod
    def read(self, uuid: str):
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, uuid: str):
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, obj: object):
        raise NotImplementedError

