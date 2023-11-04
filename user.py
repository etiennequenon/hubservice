"""
    By Etienne Quenon
"""

import datetime
from dataclasses import dataclass, field
from typing import Set, List


@dataclass(frozen=False)
class Report:
    target_uuid: str
    owner_uuid: str
    timestamp: datetime.datetime
    content: str
    status: str
    uuid: str
    comment: list = field(default_factory=list)  # List[Comment]


def user_active(func):
    def inner1(*args, **kwargs):
        if args[0]._active is False:
            raise UserNotActive
        return func(*args, **kwargs)

    return inner1


class User:
    def __init__(self, username: str, uuid: str, password: str, e_mail: str):
        self.username = username
        self.uuid = uuid
        self.password = password
        self.e_mail = e_mail
        self._active = None  # bool

    @user_active
    def report(self, target_uuid: str, content: str, uuid: str) -> Report:  # To report a profile, an Ad, Provider, etc...
        return Report(target_uuid, self.uuid, datetime.datetime.now(), content, "NEW", uuid)

    @user_active
    def comment_report(self, report: Report, content: str, comment_uuid: str):
        if report.status == "NEW":
            raise ReportNotOpened
        comment = Comment(report.uuid, self.uuid, datetime.datetime.now(), None, content, comment_uuid)
        report.comment.append(comment)
        return report

    def __repr__(self):
        return f"<User {self.uuid}>"

    def __eq__(self, other):
        if not isinstance(self, User):
            return False
        return self.uuid == other.uuid

    def __hash__(self):
        return hash(self.uuid)

    def _disable(self):
        self._active = False

    def _activate(self):
        self._active = True


@dataclass(frozen=True)
class Location:
    street: str
    number: int
    city: str
    zip_code: int
    state: str
    country: str


@dataclass(unsafe_hash=True)
class Billing:
    card_number: str
    expiry_date: datetime.date
    secret_code: str
    fullname: str


@dataclass(unsafe_hash=True)
class PremiumAdvertisement:
    provider_uuid: str
    ad_uuid: str
    date_published: datetime.datetime
    expiry_date: datetime.datetime


class NotVip(Exception):
    """ Only a VIP Provider can do this ! """


class AdAlreadyExist(Exception):
    """ This Ad already exists ! """


class AlreadyPublished(Exception):
    """ This Ad is already published ! """


class AdvertisementAlreadyPromoted(Exception):
    """ This Ad is already promoted ! """


class SmsLimitWasReached(Exception):
    """ You reached the daily 50 SMS limit ! """


class CommentNotFound(Exception):
    """ Couldn't find your comment ! """


class ReportNotOpened(Exception):
    """ This Report is not opened ! """


class UserNotActive(Exception):
    """ This User is not active ! """


@dataclass(unsafe_hash=True)
class Advertisement:
    title: str
    description: str
    date_published: datetime.datetime
    expiry_date: datetime.datetime
    localisation: Location
    service: dict
    prices: dict
    owner: str  # User uuid
    published: bool
    uuid: str


@dataclass(unsafe_hash=True)
class PrivatePicture:
    picture: bytes
    date_published: datetime.datetime


