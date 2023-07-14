"""
    By Etienne Quenon
"""
from dataclasses import dataclass
import datetime
import user


class Command:
    pass


@dataclass
class PublishAdvertisement(Command):
    title: str
    description: str
    localisation: user.Location
    service: dict
    prices: dict
    owner: str  # User uuid


@dataclass
class UnPublishAdvertisement(Command):
    owner: str
    uuid: str


@dataclass
class UpdateAdvertisementPublishedDate(Command):
    owner: str
    uuid: str


@dataclass
class PromoteAdvertisementToPremium(Command):
    owner: str
    uuid: str


@dataclass
class DeleteAdvertisement(Command):
    owner: str
    uuid: str
