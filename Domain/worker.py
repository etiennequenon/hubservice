"""
    By Etienne Quenon
"""
from __future__ import annotations
import abc
import database


class AbstractWorker(abc.ABC):
    db: database.AbstractDatabase

    def __enter__(self) -> AbstractWorker:
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self):
        self._commit()

    @abc.abstractmethod
    def _commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError
