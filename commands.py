"""
    By Etienne Quenon
"""
from dataclasses import dataclass, field
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


@dataclass
class AddComment(Command):
    target_uuid: str
    owner: str
    content: str


@dataclass
class ModifyComment(Command):
    owner: str
    uuid: str
    content: str


@dataclass
class DeleteComment(Command):
    owner: str
    uuid: str


@dataclass
class SendSms(Command):
    user_uuid: str
    to: str
    message: str


@dataclass
class Report(Command):
    owner: str
    target_uuid: str
    content: str


@dataclass
class CommentReport(Command):
    owner: str
    target_uuid: str
    content: str


@dataclass
class OpenReport(Command):
    moderator_uuid: str
    report_uuid: str


@dataclass
class CloseReport(Command):
    moderator_uuid: str
    report_uuid: str


@dataclass
class ActivateUser(Command):
    admin_uuid: str
    user_uuid: str


@dataclass
class DisableUser(Command):
    admin_uuid: str
    user_uuid: str


@dataclass
class SetPrivatePics(Command):
    pictures: field(default_factory=list)  # List[bytes]
    user_uuid: str