class Provider(User):
    def __init__(self, username: str, uuid: str, password: str, e_mail: str, ads: List[Advertisement], verified: bool, vip: bool, billing: Billing):
        self.birthday: datetime.date
        self.address: str
        self.profile_pic: bytes
        self.verified = verified
        self.vip = vip
        self._ads = ads
        self._billing = billing
        self._premium_ads = []  # Type List[PremiumAdvertisement]
        self._private_pics = []  # Type List[PrivatePicture]
        super().__init__(username, uuid, password, e_mail)

    @user_active
    def publish_ad(self, title: str, description: str, prices: dict, location: Location, services: dict, ad_uuid):
        ad = [ad for ad in self._ads if ad.uuid == ad_uuid]
        if not ad:
            self._ads.append(Advertisement(title, description, datetime.datetime.now(), datetime.datetime.now() + datetime.timedelta(days=7), location, services, prices, self.uuid, True, ad_uuid))
            return self._ads[-1]
        else:
            raise AdAlreadyExist

    @user_active
    def un_publish_ad(self, ad_uuid: str):
        ad = next(a for a in self._ads if a.uuid == ad_uuid)
        ad.published = False
        ad.date_published = None
        ad.expiry_date = None
        return ad

    @user_active
    def update_ad_published_date(self, ad_uuid: str):
        if self.vip:
            ad = next(a for a in self._ads if a.uuid == ad_uuid)
            ad.date_published = datetime.datetime.now()
            ad.expiry_date = ad.date_published + datetime.timedelta(days=7)
            return ad
        else:
            raise NotVip

    def get_billing(self):
        return self._billing

    @user_active
    def update_billing(self, card_number: str, expiry_date: datetime.date, secret_code: str, fullname: str):
        self._billing = Billing(card_number, expiry_date, secret_code, fullname)
        return self._billing

    def get_ad(self, ad_uuid):
        return next((a for a in self._ads if a.uuid == ad_uuid), None)

    @user_active
    def update_ad_location(self, ad_uuid: str, street: str, number: int, city: str, zip_code: int, state: str, country: str):
        ad = next(a for a in self._ads if a.uuid == ad_uuid)
        ad.localisation = Location(street, number, city, zip_code, state, country)
        return ad

    @user_active
    def update_ad_services(self, ad_uuid: str, offers: dict):
        ad = next(a for a in self._ads if a.uuid == ad_uuid)
        ad.service = offers
        return ad

    @user_active
    def update_ad_prices(self, ad_uuid: str, prices: dict):
        ad = next(a for a in self._ads if a.uuid == ad_uuid)
        ad.prices = prices
        return ad

    @user_active
    def delete_ad(self, ad_uuid):
        ad = next(a for a in self._ads if a.uuid == ad_uuid)
        self._ads.remove(ad)

    def promote_ad_to_premium(self, ad_uuid):
        if self.vip:
            ad_premium = [ad for ad in self._premium_ads if ad.ad_uuid == ad_uuid]
            if not ad_premium:
                ad = next(a for a in self._ads if a.uuid == ad_uuid)
                ad_premium_promoted = PremiumAdvertisement(self.uuid, ad.uuid, datetime.datetime.now(), ad.expiry_date)
                self._premium_ads.append(ad_premium_promoted)
                return ad_premium_promoted
            else:
                raise AdvertisementAlreadyPromoted
        else:
            raise NotVip

    @property
    def private_pics(self):
        return self._private_pics

    @private_pics.setter
    def private_pics(self, pictures: List[PrivatePicture]):
        self._private_pics = pictures


@dataclass(unsafe_hash=True)
class Comment:
    target_uuid: str
    owner_uuid: str
    timestamp: datetime.datetime
    modif_timestamp: datetime.datetime
    content: str
    uuid: str


class Visitor(User):
    def __init__(self, username: str, uuid: str, password: str, e_mail: str, birthday: datetime.date, address: str, profile_pic: bytes, preferences: dict, is_premium: bool, comments):
        self.birthday = birthday
        self.address = address
        self.profile_pic = profile_pic
        self.preferences = preferences
        self.is_premium = is_premium
        self._sms_sent = 0
        self.comments = comments  # Type List[Comment]
        super().__init__(username, uuid, password, e_mail)

    @user_active
    def send_sms(self):
        if self._sms_sent < 50:
            self._sms_sent += 1
        else:
            raise SmsLimitWasReached

    @property
    def sms_sent(self) -> int:
        return self._sms_sent

    @user_active
    def add_comment(self, target_uuid: str, content: str, uuid: str) -> Comment:
        comment = Comment(target_uuid, self.uuid, datetime.datetime.now(), None, content, uuid)
        self.comments.append(comment)
        return comment

    @user_active
    def modify_comment(self, uuid: str, content: str) -> Comment:
        comment = next((c for c in self.comments if uuid == c.uuid), None)
        if not comment:
            raise CommentNotFound
        comment.content = content
        comment.modif_timestamp = datetime.datetime.now()
        return comment

    @user_active
    def delete_comment(self, uuid: str):
        comment = next((c for c in self.comments if uuid == c.uuid), None)
        if not comment:
            raise CommentNotFound
        self.comments.remove(comment)


class Admin(User):
    def __init__(self, username: str, uuid: str, password: str, e_mail: str):
        super().__init__(username, uuid, password, e_mail)

    @staticmethod
    def disable_user(user: User):
        user._disable()

    @staticmethod
    def activate_user(user: User):
        user._activate()


class Moderator(User):
    def __init__(self, username: str, uuid: str, password: str, e_mail: str):
        super().__init__(username, uuid, password, e_mail)

    @user_active
    def open_report(self, report: Report, comment_uuid: str):
        report.status = "PENDING"
        first_auto_comment = Comment(report.uuid, self.uuid, datetime.datetime.now(), None, f"Moderator {self.username} has opened your ticket !", comment_uuid)
        report.comment.append(first_auto_comment)
        return report

    @user_active
    def close_report(self, report: Report, comment_uuid: str):
        if report.status != "PENDING":
            raise ReportNotOpened
        report.status = "CLOSED"
        auto_comment = Comment(report.uuid, self.uuid, datetime.datetime.now(), None, f"Moderator {self.username} has closed your ticket !", comment_uuid)
        report.comment.append(auto_comment)
        return report
