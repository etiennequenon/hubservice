import datetime
from dataclasses import dataclass
from typing import Set, List


class User:
    def __init__(self, username: str, uuid: str, password: str, e_mail: str):
        self.username = username
        self.uuid = uuid
        self.password = password
        self.e_mail = e_mail


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
        self._premium_ads = []  # Type List[PremiumAds]
        self._private_pics = []  # Type List[PrivatePicture]
        super().__init__(username, uuid, password, e_mail)

    def publish_ad(self, title: str, description: str, prices: dict, location: Location, services: dict, ad_uuid):
        ad = [ad for ad in self._ads if ad.uuid == ad_uuid]
        if not ad:
            self._ads.append(Advertisement(title, description, datetime.datetime.now(), datetime.datetime.now() + datetime.timedelta(days=7), location, services, prices, self.uuid, True, ad_uuid))
            return self._ads[-1]
        else:
            raise AdAlreadyExist

    def un_publish_ad(self, ad_uuid: str):
        ad = next(a for a in self._ads if a.uuid == ad_uuid)
        ad.published = False
        ad.date_published = None
        ad.expiry_date = None
        return ad

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

    def update_billing(self, card_number: str, expiry_date: datetime.date, secret_code: str, fullname: str):
        self._billing = Billing(card_number, expiry_date, secret_code, fullname)
        return self._billing

    def get_ad(self, ad_uuid):
        return next(a for a in self._ads if a.uuid == ad_uuid)

    def update_ad_location(self, ad_uuid: str, street: str, number: int, city: str, zip_code: int, state: str, country: str):
        ad = next(a for a in self._ads if a.uuid == ad_uuid)
        ad.localisation = Location(street, number, city, zip_code, state, country)
        return ad

    def update_ad_services(self, ad_uuid: str, offers: dict):
        ad = next(a for a in self._ads if a.uuid == ad_uuid)
        ad.service = offers
        return ad

    def update_ad_prices(self, ad_uuid: str, prices: dict):
        ad = next(a for a in self._ads if a.uuid == ad_uuid)
        ad.prices = prices
        return ad

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


@dataclass(frozen=True)
class Comment:
    provider_uuid: str
    visitor_uuid: str
    timestamp: datetime.datetime
    content: str


class Visitor(User):
    def __init__(self, username: str, uuid: str, password: str, e_mail: str):
        self.birthday: datetime.date
        self.address: str
        self.profile_pic: bytes
        self.preferences: dict
        self.is_premium: bool
        super().__init__(username, uuid, password, e_mail)
